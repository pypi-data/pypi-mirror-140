import json, os
from os.path import isfile, join
from jennie.userinput import UserInput
from jennie.filehandler import upload_angular_ui_component, upload_image
from jennie.api_calls import APICalls
from jennie.filehandler import add_file_from_link, add_script_to_angular_index_html

def check_if_angular_project(directory):
    """
    Check if directory is an angular project
    :param directory: directory path
    :return: Boolean
    """
    if directory[-1] != "/":
        directory += "/"
    search_files = [
        "angular.json", "karma.conf.js",
        "package.json"
    ]
    print("Checking Project Type Directory for ", directory)
    is_angular = True
    for file in search_files:
        if not os.path.isfile(directory + file):
            is_angular = False

    return is_angular

def check_angular_ui_module_files(directory):
    """
    Check if directory contain files releated to angular ui module
    :param directory: directory to search for
    :return: Files or raise error.
    """
    component_name = directory.split("/")[-1]
    if len(component_name) < 3:
        component_name = directory.split("/")[-2]
    files = [f for f in os.listdir(directory) if isfile(join(directory, f))]
    if component_name + ".component.ts" not in files:
        raise ValueError("Missing TS file for the component")
    elif component_name + ".component.css" not in files:
        raise ValueError("Missing CSS file for the component")
    elif component_name + ".component.html" not in files:
        raise ValueError("Missing CSS file for the component")
    return files

def does_angular_ui_gallery_exits(app_name, token):
    """
    Validates the existence of app on jennie server
    :param app_name: Name to validate
    :param token: User Token
    :return: boolean
    """
    response = APICalls().get(
        "https://api.ask-jennie.com/v1/angular/ui-lib/validate/",
        params={"app_name": app_name},
        headers={"token": token}
    )
    if not response["payload"]:
        return False
    return True

def create_angular_ui_module_conf(app_name, output_directory, token):
    """
    Get Title, Description, Image path, Tag from User.
    Upload Angular UI Component files.
    Create Jennie Conf
    :param app_name: App name to create Angular UI Module Conf
    :param output_directory: Directory to upload
    :param token: User Token
    :return: jennie conf
    """
    user_inputs = {
        "app_title": "Title for UI module", "app_description": "Description for UI module",
        "app_image": "Image file path, complete path of image", "tag": "Tag (optional) for module",
    }
    user_inputs = UserInput().take_user_input(user_inputs)
    resp = upload_angular_ui_component(app_name, output_directory, token)
    image_path = upload_image(user_inputs["app_image"], token)["image_link"]
    jennie_conf = {
        "css_file_path": "", "ts_file_path": "", "html_file_path": "",
        "scripts": {}, "app_name": app_name, "tag": user_inputs["tag"],
        "stack": "angular", "app_image": image_path, "app_title": user_inputs["app_title"],
        "app_description": user_inputs["app_description"], "type": "angular-ui-lib"
    }
    for key in resp:
        if "component.css" in key:
            jennie_conf["css_file_path"] = resp[key]
            print("Uploaded CSS File")
        elif "component.html" in key:
            jennie_conf["html_file_path"] = resp[key]
            print("Uploaded HTML File")
        elif "component.ts" in key:
            jennie_conf["ts_file_path"] = resp[key]
            print("Uploaded TS File")

    with open('jennie.conf.json', 'w') as f:
        json.dump(jennie_conf, f, ensure_ascii=False, indent=4)

    return jennie_conf

def download_and_update_ui_module_files(resp_json, output_dir):
    """
    Download Files related to ui modules from api
    response and update the same to output directory
    :param resp_json: JSON response for UI Module
    :param output_dir: Output Directory.
    :return: True
    """
    css_file_path, ts_file_path = resp_json["css_file_path"], resp_json["ts_file_path"]
    html_file_path, scripts = resp_json["html_file_path"], json.loads(resp_json["scripts"])
    add_file_from_link(html_file_path, output_dir)
    add_file_from_link(css_file_path, output_dir)
    add_file_from_link(ts_file_path, output_dir)

    # add scripts to index.html
    for script_path in scripts:
        script_link = scripts[script_path]
        add_file_from_link(script_link, script_path)
        add_script_to_angular_index_html(script_path)

    return True

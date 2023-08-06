import requests
from jennie.api_calls import APICalls

IMAGE_UPLOAD_API = "https://api.ask-jennie.com/v1/image_upload/"
TEXT_UPLOAD_API = "https://api.ask-jennie.com/v1/file_upload/"

def upload_image(image_file_path, token):
    files = {'media': open(image_file_path, 'rb')}
    image_res = requests.post(IMAGE_UPLOAD_API, headers={ "token": token }, files=files)
    return image_res.json()["payload"]


def upload_text_file(text_file_path, token, app_name, type):
    json_content = {
        "file_content": open(text_file_path, 'r').read(),
        "app_name": app_name,
        "filename": text_file_path.split("/")[-1],
        "type": type
    }
    text_res = requests.post(TEXT_UPLOAD_API, headers={ "token": token }, json=json_content)
    return text_res.json()["payload"]


def upload_angular_ui_component(app_name, filepath, token):
    files = [".component.ts", ".component.css", ".component.html"]
    if filepath[-1] != "/":
        filepath += "/"
    response = { }
    for file in files:
        current_file_path = filepath + app_name + file
        file_link = upload_text_file(current_file_path, token, app_name, "angular-ui-lib")["file_link"]
        response[file] = file_link

    return response

def add_file_from_link(link, output_directory):
    output_file_path = output_directory + link.split("/")[-1]
    output_file_content = APICalls().get_text(link)
    open(output_file_path, "w").write(output_file_content)
    return True

def add_script_to_angular_index_html(script_path):
    return True
import os
from jennie.angular.helper import check_if_angular_project
from jennie.api_calls import APICalls
from jennie.setup import get_user_access_token, get_dummy_user_access_token
from jennie.angular.automations import *
from jennie.angular.uigallery import AngularUILibrary

def upload_library():
    """
    Upload Angular Component as library on Jennie Server.
    Shell command : jennie angular upload ui-lib
    :return: upload status
    """
    # status = UploadLib().upload_ui_component
    AngularUILibrary().upload_library_module()
    return True

def update_library():
    """
    Update Angular Component on Jennie Server.
    Shell command : jennie angular update ui-lib
    :return: upload status
    """
    AngularUILibrary().update_library_module()
    print("Uploaded UI Component Successful")
    return True

def install_angular_ui_lib(app_name):
    """
    Download Angular Component from Jennie Server and Install in Angular project.
    Upload Angular Component as library on Jennie Server.
    Shell command : jennie angular install libraryname
    :param app_name:
    :return:
    """

    status = AngularUILibrary().add_library_module(app_name=app_name)
    if status:
        print("UI Component Added Successfully\nComponent Tag: <app-{0}>/<app-{0}>".format(app_name))

def create_login_signup_project(config):
    # token = get_user_access_token()["payload"]["token"]
    token = get_dummy_user_access_token()["payload"]["token"]
    headers = { "token": token }
    res = APICalls().post(url="https://api.ask-jennie.com/v1/app/create-angular-login-signup-app/", headers=headers, body=config)
    print (res)


def create_crm_project(config):
    # token = get_user_access_token()["payload"]["token"]
    token = get_dummy_user_access_token()["payload"]["token"]
    headers = { "token": token }
    # res = APICalls().post(url="https://api.ask-jennie.com/v1/app/create-angular-login-signup-app/", headers=headers, body=config)
    response = {
        "app_code": "{'project_link': 'https://projects.ask-jennie.com/1643231549-5272305.zip'",
        "pre_commands": ["ng g new {}".format(config["project_name"]), "cd {}".format(config["project_name"])],
        "post_commands": ["npm i"]
    }
    print ("Angular Login Project Ready To Use.")
    print (response)


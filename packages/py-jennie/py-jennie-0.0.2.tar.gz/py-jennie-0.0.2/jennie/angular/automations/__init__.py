"""
General Automation protocol

automation = [
    {
        "type": "raw_files",
        "files": {
            "output_dir": "filepath",
            "output_dir_1": "filepath_1",
        }
    },
    {
        "type": "shell_command",
        "commands": [
            "npm i"
        ]
    },
    {
        "type": "ui-lib",
        "libraries": [
            "bootstraploginpage", "bootstrapsignuppage", "bootstrapresetpasswordpage",
        ]
    }
    {
        "type": "angular-automations",
        "automations": [
            "user-session", "dummy-login-signup-apiservice", "dashboard-module AuthGuard=True"
        ]
    },
    {
        "type": "add_routing",
        "component": "",
        "path": "",
        "AuthGaurd": false
    },
    {
        "type": "index_script",
        "script": [ "script_path", "scripts_2_path" ]
    }
    {
        "type": "index_css"
        "script": [ "css_path", "css_2_path" ]
    }
]

"""
import os
from jennie.responses import UNKNOWN_PROJECT_TYPE
from jennie.angular.helper import check_if_angular_project

# class AngularAutomations():
#     def __init__(self):
#
#     def execute_raw_files(self):
#     def execute_shell_command(self):
#     def add_ui_lib(self):
#     def add_angular_automations(self):
#     def add_routing(self):
#     def add_index_script(self):
#     def add_index_css(self):
#     def get_automation_details(self):
#     def add_automation_details(self):
#     def update_automation_details(self):
#     def execute_automation(self, name):
#     def add_automation(self, name):


#
# DUMMY_USER_SESSION_API = [{
#         "type": "download_files",
#         "files": [
#             {
#                 "file_path": "",
#                 "output_dir": ""
#             },
#             {
#
#             },
#             {
#
#             }
#         ]
#     },
#
# ]
#
# def install_bootstrap():
#     """
#     Install Bootstrap and Jquery in the projects.
#     Shell command : jennie angular install bootstrap
#     :return:
#     """
#     current_dir = os.getcwd()
#     if current_dir[:-1] != "/":
#         current_dir += "/"
#
#     if check_if_angular_project(current_dir):
#         replace = "</head>"
#         replace_with = '''  <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css" rel="stylesheet">
# </head>'''
#         replace_for_script = "</body>"
#         replace_for_script_with = '''  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
#   <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.min.js"></script>
# </body>'''
#         dataset = open(current_dir + "src/index.html", "r").read()
#         dataset = dataset.replace(replace, replace_with)
#         dataset = dataset.replace(replace_for_script, replace_for_script_with)
#         open(current_dir + "src/index.html", "w").write(dataset)
#     else:
#         print (UNKNOWN_PROJECT_TYPE)

# def automation():

# def add_dashboard_module():
#
# def add_user_sessions():
#
# def add_dummy_signup_login_api():
#
# def run_automation(automation_name):
#     response = [
#         # {
#         #     "type": "angular_ui_galleries",
#         #     "libraries": [
#         #         "bootstraploginpage", "bootstrapsignuppage", "bootstrapresetpasswordpage",
#         #     ]
#         # },
#         # {
#         #     "type": "automations",
#         #     "libraries": [
#         #         "user-session", "dummy-login-signup-apiservice", "dashboard-module AuthGuard=True"
#         #     ]
#         # },
#         {
#             "type": "download_files",
#             "files": [{
#                 "file_path": "",
#                 "output_dir": ""
#             }]
#         },
#         {
#             "type": "shell_command",
#             "files": [{
#                 "file_path": "",
#                 "output_dir": ""
#             }]
#         }
#
#     ]
#
#     for element in response:
#         execute_task(type=element["type"], tasks=element["libraries"])
#
# def execute_task(type, tasks):
#     if type == "angular_ui_galleries":
#         for key in tasks:
#             os.system("jennie angular ui-lib {}".format(key))
#
#     elif type == "automations":
#         for key in tasks:
#             os.system("jennie angular automation {}".format(key))
#
# def add_dashboard_theme():
#     """
#     - creates login, signup, reset password page in the project.
#     - create AuthGaurd, SessionManager and Dummy Login Signup and Reset Password API Controller.
#     - Create Dashboard modules and inside dashboard module dashboard component is created. This dashboard component will show all sub pages.
#     - Creates Home Component and add it to Dashboard module and route it to /home.
#     - Add AuthGaurd to dashboard component so pages inside dashboard component can be accessed only after user has logged in
#     :return:
#     """
#     response = [
#         {
#             "type": "angular_ui_galleries",
#             "libraries": [
#                 "bootstraploginpage", "bootstrapsignuppage", "bootstrapresetpasswordpage",
#             ]
#         },
#         {
#             "type": "automations",
#             "libraries": [
#                 "user-session", "dummy-login-signup-apiservice", "dashboard-module AuthGuard=True"
#             ]
#         }
#     ]
#
#     for element in response:
#         execute_task(type=element["type"], tasks=element["libraries"])


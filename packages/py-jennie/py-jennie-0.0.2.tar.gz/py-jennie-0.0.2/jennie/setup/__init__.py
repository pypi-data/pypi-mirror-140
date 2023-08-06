import json, sys, os
from getpass import getpass
from jennie.api_calls import APICalls

LOGIN_API = "https://api.ask-jennie.com/v1/login/"
TOKEN_PATH = str(sys.executable).split("/bin/python")[0] + "/lib/python3.7/site-packages/jennie/" + "token.json"

def get_dummy_user_access_token():
    return {"status":True,"payload":{"email":"saurabh@trillbit.com","fullname":"Saurabh Pandey","city":"Not Avalible","bio":"Senior Software Engineer","is_active":1,"token":"8ee7f0795bd3e9a88b44066926d82a90a4589415"},"message":"Login Api view"}

def get_user_access_token():
    if not os.path.isfile(TOKEN_PATH):
        return None
    return json.loads(open(TOKEN_PATH, "r").read())

class Setup():
    def __init__(self):
        self.state = 0

    def is_user_logged_in(self):
        user_saved_info = None
        userinfo = get_user_access_token()
        if userinfo != None:
            user_saved_info = userinfo["payload"]

        return user_saved_info

    def login_to_ask_jennie(self, email, password):
        response = APICalls().post(
            url=LOGIN_API,
            body={"email": email, "password": password}
        )

        if response["message"] == "Invalid Password":
            print ("Invalid Password try Again....")
            print ("Input Password for ASK Jennie Email:  ", self.email)
            password = getpass()
            self.login_to_ask_jennie(email, password)
        elif response["message"] == "Email Does not exits":
            print ("Email is not registered with Jennie.")
            return False
        else:
            with open(TOKEN_PATH, 'w') as f:
                json.dump(response, f)

            print ("User Logged In Successfully")
            return True

    def get_state(self):
        if (get_user_access_token() == None):
            return False
        return True

    def setup(self, email):
        self.email = email
        token_info = self.get_state()
        if (token_info):
            raise ValueError("User already logged in, try logout to resetup ( jennie logout ) ")
        else:
            print ("Continue Login, Enter Information")
            print ("Input Password for ASK Jennie Email:  ", self.email)
            password = getpass()
            return self.login_to_ask_jennie (self.email, password)

    def logout(self):
        if (self.is_user_logged_in() != None):
            command = "rm -rf {}".format(TOKEN_PATH)
            os.system(command)
            print ("Logged out successfully")
        else:
            print ("User not logged in")
        return True
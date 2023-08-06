import requests

class APICalls():
    """
    Simply library to simplfy API Calls using python.

    """
    def recreate_url(self, url, params):
        split_keyword = "?"
        for key in params:
            url += split_keyword + key + "=" + params[key]
            split_keyword = "&"
        return url

    def get(self, url, headers=None, params=None):
        """
        Make a get api call, if params are present add params to url,
        if headers are present add headers to requests
        :param url: Request URL
        :param headers: Request Headers ( optional )
        :param params: Request Params ( optional )
        :return: API Call JSON Response.
        """
        if params != None:
            url = self.recreate_url(url, params)

        if headers == None:
            headers = {"Content-type": "application/json"}

        response = requests.get(url, headers=headers)
        return response.json()

    def get_text(self, url, headers=None, params=None):
        """
        Make a get api call, if params are present add params to url,
        if headers are present add headers to requests
        :param url: Request URL
        :param headers: Request Headers ( optional )
        :param params: Request Params ( optional )
        :return: API Call JSON Response.
        """
        if params != None:
            url = self.recreate_url(url, params)

        if headers == None:
            headers = {"Content-type": "application/json"}

        response = requests.get(url, headers=headers)
        return response.text

    def post(self, url, headers=None, body=None):
        """
        Make a post api call, if headers are present add headers to requests, if body is present
        :param url: Request URL
        :param headers: Request Headers ( optional )
        :param body: Request Params ( optional )
        :return: API Call JSON Response.
        """
        if headers == None:
            headers = {"Content-type": "application/json"}

        if body == None:
            body = {}

        response = requests.post(url, headers=headers, json=body)
        return response.json()

    def put(self, url, headers=None, body=None):
        """
        Make a put api call, if headers are present add headers to requests, if body is present
        :param url: Request URL
        :param headers: Request Headers ( optional )
        :param body: Request Params ( optional )
        :return: API Call JSON Response.
        """
        if headers == None:
            headers = {"Content-type": "application/json"}

        if body == None:
            body = {}
        response = requests.put(url, headers=headers, json=body)
        return response.json()

    def delete(self, url, headers=None, body=None):
        """
        Make a delete api call, if headers are present add headers to requests, if body is present
        :param url: Request URL
        :param headers: Request Headers ( optional )
        :param body: Request Params ( optional )
        :return: API Call JSON Response.
        """
        if headers == None:
            headers = {"Content-type": "application/json"}

        if body == None:
            body = {}
        response = requests.delete(url, headers=headers, json=body)
        return response.json()
import json
import requests
import os
from retry import retry

API_URL = {
    "prod": "https://api.sumit-labs.com",
}

class APIEPS:
    login = 'login'
    realtime_update = 'realtime/set_status'

class APIHelper:
    def __init__(self, cred_path: str, env="prod", onprem=False) -> None:
        """
        Initializes the APIHelper.

        Args:
        - cred_path (str): The credential json path
        - env (str): api environment. 'prod' for cloud env. default is 'prod'
        """        
        self._env = env
        if onprem and env not in API_URL:
            self.api_url = env
        else:
            self.api_url = API_URL[env]
        self.token = None
        self.invalid_token_code = 401
        try:
            print("load credentials")
            self.login_sa = self.load_cred(cred_path)
            print(self.login_sa)
        except Exception as e:
            print("failed to load credentials", e)
            return
        self.login()

    @retry(tries=3, delay=10)
    def load_cred(self, path):
        with open(path, 'r') as fd:
            return json.load(fd)
    
    @retry(tries=3, delay=10)
    def try_login(self):
        t = requests.post(f"{self.api_url}/{APIEPS.login}", json=self.login_sa)
        self.token = t.json()['token']
        print(self.token)
    
    def login(self):
        """
        Logs in using the provided credentials, and sets the token.

        """        
        try:
            print("try login")
            self.try_login()
        except Exception as e:
            print(e)
    
    def safe_call(self, endpoint: str, data: dict, re_login=True):
        """
        Makes a safe POST request to the given API endpoint. if not logged in, or token is expired - automatically reconnect

        Args:
        - endpoint (str): The API endpoint to make the request to.
        - data (dict): The JSON data to send in the request.

        Returns:
        - dict: The response from the API.
        """            
        if not self.token:
            self.login()
        try:
            ret = requests.post(f"{self.api_url}/{endpoint}", json=data, headers={"Authorization": f"Bearer {self.token}"})
            if ret.status_code == self.invalid_token_code:
                self.token = None
                self.login()
                if re_login:
                    return self.safe_call(endpoint, data, re_login=False)
            return ret
        except:
            pass

    def safe_call_args(self, endpoint: str, re_login=True, **kwargs):
        """
        same as safe_call, with flexible arguments for request
        """            
        if not self.token:
            self.login()
        try:
            ret = requests.post(f"{self.api_url}/{endpoint}", headers={"Authorization": f"Bearer {self.token}"}, **kwargs)
            if ret.status_code == self.invalid_token_code:
                self.token = None
                self.login()
                if re_login:
                    return self.safe_call(endpoint, re_login=False, **kwargs)
            return ret
        except:
            pass

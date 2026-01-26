import json
import requests
import os
from retry import retry
import logging

API_URL = {
    "prod": "https://api.sumit-labs.com",
    "tenants": "https://api.{tenant}.sumit-labs.com",
}

class APIEPS:
    login = 'login'
    realtime_update = 'realtime/set_status'

class APIHelper:
    def __init__(self, cred_path: str, env="prod", onprem=False, verify_ssl=None) -> None:
        """
        Initializes the APIHelper.

        Args:
        - cred_path (str): The credential json path
        - env (str): api environment. 'prod' for cloud env. default is 'prod'
        - verify_ssl (bool | None): if False - ignore ssl verification and self-sigend urls.
        """        
        self._env = env
        self.verify_ssl = verify_ssl
        if env not in API_URL:
            if onprem and env.startswith('http'):
                self.api_url = env
            else:
                self.api_url = API_URL["tenants"].format(tenant=env)
        else:
            self.api_url = API_URL[env]
        self.token = None
        self.invalid_token_code = 401
        if not os.path.exists(cred_path):
            raise Exception(f"credential file doesn't exists: {cred_path}")
        try:
            logging.info("Sumit SDK load credentials")
            self.login_sa = self.load_cred(cred_path)
        except Exception as e:
            logging.error(f"failed to load credentials: {e}")
            return
        self.login()

    @retry(tries=3, delay=10)
    def load_cred(self, path):
        with open(path, 'r') as fd:
            return json.load(fd)
    
    @retry(tries=3, delay=10)
    def try_login(self):
        t = requests.post(f"{self.api_url}/{APIEPS.login}", json=self.login_sa, verify=self.verify_ssl)
        self.token = t.json()['token']
    
    def login(self):
        """
        Logs in using the provided credentials, and sets the token.

        """        
        try:
            self.try_login()
        except Exception as e:
            logging.error(f"Sumit: failed to login: {e}")
    
    def safe_call(self, endpoint: str, data: dict, re_login=True, raise_on_failure=False):
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
            ret = requests.post(f"{self.api_url}/{endpoint}", json=data, headers={"Authorization": f"Bearer {self.token}"}, verify=self.verify_ssl)
            if ret.status_code == self.invalid_token_code:
                self.token = None
                self.login()
                if re_login:
                    return self.safe_call(endpoint, data, re_login=False)
            return ret
        except:
            if raise_on_failure:
                raise

    def safe_call_args(self, endpoint: str, re_login=True, **kwargs):
        """
        same as safe_call, with flexible arguments for request
        """            
        if not self.token:
            self.login()
        try:
            ret = requests.post(f"{self.api_url}/{endpoint}", headers={"Authorization": f"Bearer {self.token}"}, verify=self.verify_ssl, **kwargs)
            if ret.status_code == self.invalid_token_code:
                self.token = None
                self.login()
                if re_login:
                    return self.safe_call(endpoint, re_login=False, **kwargs)
            return ret
        except:
            pass

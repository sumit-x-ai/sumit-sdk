import os
from sumit_sdk.api_helper import APIHelper
import requests

class APIClient(APIHelper):

    def _get_data(self, endpoint: str, json_data: dict={}):
        """
        Makes a GET request to the given API endpoint.

        Args:
        - endpoint (str): The API endpoint to make the request to.
        - json_data (dict, optional): The JSON data to send in the request. Defaults to None.

        Returns:
        - dict: The response from the API.
        """            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.api_url}/{endpoint}", json=json_data, headers=headers)
        return response.json()
    
    def _post_data(self, endpoint: str, json_data: dict={}):
        """
        Makes a POST request to the given API endpoint.

        Args:
        - endpoint (str): The API endpoint to make the request to.
        - json_data (dict, optional): The JSON data to send in the request. Defaults to None.

        Returns:
        - dict: The response from the API.
        """        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{self.api_url}/{endpoint}", json=json_data, headers=headers)
        return response.json()
    
class BaseWrapper:
    def __init__(self, api_instance) -> None:
        if not isinstance(api_instance, APIClient):
            raise TypeError("Expected api_instance to be an instance of APIClient")
        self.api = api_instance

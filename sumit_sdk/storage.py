import requests
import json
from sumit_sdk.api import BaseWrapper


class Storage(BaseWrapper):
    """
    Manages storage client.

    Attributes:
    - None

     Methods:
    - upload(): Upload a file to storage with a signed URL.
    - upload_multi(): Upload number of file to storage with a signed URLs.
    - delete_file(): Delete file from storage.
    - files_list(): Get list of all existing files in the storage.
    """
    _UPLOAD_FILE = "storage/upload"
    _SA_UPLOAD_FILE = "storage_sa/upload"
    _SA_DOWNLOAD_JSON = "storage_sa/download_json"
    _UPLOAD_MULTI_FILES = "storage/uploads_multi"
    _DELETE_FILE = "storage/delete"
    _DOWNLOAD_FILE = "storage/download"
    _GET_FILE_LIST = "storage/list_files"

    def __init__(self, api_instance, sa=False) -> None:
        """
        Initializes the Storage.

        Args:
        - api_instance (APIClient): An instance of the APIClient class.
        """
        super().__init__(api_instance)
        self._sa = sa
    
    def _sa_upload(self, filename: str, path: str) -> dict:
        with open(path, 'rb') as file:
            files = {'file': file}
            _map = {"filename": filename}
            ret = self.api.safe_call_args(self._SA_UPLOAD_FILE, files=files, data={'request': json.dumps(_map)})
            return ret

    def _upload(self, signed_url: str, path: str) -> bool:
        """
        Upload file to storage.
        Args:
        - signed_url (str): a signed URL to the location of the storage folder
        - path (str): path to file to store

        Returns:
        - bool: True if successful
        """
        with open(path, "rb") as file:
            file_content = file.read()

        # headers = {
        #     'Content-Type': 'application/json',
        # }
        headers = None

        resource = requests.put(signed_url, headers=headers, data=file_content, verify=self.api.verify_ssl)
        if resource.status_code != 200:
            raise Exception("Failed to upload the file. Status code:", resource.content)

        return True

    def get_upload_url(self, filename: str, expiration: int = None) -> dict:
        """
        create signed URL forupload.

        Args:
            - filename (srt): Full path of the file that will appear in the storage.
            - expiration (int): [Optional] expiration of the signed URL.(Between 1-24 hours, Default - 1 hour)

       Returns:
           - dict: Contains the details sent and the requested result
        """
        req = {}
        if expiration:
            req['expiration'] = expiration

        req['filename'] = filename
        ret = self.api.safe_call(Storage._UPLOAD_FILE, req)
        if ret.status_code != 200:
            return {
                "status_code": ret.status_code,
                "content": ret.content
            }
        data = ret.json()
        signed_url = data.get("signed_url")
        if signed_url:
            return data
        return None

    def upload(self, filename: str, path: str, expiration: int = None) -> dict:
        """
        Upload a file to storage with a signed URL.

        Args:
            - filename (srt): Full path of the file that will appear in the storage.
            - path (srt): path to the uploade file.
            - expiration (int): [Optional] expiration of the signed URL.(Between 1-24 hours, Default - 1 hour)

       Returns:
           - dict: Contains the details sent and the requested result
        """
        if self._sa:
            return self._sa_upload(filename, path)
        
        req = {}
        if expiration:
            req['expiration'] = expiration

        req['filename'] = filename
        ret = self.api.safe_call(Storage._UPLOAD_FILE, req)
        if ret.status_code != 200:
            return {
                "status_code": ret.status_code,
                "content": ret.content
            }
        data = ret.json()
        signed_url = data.get("signed_url")
        if signed_url:
            self._upload(signed_url, path)

        return data

    def upload_multi(self, remote_to_local_map: dict, expiration: int = None) -> dict:
        """
        Upload files to storage with a signed URL.

        Args:
            - remote_to_local_map (dict): key -> full path to the file that will appear in the storage.
                                    val -> path to local file.
            - expiration (int): [Optional] expiration of the signed URL.(Between 1-24 hours, Default - 1 hour)

       Returns:
           - dict: Contains the details sent and the requested result
       """
        req = {}
        if expiration:
            req['expiration'] = expiration
        req['remote_to_local_map'] = remote_to_local_map
        data = self.api.safe_call(Storage._UPLOAD_MULTI_FILES, req).json()
        signed_urls = data.get('signed_urls')
        not_upload = {}
        if signed_urls:
            for val in signed_urls:
                try:
                    self._upload(val, signed_urls[val])
                except Exception as e:
                    not_upload[signed_urls[val]] = e

        data['uploads_failed'] = not_upload
        return data

    def delete_file(self, filename: str) -> dict:
        """
        Delete file fom storage.

        Args:
            - filename (str):  full path to the file.

       Returns:
           - dict: Contains the details sent and the requested result
        """
        return self.api.safe_call(Storage._DELETE_FILE, {"filename": filename}).json()

    def list_files(self, folder_name: str) -> dict:
        """
        Get list of all existing files in the storage.
        Args:
            - folder_name (str): path to the desired folder

        Returns:
           - dict: Contains the details sent and the requested result
        """
        return self.api.safe_call(Storage._GET_FILE_LIST, {"folder_name": folder_name}).json()
    
    def _download_inmem(self, signed_url: str):
        response = requests.get(signed_url, stream=True, verify=self.api.verify_ssl)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to download the file. Status code: {response.status_code}, content: {response.content}")


    def _download(self, signed_url: str, path: str, mode:str='t', chunk_size:int=8192) -> bool:
        """
        download file from storage.
        Args:
        - signed_url (str): a signed URL to the file location in the storage
        - path (str): path to save the file
        - mode (str): 't' for textual or 'b' for binary. [default 't']

        Returns:
        - bool: True if successful
        """
        response = requests.get(signed_url, stream=True, verify=self.api.verify_ssl)
        
        if response.status_code == 200:
            # Determine the write mode (text or binary)
            write_mode = 'w' if mode == 't' else 'wb'

            # Save the file locally
            with open(path, write_mode) as file:
                if mode == 't':
                    file.write(response.text)
                else:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        file.write(chunk)
            return True
        else:
            raise Exception(f"Failed to download the file. Status code: {response.status_code}, content: {response.content}")


    def _download_sa(self, endpoint: str, data: dict, path: str, mode:str='t', chunk_size:int=8192) -> bool:
        """
        download file from storage.
        Args:
        - signed_url (str): a signed URL to the file location in the storage
        - data (dict): request data, contains the remote filepath
        - path (str): path to save the file
        - mode (str): 't' for textual or 'b' for binary. [default 't']

        Returns:
        - bool: True if successful
        """
        response = requests.get(f"{self.api.api_url}/{endpoint}", json=data, headers={"Authorization": f"Bearer {self.api.token}"}, stream=True, verify=self.api.verify_ssl)
        
        if response.status_code == 200:
            # Determine the write mode (text or binary)
            write_mode = 'w' if mode == 't' else 'wb'

            # Save the file locally
            with open(path, write_mode) as file:
                if mode == 't':
                    file.write(response.text)
                else:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        file.write(chunk)
            return True
        else:
            raise Exception(f"Failed to download the file. Status code: {response.status_code}, content: {response.content}")

    def download(self, remote_filename: str, local_path: str, expiration: int = None, mode:str='t') -> dict:
        """
        Download a file from storage with a signed URL.

        Args:
            - remote_filename (str): Full path of the file in the storage.
            - local_path (str): local file path to download the file.
            - expiration (int): [Optional] expiration of the signed URL.(Between 1-24 hours, Default - 1 hour)
            - mode (str): 't' for textual or 'b' for binary. [default 't']

       Returns:
           - dict: Contains the details sent and the requested result
        """
        req = {}
        if expiration:
            req['expiration'] = expiration

        req['filename'] = remote_filename
        if self._sa:
            return self._download_sa(Storage._DOWNLOAD_FILE, req, local_path, mode )
        data = self.api.safe_call(Storage._DOWNLOAD_FILE, req).json()
        signed_url = data.get("url")
        if signed_url:
            self._download(signed_url, local_path, mode=mode)

        return data


    def download_as_text(self, remote_filename: str) -> dict:
        """
        Download a file from storage with a signed URL.

        Args:
            - remote_filename (str): Full path of the file in the storage.

       Returns:
           - text content
        """
        req = {}

        req['filename'] = remote_filename
        data = self.api.safe_call(Storage._DOWNLOAD_FILE, req).json()
        signed_url = data.get("url")
        if signed_url:
            return self._download_inmem(signed_url)

    def download_as_json(self, remote_filename: str) -> dict:
        """
        Download a file from storage with a signed URL.

        Args:
            - remote_filename (str): Full path of the file in the storage.

        Returns:
           - json object from the file content
        """
        content = self.download_as_text(remote_filename)
        if content:
            content = json.loads(content)
        return content

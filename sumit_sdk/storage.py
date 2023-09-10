import requests

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
    _UPLOAD_MULTI_FILES = "storage/uploads_multi"
    _DELETE_FILE = "storage/delete"
    _GET_FILE_LIST = "storage/list_files"

    def __init__(self, api_instance) -> None:
        """
        Initializes the Storage.

        Args:
        - api_instance (APIClient): An instance of the APIClient class.
        """
        super().__init__(api_instance)

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

        headers = {
            'Content-Type': 'application/json',
        }

        resource = requests.put(signed_url, headers=headers, data=file_content)
        if resource.status_code != 200:
            raise Exception("Failed to upload the file. Status code:", resource.status_code)

        return True

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
        req = {}
        if expiration:
            req['exp'] = expiration

        req['filename'] = filename
        data = self.api.safe_call(Storage._UPLOAD_FILE, req).json()
        signed_url = data.get("signed_url")
        if signed_url:
            self._upload(signed_url, path)

        return data

    def upload_multi(self, dict_of_files: dict, expiration: int = None) -> dict:
        """
        Upload files to storage with a signed URL.

        Args:
            - dict_of_files (dict): key -> full path to the file that will appear in the storage.
                                    val -> path to local file.
            - expiration (int): [Optional] expiration of the signed URL.(Between 1-24 hours, Default - 1 hour)

       Returns:
           - dict: Contains the details sent and the requested result
       """
        req = {}
        if expiration:
            req['exp'] = expiration
        req['local_files'] = list(dict_of_files.values())
        req['storage_path'] = list(dict_of_files.keys())
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

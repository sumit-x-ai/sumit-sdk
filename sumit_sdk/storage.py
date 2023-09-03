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
    _UPLOAD_FILE = "upload"
    _UPLOAD_MULTI_FILES = "uploads_multi"
    _DELETE_FILE = "delete"
    _GET_FILE_LIST = "files_list"

    def __init__(self, api_instance) -> None:
        """
        Initializes the RealtimeSTT.

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
        return resource.status_code == 200

    def upload(self, filename: str, path: str, exp: int = None) -> dict:
        """
        Upload a file to storage with a signed URL.

        Args:
            - filename (srt): The path + and the name of the file that will appear in the storage.
            - path (srt): path to the uploade file.
            -exp (int): [Optional] expiration of the signed URL.(Between 1-24 hours, Default - 1 hour)

       Returns:
           - dict: Contains the details sent and the requested result
        """
        req = {}
        if exp:
            req['exp'] = exp

        req['filename'] = filename
        data = self.api.safe_call(Storage._UPLOAD_FILE, req).json()
        signed_url = data.get("signed_url")
        res = False
        if signed_url:
            res = self._upload(signed_url, path)

        if not res:
            raise Exception("Failed to upload the file.")

        return data

    def upload_multi(self, filepaths_names: list[str], filepaths: list[str], exp: int = None) -> dict:
        """
        Upload files to storage with a signed URL.

        Args:
            - filepaths_names (list[str]):each cell contains the path + the name
                                of the file that will appear in the storage.
            - filepaths (list[srt]): Each cell contains path to the uploade file.
            -exp (int): [Optional] expiration of the signed URL.(Between 1-24 hours, Default - 1 hour)

       Returns:
           - dict: Contains the details sent and the requested result
       """
        req = {}
        if exp:
            req['exp'] = exp
        req['files'] = filepaths_names

        data = self.api.safe_call(Storage._UPLOAD_MULTI_FILES, req).json()
        signed_urls = data.get('signed_urls')
        not_upload = []
        if signed_urls:
            for signed_url, file in zip(signed_urls, filepaths):
                res = self._upload(signed_url, file)
                if not res:
                    not_upload.append(file)

        data['uploads_failed'] = not_upload
        return data

    def delete_file(self, filename: str) -> dict:
        """
        Delete file fom storage.

        Args:
            - filename (str):  full path to the file.
              - note: file path must start from the root folder of the client

       Returns:
           - dict: Contains the details sent and the requested result
        """
        return self.api.safe_call(Storage._DELETE_FILE, {"filename": filename}).json()

    def files_list(self, folder_name: str) -> dict:
        """
        Get list of all existing files in the storage.
        Args:
            -folder_name (str): path to the desired folder
             - note: file path must start from the root folder of the client
        Returns:
           - dict: Contains the details sent and the requested result
        """
        return self.api.safe_call(Storage._GET_FILE_LIST, {"folder_name": folder_name}).json()

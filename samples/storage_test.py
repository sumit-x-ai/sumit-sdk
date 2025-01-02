from sumit_sdk.api import APIClient
from sumit_sdk.storage import Storage

api = APIClient("api-sa.json")  # create client
storage = Storage(api)

# An example of uploading a file to storage

filename = "<PATH_TO_FILE_IN_STORAGE>"  # The path + and the name of the file that will appear in the storage.

path = "<YOUR_FILE_NAME>"  # path from my computer

exp = 10  # hours

res = storage.upload(filename, path, exp)
print(res)

# An example of uploading a multi files to storage

remote_to_local_map = {"<PATH_TO_FILE_IN_STORAGE_1>": "<YOUR_LOCAL_FILE_PATH_1>",
                 "<PATH_TO_FILE_IN_STORAGE_2>": "<YOUR_LOCAL_FILE_PATH_2>",
                 "<PATH_TO_FILE_IN_STORAGE_3>": "<YOUR_LOCAL_FILE_PATH_3>"}

res = storage.upload_multi(remote_to_local_map)
print(res)

# An example of deleting a file from storage

filename = "<FULL_PATH_TO_FILE_IN_STORAGE>"
res = storage.delete_file(filename)
print(res)

# An example NO. 1 of getting list of files from storage

folder_name = "<PATH_TO_FOLDER_NAME>"
res = storage.list_files(folder_name)
print(res)

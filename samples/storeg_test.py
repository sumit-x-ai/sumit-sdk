from sumit_sdk.api import APIClient
from sumit_sdk.storage import Storage

api = APIClient("api-sa.json", env="dev")  # create client
storage = Storage(api)

# An example of uploading a file to storage

filename = "0309/my_file.wav"  # The path + and the name of the file that will appear in the storage.

path = "/home/my_computer/path_to_wav_file.wav"  # path from my computer

exp = 10  # hors

res = storage.upload(filename, path, exp)
print(res)

# An example of uploading a multi files to storage

filepaths_names = ["folder_A/file1.wav", "folder_A/file2.wav", "folder_A/file3.wav"]

files_paths = ["file1.wav", "file2.wav", "file3.wav"]

res = storage.upload_multi(filepaths_names, files_paths)
print(res)

# An example of deleting a file from storage

filename = "company_name/folder_A/file2.wav"
res = storage.delete_file(filename)
print(res)

# An example NO. 1 of getting list of files from storage

folder_name = "company_name"
res = storage.files_list(folder_name)
print(res)

# An example NO. 2 of getting list of files from storage

folder_name = "company_name/folder_A"
res = storage.files_list(folder_name)
print(res)

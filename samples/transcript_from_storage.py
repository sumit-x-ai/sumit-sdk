from sumit_sdk.api import APIClient
from sumit_sdk.transcript import Transcript, SupportedModels

# initialize API
api = APIClient("api-sa.json", env="dev")  # create client
transcripter = Transcript(api)

config = transcripter.build_request("filename.wav", "filename.json", 
    language='he-IL', model=SupportedModels.GENERIC_HEBREW, 
    flat_output_path="filename_flat.json", bucket_name="archive")

ret = transcripter.execute(config)
print(ret)
task_id = ret['task_id']
status = transcripter.get_task_status(task_id)
print(status)

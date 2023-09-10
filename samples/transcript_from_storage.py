from sumit_sdk.api import APIClient    # API core client
from sumit_sdk.storage import Storage  # to upload files from local machine to our bucket
from sumit_sdk.transcript import Transcript, SupportedModels

# initialize API
api = APIClient("api-sa.json", env="dev")  # create client
transcripter = Transcript(api)

# upload file to storage
local_filename = "/tmp/t.wav"
remote_filename = "test.wav"
output_filename = f"{remote_filename}.json"  # nested result format. group by speakers of subtitles
flat_output_filename = f"{remote_filename}_flat.json"  # flat result format. optional

storage = Storage(api)
res = storage.upload(remote_filename, local_filename)
print(res)

config = transcripter.build_request(remote_filename, output_filename, 
    language='he-IL', model=SupportedModels.GENERIC_HEBREW, 
    flat_output_path=flat_output_filename)

ret = transcripter.execute(config)
print(ret)
if ret['success']:
    task_id = ret['response']['job_id']
    status = transcripter.get_task_status(task_id)
    print(status)
    print("wait until finish...")
    ret = transcripter.wait_for_task(task_id)
    print("done", ret)
    res = storage.download_as_json(output_filename)
    print(res)
else:
    print("transcript execution failed")


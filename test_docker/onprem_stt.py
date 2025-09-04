from sumit_sdk.api import APIClient    # API core client
from sumit_sdk.storage import Storage  # to upload files from local machine to our bucket
from sumit_sdk.transcript import Transcript, SupportedModels, SupportedDiarization
import json
import os

_dir = os.getenv("DATA_DIR", "/data")
_api_url = os.getenv("API_URL", "https://sumit-ai.com/api")
_key_path = os.getenv("KEY_PATH", os.path.join(_dir,"user.json"))
# initialize API
# sumit-ai.com is a DNS name for the on-prem deployment server. may be DNS or /etc/hosts record
api = APIClient(_key_path, env=_api_url, onprem=True, verify_ssl=False)  # create client
transcripter = Transcript(api)

# upload file to storage
local_filename = os.path.join(_dir, "t.wav")
remote_filename = "test.wav"
output_filename = f"{remote_filename}.json"  # nested result format. group by speakers of subtitles
flat_output_filename = f"{remote_filename}_flat.json"  # flat result format. optional
local_output_filename = os.path.join(_dir, "t.json")  # where to store the results in your local machine

storage = Storage(api, sa=True)  # configure for standalone deployment (i.e upload to filesystem instead of cloud bucket)
res = storage.upload(remote_filename, local_filename)
print(res)

config = transcripter.build_request(remote_filename, output_filename, 
    language='he-IL', model=SupportedModels.HEBREW_LEGAL, 
    flat_output_path=flat_output_filename, 
    # multichannel_diarize=True, group_by_speaker=True,  # set true to diarize speakers based on audio channels
    # diarize=SupportedDiarization.UNSUPERVISED, min_speakers=2, max_speakers=4, group_by_speaker=True,  # use unsupervised speaker diarization
    )

ret = transcripter.execute(config)
print(ret)
if ret['success']:
    task_id = ret['response']['job_id']
    status = transcripter.get_task_status(task_id)
    print(status)
    print("wait until finish...")
    ret = transcripter.wait_for_task(task_id)
    print("done", ret)
    res = storage.download(output_filename, local_output_filename)
    print(res)
    with open(local_output_filename, 'r') as fd:
        stt = json.load(fd)
    print(json.dumps(stt, indent=2))
else:
    print("transcript execution failed")


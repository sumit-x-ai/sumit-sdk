from sumit_sdk.api import APIClient    # API core client
from sumit_sdk.storage import Storage  # to upload files from local machine to our bucket
from sumit_sdk.transcript import Transcript, SupportedModels, MultichannelConfig, MultichannelDiarizeParam

# initialize API
api = APIClient("api-sa.json")  # create client
transcripter = Transcript(api)

# upload file to storage
local_filename = "/tmp/t.mp4"
remote_filename = "test.mp4"
output_filename = f"{remote_filename}.json"  # nested result format. group by speakers of subtitles
flat_output_filename = f"{remote_filename}_flat.json"  # flat result format. optional

storage = Storage(api)
res = storage.upload(remote_filename, local_filename)
print(res)

ignore_channels = [5]  # do not use the 6th channel (number 5 in zero based index)
# give names for the channels. 
# if ignore_channels is not None, the channel index refer to the order after channel removing
names = [  
    "speaker 1",
    "speaker 2",
    "witness",
    "judge",
    "speaker 3",
]
config = transcripter.build_request(remote_filename, output_filename, 
    language='he-IL', model=SupportedModels.HEBREW_LEGAL, 
    flat_output_path=flat_output_filename, 
    multichannel_diarize=True,  # set true to diarize speakers based on audio channels
    multichannel_config=MultichannelConfig(  # all parameters are optional
        ignore_channels=ignore_channels, channels_names=names,  
        diarize_param=MultichannelDiarizeParam(auto_naming=True, mic_arr_split_unsupervised=True)
        ),
    group_by_speaker=True,  
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
    res = storage.download_as_json(output_filename)
    print(res)
else:
    print("transcript execution failed")


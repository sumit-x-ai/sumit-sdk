import time
from sumit_sdk.api import APIClient
from sumit_sdk.realtime_stt import RealtimeSTT
from sumit_sdk.realtime_stt import Profiles, VadProfile
from sumit_sdk.realtime_stt import BufferMode
from sumit_sdk.utils.audio_helper import Recorder  # helper class to async record from microphone

# initialize API
api = APIClient("api-sa.json")  # create client
rt_mgr = RealtimeSTT(api)  # create realtime manager

# start session
def callback(data):
    print('\u202b' + data['txt'] + '\u202c' )  # Reverse for proper view of Hebrew in terminal. 

def write_segments_callbcak(data):
    with open('out.txt', 'a') as fd:
        fd.write(f'{time.time()}\t\t{data['txt']}\n')
    print('\u202b' + data['txt'][::-1] + '\u202c' )

rt_mgr.start_session(callback, profile=Profiles.accurate, vad_profile=VadProfile.low, buffer_mode=BufferMode.default) 

sock = rt_mgr.connect()

# create recorder
rec = Recorder(as_base64=True, buffer_sec=2.5)  # encode samples as base64, to send the chunks over web-socket
rec.start()
stop_sig = False
while sock.connected and not stop_sig:
    try:
        data = rec.safe_get()
        if data is None:
            time.sleep(0.1)
            continue
        rt_mgr.send(sock, data)
    except KeyboardInterrupt:
        stop_sig = True
        print("keyboard interupt. stop streaming")

# cleanup
rt_mgr.stop_session()
rec.stop()

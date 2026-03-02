import time
from sumit_sdk.api import APIClient
from sumit_sdk.realtime_stt import RealtimeSTT, Profiles
from sumit_sdk.utils.streamlink_helper import StreamlinkHelper   # helper class to async record from URLs

# initialize API
api = APIClient("api-sa.json")  # create client
rt_mgr = RealtimeSTT(api)  # create realtime manager

# start session
def callback(data):
    print(data['st'], data['txt'][::-1])  # Reverse for proper view of Hebrew in terminal. 

rt_mgr.start_session(callback, profile=Profiles.very_accurate)
sock = rt_mgr.connect()

# create recorder
rec = StreamlinkHelper(chunk_len=5, as_base64=True)
rec.open_stream("https://www.youtube.com/watch?v=1IMi74Ybg8s")
rec.async_read()
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

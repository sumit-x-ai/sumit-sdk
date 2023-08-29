import time
from sumit_sdk.api import APIClient
from sumit_sdk.realtime_stt import RealtimeSTT
from sumit_sdk.utils.streamlink_helper import StreamlinkHelper   # helper class to async record from URLs

# initialize API
api = APIClient("api-sa.json", env="dev")  # create client
rt_mgr = RealtimeSTT(api)  # create realtime manager

# start session
def callback(data):
    print(data['st'], data['txt'][::-1])  # Reverse for proper view of Hebrew in terminal. 

rt_mgr.start_session(callback)
# rt_mgr._inject_session("05fa3c71-2c6c-43b4-8c14-986270aed37c", "05fa3c712c6c43b48c14986270aed37c.sumit-labs-dev.com", callback)
sock = rt_mgr.connect()

# create recorder
rec = StreamlinkHelper(chunk_len=3, as_base64=True)
rec.open_stream("https://www.youtube.com/watch?v=CjT5bF4Rk3U")
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

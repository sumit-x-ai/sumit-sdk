import time
from sumit_sdk.api import APIClient
from sumit_sdk.realtime_stt import RealtimeSTT

# initialize API
api = APIClient("api-sa.json", env="dev")  # create client
rt_mgr = RealtimeSTT(api)  # create realtime manager

# start session
session = rt_mgr.start_session()

# cleanup
time.sleep(5)
rt_mgr.stop_session(session['session_id'])
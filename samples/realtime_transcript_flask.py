import time
from sumit_sdk.api import APIClient
from sumit_sdk.realtime_stt import RealtimeSTT
from sumit_sdk.realtime_stt import Profiles
from sumit_sdk.utils.audio_helper import Recorder  # helper class to async record from microphone
from flask import Flask, request, Response, json

app = Flask(__name__)

# initialize API
api = APIClient("api-sa-prod.json", env="prod")  # create client
rt_mgr = RealtimeSTT(api)  # create realtime manager

# start session
def callback(data):
    print(data['txt'][::-1])  # Reverse for proper view of Hebrew in terminal. 

rt_mgr.start_session(callback, profile=Profiles.default)

sock = rt_mgr.connect()

# create recorder
rec = Recorder(as_base64=True, buffer_sec=3)  # encode samples as base64, to send the chunks over web-socket
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

@app.route('/rt', methods=['POST'])
def add_user(**kwargs):
    name = "add_user"
    section = tag.SECTION.FUNCTION
    fields, regex = get_regex_and_validation_regex(name, section)
    return general_request(mang._add_user, fields, regex=regex,
                           **kwargs)


app.run(host="127.0.0.1", port=5000)

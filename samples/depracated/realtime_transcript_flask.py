import time
from sumit_sdk.api import APIClient
from sumit_sdk.realtime_stt import RealtimeSTT
from sumit_sdk.realtime_stt import Profiles, VadProfile
from sumit_sdk.utils.audio_helper import Recorder  # helper class to async record from microphone
from flask import Flask, request, Response, json, render_template
from threading import Thread
from flask_socketio import SocketIO, emit
import asyncio

app = Flask(__name__, template_folder='webui')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# initialize API
api = APIClient("api-sa.json")  # create client
rt_mgr = RealtimeSTT(api)  # create realtime manager
transcriptions = []

@app.route('/', methods=['POST', 'GET'])
def index(**kwargs):
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')


@app.route('/transcription')
def suggestions():
    return render_template('transcript.html', transcriptions=transcriptions)

last_two_texts = []
# start session
def callback(data):
    # global transcriptions
    print(data['txt'][::-1])  # Reverse for proper view of Hebrew in terminal. 
    # transcriptions.append(data['txt'])
    global last_two_texts
    last_two_texts.append(data['txt'])
    last_two_texts = last_two_texts[-2:]
    socketio.emit('update_texts', {'texts': last_two_texts})

rt_mgr.start_session(callback, profile=Profiles.default, vad_profile=VadProfile.default) 

sock = rt_mgr.connect()

# create recorder
rec = Recorder(as_base64=True, buffer_sec=3)  # encode samples as base64, to send the chunks over web-socket
rec.start()

Thread(target=lambda: socketio.run(app, host="127.0.0.1", port=5000, debug=False)).start()

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


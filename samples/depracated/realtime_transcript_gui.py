import time
from sumit_sdk.api import APIClient
from sumit_sdk.realtime_stt import RealtimeSTT
from sumit_sdk.utils.audio_helper import Recorder  # helper class to async record from microphone
import gradio as gr  # for GUI
import numpy as np
import queue
import base64
import scipy.signal as sps
from scipy import signal

# initialize API
api = APIClient("api-sa-prod.json")  # create client
rt_mgr = RealtimeSTT(api)  # create realtime manager

# start session
txt_buf = queue.Queue()
def callback(data):
    txt_buf.put(data)

rt_mgr.start_session(callback)
sock = rt_mgr.connect()

# create recorder GUI
def butter_lowpass(lowcut, fs, order=10):
    nyq = 0.5 * fs
    low = lowcut / nyq
    sos = signal.butter(order, low, analog=False, btype='low', output='sos')
    return sos

sos = None # butter_lowpass(15680, 44100, 5)
def reformat_freq(sr, y):
    global sos
    if sos is None:
        sos = butter_lowpass(15680, sr, 5)
    if len(y.shape) > 1:
        y = (y[:,0]+y[:,1])*0.5
    number_of_samples = round(len(y) * float(16000) / sr)
    data = signal.sosfilt(sos, y)
    data = sps.resample(data, number_of_samples)
    return sr, data.astype(np.int16)

audio_buf = np.array([], dtype=np.int16)
def transcribe(speech, state=""):
    global audio_buf
    try:
        sr, y = reformat_freq(*speech)
    except:
        print("failed to parse data")
    audio_buf = np.concatenate([audio_buf, y])
    if len(audio_buf) < 46000:
        return state, state
    data = base64.b64encode(audio_buf.tobytes())
    audio_buf = np.array([], dtype=np.int16)
    rt_mgr.send(sock, data)
    try:
        ready = txt_buf.get(block=False)
        while ready is not None:
            if ready:
                text = ready["txt"]
                state += text + " "
            try:
                ready = txt_buf.get(block=False)
            except:
                break
    except:
        pass
    return state, state

gr.Interface(
    fn=transcribe,
    inputs=[
        gr.Audio(source="microphone", type="numpy", streaming=True, label="Speech"),
        "state"
    ],
    outputs=[
        gr.Textbox(label="Transcript"),
        "state"
    ],
    theme=gr.themes.Soft(),
    title="Sumit Realtime Example",
    allow_flagging="never",
    live=True).launch()

# cleanup
rt_mgr.stop_session()

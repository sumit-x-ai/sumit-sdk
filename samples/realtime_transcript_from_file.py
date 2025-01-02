import time
from sumit_sdk.api import APIClient
from sumit_sdk.realtime_stt import RealtimeSTT
from sumit_sdk.realtime_stt import Profiles, VadProfile
from sumit_sdk.realtime_stt import BufferMode
from sumit_sdk.utils.audio_helper import Recorder  # helper class to async record from microphone
from scipy.io import wavfile as wf
from threading import Thread, Event
import sys

class FileRecorder(Recorder):
    def __init__(self, filename: str, as_base64=False, buffer_sec: float = 1) -> None:
        super().__init__(as_base64, buffer_sec)
        self.filename = filename
        self.sr, self.data = wf.read(self.filename)
        self.stop_sig = Event()
        self._ix = 0
        self._thread = None
    
    def _start(self):
        while not self.stop_sig.is_set():
            time.sleep(self.TIME_BUFFER)
            d = self.data[self._ix:self._ix+self.CHUNK]
            self._fill_buffer(d.tobytes(), None, None, None)
            self._ix += self.CHUNK
            if self._ix >= self.data.shape[0]:
                self.stop()
    
    def start(self):
        self.stop_sig.clear()
        self._thread = Thread(target=self._start)
        self._thread.start()
    
    def stop(self):
        self.stop_sig.set()

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

rt_mgr.start_session(write_segments_callbcak, profile=Profiles.accurate, vad_profile=VadProfile.low, buffer_mode=BufferMode.default) 

sock = rt_mgr.connect()

# create recorder
rec = FileRecorder(sys.argv[1], as_base64=True, buffer_sec=2.5)  # encode samples as base64, to send the chunks over web-socket
rec.start()
stop_sig = False
with open('out.txt', 'a') as fd:
    fd.write(f'{time.time()}\t\tSTART_NEW_SESSION\n')
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

import pyaudio
import queue
import numpy as np
import base64

class Recorder:
    def __init__(self, as_base64=False, buffer_sec: float = 1) -> None:
        self.RATE = 16000
        self.TIME_BUFFER = buffer_sec
        self.CHUNK = int(self.RATE*self.TIME_BUFFER)
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self._p = None
        self._stream = None
        self._ab64 = as_base64
        self._buff = queue.Queue()
    
    def start(self):
        self._p = pyaudio.PyAudio()
        self._stream = self._p.open(format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK,
                    stream_callback=self._fill_buffer)
    
    def stop(self):
        self._stream.stop_stream()
        self._stream.close()
        self._p.terminate()
    
    def safe_get(self):
        try:
            data = self._buff.get(block=False)
        except:
            data = None
        return data
    
    def _fill_buffer(self, in_data, frame_count, time_info, status):
        d = np.frombuffer(in_data, np.int16)
        audio = (d / np.abs(d).max())*(2**15-1)
        audio = audio.astype(np.int16)
        if self._ab64:
            audio = base64.b64encode(audio.tobytes())
        self._buff.put(audio)
        return None, pyaudio.paContinue

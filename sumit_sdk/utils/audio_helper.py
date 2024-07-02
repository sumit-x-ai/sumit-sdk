import pyaudio
import queue
import numpy as np
import base64
try:
    import sumit_sdk.utils.downsample_helper as dsh
except:
    print("failed to import downsampler")

class Recorder:
    def __init__(self, as_base64=False, buffer_sec: float = 1, sr=16000, norm=True, out_sr=16000) -> None:
        self.RATE = sr
        self.OUT_RATE = out_sr
        self.TIME_BUFFER = buffer_sec
        if self.RATE:
            self.CHUNK = int(self.RATE*self.TIME_BUFFER)
        else:
            self.CHUNK = int(self.OUT_RATE*self.TIME_BUFFER)
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self._p = None
        self.norm = norm
        self._stream = None
        self._ab64 = as_base64
        self._buff = queue.Queue()
        self.downsampler = None
    
    def start(self, in_dev=None):
        self._p = pyaudio.PyAudio()
        if in_dev and not self.RATE:
            inf = self._p.get_device_info_by_index(in_dev)
            self.RATE = int(inf['defaultSampleRate'])
            print("set rate to", self.RATE)
            self.CHUNK = int(self.RATE*self.TIME_BUFFER)
        if self.OUT_RATE < self.RATE:
            self.downsampler = dsh.Downsampler()
            self.downsampler.create_filter(self.OUT_RATE, self.RATE, guard=0.99)
        self._stream = self._p.open(format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK,
                    input_device_index=in_dev,
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
        if self.norm and np.abs(d).max() > 0:
            audio = (d / np.abs(d).max())*(2**15-1)
        else:
            audio = d
        if self.OUT_RATE < self.RATE:
            audio = self.downsampler.downsample_audio(audio, self.RATE, self.OUT_RATE)
        audio = audio.astype(np.int16)
        if self._ab64:
            audio = base64.b64encode(audio.tobytes())
        self._buff.put(audio)
        return None, pyaudio.paContinue

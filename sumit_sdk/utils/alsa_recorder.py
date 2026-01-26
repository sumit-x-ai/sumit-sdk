import alsaaudio
import queue
import numpy as np
import base64
import threading
try:
    import sumit_sdk.utils.downsample_helper as dsh
except:
    print("failed to import downsampler")


class Recorder:
    def __init__(self, as_base64=False, buffer_sec: float = 1, sr=16000, norm=False, out_sr=16000) -> None:
        self.RATE = sr
        self.OUT_RATE = out_sr
        self.TIME_BUFFER = buffer_sec
        self.CHUNK = int(self.RATE * self.TIME_BUFFER)
        self.FORMAT = alsaaudio.PCM_FORMAT_S16_LE
        self.CHANNELS = 1
        self._stream = None
        self.norm = norm
        self._ab64 = as_base64
        self._buff = queue.Queue()
        self.buffer_thread = None
        self.stop_sig = threading.Event()
        self.downsampler = None
        

    def start(self, in_dev=None):
        if in_dev:
            self._stream = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, mode=alsaaudio.PCM_NORMAL, device=in_dev)
        else:
            self._stream = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, mode=alsaaudio.PCM_NORMAL)
        if self.OUT_RATE < self.RATE:
            self.downsampler = dsh.Downsampler()
            self.downsampler.create_filter(self.OUT_RATE, self.RATE, guard=0.99)
        self._stream.setchannels(self.CHANNELS)
        self._stream.setrate(self.RATE)
        self._stream.setformat(self.FORMAT)
        self._stream.setperiodsize(self.CHUNK)
        self.stop_sig.clear()
        self.buffer_thread = threading.Thread(target=self._fill_buffer)
        self.buffer_thread.start()

    def stop(self):
        self._stream.close()
        self._stream = None  # Just dereference the stream

    def safe_get(self):
        try:
            data = self._buff.get(block=False)
        except queue.Empty:
            data = None
        return data

    def _fill_buffer(self):
        while self._stream and not self.stop_sig.is_set():
            length, in_data = self._stream.read()
            if length > 0:
                audio = np.frombuffer(in_data, np.int16)
                # print(audio, audio.shape)
                # if np.abs(d).max() > 0:
                #     audio = (d / np.abs(d).max()) * (2 ** 15 - 1)
                # else:
                #     audio = d
                # audio = audio.astype(np.int16)
                if self.norm and np.abs(d).max() > 0:
                    audio = (audio / np.abs(audio).max())*(2**15-1).astype(np.int16)
                if self.OUT_RATE < self.RATE:
                    audio = self.downsampler.downsample_audio(audio, self.RATE, self.OUT_RATE)
                    audio = audio.astype(np.int16)
                if self._ab64:
                    audio = base64.b64encode(audio.tobytes())
                self._buff.put(audio)

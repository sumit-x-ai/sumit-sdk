import streamlink
import subprocess
import threading
from threading import Event
import queue
import time
import base64
import ffmpeg
import numpy as np

class StreamlinkHelper:
    def __init__(self, chunk_len=1, as_base64=False) -> None:
        self.ffmpeg_process = None
        self.streamlink_process = None
        self.reader_thread = None
        self.reader_stop_sig = Event()
        self.n_bytes = int(chunk_len *16000*2)
        self.interval = chunk_len
        self._ab64 = as_base64
        self._buff = queue.Queue()
    
    def open_stream(self, stream, direct_url=None, preferred_quality='audio_only', sample_rate=16000):
        if direct_url:
            try:
                process = (
                    ffmpeg.input(stream, loglevel="panic")
                    .output("pipe:", format="s16le", acodec="pcm_s16le", ac=1, ar=sample_rate)
                    .run_async(pipe_stdout=True)
                )
            except ffmpeg.Error as e:
                raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e
            self.ffmpeg_process = process
            return True

        stream_options = streamlink.streams(stream)
        if not stream_options:
            raise RuntimeError("No streams found on:", stream)
            return False

        option = None
        for quality in [preferred_quality, 'audio_only', 'audio_mp4a', 'audio_opus', 'best']:
            if quality in stream_options:
                option = quality
                break
        if option is None:
            # Fallback
            option = next(iter(stream_options.values()))

        def writer(streamlink_proc, ffmpeg_proc):
            while (not streamlink_proc.poll()) and (not ffmpeg_proc.poll()):
                try:
                    chunk = streamlink_proc.stdout.read(1024)
                    ffmpeg_proc.stdin.write(chunk)
                except (BrokenPipeError, OSError):
                    pass

        cmd = ['streamlink', stream, option, "-O"]
        streamlink_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        try:
            ffmpeg_process = (
                ffmpeg.input("pipe:", loglevel="panic")
                .output("pipe:", format="s16le", acodec="pcm_s16le", ac=1, ar=sample_rate)
                .run_async(pipe_stdin=True, pipe_stdout=True)
            )
        except ffmpeg.Error as e:
            raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

        thread = threading.Thread(target=writer, args=(streamlink_process, ffmpeg_process))
        thread.start()
        self.ffmpeg_process = ffmpeg_process
        self.streamlink_process = streamlink_process
        return True

    def read_chunk(self, leng):
        in_bytes = self.ffmpeg_process.stdout.read(self.n_bytes)
        if in_bytes:
            in_bytes = np.frombuffer(in_bytes, np.int16).flatten()
        return in_bytes

    def _async_read_func(self):
        while not self.reader_stop_sig.is_set():
            data = self.read_chunk(self.n_bytes)
            if data is not None:
                self._fill_buffer(data)
                time.sleep(self.interval/2)
    
    def _async_read_func_agg(self):
        agg = np.array([], dtype=np.int16)
        csize = self.n_bytes //10
        while not self.reader_stop_sig.is_set():
            data = self.read_chunk(csize)
            if data:
                agg = np.concatenate([agg, data])
                if len(agg)/16000 >= self.interval:
                    self._fill_buffer(agg[:int(self.interval*16000)])
                    try:
                        agg = agg[int(self.interval*16000):]
                    except:
                        agg = np.array([], dtype=np.int16)
                time.sleep(self.interval/10)

    def async_read(self, aggregate=True):
        self.reader_thread = threading.Thread(target=self._async_read_func)
        self.reader_stop_sig.clear()
        self.reader_thread.start()

    def safe_get(self):
        try:
            data = self._buff.get(block=False)
        except:
            data = None
        return data
    
    def _fill_buffer(self, in_data):
        audio = in_data
        if self._ab64:
            audio = base64.b64encode(audio.tobytes())
        self._buff.put(audio)

    def stop(self):
        self.reader_stop_sig.set()
        if self.reader_thread:
            try:
                self.reader_thread.join(3)
            except:
                pass
        self.ffmpeg_process.kill()
        if self.streamlink_process:
            self.streamlink_process.kill()

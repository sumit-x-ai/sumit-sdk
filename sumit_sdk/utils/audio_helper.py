import pyaudio
import queue
import numpy as np
import base64
import logging

log = logging.getLogger(__name__)
try:
    import sumit_sdk.utils.downsample_helper as dsh
except:
    print("failed to import downsampler")


class Recorder:
    def __init__(self, as_base64=False, buffer_sec: float = 1, sr=16000, norm=True, out_sr=16000, channels=1,
                 mixdown_channels=None, zero_phase_lpf=False) -> None:
        self.RATE = sr
        self.OUT_RATE = out_sr
        self.TIME_BUFFER = buffer_sec
        if self.RATE:
            self.CHUNK = int(self.RATE * self.TIME_BUFFER)
        else:
            self.CHUNK = int(self.OUT_RATE * self.TIME_BUFFER)
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.mixdown_channels = mixdown_channels
        self._p = None
        self.norm = norm
        self._stream = None
        self._ab64 = as_base64
        self._buff = queue.Queue()
        self.downsampler = None
        self.downsample_func = None
        self.zero_phase_lpf = zero_phase_lpf

    def start(self, in_dev=None):
        # idempotent: לעולם לא לפתוח חדש מעל ישן פתוח
        if self._stream is not None or self._p is not None:
            self.stop()
        # ניקוי buffer מ-session קודם
        with self._buff.mutex:
            self._buff.queue.clear()

        self._p = pyaudio.PyAudio()
        try:
            if in_dev is not None and not self.RATE:
                inf = self._p.get_device_info_by_index(in_dev)
                self.RATE = int(inf['defaultSampleRate'])
                # print("set rate to", self.RATE)
                self.CHUNK = int(self.RATE * self.TIME_BUFFER)
            if self.OUT_RATE < self.RATE:
                if self.zero_phase_lpf:
                    self.downsample_func = dsh.Downsampler.resample_poly
                else:
                    self.downsampler = dsh.Downsampler()
                    self.downsampler.create_filter(self.OUT_RATE, self.RATE, guard=0.99)
                    self.downsample_func = self.downsampler.downsample_audio
            self._stream = self._p.open(format=self.FORMAT,
                                        channels=self.CHANNELS,
                                        rate=self.RATE,
                                        input=True,
                                        frames_per_buffer=self.CHUNK,
                                        input_device_index=in_dev,
                                        stream_callback=self._fill_buffer)
        except Exception:
            # אם הפתיחה נכשלה - אל תשאיר PyAudio תלוי שמחזיק את ההתקן
            self.stop()
            raise

    # TODO(yishay): stream_is_active() returns get_time() (float) instead of a real
    #   active flag. Despite the name, the return type is a timestamp, not a bool.
    #   Edge case: get_time() can return 0.0 on an active stream -> falsy -> callers
    #   treating it as "is active" get a wrong answer.
    #   Proposed fix: return self._stream.is_active().
    #   RISK: this is a PUBLIC SDK method. Changing the return type (float -> bool)
    #   may break external consumers who use the returned value as a stream time.
    #   REVIEWER: is it worth changing? Options:
    #     (a) change to is_active() and accept the breaking change (bump major?),
    #     (b) keep get_time() and add a separate is_active() method,
    #     (c) leave as-is.
    #   Out of scope for the device-release fix; left for a separate, coordinated change.
    def stream_is_active(self):
        if not self._stream:
            return False
        try:
            return self._stream.get_time()
        except:
            return False

    def stop(self):
        s, p = self._stream, self._p
        try:
            if s is not None:
                s.stop_stream()
        except Exception as e:
            log.warning(f"stop_stream failed: {e}", exc_info=True)
        try:
            if s is not None:
                s.close()  # רץ גם אם stop_stream נכשל
        except Exception as e:
            log.warning(f"close failed: {e}", exc_info=True)
        try:
            if p is not None:
                p.terminate()  # רשת ביטחון: סוגר כל stream שנשאר במופע
        except Exception as e:
            log.warning(f"terminate failed: {e}", exc_info=True)
        self._stream = None
        self._p = None

    def safe_get(self):
        try:
            data = self._buff.get(block=False)
        except:
            data = None
        return data

    def _fill_buffer(self, in_data, frame_count, time_info, status):
        try:
            d = np.frombuffer(in_data, np.int16)
            if d.size == 0:
                return None, pyaudio.paContinue
            if self.CHANNELS > 1:
                d = d.reshape(-1, self.CHANNELS).T
                if self.mixdown_channels:
                    d = np.mean(d[self.mixdown_channels, :], axis=0)
            peak = np.abs(d).max()
            if self.norm and peak > 0:
                audio = (d / peak) * (2 ** 15 - 1)
            else:
                audio = d
            if self.OUT_RATE < self.RATE:
                if audio.ndim > 1:
                    audio = np.array(
                        [self.downsample_func(audio[c, :], self.RATE, self.OUT_RATE)
                         for c in range(audio.shape[0])],
                        dtype=audio.dtype)
                else:
                    audio = self.downsample_func(audio, self.RATE, self.OUT_RATE)
            audio = audio.astype(np.int16)
            if self._ab64:
                audio = base64.b64encode(audio.tobytes())
            self._buff.put(audio)
        except Exception as e:
            # קריטי: לעולם לא לתת לחריגה לצאת מה-callback - היא הורגת את ה-stream
            log.warning(f"_fill_buffer error, dropping frame: {e}", exc_info=True)
        return None, pyaudio.paContinue
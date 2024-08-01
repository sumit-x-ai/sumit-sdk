import numpy as np
from scipy.signal import butter, lfilter, resample, resample_poly

class Downsampler:
    def __init__(self):
        self.filter_b = None
        self.filter_a = None
    
    def create_filter(self, target_fs, fs, order=5, guard=1):
        cutoff = target_fs / 2 * guard
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        self.filter_b, self.filter_a = butter(order, normal_cutoff, btype='low', analog=False)

    def downsample_audio(self, audio, original_fs, target_fs):
        filtered_audio = lfilter(self.filter_b, self.filter_a, audio)
        # Calculate the number of samples in the downsampled audio
        num_samples = int(len(filtered_audio) * target_fs / original_fs)

        # Resample the audio
        downsampled_audio = resample(filtered_audio, num_samples)

        return downsampled_audio

    @staticmethod
    def resample_poly(audio, original_fs, target_fs):
        filtered = resample_poly(audio, up=target_fs, down=original_fs)
        filtered = filtered.astype(audio.dtype)
        return filtered

import numpy


class AudioClip:
    def __init__(self, samples: numpy.ndarray, sample_rate: int, channels: int):
        self.samples = samples
        self.sample_rate = sample_rate
        self.channels = channels

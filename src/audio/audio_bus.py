import numpy
from typing import Self

from audio.root_audio_bus import RootAudioBus


class AudioBus:
    def __init__(
        self,
        name: str,
        childs: list[Self | RootAudioBus | None] = [],
        volume: float = 1.0,
        pitch: float = 1.0,
    ):
        self.name = name

        self.childs = childs
        for child in childs:
            child.master = self
        self.master: Self | None = None

        self._volume = volume
        self._pitch = pitch

        self.buffer: numpy.ndarray | None = None

    def mix(self, frame_count):
        output = numpy.zeros((frame_count, 2), dtype=numpy.float32)

        for child in self.childs:
            child.mix(frame_count)
            output += child.buffer

        self.buffer = output

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, new_volume: float):
        self._volume = new_volume

        for child in self.childs:
            child.volume = new_volume

    @property
    def pitch(self) -> float:
        return self._pitch

    @pitch.setter
    def pitch(self, new_pitch: float):
        self._pitch = new_pitch

        for child in self.childs:
            child._pitch = new_pitch

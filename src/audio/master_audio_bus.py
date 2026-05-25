from audio.audio_bus import AudioBus
from audio.root_audio_bus import RootAudioBus
import numpy


class MasterAudioBus(AudioBus):
        def __init__(self, childs: list[AudioBus | RootAudioBus | None] = [], volume: float = 1.0, pitch: float = 1.0):
                super().__init__('master', childs, volume, pitch)
        
        def generator(self):
                frame_count = yield

                while True:
                        self.mix(frame_count)

                        output = numpy.clip(
                                self.buffer,
                                -1.0,
                                1.0
                        )

                        frame_count = yield output.astype(
                                numpy.float32
                        ).tobytes()
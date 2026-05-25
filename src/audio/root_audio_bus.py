from typing import TYPE_CHECKING

if TYPE_CHECKING:
        from audio.audio_bus import AudioBus
from audio.audio_voice import AudioVoice
import miniaudio
import numpy

class RootAudioBus:
        def __init__(self, name: str, volume: float = 1.0, pitch: float = 1.0):
                self.master: AudioBus = None
                
                self.name = name
                
                self.volume = volume
                self.pitch = pitch
                
                self.buffer: numpy.ndarray | None = None

                self.voices = []
        
        def add_voice(self, voice : AudioVoice):
                self.voices.append(voice)

        def mix(self, frame_count):
                output = numpy.zeros(
                        (frame_count, 2),
                        dtype = numpy.float32
                )

                dead = []

                for voice in self.voices:
                        if voice.playing:
                                voice.mix(output, frame_count)
                        else:
                                dead.append(voice)

                for voice in dead:
                        self.voices.remove(voice)

                numpy.clip(
                        output,
                        -1.0,
                        1.0,
                        out = output
                )
                
                self.buffer = output
                
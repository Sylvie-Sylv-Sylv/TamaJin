import miniaudio
import numpy

class Outmix:
        def __init__(self):
                self.playback_device = miniaudio.PlaybackDevice(
                        output_format = miniaudio.SampleFormat.FLOAT32,
                        nchannels = 2,
                        sample_rate = 44100
                )

                self.voices = []

        def mix(self, output, frames):
                output[:] = 0

                dead = []

                for voice in self.voices:
                        if voice.playing:
                                voice.mix(output, frames)
                        else:
                                dead.append(voice)

                for voice in dead:
                        self.voices.remove(voice)

                numpy.clip(
                        output,
                        -1.0,
                        1.0,
                        out=output
                )

        def generator(self):
                frames = yield b""

                while True:
                        output = numpy.zeros(
                                (frames, 2),
                                dtype=numpy.float32
                        )

                        self.mix(output, frames)
                        frames = yield output.tobytes()

        def play(self):
                self.stream = self.generator()
                next(self.stream)
                self.playback_device.start(self.stream)

        def stop(self):
                self.playback_device.stop()
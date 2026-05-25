from audio.audio_clip import AudioClip

class AudioVoice:
        def __init__(
                self,
                clip: AudioClip,
                position = 0.0,
                pitch = 1.0,
                volume = 1.0,
                looping = False,
                playing = False
        ):
                self.clip = clip

                self.position = position

                self.pitch = pitch
                self.volume = volume

                self.looping = looping
                self.playing = playing

        def mix(self, output, frames):
                samples = self.clip.samples

                for i in range(frames):
                        pos = int(self.position)

                        if pos >= len(samples):
                                if self.looping:
                                        self.position = 0.0
                                        pos = 0
                                else:
                                        self.playing = False
                                        break

                        sample = samples[pos]
                        output[i] += sample * self.volume
                        self.position += self.pitch
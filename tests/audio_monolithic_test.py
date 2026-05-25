import wave
import numpy
import miniaudio
import pygame
import time


# =========================================================
# AUDIO CLIP
# =========================================================

class AudioClip:

        def __init__(
                self,
                samples: numpy.ndarray,
                sample_rate: int,
                channels: int
        ):
                self.samples = samples
                self.sample_rate = sample_rate
                self.channels = channels


# =========================================================
# WAV LOADER
# =========================================================

def load_wav(path: str) -> AudioClip:
        with wave.open(path, "rb") as wav:
                channels = wav.getnchannels()
                sample_rate = wav.getframerate()
                sample_width = wav.getsampwidth()
                frame_count = wav.getnframes()

                raw_data = wav.readframes(frame_count)

        if sample_width == 1:
                dtype = numpy.uint8

        elif sample_width == 2:
                dtype = numpy.int16

        elif sample_width == 4:
                dtype = numpy.int32

        else:
                raise ValueError("Unsupported sample width")

        samples = numpy.frombuffer(raw_data, dtype=dtype)

        if sample_width == 1:
                samples = (
                        samples.astype(numpy.float32) - 128
                ) / 128.0

        elif sample_width == 2:
                samples = (
                        samples.astype(numpy.float32)
                ) / 32768.0

        elif sample_width == 4:
                samples = (
                        samples.astype(numpy.float32)
                ) / 2147483648.0

        samples = samples.reshape(-1, channels)

        return AudioClip(
                samples=samples,
                sample_rate=sample_rate,
                channels=channels
        )


# =========================================================
# OGG LOADER
# =========================================================

def load_ogg(path: str) -> AudioClip:
        decoded = miniaudio.decode_file(path)

        samples = numpy.frombuffer(
                decoded.samples,
                dtype=numpy.int16
        )

        samples = samples.reshape(
                -1,
                decoded.nchannels
        )

        samples = (
                samples.astype(numpy.float32)
                / 32768.0
        )

        return AudioClip(
                samples=samples,
                sample_rate=decoded.sample_rate,
                channels=decoded.nchannels
        )


# =========================================================
# AUDIO VOICE
# =========================================================

class AudioVoice:

        def __init__(
                self,
                clip: AudioClip,
                position=0.0,
                pitch=1.0,
                volume=1.0,
                looping=False,
                playing=False
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


# =========================================================
# MIXER
# =========================================================

class Mixer:

        def __init__(self):

                self.playback_device = miniaudio.PlaybackDevice(
                        output_format=miniaudio.SampleFormat.FLOAT32,
                        nchannels=2,
                        sample_rate=44100
                )

                self.voices = []

        def mix(self, output, frames):

                output[:] = 0

                dead = []

                for voice in self.voices:

                        if voice.playing:
                                voice.mix(output, frames)

                        if not voice.playing:
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


# =========================================================
# CREATE MIXER
# =========================================================

mixer = Mixer()


# =========================================================
# LOAD SOUND
# =========================================================

sword_hit_clip = load_ogg(
        "resources/test_resources/sword_hit_1.ogg"
)


# =========================================================
# PYGAME
# =========================================================

pygame.init()

screen = pygame.display.set_mode((800, 600))

clock = pygame.time.Clock()

running = True


# =========================================================
# START AUDIO
# =========================================================

mixer.play()


# =========================================================
# TIMER
# =========================================================

last_sound_time = time.time()


# =========================================================
# MAIN LOOP
# =========================================================

while running:

        for event in pygame.event.get():

                if event.type == pygame.QUIT:
                        running = False

        current_time = time.time()

        # play sound every 3 seconds

        if current_time - last_sound_time >= 3.0:

                mixer.voices.append(
                        AudioVoice(
                                sword_hit_clip,
                                volume=1.0,
                                playing=True
                        )
                )

                last_sound_time = current_time

        screen.fill((30, 30, 30))

        pygame.display.flip()

        clock.tick(60)


# =========================================================
# CLEANUP
# =========================================================

mixer.stop()

pygame.quit()
from audio.audio_clip import AudioClip
import wave
import numpy
import miniaudio

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
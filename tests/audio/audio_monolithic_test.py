import wave
from audio.audio_bus import AudioBus
from audio.master_audio_bus import MasterAudioBus
from audio.root_audio_bus import RootAudioBus
import numpy
import miniaudio
import pygame
import time

from audio.audio_voice import AudioVoice
from audio.utils import load_ogg

sfx_bus = RootAudioBus("sfx_bus")
music_bus = RootAudioBus("music_bus")

middle_bus = AudioBus("middle_bus", [sfx_bus, music_bus])

master_bus = MasterAudioBus([middle_bus])

playback_device = miniaudio.PlaybackDevice(
    output_format=miniaudio.SampleFormat.FLOAT32, nchannels=2, sample_rate=44100
)

sword_hit_clip = load_ogg("resources/test_resources/sword_hit_1.ogg")

if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((800, 600))

    clock = pygame.time.Clock()

    running = True

    stream = master_bus.generator()
    next(stream)
    playback_device.start(stream)

    last_sound_time = time.time()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = time.time()

        # play sound every 3 seconds

        if current_time - last_sound_time >= 2.0:
            sfx_bus.add_voice(AudioVoice(sword_hit_clip, volume=1.0, playing=True))

            last_sound_time = current_time

        screen.fill((30, 30, 30))

        pygame.display.flip()

        clock.tick(60)

    playback_device.stop()

    pygame.quit()

import wave
import numpy
import miniaudio
import pygame
import time

from audio.outmix import Outmix
from audio.audio_voice import AudioVoice
from audio.utils import load_ogg

outmix = Outmix()

sword_hit_clip = load_ogg("resources/test_resources/sword_hit_1.ogg")

pygame.init()

screen = pygame.display.set_mode((800, 600))

clock = pygame.time.Clock()

running = True

outmix.play()

last_sound_time = time.time()

while running:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        running = False

        current_time = time.time()

        # play sound every 3 seconds

        if current_time - last_sound_time >= 3.0:
                outmix.voices.append(
                        AudioVoice(
                                sword_hit_clip,
                                volume = 1.0,
                                playing = True
                        )
                )

                last_sound_time = current_time

        screen.fill((30, 30, 30))

        pygame.display.flip()

        clock.tick(60)

outmix.stop()

pygame.quit()
"""
PyGame audio test - plays looping tone with visual feedback.
Run: python tests/audio_pygame_test.py
"""

import pygame
import numpy as np
import time
import sys

def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    
    print(f"PyGame: {pygame.version.ver}")
    print(f"Mixer: {pygame.mixer.get_init()}")
    print()
    
    # Generate 440Hz tone
    SAMPLE_RATE = 44100
    DURATION = 1.0
    FREQUENCY = 440
    
    frames = int(DURATION * SAMPLE_RATE)
    t = np.linspace(0, DURATION, frames)
    samples = np.sin(2 * np.pi * FREQUENCY * t)
    
    # Convert to 16-bit stereo
    data = (samples * 32767).astype(np.int16)
    stereo = np.column_stack([data, data])
    
    # Create sound
    sound = pygame.mixer.Sound(buffer=stereo.tobytes())
    sound.set_volume(0.5)
    channel = sound.play(-1)  # Loop forever
    
    print(f"Playing {FREQUENCY}Hz tone (loops)")
    print("=" * 50)
    
    # Play with progress bar
    try:
        for i in range(50):
            time.sleep(0.1)
            
            # Progress bar
            bar_len = 40
            filled = int(bar_len * i / 50)
            bar = "[" + "#" * filled + " " * (bar_len - filled) + "]"
            
            status = "PLAYING" if channel.get_busy() else "PAUSED"
            sys.stdout.write(f"\r{bar} {i//10}s {status}    ")
            sys.stdout.flush()
            
    except KeyboardInterrupt:
        print("\nStopped")
    
    print()
    pygame.mixer.stop()
    pygame.quit()
    print("Done!")

if __name__ == "__main__":
    main()
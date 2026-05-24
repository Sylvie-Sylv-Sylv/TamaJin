"""
PyGame Audio Test - Pure Framework

Tests the complete audio pipeline using ONLY our framework:
- AudioSource (ECS)
- AudioVoice, VoicePool, ClipDatabase
- AudioBus, AudioGraph
- SpatialProcessor
- CallbackBackend (no pygame mixer)

Run: python tests/audio_pygame_test.py
"""

import pygame
import numpy as np
import sys
import math
import wave
import struct

from audio.audio_source import AudioSource, AudioListener, BusIndex
from audio.voice import AudioVoice, VoicePool, ClipDatabase, SpatialProcessor
from audio.bus import AudioBus
from audio.graph import AudioGraph
from audio.clip import create_tone_clip, create_silent_clip
from audio.backend import CallbackBackend, BufferedBackend, SoundDeviceBackend


def main():
    pygame.init()
    
    print("=" * 60)
    print("TamaJin Pure Framework Audio Test")
    print("=" * 60)
    print(f"PyGame: {pygame.version.ver}")
    print()
    
    # Create buffered backend to capture audio (our framework!)
    buffer_backend = BufferedBackend(max_buffers=1000)
    
    # Callback - just store (no pygame playback)
    def audio_callback(buffer):
        buffer_backend.submit(buffer.copy())
    
    # Create callback backend
    callback_backend = CallbackBackend(
        callback=audio_callback,
        sample_rate=48000,
        channels=2
    )
    
    # Initialize audio graph
    graph = AudioGraph(
        buffer_size=512,
        sample_rate=48000
    )
    graph.add_bus("sfx")
    graph.add_bus("music")
    graph.add_bus("voice")
    # Create sounddevice backend for real-time playback
    # Use device 8 (Speakers via WASAPI) for low latency
    # Note: Device uses 48000 Hz sample rate
    sounddevice_backend = SoundDeviceBackend(
        sample_rate=48000,
        channels=2,
        blocksize=512,
        device=8  # WASAPI Speakers
    )
    graph.add_master("master", backend=sounddevice_backend)
    graph.connect("sfx", "master")
    graph.connect("music", "master")
    graph.connect("voice", "master")
    
    # Create clip database
    db = ClipDatabase()
    
    # Create test tones (2 seconds each)
    tone_440 = create_tone_clip(440.0, 2.0, 48000, 1)
    tone_880 = create_tone_clip(880.0, 2.0, 48000, 1)
    tone_220 = create_tone_clip(220.0, 2.0, 48000, 1)
    tone_660 = create_tone_clip(660.0, 2.0, 48000, 1)
    
    # Add to database
    db.add(tone_440, "tone_440")
    db.add(tone_880, "tone_880")
    db.add(tone_220, "tone_220")
    db.add(tone_660, "tone_660")
    
    print("Clips loaded:")
    for i in range(db.count):
        clip = db.get(i)
        print(f"  [{i}] {clip.frames} frames, {clip.sample_rate}Hz")
    print()
    
    # Create voice pool
    pool = VoicePool()
    
    # Create spatial processor
    spatial = SpatialProcessor(listener_x=400, listener_y=300)
    
    # Get buses
    sfx_bus = graph.get_bus("sfx")
    music_bus = graph.get_bus("music")
    voice_bus = graph.get_bus("voice")
    
    # Play sounds on different buses (our framework!)
    sfx_bus.play(tone_440, volume=0.8, looping=True)
    music_bus.play(tone_220, volume=0.8, looping=True)
    voice_bus.play(tone_880, volume=0.8, looping=True)
    
    print("Playing: SFX 440Hz @ 80% (looping)")
    print("Playing: Music 220Hz @ 80% (looping)")
    print("Playing: Voice 880Hz @ 80% (looping)")
    print()
    print("NOTE: Audio saved to test_output.wav - play it to hear!")
    
    # Create window
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("TamaJin Pure Framework Audio Test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    running = True
    frame = 0
    sounds_playing = True
    
    print("=" * 60)
    print("Controls: [SPACE] toggle  [Q] quit")
    print("=" * 60)
    print()
    
    while running:
        frame += 1
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_SPACE:
                    sounds_playing = not sounds_playing
                    if sounds_playing:
                        sfx_bus.play(tone_440, volume=0.8, looping=True)
                        music_bus.play(tone_220, volume=0.8, looping=True)
                        voice_bus.play(tone_880, volume=0.8, looping=True)
                        print("Sounds resumed")
                    else:
                        sfx_bus.stop_all()
                        music_bus.stop_all()
                        voice_bus.stop_all()
                        print("Sounds paused")
        
        # Update audio graph (our framework!)
        if sounds_playing:
            # Submit to backend (plays audio in real-time!)
            graph.submit()
            # Also capture for visualization
            buffer = graph.get_output()
            callback_backend.submit(buffer)
            
            # Debug: print buffer stats every 60 frames
            if frame % 60 == 0:
                print(f"  Buffer: shape={buffer.shape}, min={buffer.min():.4f}, max={buffer.max():.4f}")
        
        # Render
        screen.fill((20, 20, 30))
        
        # Draw title
        title = font.render("TamaJin Pure Framework Audio Test", True, (255, 255, 255))
        screen.blit(title, (20, 20))
        
        # Draw bus status
        y = 60
        for bus_name in ["sfx", "music", "voice", "master"]:
            bus = graph.get_bus(bus_name)
            status = f"{bus_name.upper()}: {bus.voice_count} voices, vol={bus.volume:.2f}"
            text = font.render(status, True, (200, 200, 200))
            screen.blit(text, (20, y))
            y += 25
        
        # Draw audio waveform visualization
        if sounds_playing and buffer_backend.buffers:
            last_buffer = buffer_backend.buffers[-1]
            
            # Draw waveform
            center_y = height // 2 + 50
            points = []
            stride = max(1, len(last_buffer) // 100)
            for i in range(0, len(last_buffer), stride):
                x = 50 + (i // stride) * 7
                y = center_y - int(last_buffer[i, 0] * 100)
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(screen, (0, 255, 100), False, points, 2)
            
            # Draw center line
            pygame.draw.line(screen, (50, 50, 50), (50, center_y), (750, center_y), 1)
        
        # Draw animated circles
        center_x, center_y = width // 2, 150
        radius = 150
        
        bus_colors = {
            "sfx": (255, 100, 100),
            "music": (100, 255, 100),
            "voice": (100, 100, 255),
            "master": (255, 255, 100)
        }
        
        for i, bus_name in enumerate(["sfx", "music", "voice", "master"]):
            bus = graph.get_bus(bus_name)
            angle = i * math.pi / 2 + frame * 0.02
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            
            pulse = 20 + bus.voice_count * 10
            color = bus_colors[bus_name]
            
            pygame.draw.circle(screen, color, (int(x), int(y)), pulse)
            pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), pulse, 2)
            
            label = font.render(bus_name.upper(), True, color)
            screen.blit(label, (int(x) - 30, int(y) - 10))
        
        # Draw instructions
        inst = font.render("[SPACE] toggle  [Q] quit", True, (150, 150, 150))
        screen.blit(inst, (20, height - 30))
        
        fps_text = font.render(f"Frame: {frame}  Buffers: {len(buffer_backend.buffers)}", True, (150, 150, 150))
        screen.blit(fps_text, (width - 250, 20))
        
        pygame.display.flip()
        clock.tick(60)
        
        if frame % 60 == 0:
            print(f"Frame {frame}: SFX={sfx_bus.voice_count}, Music={music_bus.voice_count}, Voice={voice_bus.voice_count}")
    
    # Save audio to WAV
    print()
    print("Saving audio to test_output.wav...")
    
    if buffer_backend.buffers:
        # Concatenate all buffers
        all_audio = np.concatenate(buffer_backend.buffers[:300])  # First 300 buffers
        
        # Convert to int16
        int16 = (np.clip(all_audio, -1.0, 1.0) * 32767).astype(np.int16)
        
        # Write WAV
        with wave.open("test_output.wav", "w") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(48000)
            wav.writeframes(int16.tobytes())
        
        print(f"Saved: {len(int16)} frames ({len(int16)/44100:.1f}s)")
        
        # Play using winsound (built-in Windows audio)
        import winsound
        print("Playing audio with winsound...")
        winsound.PlaySound("test_output.wav", winsound.SND_FILENAME)
    
    pygame.quit()
    print()
    print("=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
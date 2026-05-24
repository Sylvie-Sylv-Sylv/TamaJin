"""
VoiceUpdateSystem: Updates voice playback positions.
"""

import numpy as np
from gameplay.scenes.scene import Scene
from gameplay.systems.system import System

from audio.voice import VoicePool


class VoiceUpdateSystem(System):
    """
    System that updates voice playback positions.
    
    Advances sample positions based on pitch.
    Handles looping and voice completion.
    """
    
    @staticmethod
    def step(
        scene: Scene,
        voice_pool: VoicePool,
        buffer_size: int = 512
    ):
        """
        Update all voice positions.
        
        Args:
            scene: Scene (unused, for compatibility)
            voice_pool: Runtime voice pool
            buffer_size: Frames to advance
        """
        # Update each active voice
        for voice in voice_pool._voices[:]:
            if not voice.playing:
                continue
            
            # Advance position
            new_pos = voice.position + int(buffer_size * voice.pitch)
            
            # Handle end of playback
            if new_pos >= voice.frames:
                if voice.looping:
                    # Wrap around
                    voice._position = new_pos % voice.frames
                else:
                    # End of clip
                    voice._position = voice.frames
                    voice._playing = False
            else:
                voice._position = new_pos


class VoiceCleanupSystem(System):
    """
    System that cleans up finished voices.
    
    Removes voices that have finished playing.
    """
    
    @staticmethod
    def step(scene: Scene, voice_pool: VoicePool):
        """
        Clean up finished voices.
        
        Args:
            scene: Scene (unused)
            voice_pool: Runtime voice pool
        """
        # Find finished voices
        finished = []
        
        for voice in voice_pool._voices:
            if not voice.active:
                finished.append(voice)
        
        # Release finished voices
        for voice in finished:
            voice_pool.release(voice)
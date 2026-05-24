"""
MixerSystem: Mixes voices to buses.
"""

import numpy as np
from gameplay.scenes.scene import Scene
from gameplay.systems.system import System

from audio.voice import VoicePool
from audio.bus import AudioBus


class MixerSystem(System):
    """
    System that mixes voices to buses.
    
    Mixes all active voices into their assigned buses.
    """
    
    @staticmethod
    def step(
        scene: Scene,
        voice_pool: VoicePool,
        bus_mapping: dict,
        buffer_size: int = 512
    ):
        """
        Mix voices to buses.
        
        Args:
            scene: Scene (unused)
            voice_pool: Runtime voice pool
            bus_mapping: Map bus_index to AudioBus
            buffer_size: Buffer size
        """
        # Group voices by bus
        bus_voices = {}
        
        for voice in voice_pool._voices:
            if not voice.playing:
                continue
            
            # Find which bus this voice is on
            # This is tracked in the bus's voice list
            for bus_index, bus in bus_mapping.items():
                if voice in bus.voices:
                    if bus not in bus_voices:
                        bus_voices[bus] = []
                    bus_voices[bus].append(voice)
                    break
        
        # Each bus will mix its own voices in update()
        # This system just ensures they're tracked
        pass


def mix_voice_to_buffer(
    voice,
    buffer: np.ndarray,
    buffer_size: int = 512
) -> np.ndarray:
    """
    Mix a single voice into a buffer.
    
    Args:
        voice: Voice to mix
        buffer: Output buffer
        buffer_size: Buffer size
    
    Returns:
        Mixed buffer
    """
    clip = voice.clip
    samples = clip.samples
    channels = clip.channels
    
    position = voice.position
    pitch = voice.pitch
    volume = voice.volume
    
    # Calculate end position
    end_pos = position + int(buffer_size * pitch)
    end_pos = min(end_pos, clip.frames)
    
    # Get source samples
    if pitch == 1.0:
        src = samples[position:end_pos]
    else:
        indices = np.linspace(position, end_pos - 1, buffer_size, dtype=np.float32)
        src = samples[indices.astype(np.int32)]
    
    # Mix based on channels
    if channels == 1:
        buffer[:len(src), 0] += src * volume
        buffer[:len(src), 1] += src * volume
    else:
        buffer[:len(src)] += src * volume
    
    return buffer
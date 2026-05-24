"""
SpatialAudioSystem: Applies spatial audio processing.
"""

import numpy as np
from gameplay.scenes.scene import Scene
from gameplay.systems.system import System

from audio.voice import VoicePool, SpatialProcessor


class SpatialAudioSystem(System):
    """
    System that applies spatial audio processing.
    
    Applies panning and distance attenuation.
    """
    
    @staticmethod
    def step(
        scene: Scene,
        voice_pool: VoicePool,
        spatial_processor: SpatialProcessor,
        position_component_type=None
    ):
        """
        Apply spatialization to voices.
        
        Args:
            scene: Scene with position data
            voice_pool: Runtime voice pool
            spatial_processor: Spatial processor
            position_component_type: Position component type
        """
        # Get position array
        position_array = None
        if position_component_type:
            position_array = scene.chunk.component_arrays.get(position_component_type)
        
        # Update listener position
        if position_array and position_array.size > 0:
            # Assume first entity is listener
            spatial_processor.set_listener_position(
                position_array[0]["x"],
                position_array[0]["y"]
            )
        
        # Apply spatialization to each voice
        # Note: This is done at mix time, not here
        # This system just updates the spatial processor state
        pass


def apply_spatial_to_buffer(
    buffer: np.ndarray,
    voice,
    source_x: float,
    source_y: float,
    spatial: SpatialProcessor
) -> np.ndarray:
    """
    Apply spatialization to a buffer.
    
    Args:
        buffer: Audio buffer
        voice: Voice being spatialized
        source_x: Source X position
        source_y: Source Y position
        spatial: Spatial processor
    
    Returns:
        Spatially processed buffer
    """
    if buffer.shape[1] < 2:
        return buffer
    
    left, right = spatial.process(voice, source_x, source_y)
    
    buffer[:, 0] *= left
    buffer[:, 1] *= right
    
    return buffer
"""
AudioSource: ECS component for audio playback.

Pure data component - no runtime state.
Stored in SharedChunkBuffer as numpy dtype.
"""

import numpy as np


class AudioSource:
    """
    ECS component for audio playback.
    
    This is pure data - no playback cursor, no decoder state.
    The clip_index references the audio asset database.
    
    Attributes:
        clip_index: Index into clip database (-1 = none)
        volume: Playback volume (0.0 to 1.0)
        pitch: Playback speed multiplier (1.0 = normal)
        looping: Whether to loop when finished
        spatial: Whether spatialization is enabled
        bus_index: Which bus to route to (0=sfx, 1=music, 2=voice)
    """
    
    # NumPy dtype for ECS storage
    schema = np.dtype([
        ("clip_index", np.int32),      # Index into clip database
        ("volume", np.float32),        # Volume 0.0-1.0
        ("pitch", np.float32),        # Pitch multiplier
        ("looping", np.uint8),       # Boolean
        ("spatial", np.uint8),        # Boolean
        ("bus_index", np.uint8),      # Bus routing (0=sfx, 1=music, 2=voice)
    ], align=True)
    
    # Default values
    DEFAULT_CLIP_INDEX = -1
    DEFAULT_VOLUME = 1.0
    DEFAULT_PITCH = 1.0
    DEFAULT_LOOPING = False
    DEFAULT_SPATIAL = False
    DEFAULT_BUS_INDEX = 0  # SFX bus by default
    
    @staticmethod
    def create(
        clip_index: int = -1,
        volume: float = 1.0,
        pitch: float = 1.0,
        looping: bool = False,
        spatial: bool = False,
        bus_index: int = 0
    ) -> np.ndarray:
        """
        Create an AudioSource as a structured array.
        
        Args:
            clip_index: Index into clip database
            volume: Volume 0.0-1.0
            pitch: Pitch multiplier
            looping: Whether to loop
            spatial: Whether to spatialize
            bus_index: Bus routing (0=sfx, 1=music, 2=voice)
        
        Returns:
            Structured numpy array
        """
        return np.array([
            (
                int(clip_index),
                float(volume),
                float(pitch),
                bool(looping),
                bool(spatial),
                int(bus_index)
            )
        ], dtype=AudioSource.schema)[0]
    
    @staticmethod
    def create_batch(count: int) -> np.ndarray:
        """Create a batch of uninitialized AudioSource."""
        return np.zeros(count, dtype=AudioSource.schema)


class AudioListener:
    """
    ECS component for audio listener (player position).
    
    Used for spatial audio calculations.
    
    Attributes:
        x: Listener X position
        y: Listener Y position
    """
    
    schema = np.dtype([
        ("x", np.float32),
        ("y", np.float32)
    ], align=True)
    
    @staticmethod
    def create(x: float = 0.0, y: float = 0.0) -> np.ndarray:
        """Create an AudioListener."""
        return np.array([(x, y)], dtype=AudioListener.schema)[0]


class AudioSourceState:
    """
    Runtime state for AudioSource.
    
    This is NOT stored in ECS - it's runtime only.
    Created by AudioSourceSyncSystem.
    
    Attributes:
        entity_id: Entity this voice belongs to
        voice: Runtime voice reference
        active: Whether voice is currently playing
    """
    
    def __init__(
        self,
        entity_id: str,
        clip_index: int,
        volume: float,
        pitch: float,
        looping: bool,
        spatial: bool,
        bus_index: int
    ) -> None:
        self.entity_id = entity_id
        self.clip_index = clip_index
        self.volume = volume
        self.pitch = pitch
        self.looping = looping
        self.spatial = spatial
        self.bus_index = bus_index
        self.voice = None
        self.active = False
    
    def __repr__(self) -> str:
        return (
            f"AudioSourceState(entity={self.entity_id}, "
            f"clip={self.clip_index}, active={self.active})"
        )


# Bus indices for routing
class BusIndex:
    """Bus routing constants."""
    SFX = 0
    MUSIC = 1
    VOICE = 2
    MASTER = 3
    
    @staticmethod
    def to_name(index: int) -> str:
        """Convert bus index to name."""
        names = {0: "sfx", 1: "music", 2: "voice", 3: "master"}
        return names.get(index, "sfx")
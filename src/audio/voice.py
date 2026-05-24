"""
Runtime voice management.

Runtime state separate from ECS - handles playback.
"""

import numpy as np
from typing import Optional, Dict, List

from audio.clip import AudioClip


class AudioVoice:
    """
    Runtime voice for audio playback.
    
    This is runtime state - NOT stored in ECS.
    Created by AudioSourceSyncSystem.
    
    Attributes:
        clip: Reference to AudioClip (immutable asset)
        position: Current sample position
        volume: Playback volume
        pitch: Pitch multiplier
        looping: Whether to loop
        playing: Whether actively playing
    """
    
    __slots__ = (
        "_clip",
        "_position",
        "_volume",
        "_pitch",
        "_looping",
        "_playing",
    )
    
    def __init__(
        self,
        clip: AudioClip,
        volume: float = 1.0,
        pitch: float = 1.0,
        looping: bool = False,
        position: int = 0
    ) -> None:
        self._clip = clip
        self._position = int(position)
        self._volume = float(max(0.0, min(1.0, volume)))
        self._pitch = float(pitch)
        self._looping = bool(looping)
        self._playing = True
    
    @property
    def clip(self) -> AudioClip:
        """Audio clip reference."""
        return self._clip
    
    @property
    def position(self) -> int:
        """Current sample position."""
        return self._position
    
    @position.setter
    def position(self, value: int) -> None:
        self._position = int(value)
    
    @property
    def volume(self) -> float:
        """Playback volume."""
        return self._volume
    
    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = float(max(0.0, min(1.0, value)))
    
    @property
    def pitch(self) -> float:
        """Pitch multiplier."""
        return self._pitch
    
    @pitch.setter
    def pitch(self, value: float) -> None:
        self._pitch = float(value)
    
    @property
    def looping(self) -> bool:
        """Whether to loop."""
        return self._looping
    
    @looping.setter
    def looping(self, value: bool) -> None:
        self._looping = bool(value)
    
    @property
    def playing(self) -> bool:
        """Whether playing."""
        return self._playing
    
    @playing.setter
    def playing(self, value: bool) -> None:
        self._playing = bool(value)
    
    @property
    def active(self) -> bool:
        """Whether voice has remaining audio."""
        if not self._playing:
            return False
        return self._position < self._clip.frames
    
    @property
    def frames(self) -> int:
        """Total frames in clip."""
        return self._clip.frames
    
    @property
    def sample_rate(self) -> int:
        """Sample rate."""
        return self._clip.sample_rate
    
    @property
    def channels(self) -> int:
        """Channel count."""
        return self._clip.channels
    
    def play(self) -> None:
        """Start playing."""
        self._playing = True
    
    def stop(self) -> None:
        """Stop and reset."""
        self._playing = False
        self._position = 0
    
    def pause(self) -> None:
        """Pause without resetting."""
        self._playing = False
    
    def resume(self) -> None:
        """Resume from pause."""
        if self._position < self._clip.frames:
            self._playing = True
    
    def seek(self, position: int) -> None:
        """Seek to position."""
        self._position = max(0, min(position, self._clip.frames))
    
    def __repr__(self) -> str:
        return (
            f"AudioVoice(clip={self._clip.frames} frames, "
            f"pos={self._position}, vol={self._volume:.2f}, "
            f"pitch={self._pitch:.2f}, playing={self._playing})"
        )


class VoicePool:
    """
    Pool of runtime voices.
    
    Manages voice allocation/recycling.
    """
    
    def __init__(self) -> None:
        self._voices: List[AudioVoice] = []
        self._free: List[AudioVoice] = []
    
    def acquire(
        self,
        clip: AudioClip,
        volume: float = 1.0,
        pitch: float = 1.0,
        looping: bool = False
    ) -> AudioVoice:
        """Acquire a voice from the pool."""
        if self._free:
            voice = self._free.pop()
            # Reinitialize
            voice._clip = clip
            voice._position = 0
            voice._volume = volume
            voice._pitch = pitch
            voice._looping = looping
            voice._playing = True
        else:
            voice = AudioVoice(
                clip=clip,
                volume=volume,
                pitch=pitch,
                looping=looping
            )
        
        self._voices.append(voice)
        return voice
    
    def release(self, voice: AudioVoice) -> None:
        """Release a voice back to the pool."""
        if voice in self._voices:
            self._voices.remove(voice)
            voice.stop()
            self._free.append(voice)
    
    def release_all(self) -> None:
        """Release all voices."""
        for voice in self._voices[:]:
            self.release(voice)
    
    @property
    def active_count(self) -> int:
        """Number of active voices."""
        return len(self._voices)
    
    @property
    def free_count(self) -> int:
        """Number of free voices."""
        return len(self._free)


class ClipDatabase:
    """
    Central clip storage.
    
    Audio clips are stored here and referenced by index.
    """
    
    def __init__(self) -> None:
        self._clips: Dict[int, AudioClip] = {}
        self._next_index: int = 0
        self._name_to_index: Dict[str, int] = {}
    
    def add(
        self,
        clip: AudioClip,
        name: Optional[str] = None
    ) -> int:
        """Add a clip and return its index."""
        index = self._next_index
        self._next_index += 1
        
        self._clips[index] = clip
        
        if name is not None:
            self._name_to_index[name] = index
        
        return index
    
    def get(self, index: int) -> Optional[AudioClip]:
        """Get clip by index."""
        return self._clips.get(index)
    
    def get_by_name(self, name: str) -> Optional[AudioClip]:
        """Get clip by name."""
        index = self._name_to_index.get(name)
        if index is None:
            return None
        return self._clips.get(index)
    
    def remove(self, index: int) -> None:
        """Remove a clip."""
        if index in self._clips:
            del self._clips[index]
    
    @property
    def count(self) -> int:
        """Number of clips."""
        return len(self._clips)
    
    def __getitem__(self, index: int) -> AudioClip:
        """Get clip by index."""
        return self._clips[index]
    
    def __len__(self) -> int:
        return len(self._clips)


class SpatialProcessor:
    """
    Spatial audio processor.
    
    Applies panning and distance attenuation.
    """
    
    def __init__(
        self,
        listener_x: float = 0.0,
        listener_y: float = 0.0
    ) -> None:
        self._listener_x = listener_x
        self._listener_y = listener_y
    
    @property
    def listener_position(self) -> tuple:
        """Listener position."""
        return (self._listener_x, self._listener_y)
    
    def set_listener_position(self, x: float, y: float) -> None:
        """Set listener position."""
        self._listener_x = x
        self._listener_y = y
    
    def process(
        self,
        voice: AudioVoice,
        source_x: float,
        source_y: float
    ) -> tuple:
        """
        Process spatialization.
        
        Returns:
            (left_gain, right_gain) for stereo panning
        """
        # Calculate distance
        dx = source_x - self._listener_x
        dy = source_y - self._listener_y
        distance = np.sqrt(dx * dx + dy * dy)
        
        # Inverse distance attenuation
        if distance < 1.0:
            distance = 1.0
        
        # Simple inverse square-ish falloff
        gain = 1.0 / (1.0 + distance * 0.1)
        
        # Stereo panning based on direction
        if distance > 0.001:
            pan = dx / distance
        else:
            pan = 0.0
        
        # Simple panning
        left_gain = gain * max(0.0, 1.0 - pan * 0.5)
        right_gain = gain * max(0.0, 1.0 + pan * 0.5)
        
        return (left_gain, right_gain)
    
    def apply_to_buffer(
        self,
        buffer: np.ndarray,
        voice: AudioVoice,
        source_x: float,
        source_y: float
    ) -> np.ndarray:
        """Apply spatialization to a buffer."""
        if buffer.shape[1] < 2:
            return buffer
        
        left, right = self.process(voice, source_x, source_y)
        
        # Apply panning
        buffer[:, 0] *= left
        buffer[:, 1] *= right
        
        return buffer
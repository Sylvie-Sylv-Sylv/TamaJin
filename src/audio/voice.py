"""
AudioVoice: runtime playback state.

AudioVoice references an AudioClip and stores playback state.
Multiple voices can reference the same clip simultaneously without duplicating memory.
"""

from typing import Optional
from audio.clip import AudioClip


class AudioVoice:
    """
    Runtime playback state for an AudioClip.
    
    AudioVoice does NOT own the audio data - it references an AudioClip.
    Multiple voices can play the same clip simultaneously.
    
    Attributes:
        clip: reference to the AudioClip being played
        position: current sample position (in frames, before pitch adjustment)
        volume: playback volume (0.0 to 1.0)
        pitch: playback speed multiplier (1.0 = normal speed)
        looping: whether to loop when reaching end
        playing: whether playback is active
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
        """
        Create an AudioVoice.
        
        Args:
            clip: AudioClip to play
            volume: playback volume (0.0 to 1.0), default 1.0
            pitch: playback speed multiplier, default 1.0
            looping: whether to loop, default False
            position: starting position in frames, default 0
        """
        self._clip = clip
        self._volume = float(max(0.0, min(1.0, volume)))
        self._pitch = float(pitch)
        self._looping = bool(looping)
        self._position = int(position)
        self._playing = True
    
    @property
    def clip(self) -> AudioClip:
        """Reference to the AudioClip."""
        return self._clip
    
    @property
    def position(self) -> int:
        """Current sample position (in frames, before pitch)."""
        return self._position
    
    @position.setter
    def position(self, value: int) -> None:
        self._position = int(value)
    
    @property
    def volume(self) -> float:
        """Playback volume (0.0 to 1.0)."""
        return self._volume
    
    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = float(max(0.0, min(1.0, value)))
    
    @property
    def pitch(self) -> float:
        """Playback speed multiplier (1.0 = normal)."""
        return self._pitch
    
    @pitch.setter
    def pitch(self, value: float) -> None:
        self._pitch = float(value)
    
    @property
    def looping(self) -> bool:
        """Whether to loop when reaching end."""
        return self._looping
    
    @looping.setter
    def looping(self, value: bool) -> None:
        self._looping = bool(value)
    
    @property
    def playing(self) -> bool:
        """Whether playback is active."""
        return self._playing
    
    @playing.setter
    def playing(self, value: bool) -> None:
        self._playing = bool(value)
    
    @property
    def active(self) -> bool:
        """True if playing or has remaining samples."""
        if not self._playing:
            return False
        return self._position < self._clip.frames
    
    @property
    def frames(self) -> int:
        """Total frames in the clip."""
        return self._clip.frames
    
    @property
    def sample_rate(self) -> int:
        """Sample rate of the clip."""
        return self._clip.sample_rate
    
    @property
    def channels(self) -> int:
        """Number of channels."""
        return self._clip.channels
    
    def play(self) -> None:
        """Start or resume playback."""
        self._playing = True
    
    def stop(self) -> None:
        """Stop playback and reset position."""
        self._playing = False
        self._position = 0
    
    def pause(self) -> None:
        """Pause playback without resetting position."""
        self._playing = False
    
    def resume(self) -> None:
        """Resume playback from current position."""
        if self._position < self._clip.frames:
            self._playing = True
    
    def seek(self, position: int) -> None:
        """Seek to a specific position."""
        self._position = max(0, min(position, self._clip.frames))
    
    def __repr__(self) -> str:
        return (
            f"AudioVoice(clip={self._clip!r}, "
            f"position={self._position}, "
            f"volume={self._volume:.2f}, "
            f"pitch={self._pitch:.2f}, "
            f"looping={self._looping}, "
            f"playing={self._playing})"
        )
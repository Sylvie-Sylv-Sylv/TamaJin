"""
AudioBackend: abstraction for audio output.

Allows swapping backends (null, callback, SDL, etc.) without
changing the core audio system.
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Callable, Optional, List


class AudioBackend(ABC):
    """
    Abstract audio backend.
    
    Subclass this to implement custom audio output.
    """
    
    @abstractmethod
    def submit(self, buffer: np.ndarray) -> None:
        """
        Submit audio buffer for playback.
        
        Args:
            buffer: numpy array of float32 samples, shape (frames, channels)
        """
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """True if backend is currently active."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close and clean up backend resources."""
        pass


class NullBackend(AudioBackend):
    """
    No-op audio backend.
    
    Discards all audio. Useful for testing or when audio is not needed.
    """
    
    def __init__(self) -> None:
        self._active = False
    
    def submit(self, buffer: np.ndarray) -> None:
        """Discard audio buffer."""
        pass
    
    def is_active(self) -> bool:
        return self._active
    
    def close(self) -> None:
        self._active = False


class CallbackBackend(AudioBackend):
    """
    Callback-based audio backend.
    
    Calls a user-provided callback with each audio buffer.
    Useful for integration with game engines or custom output.
    """
    
    def __init__(
        self,
        callback: Callable[[np.ndarray], None],
        sample_rate: int = 44100,
        channels: int = 2
    ) -> None:
        """
        Create a CallbackBackend.
        
        Args:
            callback: function called with each audio buffer
            sample_rate: output sample rate
            channels: number of output channels
        """
        self._callback = callback
        self._sample_rate = sample_rate
        self._channels = channels
        self._active = True
    
    @property
    def callback(self) -> Callable:
        """The audio callback."""
        return self._callback
    
    def submit(self, buffer: np.ndarray) -> None:
        """Call the callback with the buffer."""
        if self._active and self._callback:
            self._callback(buffer)
    
    def is_active(self) -> bool:
        return self._active
    
    def close(self) -> None:
        self._active = False
        self._callback = None


class BufferedBackend(AudioBackend):
    """
    Buffered audio backend.
    
    Stores submitted buffers for later retrieval.
    Useful for testing or capturing output.
    """
    
    def __init__(self, max_buffers: int = 100) -> None:
        """
        Create a BufferedBackend.
        
        Args:
            max_buffers: maximum number of buffers to store
        """
        self._buffers: List[np.ndarray] = []
        self._max_buffers = max_buffers
        self._active = True
    
    def submit(self, buffer: np.ndarray) -> None:
        """Store buffer."""
        if not self._active:
            return
        
        # Store copy to avoid mutation
        self._buffers.append(buffer.copy())
        
        # Limit buffer count
        if len(self._buffers) > self._max_buffers:
            self._buffers.pop(0)
    
    def is_active(self) -> bool:
        return self._active
    
    def close(self) -> None:
        self._active = False
        self._buffers.clear()
    
    @property
    def buffers(self) -> List[np.ndarray]:
        """Submitted buffers."""
        return list(self._buffers)
    
    def clear(self) -> None:
        """Clear stored buffers."""
        self._buffers.clear()
    
    def get_latest(self) -> Optional[np.ndarray]:
        """Get most recent buffer."""
        if self._buffers:
            return self._buffers[-1]
        return None
    
    def get_all(self) -> List[np.ndarray]:
        """Get all buffers."""
        return list(self._buffers)


# Future backend implementations (placeholders for extensibility)

class SDLBackend(AudioBackend):
    """SDL2 audio backend (placeholder)."""
    
    def __init__(self, sample_rate: int = 44100, channels: int = 2):
        raise NotImplementedError("SDL backend requires sdl2")
    
    def submit(self, buffer: np.ndarray) -> None:
        pass
    
    def is_active(self) -> bool:
        return False
    
    def close(self) -> None:
        pass


class PyGameBackend(AudioBackend):
    """PyGame audio backend (placeholder)."""
    
    def __init__(self):
        raise NotImplementedError("PyGame backend requires pygame")
    
    def submit(self, buffer: np.ndarray) -> None:
        pass
    
    def is_active(self) -> bool:
        return False
    
    def close(self) -> None:
        pass


class SoundDeviceBackend(AudioBackend):
    """sounddevice library backend (placeholder)."""
    
    def __init__(self, sample_rate: int = 44100, channels: int = 2):
        raise NotImplementedError("sounddevice backend requires sounddevice")
    
    def submit(self, buffer: np.ndarray) -> None:
        pass
    
    def is_active(self) -> bool:
        return False
    
    def close(self) -> None:
        pass
"""
AudioBackend: abstraction for audio output.

Allows swapping backends (null, callback, SDL, etc.) without
changing the core audio system.
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Callable, List, Optional


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
    """sounddevice library backend for low-latency audio playback."""
    
    def __init__(
        self,
        sample_rate: int = 44100,
        channels: int = 2,
        blocksize: int = 512,
        device: Optional[int] = None
    ) -> None:
        """Create a SoundDeviceBackend.
        
        Args:
            sample_rate: output sample rate
            channels: number of output channels
            blocksize: frames per block
            device: audio device index (None = default)
        """
        import sounddevice as sd
        self._sd = sd
        self._sample_rate = sample_rate
        self._channels = channels
        self._blocksize = blocksize
        self._device = device
        self._active = True
        self._stream: Optional[sd.OutputStream] = None
        self._queue: List[np.ndarray] = []
        self._lock = __import__('threading').Lock()
        
        # Start audio stream
        self._stream = sd.OutputStream(
            samplerate=sample_rate,
            channels=channels,
            blocksize=blocksize,
            device=device,
            callback=self._audio_callback,
            finished_callback=None
        )
        self._stream.start()
    
    def _audio_callback(
        self,
        outdata: np.ndarray,
        frames: int,
        time_info,
        status: "sd.CallbackFlags"
    ) -> None:
        """Audio stream callback."""
        if status:
            print(f"Audio callback status: {status}")
        
        with self._lock:
            if self._queue:
                data = self._queue.pop(0)
                # Ensure correct shape
                if len(data) >= frames:
                    outdata[:] = data[:frames]
                else:
                    outdata[:len(data)] = data
                    outdata[len(data):] = 0
            else:
                outdata.fill(0)
                # Debug: print when queue is empty
                # print(f"  Callback: queue empty, filling with zeros")
    
    def submit(self, buffer: np.ndarray) -> None:
        """Queue audio buffer for playback."""
        if not self._active:
            return
        
        with self._lock:
            self._queue.append(buffer.copy())
            
            # Limit queue size to prevent memory issues
            if len(self._queue) > 100:
                self._queue.pop(0)
    
    def is_active(self) -> bool:
        return self._active and (self._stream is not None and self._stream.active)
    
    def close(self) -> None:
        self._active = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self._queue.clear()


class WinsoundBackend(AudioBackend):
    """Winsound backend for Windows audio playback."""
    
    def __init__(self) -> None:
        import winsound
        self._winsound = winsound
        self._active = True
        self._buffer: Optional[np.ndarray] = None
    
    def submit(self, buffer: np.ndarray) -> None:
        """Accumulate buffer and play when full."""
        if not self._active:
            return
        
        # Accumulate buffers
        if self._buffer is None:
            self._buffer = buffer.copy()
        else:
            self._buffer = np.concatenate([self._buffer, buffer.copy()])
        
        # Play when we have enough samples (~0.5 seconds = 22050 frames)
        if len(self._buffer) >= 22050:
            self._play_buffer()
            self._buffer = None
    
    def _play_buffer(self) -> None:
        """Play accumulated buffer as WAV."""
        import tempfile
        import wave
        import os
        
        if self._buffer is None or len(self._buffer) < 512:
            return
        
        # Convert to int16
        int16 = (np.clip(self._buffer, -1.0, 1.0) * 32767).astype(np.int16)
        
        # Write to temp WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
            temp_path = f.name
        
        try:
            with wave.open(temp_path, 'w') as wav:
                wav.setnchannels(2)
                wav.setsampwidth(2)
                wav.setframerate(44100)
                wav.writeframes(int16.tobytes())
            
            # Play async
            self._winsound.PlaySound(temp_path, self._winsound.SND_FILENAME | self._winsound.SND_ASYNC)
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
    
    def is_active(self) -> bool:
        return self._active
    
    def close(self) -> None:
        self._active = False
        self._buffer = None
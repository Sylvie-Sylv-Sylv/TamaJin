"""
AudioClip: immutable audio asset data.

AudioClip owns decoded PCM sample memory. It is immutable after creation
and can be safely shared across multiple voices without duplication.
"""

import numpy as np
from typing import Optional


class AudioClip:
    """
    Immutable decoded audio data.
    
    Attributes:
        samples: numpy array of float32 samples, shape (frames, channels)
                 or (frames,) for mono. Values in [-1.0, 1.0].
        sample_rate: samples per second (e.g., 44100)
        channels: number of audio channels (1=mono, 2=stereo)
    """
    
    __slots__ = ("_samples", "_sample_rate", "_channels")
    
    def __init__(
        self,
        samples: np.ndarray,
        sample_rate: int,
        channels: int
    ) -> None:
        """
        Create an AudioClip.
        
        Args:
            samples: numpy array of float32 samples, shape (frames,) or (frames, channels)
            sample_rate: samples per second
            channels: number of channels (1 or 2)
        """
        # Ensure float32 and contiguous memory
        self._samples = np.ascontiguousarray(samples, dtype=np.float32)
        self._sample_rate = int(sample_rate)
        self._channels = int(channels)
        
        # Validate
        if self._sample_rate <= 0:
            raise ValueError(f"Invalid sample_rate: {sample_rate}")
        if self._channels not in (1, 2):
            raise ValueError(f"Invalid channels: {channels}. Must be 1 or 2.")
        if self._samples.size == 0:
            raise ValueError("Empty samples array")
        if self._samples.dtype != np.float32:
            self._samples = self._samples.astype(np.float32)
        
        # Normalize shape
        if self._channels == 1:
            # Mono: ensure 1D
            self._samples = self._samples.reshape(-1)
        else:
            # Stereo: ensure 2D with channels last
            if self._samples.ndim == 1:
                raise ValueError(
                    f"Stereo clip requires 2D samples, got 1D"
                )
            if self._samples.shape[1] != 2:
                raise ValueError(
                    f"Stereo clip must have 2 channels, got {self._samples.shape[1]}"
                )
    
    @property
    def samples(self) -> np.ndarray:
        """Decoded PCM samples (read-only view)."""
        return self._samples
    
    @property
    def sample_rate(self) -> int:
        """Samples per second."""
        return self._sample_rate
    
    @property
    def channels(self) -> int:
        """Number of channels (1=mono, 2=stereo)."""
        return self._channels
    
    @property
    def duration(self) -> float:
        """Duration in seconds."""
        frames = self._samples.shape[0]
        return frames / self._sample_rate
    
    @property
    def frames(self) -> int:
        """Number of frames (samples per channel)."""
        return self._samples.shape[0]
    
    @property
    def is_stereo(self) -> bool:
        """True if stereo audio."""
        return self._channels == 2
    
    @property
    def is_mono(self) -> bool:
        """True if mono audio."""
        return self._channels == 1
    
    def __repr__(self) -> str:
        return (
            f"AudioClip(frames={self.frames}, "
            f"channels={self.channels}, "
            f"sample_rate={self.sample_rate}, "
            f"duration={self.duration:.3f}s)"
        )
    
    def __len__(self) -> int:
        """Number of frames."""
        return self.frames


def create_silent_clip(
    duration: float,
    sample_rate: int = 44100,
    channels: int = 2
) -> AudioClip:
    """
    Create a silent audio clip.
    
    Args:
        duration: duration in seconds
        sample_rate: samples per second
        channels: number of channels
    
    Returns:
        AudioClip with silence
    """
    frames = int(duration * sample_rate)
    if channels == 1:
        samples = np.zeros(frames, dtype=np.float32)
    else:
        samples = np.zeros((frames, channels), dtype=np.float32)
    return AudioClip(samples, sample_rate, channels)


def create_tone_clip(
    frequency: float,
    duration: float,
    sample_rate: int = 44100,
    channels: int = 2
) -> AudioClip:
    """
    Create a sine wave tone clip.
    
    Args:
        frequency: tone frequency in Hz
        duration: duration in seconds
        sample_rate: samples per second
        channels: number of channels
    
    Returns:
        AudioClip with sine wave
    """
    frames = int(duration * sample_rate)
    t = np.linspace(0, duration, frames, dtype=np.float32)
    samples = np.sin(2.0 * np.pi * frequency * t)
    
    if channels == 2:
        # Duplicate for stereo
        samples = np.column_stack([samples, samples])
    
    return AudioClip(samples, sample_rate, channels)
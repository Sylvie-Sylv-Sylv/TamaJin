"""
MasterBus: final output bus that connects to audio backend.
"""

import numpy as np
from typing import Optional

from audio.bus import AudioBus
from audio.backend import AudioBackend, NullBackend


class MasterBus(AudioBus):
    """
    Master output bus.
    
    The final bus that outputs to the audio backend/speakers.
    All other buses should route to the master bus.
    """
    
    def __init__(
        self,
        name: str = "master",
        volume: float = 1.0,
        muted: bool = False,
        backend: Optional[AudioBackend] = None
    ) -> None:
        """
        Create a MasterBus.
        
        Args:
            name: bus name
            volume: master volume
            muted: whether muted
            backend: audio output backend
        """
        super().__init__(name=name, volume=volume, muted=muted)
        
        self._backend = backend if backend is not None else NullBackend()
    
    @property
    def backend(self) -> AudioBackend:
        """Audio output backend."""
        return self._backend
    
    def submit(self) -> None:
        """Update and submit audio to backend."""
        buffer = self.update()
        self._backend.submit(buffer)
    
    def get_output(self) -> np.ndarray:
        """Get output buffer without submitting."""
        return self.update()
    
    def __repr__(self) -> str:
        return f"MasterBus(name={self.name}, volume={self.volume:.2f})"
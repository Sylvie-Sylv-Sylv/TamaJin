"""
AudioDevice: Backward-compatible audio device.

AudioDevice: Submits audio to the backend.
"""

import numpy as np
from typing import List, Optional
from gameplay.scenes.scene import Scene
from gameplay.systems.system import System

from audio.clip import AudioClip
from audio.voice import AudioVoice
from audio.bus import AudioBus
from audio.backend import AudioBackend, NullBackend


class AudioDevice:
    """
    Backward-compatible audio device.
    
    Manages voices and submits to backend.
    """
    
    def __init__(
        self,
        sample_rate: int = 44100,
        buffer_size: int = 512,
        backend: Optional[AudioBackend] = None
    ) -> None:
        self._sample_rate = sample_rate
        self._buffer_size = buffer_size
        self._backend = backend if backend else NullBackend()
        self._voices: List[AudioVoice] = []
        self._master_volume = 1.0
        self._bus = AudioBus(name="master")
        self._bus.set_buffer_config(sample_rate, buffer_size, 2)
    
    @property
    def sample_rate(self) -> int:
        return self._sample_rate
    
    @property
    def buffer_size(self) -> int:
        return self._buffer_size
    
    @property
    def backend(self) -> AudioBackend:
        return self._backend
    
    @property
    def voices(self) -> List[AudioVoice]:
        return list(self._voices)
    
    @property
    def voice_count(self) -> int:
        return len(self._voices)
    
    @property
    def master_volume(self) -> float:
        return self._master_volume
    
    @master_volume.setter
    def master_volume(self, value: float) -> None:
        self._master_volume = float(max(0.0, min(1.0, value)))
    
    def play(
        self,
        clip: AudioClip,
        volume: float = 1.0,
        pitch: float = 1.0,
        looping: bool = False,
        position: int = 0
    ) -> AudioVoice:
        voice = AudioVoice(
            clip=clip,
            volume=volume,
            pitch=pitch,
            looping=looping,
            position=position
        )
        self._voices.append(voice)
        self._bus.add_voice(voice)
        return voice
    
    def stop(self, voice: AudioVoice) -> None:
        if voice in self._voices:
            voice.stop()
            self._voices.remove(voice)
    
    def stop_all(self) -> None:
        for voice in self._voices:
            voice.stop()
        self._voices.clear()
    
    def update(self, buffer: Optional[np.ndarray] = None) -> np.ndarray:
        if buffer is None:
            buffer = np.zeros((self._buffer_size, 2), dtype=np.float32)
        else:
            buffer.fill(0.0)
        
        # Update bus
        buffer = self._bus.update(buffer)
        
        # Apply master volume
        if self._master_volume != 1.0:
            buffer *= self._master_volume
        
        # Remove finished voices
        finished = [v for v in self._voices if not v.active]
        for v in finished:
            self._voices.remove(v)
        
        return buffer
    
    def submit(self) -> None:
        buffer = self.update()
        self._backend.submit(buffer)
    
    def get_output(self) -> np.ndarray:
        return self.update()
    
    def __repr__(self) -> str:
        return f"AudioDevice(voices={self.voice_count})"


from audio.bus import AudioBus
from audio.backend import AudioBackend


class AudioDeviceSystem(System):
    """
    System that submits audio to the backend.
    
    Updates the master bus and submits to audio backend.
    """
    
    @staticmethod
    def step(
        scene: Scene,
        master_bus: AudioBus,
        backend: AudioBackend
    ):
        """
        Submit audio to backend.
        
        Args:
            scene: Scene (unused)
            master_bus: Master bus
            backend: Audio backend
        """
        # Get output from master bus
        buffer = master_bus.update()
        
        # Submit to backend
        backend.submit(buffer)


class AudioSubmitSystem(System):
    """
    System that submits audio from a graph.
    
    Alternative to AudioDeviceSystem for graph-based routing.
    """
    
    @staticmethod
    def step(scene: Scene, graph, backend):
        """
        Submit audio from graph.
        
        Args:
            scene: Scene (unused)
            graph: AudioGraph
            backend: Audio backend
        """
        buffer = graph.get_output()
        backend.submit(buffer)
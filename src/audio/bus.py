"""
AudioBus: mixer bus for audio routing.

A bus is a mixer that receives audio from inputs (voices or other buses)
and routes to outputs. Supports arbitrary graph routing.
"""

import numpy as np
from typing import List, Optional, Callable, Union, Set

from audio.clip import AudioClip
from audio.voice import AudioVoice


class AudioBus:
    """
    Mixer bus for audio routing.
    
    Buses can receive audio from:
    - Voices (AudioVoice instances)
    - Child buses (AudioBus instances)
    
    Buses route to:
    - Output buses (connected via graph)
    
    Attributes:
        name: bus identifier
        volume: bus volume (0.0 to 1.0)
        muted: whether bus is muted
        dsp_chain: list of DSP effects
    """
    
    def __init__(
        self,
        name: str = "bus",
        volume: float = 1.0,
        muted: bool = False
    ) -> None:
        """
        Create an AudioBus.
        
        Args:
            name: bus identifier
            volume: bus volume (0.0 to 1.0)
            muted: whether bus is muted
        """
        self._name = name
        self._volume = float(max(0.0, min(1.0, volume)))
        self._muted = bool(muted)
        
        # Inputs: voices and child buses
        self._voices: List[AudioVoice] = []
        self._input_buses: List[AudioBus] = []
        
        # Outputs: connected buses (set by graph)
        self._output_buses: List[AudioBus] = []
        
        # DSP chain
        self._dsp_chain: List[Callable[[np.ndarray], np.ndarray]] = []
        
        # Buffer config
        self._sample_rate = 44100
        self._buffer_size = 512
        self._channels = 2
    
    @property
    def name(self) -> str:
        """Bus name."""
        return self._name
    
    @property
    def volume(self) -> float:
        """Bus volume."""
        return self._volume
    
    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = float(max(0.0, min(1.0, value)))
    
    @property
    def muted(self) -> bool:
        """Whether bus is muted."""
        return self._muted
    
    @muted.setter
    def muted(self, value: bool) -> None:
        self._muted = bool(value)
    
    @property
    def voices(self) -> List[AudioVoice]:
        """Active voices on this bus."""
        return list(self._voices)
    
    @property
    def voice_count(self) -> int:
        """Number of active voices."""
        return len(self._voices)
    
    @property
    def input_buses(self) -> List["AudioBus"]:
        """Input buses connected to this bus."""
        return list(self._input_buses)
    
    @property
    def output_buses(self) -> List["AudioBus"]:
        """Output buses this bus connects to."""
        return list(self._output_buses)
    
    @property
    def sample_rate(self) -> int:
        """Sample rate."""
        return self._sample_rate
    
    @property
    def buffer_size(self) -> int:
        """Buffer size."""
        return self._buffer_size
    
    @property
    def channels(self) -> int:
        """Channel count."""
        return self._channels
    
    def set_buffer_config(
        self,
        sample_rate: int,
        buffer_size: int,
        channels: int = 2
    ) -> None:
        """Set buffer configuration."""
        self._sample_rate = int(sample_rate)
        self._buffer_size = int(buffer_size)
        self._channels = int(channels)
    
    def add_voice(self, voice: AudioVoice) -> None:
        """Add a voice to this bus."""
        if voice not in self._voices:
            self._voices.append(voice)
    
    def remove_voice(self, voice: AudioVoice) -> None:
        """Remove a voice from this bus."""
        if voice in self._voices:
            self._voices.remove(voice)
    
    def connect_input(self, bus: "AudioBus") -> None:
        """Connect an input bus."""
        if bus not in self._input_buses:
            self._input_buses.append(bus)
            if self not in bus._output_buses:
                bus._output_buses.append(self)
    
    def disconnect_input(self, bus: "AudioBus") -> None:
        """Disconnect an input bus."""
        if bus in self._input_buses:
            self._input_buses.remove(bus)
            if self in bus._output_buses:
                bus._output_buses.remove(self)
    
    def play(
        self,
        clip: AudioClip,
        volume: float = 1.0,
        pitch: float = 1.0,
        looping: bool = False,
        position: int = 0
    ) -> AudioVoice:
        """
        Play a clip on this bus.
        
        Args:
            clip: AudioClip to play
            volume: voice volume
            pitch: pitch multiplier
            looping: whether to loop
            position: starting position
        
        Returns:
            AudioVoice for the playback
        """
        voice = AudioVoice(
            clip=clip,
            volume=volume,
            pitch=pitch,
            looping=looping,
            position=position
        )
        self.add_voice(voice)
        return voice
    
    def stop(self, voice: AudioVoice) -> None:
        """Stop a specific voice."""
        if voice in self._voices:
            voice.stop()
            self._voices.remove(voice)
    
    def stop_all(self) -> None:
        """Stop all voices on this bus."""
        for voice in self._voices:
            voice.stop()
        self._voices.clear()
    
    def pause_all(self) -> None:
        """Pause all voices."""
        for voice in self._voices:
            voice.pause()
    
    def resume_all(self) -> None:
        """Resume all voices."""
        for voice in self._voices:
            voice.resume()
    
    def add_dsp(self, dsp: Callable[[np.ndarray], np.ndarray]) -> None:
        """Add a DSP effect to the chain."""
        if dsp not in self._dsp_chain:
            self._dsp_chain.append(dsp)
    
    def remove_dsp(self, dsp: Callable[[np.ndarray], np.ndarray]) -> None:
        """Remove a DSP effect."""
        if dsp in self._dsp_chain:
            self._dsp_chain.remove(dsp)
    
    def update(self, buffer: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Update bus and produce mixed output.
        
        Mixes all voices and input buses to output buffer.
        
        Args:
            buffer: optional output buffer
        
        Returns:
            Mixed audio buffer
        """
        frames = self._buffer_size
        
        # Create output buffer
        if buffer is None:
            buffer = np.zeros((frames, self._channels), dtype=np.float32)
        else:
            buffer.fill(0.0)
        
        # If muted, skip mixing and return silence
        if self._muted:
            return buffer
        
        # Mix voices
        for voice in self._voices[:]:  # Copy list for safe removal
            if not voice.playing:
                self._voices.remove(voice)
                continue
            
            self._mix_voice(voice, buffer)
            
            # Check if finished
            if not voice.active:
                self._voices.remove(voice)
        
        # Mix input buses
        for bus in self._input_buses:
            input_buffer = bus.update()
            buffer += input_buffer
        
        # Apply volume
        if self._volume != 1.0:
            buffer *= self._volume
        
        # Apply DSP chain
        for dsp in self._dsp_chain:
            buffer = dsp(buffer)
        
        # Clip to valid range
        buffer = np.clip(buffer, -1.0, 1.0)
        
        return buffer
    
    def _mix_voice(self, voice: AudioVoice, buffer: np.ndarray) -> None:
        """Mix a voice into the buffer."""
        clip = voice.clip
        samples = clip.samples
        channels = clip.channels
        frames = buffer.shape[0]
        
        position = voice.position
        pitch = voice.pitch
        volume = voice.volume
        
        # Calculate end position
        end_pos = position + int(frames * pitch)
        end_pos = min(end_pos, clip.frames)
        
        # Get source samples
        if pitch == 1.0:
            src = samples[position:end_pos]
        else:
            indices = np.linspace(position, end_pos - 1, frames, dtype=np.float32)
            src = samples[indices.astype(np.int32)]
        
        # Mix based on channels
        if channels == 1:
            # Mono to stereo
            buffer[:len(src), 0] += src * volume
            buffer[:len(src), 1] += src * volume
        else:
            # Stereo
            buffer[:len(src)] += src * volume
        
        # Advance position
        if end_pos >= clip.frames:
            if voice.looping:
                voice._position = end_pos % clip.frames
            else:
                voice._position = clip.frames
                voice._playing = False
        else:
            voice._position = end_pos
    
    def get_connected_buses(self, visited: Optional[Set["AudioBus"]] = None) -> Set["AudioBus"]:
        """Get all buses in the routing graph."""
        if visited is None:
            visited = set()
        
        if self in visited:
            return visited
        
        visited.add(self)
        
        for bus in self._input_buses:
            bus.get_connected_buses(visited)
        
        for bus in self._output_buses:
            bus.get_connected_buses(visited)
        
        return visited
    
    def __repr__(self) -> str:
        return f"AudioBus(name={self.name}, volume={self.volume:.2f}, voices={self.voice_count})"
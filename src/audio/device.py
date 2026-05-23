"""
AudioDevice: audio mixer and playback engine.

AudioDevice manages active voices, mixes them to output buffer,
removes finished voices, and submits audio to the backend.
"""

import numpy as np
from typing import List, Optional, Callable

from audio.clip import AudioClip
from audio.voice import AudioVoice
from audio.backend import AudioBackend, NullBackend


class AudioDevice:
    """
    Audio mixer and playback engine.
    
    Manages active voices, mixes to output, and submits to backend.
    Designed for extensibility: DSP chains, mixer buses, spatial audio.
    
    Attributes:
        sample_rate: output sample rate
        buffer_size: frames per update
        backend: audio output backend
    """
    
    def __init__(
        self,
        sample_rate: int = 44100,
        buffer_size: int = 512,
        backend: Optional[AudioBackend] = None
    ) -> None:
        """
        Create an AudioDevice.
        
        Args:
            sample_rate: output sample rate
            buffer_size: frames per update
            backend: audio output backend (default: NullBackend)
        """
        self._sample_rate = int(sample_rate)
        self._buffer_size = int(buffer_size)
        self._backend = backend if backend is not None else NullBackend()
        self._voices: List[AudioVoice] = []
        self._master_volume = 1.0
        
        # Future extensibility hooks
        self._dsp_chain: List[Callable] = []
        self._mixer_buses: dict = {}
    
    @property
    def sample_rate(self) -> int:
        """Output sample rate."""
        return self._sample_rate
    
    @property
    def buffer_size(self) -> int:
        """Frames per update."""
        return self._buffer_size
    
    @property
    def backend(self) -> AudioBackend:
        """Audio output backend."""
        return self._backend
    
    @property
    def voices(self) -> List[AudioVoice]:
        """Active voices (read-only)."""
        return list(self._voices)
    
    @property
    def voice_count(self) -> int:
        """Number of active voices."""
        return len(self._voices)
    
    @property
    def master_volume(self) -> float:
        """Master output volume."""
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
        """
        Play an AudioClip, creating a new voice.
        
        Args:
            clip: AudioClip to play
            volume: voice volume (0.0 to 1.0)
            pitch: pitch multiplier
            looping: whether to loop
            position: starting position in frames
        
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
        self._voices.append(voice)
        return voice
    
    def stop(self, voice: AudioVoice) -> None:
        """
        Stop a specific voice.
        
        Args:
            voice: AudioVoice to stop
        """
        if voice in self._voices:
            voice.stop()
            self._voices.remove(voice)
    
    def stop_all(self) -> None:
        """Stop all active voices."""
        for voice in self._voices:
            voice.stop()
        self._voices.clear()
    
    def pause(self, voice: AudioVoice) -> None:
        """
        Pause a specific voice.
        
        Args:
            voice: AudioVoice to pause
        """
        if voice in self._voices:
            voice.pause()
    
    def pause_all(self) -> None:
        """Pause all voices."""
        for voice in self._voices:
            voice.pause()
    
    def resume(self, voice: AudioVoice) -> None:
        """
        Resume a specific voice.
        
        Args:
            voice: AudioVoice to resume
        """
        if voice in self._voices:
            voice.resume()
    
    def resume_all(self) -> None:
        """Resume all paused voices."""
        for voice in self._voices:
            voice.resume()
    
    def update(self, buffer: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Update audio device and produce output.
        
        Mixes all active voices to output buffer, advances positions,
        handles looping, and removes finished voices.
        
        Args:
            buffer: optional output buffer to write to
        
        Returns:
            Output audio buffer, shape (frames, channels)
        """
        frames = self._buffer_size
        
        # Create output buffer (stereo by default)
        if buffer is None:
            buffer = np.zeros((frames, 2), dtype=np.float32)
        else:
            buffer.fill(0.0)
        
        # Mix each active voice
        voices_to_remove = []
        
        for voice in self._voices:
            if not voice.playing:
                continue
            
            # Mix this voice
            self._mix_voice(voice, buffer)
            
            # Check if voice finished
            if not voice.active:
                voices_to_remove.append(voice)
        
        # Remove finished voices
        for voice in voices_to_remove:
            self._voices.remove(voice)
        
        # Apply master volume
        if self._master_volume != 1.0:
            buffer *= self._master_volume
        
        # Apply DSP chain (future extensibility)
        buffer = self._apply_dsp(buffer)
        
        # Clip to valid range
        buffer = np.clip(buffer, -1.0, 1.0)
        
        return buffer
    
    def _mix_voice(self, voice: AudioVoice, buffer: np.ndarray) -> None:
        """Mix a single voice into the output buffer."""
        clip = voice.clip
        sample_rate = clip.sample_rate
        channels = clip.channels
        frames = buffer.shape[0]
        
        # Calculate pitch-adjusted position increment
        position = voice.position
        pitch = voice.pitch
        
        # Get source samples
        samples = clip.samples
        
        # Mix based on channel count
        if channels == 1:
            # Mono source
            self._mix_mono(voice, samples, buffer)
        else:
            # Stereo source
            self._mix_stereo(voice, samples, buffer)
        
        # Advance position with pitch
        new_position = position + int(frames * pitch)
        
        if new_position >= clip.frames:
            if voice.looping:
                # Loop: wrap position
                voice._position = new_position % clip.frames
            else:
                # End: clamp and mark inactive
                voice._position = clip.frames
                voice._playing = False
        else:
            voice._position = new_position
    
    def _mix_mono(
        self,
        voice: AudioVoice,
        samples: np.ndarray,
        buffer: np.ndarray
    ) -> None:
        """Mix mono source to stereo buffer."""
        frames = buffer.shape[0]
        position = voice.position
        pitch = voice.pitch
        volume = voice.volume
        
        # Calculate end position
        end_pos = position + int(frames * pitch)
        end_pos = min(end_pos, len(samples))
        
        # Simple linear interpolation for pitch
        if pitch == 1.0:
            # No pitch change - direct copy
            src = samples[position:end_pos]
        else:
            # Resample
            indices = np.linspace(position, end_pos - 1, frames, dtype=np.float32)
            src = samples[indices.astype(np.int32)]
        
        # Mix to both channels
        buffer[:len(src), 0] += src * volume
        buffer[:len(src), 1] += src * volume
    
    def _mix_stereo(
        self,
        voice: AudioVoice,
        samples: np.ndarray,
        buffer: np.ndarray
    ) -> None:
        """Mix stereo source to stereo buffer."""
        frames = buffer.shape[0]
        position = voice.position
        pitch = voice.pitch
        volume = voice.volume
        
        # Calculate end position
        end_pos = position + int(frames * pitch)
        end_pos = min(end_pos, samples.shape[0])
        
        # Resample if needed
        if pitch == 1.0:
            src = samples[position:end_pos]
        else:
            indices = np.linspace(position, end_pos - 1, frames, dtype=np.float32)
            src = samples[indices.astype(np.int32)]
        
        # Mix with volume
        src = src * volume
        buffer[:len(src)] += src
    
    def _apply_dsp(self, buffer: np.ndarray) -> np.ndarray:
        """Apply DSP chain (placeholder for future)."""
        for dsp in self._dsp_chain:
            buffer = dsp(buffer)
        return buffer
    
    def submit(self) -> None:
        """Submit mixed audio to backend."""
        buffer = self.update()
        self._backend.submit(buffer)
    
    def get_output(self) -> np.ndarray:
        """Get output buffer without submitting."""
        return self.update()
    
    def __repr__(self) -> str:
        return (
            f"AudioDevice(sample_rate={self.sample_rate}, "
            f"buffer_size={self.buffer_size}, "
            f"voices={self.voice_count})"
        )
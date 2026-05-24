"""
TamaJin Audio System

Modular game audio playback system with bus-based routing:
- AudioClip: immutable decoded audio data
- AudioVoice: runtime playback state
- AudioBus: mixer bus for routing
- AudioGraph: routing container
- MasterBus: final output
"""

from audio.clip import AudioClip, create_silent_clip, create_tone_clip
from audio.voice import AudioVoice
from audio.bus import AudioBus
from audio.master import MasterBus
from audio.graph import AudioGraph, create_game_graph
from audio.audio_device import AudioDevice
from audio.loader import load_clip, load_wav, load_ogg
from audio.backend import AudioBackend, NullBackend, CallbackBackend, BufferedBackend
from audio.debug import AudioDebugger, TextDebugger, create_debugger

__all__ = [
    # Core
    "AudioClip",
    "AudioVoice",
    "AudioBus",
    "MasterBus",
    "AudioGraph",
    "AudioDevice",
    # Loaders
    "load_clip",
    "load_wav",
    "load_ogg",
    # Backends
    "AudioBackend",
    "NullBackend",
    "CallbackBackend",
    "BufferedBackend",
    # Debug
    "AudioDebugger",
    "TextDebugger",
    "create_debugger",
    # Utilities
    "create_silent_clip",
    "create_tone_clip",
    "create_game_graph",
]
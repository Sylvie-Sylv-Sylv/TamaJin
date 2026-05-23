"""
Audio loader: WAV/OGG file loading.

Loads audio files and decodes to AudioClip.
"""

import os
import wave
import numpy as np
from typing import Optional

from audio.clip import AudioClip


def load_wav(path: str) -> AudioClip:
    """
    Load a WAV file.
    
    Args:
        path: path to WAV file
    
    Returns:
        AudioClip with decoded audio
    
    Raises:
        FileNotFoundError: if file doesn't exist
        ValueError: if file is not a valid WAV
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"WAV file not found: {path}")
    
    with wave.open(path, "rb") as wf:
        # Get WAV parameters
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        frames = wf.getnframes()
        
        # Read raw data
        raw = wf.readframes(frames)
    
    # Convert to numpy
    if sample_width == 1:
        # 8-bit unsigned
        samples = np.frombuffer(raw, dtype=np.uint8)
        samples = (samples.astype(np.float32) - 128.0) / 128.0
    elif sample_width == 2:
        # 16-bit signed
        samples = np.frombuffer(raw, dtype=np.int16)
        samples = samples.astype(np.float32) / 32768.0
    elif sample_width == 4:
        # 32-bit signed
        samples = np.frombuffer(raw, dtype=np.int32)
        samples = samples.astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")
    
    # Reshape for channels
    if channels == 1:
        samples = samples.reshape(-1)
    else:
        samples = samples.reshape(-1, channels)
    
    return AudioClip(samples, sample_rate, channels)


def load_ogg(path: str) -> AudioClip:
    """
    Load an OGG Vorbis file.
    
    Requires vorbis or ogg library.
    
    Args:
        path: path to OGG file
    
    Returns:
        AudioClip with decoded audio
    
    Raises:
        FileNotFoundError: if file doesn't exist
        ImportError: if ogg/vorbis library not available
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"OGG file not found: {path}")
    
    # Try vorbisfile (PyOgg)
    try:
        import vorbisfile
        return _load_ogg_vorbisfile(path)
    except ImportError:
        pass
    
    # Try soundfile
    try:
        import soundfile as sf
        return _load_ogg_soundfile(path)
    except ImportError:
        pass
    
    raise ImportError(
        "OGG loading requires 'vorbisfile' or 'soundfile' library. "
        "Install with: pip install vorbisfile soundfile"
    )


def _load_ogg_vorbisfile(path: str) -> AudioClip:
    """Load OGG using vorbisfile."""
    import vorbisfile
    
    vf = vorbisfile.VorbisFile(path)
    
    # Read all samples
    samples, sample_rate, channels, _ = vf.read(-1)
    
    vf.close()
    
    # Convert to float32
    if channels == 1:
        samples = samples.reshape(-1)
    else:
        samples = np.array(samples, dtype=np.float32)
    
    return AudioClip(samples, sample_rate, channels)


def _load_ogg_soundfile(path: str) -> AudioClip:
    """Load OGG using soundfile."""
    import soundfile as sf
    
    data, sample_rate = sf.read(path, dtype=np.float32)
    channels = data.shape[1] if data.ndim > 1 else 1
    
    return AudioClip(data, sample_rate, channels)


def load_clip(path: str) -> AudioClip:
    """
    Load an audio file, auto-detecting format.
    
    Args:
        path: path to audio file
    
    Returns:
        AudioClip with decoded audio
    
    Raises:
        FileNotFoundError: if file doesn't exist
        ValueError: if format not supported
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Audio file not found: {path}")
    
    # Get extension
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    
    if ext in (".wav", ".wave"):
        return load_wav(path)
    elif ext in (".ogg", ".oga", ".vorbis"):
        return load_ogg(path)
    else:
        raise ValueError(f"Unsupported audio format: {ext}")


# Utility functions

def save_wav(clip: AudioClip, path: str) -> None:
    """
    Save an AudioClip as WAV file.
    
    Args:
        clip: AudioClip to save
        path: output path
    """
    samples = clip.samples
    sample_rate = clip.sample_rate
    channels = clip.channels
    
    # Convert to int16
    if samples.ndim == 1:
        # Mono
        data = (samples * 32767.0).astype(np.int16)
    else:
        # Interleave stereo
        data = (samples * 32767.0).astype(np.int16)
    
    with wave.open(path, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(data.tobytes())


def info(path: str) -> dict:
    """
    Get audio file information without loading.
    
    Args:
        path: path to audio file
    
    Returns:
        dict with keys: duration, sample_rate, channels, frames, format
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Audio file not found: {path}")
    
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    
    if ext in (".wav", ".wave"):
        return _info_wav(path)
    elif ext in (".ogg", ".oga", ".vorbis"):
        return _info_ogg(path)
    else:
        raise ValueError(f"Unsupported audio format: {ext}")


def _info_wav(path: str) -> dict:
    """Get WAV file info."""
    with wave.open(path, "rb") as wf:
        channels = wf.getnchannels()
        sample_rate = wf.getframerate()
        frames = wf.getnframes()
        duration = frames / sample_rate
    
    return {
        "format": "wav",
        "sample_rate": sample_rate,
        "channels": channels,
        "frames": frames,
        "duration": duration,
    }


def _info_ogg(path: str) -> dict:
    """Get OGG file info."""
    try:
        import soundfile as sf
        info = sf.info(path)
        return {
            "format": "ogg",
            "sample_rate": info.samplerate,
            "channels": info.channels,
            "frames": info.frames,
            "duration": info.duration,
        }
    except ImportError:
        # Fallback: load and get info
        clip = load_ogg(path)
        return {
            "format": "ogg",
            "sample_rate": clip.sample_rate,
            "channels": clip.channels,
            "frames": clip.frames,
            "duration": clip.duration,
        }
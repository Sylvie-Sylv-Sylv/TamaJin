"""
ECS Audio system tests.
"""

import numpy as np
import pytest

from audio.audio_source import AudioSource, AudioListener, AudioSourceState, BusIndex
from audio.clip import create_tone_clip
from audio.voice import AudioVoice, VoicePool, ClipDatabase, SpatialProcessor
from audio.bus import AudioBus
from audio.graph import AudioGraph


# ====================
# AudioSource Tests
# ====================

def test_audio_source_dtype():
    """Test AudioSource dtype."""
    assert list(AudioSource.schema.names) == [
        "clip_index",
        "volume",
        "pitch",
        "looping",
        "spatial",
        "bus_index"
    ]


def test_audio_source_create():
    """Test creating AudioSource."""
    source = AudioSource.create(
        clip_index=0,
        volume=0.8,
        pitch=1.2,
        looping=True,
        spatial=True,
        bus_index=1
    )
    
    assert source["clip_index"] == 0
    assert source["volume"] == 0.8
    assert source["pitch"] == 1.2
    assert source["looping"] == True
    assert source["spatial"] == True
    assert source["bus_index"] == 1


def test_audio_source_defaults():
    """Test default values."""
    source = AudioSource.create()
    
    assert source["clip_index"] == -1
    assert source["volume"] == 1.0
    assert source["pitch"] == 1.0
    assert source["looping"] == False
    assert source["spatial"] == False
    assert source["bus_index"] == 0


def test_audio_source_batch():
    """Test batch creation."""
    batch = AudioSource.create_batch(10)
    
    assert len(batch) == 10
    assert batch.dtype == AudioSource.schema


# ====================
# AudioListener Tests
# ====================

def test_audio_listener():
    """Test AudioListener."""
    listener = AudioListener.create(x=100.0, y=200.0)
    
    assert listener["x"] == 100.0
    assert listener["y"] == 200.0


# ====================
# BusIndex Tests
# ====================

def test_bus_index():
    """Test BusIndex constants."""
    assert BusIndex.SFX == 0
    assert BusIndex.MUSIC == 1
    assert BusIndex.VOICE == 2
    assert BusIndex.MASTER == 3


def test_bus_index_to_name():
    """Test bus index to name."""
    assert BusIndex.to_name(0) == "sfx"
    assert BusIndex.to_name(1) == "music"
    assert BusIndex.to_name(2) == "voice"
    assert BusIndex.to_name(3) == "master"


# ====================
# AudioVoice Tests
# ====================

def test_voice_creation():
    """Test AudioVoice creation."""
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    voice = AudioVoice(clip, volume=0.8, pitch=1.2, looping=True)
    
    assert voice.clip is clip
    assert voice.volume == 0.8
    assert voice.pitch == 1.2
    assert voice.looping == True
    assert voice.playing == True
    assert voice.position == 0


def test_voice_volume_clamping():
    """Test volume clamping."""
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    
    voice = AudioVoice(clip, volume=1.5)
    assert voice.volume == 1.0
    
    voice = AudioVoice(clip, volume=-0.5)
    assert voice.volume == 0.0


def test_voice_play_pause():
    """Test play/pause."""
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    voice = AudioVoice(clip)
    
    assert voice.playing == True
    
    voice.pause()
    assert voice.playing == False
    
    voice.resume()
    assert voice.playing == True


def test_voice_stop():
    """Test stop."""
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    voice = AudioVoice(clip, position=100)
    
    voice.stop()
    assert voice.playing == False
    assert voice.position == 0


def test_voice_active():
    """Test active property."""
    clip = create_tone_clip(440.0, 0.001, 44100, 1)
    voice = AudioVoice(clip)
    
    assert voice.active == True
    
    voice._position = clip.frames
    assert voice.active == False


# ====================
# VoicePool Tests
# ====================

def test_voice_pool():
    """Test VoicePool."""
    pool = VoicePool()
    
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    
    voice = pool.acquire(clip, volume=0.8)
    
    assert pool.active_count == 1
    assert voice.volume == 0.8
    
    pool.release(voice)
    
    assert pool.active_count == 0
    assert pool.free_count == 1


def test_voice_pool_reuse():
    """Test voice reuse from pool."""
    pool = VoicePool()
    
    clip1 = create_tone_clip(440.0, 0.1, 44100, 1)
    clip2 = create_tone_clip(880.0, 0.1, 44100, 1)
    
    voice1 = pool.acquire(clip1)
    pool.release(voice1)
    
    voice2 = pool.acquire(clip2)
    
    # Should reuse the released voice
    assert pool.free_count == 0


# ====================
# ClipDatabase Tests
# ====================

def test_clip_database():
    """Test ClipDatabase."""
    db = ClipDatabase()
    
    clip1 = create_tone_clip(440.0, 0.1, 44100, 1)
    clip2 = create_tone_clip(880.0, 0.1, 44100, 1)
    
    index1 = db.add(clip1, "tone_440")
    index2 = db.add(clip2)
    
    assert index1 == 0
    assert index2 == 1
    
    assert db.get(0) is clip1
    assert db.get(1) is clip2
    
    assert db.get_by_name("tone_440") is clip1
    
    assert db.count == 2


# ====================
# SpatialProcessor Tests
# ====================

def test_spatial_processor():
    """Test SpatialProcessor."""
    spatial = SpatialProcessor(listener_x=0.0, listener_y=0.0)
    
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    voice = AudioVoice(clip)
    
    # Source at origin - should be close to 1.0
    left, right = spatial.process(voice, 0.0, 0.0)
    
    assert left > 0.9
    assert right > 0.9


def test_spatial_distance():
    """Test distance attenuation."""
    spatial = SpatialProcessor(listener_x=0.0, listener_y=0.0)
    
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    voice = AudioVoice(clip)
    
    # Source far away
    left, right = spatial.process(voice, 100.0, 0.0)
    
    # Should be quieter
    assert left < 1.0
    assert right < 1.0


def test_spatial_panning():
    """Test stereo panning."""
    spatial = SpatialProcessor(listener_x=0.0, listener_y=0.0)
    
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    voice = AudioVoice(clip)
    
    # Source to the right
    left, right = spatial.process(voice, 10.0, 0.0)
    
    # Right should be louder
    assert right > left


# ====================
# Integration Tests
# ====================

def test_full_pipeline():
    """Test full audio pipeline."""
    # Create clip database
    db = ClipDatabase()
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    clip_index = db.add(clip, "test_tone")
    
    # Create voice pool
    pool = VoicePool()
    
    # Acquire voice
    voice = pool.acquire(clip, volume=0.8)
    
    assert voice is not None
    assert pool.active_count == 1
    
    # Create bus
    bus = AudioBus(name="test")
    bus.set_buffer_config(44100, 512, 2)
    
    # Add to bus
    bus.add_voice(voice)
    
    # Update bus
    buffer = bus.update()
    
    assert buffer.shape == (512, 2)
    assert np.any(buffer != 0.0)
    
    # Release
    pool.release(voice)
    
    assert pool.active_count == 0


def test_bus_routing():
    """Test bus routing."""
    graph = AudioGraph(buffer_size=512)
    
    graph.add_bus("sfx")
    graph.add_bus("music")
    graph.add_bus("voice")
    graph.add_master("master")
    
    graph.connect("sfx", "master")
    graph.connect("music", "master")
    graph.connect("voice", "master")
    
    # Get buses
    sfx = graph.get_bus("sfx")
    music = graph.get_bus("music")
    voice = graph.get_bus("voice")
    master = graph.get_bus("master")
    
    # Add clip to database
    db = ClipDatabase()
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    db.add(clip, "test")
    
    # Play on different buses
    sfx.play(clip, volume=0.5)
    music.play(clip, volume=0.3)
    voice.play(clip, volume=0.8)
    
    # Update
    buffer = graph.update()
    
    assert buffer.shape == (512, 2)
    assert np.any(buffer != 0.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
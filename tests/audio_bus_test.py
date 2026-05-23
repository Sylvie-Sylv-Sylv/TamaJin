"""
Audio bus system tests.
"""

import numpy as np
import pytest

from audio.clip import AudioClip, create_tone_clip
from audio.voice import AudioVoice
from audio.bus import AudioBus
from audio.master import MasterBus
from audio.graph import AudioGraph, create_game_graph
from audio.backend import NullBackend, BufferedBackend


# ====================
# AudioBus Tests
# ====================

def test_bus_creation():
    """Test AudioBus creation."""
    bus = AudioBus(name="test", volume=0.8)
    
    assert bus.name == "test"
    assert bus.volume == 0.8
    assert bus.voice_count == 0
    assert not bus.muted


def test_bus_volume_clamping():
    """Test volume is clamped."""
    bus = AudioBus(volume=1.5)
    assert bus.volume == 1.0
    
    bus = AudioBus(volume=-0.5)
    assert bus.volume == 0.0


def test_bus_play():
    """Test playing a clip on a bus."""
    bus = AudioBus(name="test")
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    
    voice = bus.play(clip, volume=0.5)
    
    assert bus.voice_count == 1
    assert voice.clip is clip
    assert voice.volume == 0.5


def test_bus_stop():
    """Test stopping a voice on a bus."""
    bus = AudioBus(name="test")
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    
    voice = bus.play(clip)
    bus.stop(voice)
    
    assert bus.voice_count == 0
    assert not voice.playing


def test_bus_stop_all():
    """Test stopping all voices."""
    bus = AudioBus(name="test")
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    
    bus.play(clip)
    bus.play(clip)
    bus.play(clip)
    
    assert bus.voice_count == 3
    
    bus.stop_all()
    
    assert bus.voice_count == 0


def test_bus_connect():
    """Test connecting buses."""
    bus1 = AudioBus(name="source")
    bus2 = AudioBus(name="dest")
    
    bus2.connect_input(bus1)
    
    assert bus1 in bus2.input_buses
    assert bus2 in bus1.output_buses


def test_bus_disconnect():
    """Test disconnecting buses."""
    bus1 = AudioBus(name="source")
    bus2 = AudioBus(name="dest")
    
    bus2.connect_input(bus1)
    bus2.disconnect_input(bus1)
    
    assert bus1 not in bus2.input_buses


def test_bus_update():
    """Test bus update produces output."""
    bus = AudioBus(name="test")
    bus.set_buffer_config(44100, 512, 2)
    
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    bus.play(clip)
    
    buffer = bus.update()
    
    assert buffer.shape == (512, 2)
    assert buffer.dtype == np.float32


def test_bus_mute():
    """Test bus mute."""
    bus = AudioBus(name="test", volume=0.5)
    bus.muted = True
    
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    bus.play(clip)
    
    buffer = bus.update()
    
    # Should be silent when muted
    assert np.all(buffer == 0.0)


# ====================
# MasterBus Tests
# ====================

def test_master_bus():
    """Test MasterBus creation."""
    backend = NullBackend()
    master = MasterBus(name="master", volume=0.9, backend=backend)
    
    assert master.name == "master"
    assert master.volume == 0.9
    assert master.backend is backend


def test_master_submit():
    """Test master submit."""
    backend = BufferedBackend()
    master = MasterBus(backend=backend)
    master.set_buffer_config(44100, 512, 2)
    
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    master.play(clip)
    
    master.submit()
    
    assert len(backend.buffers) == 1


# ====================
# AudioGraph Tests
# ====================

def test_graph_creation():
    """Test AudioGraph creation."""
    graph = AudioGraph(sample_rate=48000, buffer_size=256)
    
    assert graph.sample_rate == 48000
    assert graph.buffer_size == 256


def test_graph_add_bus():
    """Test adding buses to graph."""
    graph = AudioGraph()
    
    graph.add_bus("sfx", volume=0.8)
    graph.add_bus("music", volume=0.6)
    
    assert "sfx" in graph.buses
    assert "music" in graph.buses
    
    assert graph.get_bus("sfx").volume == 0.8
    assert graph.get_bus("music").volume == 0.6


def test_graph_add_master():
    """Test adding master bus."""
    graph = AudioGraph()
    
    graph.add_master("master")
    
    assert graph.master is not None
    assert graph.master.name == "master"


def test_graph_connect():
    """Test connecting buses."""
    graph = AudioGraph()
    
    graph.add_bus("sfx")
    graph.add_master("master")
    
    graph.connect("sfx", "master")
    
    sfx = graph.get_bus("sfx")
    master = graph.get_bus("master")
    
    assert sfx in master.input_buses


def test_graph_update():
    """Test graph update."""
    graph = AudioGraph(buffer_size=512)
    
    graph.add_bus("sfx")
    graph.add_master("master")
    graph.connect("sfx", "master")
    
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    graph.get_bus("sfx").play(clip)
    
    buffer = graph.update()
    
    assert buffer.shape == (512, 2)


def test_graph_get_update_order():
    """Test topological update order."""
    graph = AudioGraph()
    
    graph.add_bus("sfx")
    graph.add_bus("music")
    graph.add_master("master")
    
    graph.connect("sfx", "master")
    graph.connect("music", "master")
    
    order = graph.get_update_order()
    
    # Master should be in the order
    assert graph.master in order


def test_graph_stats():
    """Test graph statistics."""
    graph = AudioGraph()
    
    graph.add_bus("sfx")
    graph.add_master("master")
    graph.connect("sfx", "master")
    
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    graph.get_bus("sfx").play(clip)
    graph.get_bus("sfx").play(clip)
    
    stats = graph.get_graph_stats()
    
    assert stats["bus_count"] == 2
    assert stats["total_voices"] == 2
    assert stats["master"] == "master"


def test_create_game_graph():
    """Test game graph creation."""
    graph = create_game_graph()
    
    assert "sfx" in graph.buses
    assert "music" in graph.buses
    assert "voice" in graph.buses
    assert "master" in graph.buses
    
    # Check routing
    master = graph.get_bus("master")
    assert graph.get_bus("sfx") in master.input_buses
    assert graph.get_bus("music") in master.input_buses
    assert graph.get_bus("voice") in master.input_buses


# ====================
# Routing Tests
# ====================

def test_multiple_buses_to_master():
    """Test multiple buses routing to master."""
    graph = AudioGraph(buffer_size=512)
    
    graph.add_bus("sfx")
    graph.add_bus("music")
    graph.add_bus("voice")
    graph.add_master("master")
    
    graph.connect("sfx", "master")
    graph.connect("music", "master")
    graph.connect("voice", "master")
    
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    
    graph.get_bus("sfx").play(clip, volume=0.3)
    graph.get_bus("music").play(clip, volume=0.5)
    graph.get_bus("voice").play(clip, volume=0.8)
    
    buffer = graph.update()
    
    # All should be mixed
    assert np.any(buffer != 0.0)


def test_bus_volume_control():
    """Test controlling volume on different buses."""
    graph = create_game_graph()
    
    graph.get_bus("sfx").volume = 0.5
    graph.get_bus("music").volume = 0.2
    graph.get_bus("voice").volume = 1.0
    graph.master.volume = 0.8
    
    assert graph.get_bus("sfx").volume == 0.5
    assert graph.get_bus("music").volume == 0.2
    assert graph.get_bus("voice").volume == 1.0
    assert graph.master.volume == 0.8


def test_bus_mute():
    """Test muting buses."""
    graph = create_game_graph()
    
    clip = create_tone_clip(440.0, 0.1, 44100, 1)
    graph.get_bus("sfx").play(clip)
    
    # Mute SFX
    graph.get_bus("sfx").muted = True
    
    buffer = graph.update()
    
    # Should be silent from SFX
    assert np.all(buffer == 0.0)


def test_remove_bus():
    """Test removing a bus."""
    graph = AudioGraph()
    
    graph.add_bus("sfx")
    graph.add_master("master")
    graph.connect("sfx", "master")
    
    graph.remove_bus("sfx")
    
    assert "sfx" not in graph.buses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
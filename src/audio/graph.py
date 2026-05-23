"""
AudioGraph: routing container for audio buses.

Manages bus connections and provides graph traversal.
"""

from typing import Dict, List, Optional, Set
from collections import deque

from audio.bus import AudioBus
from audio.master import MasterBus
from audio.backend import AudioBackend, NullBackend


class AudioGraph:
    """
    Audio routing graph.
    
    Manages buses and their connections.
    Provides traversal for update order.
    """
    
    def __init__(
        self,
        sample_rate: int = 44100,
        buffer_size: int = 512,
        channels: int = 2
    ) -> None:
        """
        Create an AudioGraph.
        
        Args:
            sample_rate: output sample rate
            buffer_size: frames per buffer
            channels: output channels
        """
        self._sample_rate = sample_rate
        self._buffer_size = buffer_size
        self._channels = channels
        
        self._buses: Dict[str, AudioBus] = {}
        self._master: Optional[MasterBus] = None
    
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
    
    @property
    def buses(self) -> Dict[str, AudioBus]:
        """All buses in the graph."""
        return dict(self._buses)
    
    @property
    def master(self) -> Optional[MasterBus]:
        """Master bus."""
        return self._master
    
    def add_bus(
        self,
        name: str,
        bus: Optional[AudioBus] = None,
        volume: float = 1.0
    ) -> AudioBus:
        """
        Add a bus to the graph.
        
        Args:
            name: bus name
            bus: existing bus (or None to create)
            volume: bus volume
        
        Returns:
            The added bus
        """
        if name in self._buses:
            raise ValueError(f"Bus already exists: {name}")
        
        if bus is None:
            bus = AudioBus(name=name, volume=volume)
        
        # Set buffer config
        bus.set_buffer_config(
            self._sample_rate,
            self._buffer_size,
            self._channels
        )
        
        self._buses[name] = bus
        return bus
    
    def add_master(
        self,
        name: str = "master",
        volume: float = 1.0,
        backend: Optional[AudioBackend] = None
    ) -> MasterBus:
        """
        Add the master bus.
        
        Args:
            name: master bus name
            volume: master volume
            backend: audio backend
        
        Returns:
            The master bus
        """
        if self._master is not None:
            raise ValueError("Master bus already exists")
        
        master = MasterBus(
            name=name,
            volume=volume,
            backend=backend
        )
        
        master.set_buffer_config(
            self._sample_rate,
            self._buffer_size,
            self._channels
        )
        
        self._master = master
        self._buses[name] = master
        return master
    
    def get_bus(self, name: str) -> Optional[AudioBus]:
        """Get a bus by name."""
        return self._buses.get(name)
    
    def connect(
        self,
        from_bus: str,
        to_bus: str
    ) -> None:
        """
        Connect two buses.
        
        Args:
            from_bus: source bus name
            to_bus: destination bus name
        """
        source = self._buses.get(from_bus)
        dest = self._buses.get(to_bus)
        
        if source is None:
            raise ValueError(f"Source bus not found: {from_bus}")
        if dest is None:
            raise ValueError(f"Destination bus not found: {to_bus}")
        
        dest.connect_input(source)
    
    def disconnect(
        self,
        from_bus: str,
        to_bus: str
    ) -> None:
        """
        Disconnect two buses.
        
        Args:
            from_bus: source bus name
            to_bus: destination bus name
        """
        source = self._buses.get(from_bus)
        dest = self._buses.get(to_bus)
        
        if source and dest:
            dest.disconnect_input(source)
    
    def remove_bus(self, name: str) -> None:
        """Remove a bus from the graph."""
        if name not in self._buses:
            return
        
        bus = self._buses[name]
        
        # Disconnect from all
        for input_bus in bus.input_buses:
            input_bus.disconnect_input(bus)
        
        for output_bus in bus.output_buses:
            output_bus.disconnect_input(bus)
        
        del self._buses[name]
        
        if self._master and self._master.name == name:
            self._master = None
    
    def get_update_order(self) -> List[AudioBus]:
        """
        Get buses in topological update order.
        
        Returns:
            List of buses in order they should be updated
        """
        # Find all buses that feed into master
        if self._master is None:
            return list(self._buses.values())
        
        # BFS from master to find all reachable
        visited: Set[AudioBus] = set()
        queue = deque([self._master])
        
        while queue:
            bus = queue.popleft()
            if bus in visited:
                continue
            visited.add(bus)
            
            for input_bus in bus.input_buses:
                if input_bus not in visited:
                    queue.append(input_bus)
        
        # Return in reverse (leaves first)
        result = list(visited)
        result.reverse()
        return result
    
    def update(self):
        """
        Update all buses in order.
        
        Returns:
            Final output buffer
        """
        import numpy as np
        
        # Get update order
        order = self.get_update_order()
        
        # Update each bus
        for bus in order:
            if bus == self._master:
                continue
            bus.update()
        
        # Update master and get output
        if self._master:
            return self._master.update()
        
        return np.zeros((self._buffer_size, self._channels), dtype=np.float32)
    
    def submit(self) -> None:
        """Update and submit to backend."""
        if self._master:
            self._master.submit()
    
    def get_output(self):
        """Get output without submitting."""
        if self._master:
            return self._master.get_output()
        return self.update()
    
    def get_graph_stats(self) -> dict:
        """Get statistics about the graph."""
        total_voices = 0
        for bus in self._buses.values():
            total_voices += bus.voice_count
        
        return {
            "bus_count": len(self._buses),
            "total_voices": total_voices,
            "master": self._master.name if self._master else None,
        }
    
    def __repr__(self) -> str:
        stats = self.get_graph_stats()
        return f"AudioGraph(buses={stats['bus_count']}, voices={stats['total_voices']})"


# Convenience function to create standard game audio graph
def create_game_graph(
    sample_rate: int = 44100,
    buffer_size: int = 512,
    backend: Optional[AudioBackend] = None
) -> "AudioGraph":
    """
    Create a standard game audio routing graph.
    
    Creates:
    - SFX bus (gunshots, footsteps)
    - Music bus (background music)
    - Voice bus (dialogue)
    - Master bus (output)
    
    Args:
        sample_rate: output sample rate
        buffer_size: frames per buffer
        backend: audio backend
    
    Returns:
        Configured AudioGraph
    """
    graph = AudioGraph(
        sample_rate=sample_rate,
        buffer_size=buffer_size
    )
    
    # Add buses
    graph.add_bus("sfx", volume=1.0)
    graph.add_bus("music", volume=1.0)
    graph.add_bus("voice", volume=1.0)
    graph.add_master("master", volume=1.0, backend=backend)
    
    # Connect to master
    graph.connect("sfx", "master")
    graph.connect("music", "master")
    graph.connect("voice", "master")
    
    return graph
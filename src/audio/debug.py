"""
AudioDebugger: visualize audio graph.

Renders the audio routing graph for debugging.
"""

import pygame
import numpy as np
from typing import Dict, List, Optional, Tuple

from audio.graph import AudioGraph
from audio.bus import AudioBus
from audio.master import MasterBus
from audio.voice import AudioVoice


class AudioDebugger:
    """
    Visual debugger for audio graph.
    
    Draws buses as nodes, connections as edges,
    and shows active voices.
    """
    
    def __init__(
        self,
        graph: AudioGraph,
        width: int = 800,
        height: int = 600
    ) -> None:
        """
        Create debugger.
        
        Args:
            graph: AudioGraph to visualize
            width: window width
            height: window height
        """
        self._graph = graph
        self._width = width
        self._height = height
        
        # Node positions (computed)
        self._positions: Dict[str, Tuple[int, int]] = {}
        
        # Colors
        self._colors = {
            "background": (30, 30, 40),
            "bus": (80, 120, 200),
            "bus_muted": (100, 100, 100),
            "master": (200, 100, 100),
            "voice": (100, 200, 100),
            "edge": (150, 150, 150),
            "text": (255, 255, 255),
            "text_dim": (180, 180, 180),
        }
        
        # Initialize pygame
        pygame.init()
        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Audio Graph Debugger")
        self._font = pygame.font.Font(None, 24)
        self._font_small = pygame.font.Font(None, 18)
        self._clock = pygame.time.Clock()
        
        # Compute layout
        self._compute_layout()
    
    def _compute_layout(self) -> None:
        """Compute node positions."""
        buses = self._graph.buses
        count = len(buses)
        
        if count == 0:
            return
        
        # Arrange in layers
        master = self._graph.master
        others = [b for b in buses.values() if b != master]
        
        if master:
            self._positions[master.name] = (
                self._width // 2,
                self._height - 80
            )
        
        layer_height = (self._height - 150) // max(1, len(others))
        
        for i, bus in enumerate(others):
            x = 100 + (i * (self._width - 200) // max(1, len(others) - 1)) if len(others) > 1 else self._width // 2
            y = 80 + i * layer_height
            self._positions[bus.name] = (x, y)
    
    def render(self) -> None:
        """Render one frame."""
        self._screen.fill(self._colors["background"])
        
        self._draw_edges()
        self._draw_buses()
        self._draw_info()
        
        pygame.display.flip()
    
    def _draw_edges(self) -> None:
        """Draw routing connections."""
        for name, pos in self._positions.items():
            bus = self._graph.get_bus(name)
            if bus is None:
                continue
            
            for output in bus.output_buses:
                if output.name in self._positions:
                    end_pos = self._positions[output.name]
                    
                    pygame.draw.line(
                        self._screen,
                        self._colors["edge"],
                        pos,
                        end_pos,
                        2
                    )
                    
                    mid = ((pos[0] + end_pos[0]) // 2, (pos[1] + end_pos[1]) // 2)
                    pygame.draw.circle(self._screen, self._colors["edge"], mid, 4)
    
    def _draw_buses(self) -> None:
        """Draw bus nodes."""
        for name, pos in self._positions.items():
            bus = self._graph.get_bus(name)
            if bus is None:
                continue
            
            if isinstance(bus, MasterBus):
                color = self._colors["master"]
            elif bus.muted:
                color = self._colors["bus_muted"]
            else:
                color = self._colors["bus"]
            
            radius = 30 + bus.voice_count * 5
            radius = min(radius, 50)
            
            pygame.draw.circle(self._screen, color, pos, radius)
            pygame.draw.circle(self._screen, (255, 255, 255), pos, radius, 2)
            
            label = self._font.render(name.upper(), True, self._colors["text"])
            self._screen.blit(label, (pos[0] - label.get_width() // 2, pos[1] - radius - 25))
            
            vol_text = f"Vol: {bus.volume:.2f}"
            vol = self._font_small.render(vol_text, True, self._colors["text_dim"])
            self._screen.blit(vol, (pos[0] - vol.get_width() // 2, pos[1] + radius + 5))
            
            if bus.voice_count > 0:
                voice_text = f"{bus.voice_count} voice(s)"
                voices = self._font_small.render(voice_text, True, self._colors["voice"])
                self._screen.blit(voices, (pos[0] - voices.get_width() // 2, pos[1] + radius + 25))
    
    def _draw_info(self) -> None:
        """Draw graph info."""
        stats = self._graph.get_graph_stats()
        
        info = [
            f"Audio Graph Debugger",
            f"Buses: {stats['bus_count']}",
            f"Voices: {stats['total_voices']}",
            f"Master: {stats['master'] or 'None'}",
            "",
            "Controls:",
            "  SPACE - pause/resume",
            "  Q - quit",
        ]
        
        y = 10
        for line in info:
            text = self._font_small.render(line, True, self._colors["text_dim"])
            self._screen.blit(text, (10, y))
            y += 20
    
    def run(self) -> None:
        """Run the debugger."""
        running = True
        paused = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
            
            if not paused:
                self._graph.update()
            
            self.render()
            self._clock.tick(30)
        
        pygame.quit()
    
    def close(self) -> None:
        """Close the debugger."""
        pygame.quit()


class TextDebugger:
    """Text-based debugger for terminal output."""
    
    def __init__(self, graph: AudioGraph) -> None:
        """Create text debugger."""
        self._graph = graph
    
    def render(self) -> None:
        """Print graph state."""
        print("\n" + "=" * 50)
        print("AUDIO GRAPH STATE")
        print("=" * 50)
        
        stats = self._graph.get_graph_stats()
        print(f"Buses: {stats['bus_count']}")
        print(f"Voices: {stats['total_voices']}")
        print(f"Master: {stats['master']}")
        print()
        
        for name, bus in self._graph.buses.items():
            print(f"Bus: {name}")
            print(f"  Volume: {bus.volume:.2f}")
            print(f"  Muted: {bus.muted}")
            print(f"  Voices: {bus.voice_count}")
            print(f"  Inputs: {[b.name for b in bus.input_buses]}")
            print(f"  Outputs: {[b.name for b in bus.output_buses]}")
            print()
        
        print("=" * 50)


def create_debugger(
    graph: AudioGraph,
    visual: bool = False
):
    """Create a debugger."""
    if visual:
        return AudioDebugger(graph)
    return TextDebugger(graph)
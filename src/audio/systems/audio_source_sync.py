"""
AudioSourceSyncSystem: Syncs ECS AudioSource to runtime voices.

Creates/destroys runtime voices based on ECS AudioSource components.
"""

from typing import TYPE_CHECKING

from gameplay.scenes.scene import Scene
from gameplay.systems.system import System

from audio.audio_source import AudioSource, AudioSourceState, BusIndex
from audio.voice import VoicePool, ClipDatabase


class AudioSourceSyncSystem(System):
    """
    System that syncs ECS AudioSource to runtime voices.
    
    Reads AudioSource components from ECS and creates runtime voices.
    Handles voice lifecycle based on component state.
    """
    
    @staticmethod
    def step(
        scene: Scene,
        voice_pool: VoicePool,
        clip_database: ClipDatabase,
        bus_mapping: dict,
        position_component_type=None,
        listener_component_type=None
    ):
        """
        Sync AudioSource components to runtime voices.
        
        Args:
            scene: Scene with ECS data
            voice_pool: Runtime voice pool
            clip_database: Clip database for lookups
            bus_mapping: Map bus_index to AudioBus
            position_component_type: Optional position component type
            listener_component_type: Optional listener component type
        """
        # Get AudioSource array
        source_array = scene.chunk.component_arrays.get(AudioSource)
        if source_array is None:
            return
        
        # Get position array if provided
        position_array = None
        if position_component_type:
            position_array = scene.chunk.component_arrays.get(position_component_type)
        
        # Get listener position
        listener_x = 0.0
        listener_y = 0.0
        if listener_component_type:
            listener_array = scene.chunk.component_arrays.get(listener_component_type)
            if listener_array and listener_array.size > 0:
                listener_x = listener_array[0]["x"]
                listener_y = listener_array[0]["y"]
        
        # Track which entities have runtime voices
        active_states = set()
        
        # Iterate over all AudioSource components
        for i in range(scene.chunk.size):
            source = source_array[i]
            
            clip_index = source["clip_index"]
            if clip_index < 0:
                continue
            
            # Get clip
            clip = clip_database.get(clip_index)
            if clip is None:
                continue
            
            # Get entity ID
            entity_id = scene.chunk.index_to_entity[i]
            
            # Get position for spatial
            source_x = 0.0
            source_y = 0.0
            if position_array is not None:
                source_x = position_array[i]["x"]
                source_y = position_array[i]["y"]
            
            # Get bus
            bus_index = source["bus_index"]
            bus = bus_mapping.get(bus_index)
            if bus is None:
                bus = bus_mapping.get(0)  # Default to SFX
            
            # Check if we already have a voice for this entity
            state = _get_voice_state(entity_id)
            
            if state is None:
                # Create new voice
                voice = voice_pool.acquire(
                    clip=clip,
                    volume=source["volume"],
                    pitch=source["pitch"],
                    looping=bool(source["looping"])
                )
                
                # Create state
                state = AudioSourceState(
                    entity_id=entity_id,
                    clip_index=clip_index,
                    volume=source["volume"],
                    pitch=source["pitch"],
                    looping=bool(source["looping"]),
                    spatial=bool(source["spatial"]),
                    bus_index=bus_index
                )
                state.voice = voice
                state.active = True
                
                _voice_states[entity_id] = state
                
                # Add to bus
                bus.add_voice(voice)
            
            else:
                # Update existing voice
                voice = state.voice
                
                # Update volume/pitch if changed
                if state.volume != source["volume"]:
                    voice.volume = source["volume"]
                    state.volume = source["volume"]
                
                if state.pitch != source["pitch"]:
                    voice.pitch = source["pitch"]
                    state.pitch = source["pitch"]
                
                # Update spatial position
                if state.spatial and position_array is not None:
                    state._source_x = source_x
                    state._source_y = source_y
            
            active_states.add(entity_id)
        
        # Remove voices for entities that no longer have AudioSource
        for entity_id in list(_voice_states.keys()):
            if entity_id not in active_states:
                state = _voice_states.pop(entity_id)
                if state and state.voice:
                    voice_pool.release(state.voice)


# Global voice state storage (per-process)
_voice_states: dict = {}


def _get_voice_state(entity_id: str) -> AudioSourceState:
    """Get voice state for entity."""
    return _voice_states.get(entity_id)


def get_voice_state(entity_id: str) -> AudioSourceState:
    """Public accessor."""
    return _get_voice_state(entity_id)


def clear_voice_states() -> None:
    """Clear all voice states."""
    global _voice_states
    _voice_states = {}


# Extend AudioSourceState with position
AudioSourceState._source_x = 0.0
AudioSourceState._source_y = 0.0
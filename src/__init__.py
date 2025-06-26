"""MIDI generation app package."""

from .core import request_midi, midi_to_bytes, analyze_midi_data, combine_midi_layers
from .presets import ARTIST_PRESETS, LAYER_TYPES, CREATIVE_CONTROLS
from .session import (
    init_session_state,
    add_layer,
    remove_layer,
    get_layers_by_type,
    toggle_layer_mute,
    toggle_layer_solo,
    get_active_layers,
    clear_all_layers,
)
from .interfaces import (
    create_layer_interface,
    layer_analysis_interface,
    mix_export_interface,
)
from .visualization import (
    plot_midi_layers,
    plot_single_layer_analysis,
    create_velocity_heatmap,
)

__all__ = [
    # Core functionality
    "request_midi",
    "midi_to_bytes",
    "analyze_midi_data",
    "combine_midi_layers",
    # Presets and configurations
    "ARTIST_PRESETS",
    "LAYER_TYPES",
    "CREATIVE_CONTROLS",
    # Session management
    "init_session_state",
    "add_layer",
    "remove_layer",
    "get_layers_by_type",
    "toggle_layer_mute",
    "toggle_layer_solo",
    "get_active_layers",
    "clear_all_layers",
    # User interfaces
    "create_layer_interface",
    "layer_analysis_interface",
    "mix_export_interface",
    # Visualization
    "plot_midi_layers",
    "plot_single_layer_analysis",
    "create_velocity_heatmap",
]

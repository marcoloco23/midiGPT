"""Session state management and layer operations for the MIDI generation app."""

import random
import string
from typing import Dict, List, Tuple

import streamlit as st

from .core import analyze_midi_data


def init_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "layers" not in st.session_state:
        st.session_state.layers = []
    if "layer_counter" not in st.session_state:
        st.session_state.layer_counter = 0


def add_layer(
    layer_type: str, title: str, midi_data: List[Tuple[str, float, float, int]]
) -> None:
    """Add a new MIDI layer to the session."""
    st.session_state.layer_counter += 1

    layer = {
        "id": st.session_state.layer_counter,
        "type": layer_type,
        "title": title,
        "midi_data": midi_data,
        "analysis": analyze_midi_data(midi_data),
        "muted": False,
        "solo": False,
    }

    st.session_state.layers.append(layer)


def remove_layer(layer_id: int) -> None:
    """Remove a layer by ID."""
    st.session_state.layers = [
        layer for layer in st.session_state.layers if layer["id"] != layer_id
    ]


def get_layers_by_type(layer_type: str) -> List[dict]:
    """Get all layers of a specific type."""
    type_key = layer_type.split(" ", 1)[1] if " " in layer_type else layer_type
    return [
        layer
        for layer in st.session_state.layers
        if layer["type"] == layer_type or (type_key.lower() in layer["type"].lower())
    ]


def generate_unique_id(length: int = 8) -> str:
    """Generate a unique identifier string."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def toggle_layer_mute(layer_id: int) -> None:
    """Toggle mute state for a layer."""
    for layer in st.session_state.layers:
        if layer["id"] == layer_id:
            layer["muted"] = not layer["muted"]
            break


def toggle_layer_solo(layer_id: int) -> None:
    """Toggle solo state for a layer."""
    for layer in st.session_state.layers:
        if layer["id"] == layer_id:
            layer["solo"] = not layer["solo"]
        else:
            layer["solo"] = False  # Only one layer can be solo at a time


def get_active_layers() -> List[dict]:
    """Get layers that should be audible (not muted, or solo if any solo exists)."""
    solo_layers = [layer for layer in st.session_state.layers if layer["solo"]]

    if solo_layers:
        return solo_layers
    else:
        return [layer for layer in st.session_state.layers if not layer["muted"]]


def clear_all_layers() -> None:
    """Clear all layers from the session."""
    st.session_state.layers = []
    st.session_state.layer_counter = 0

"""MIDI visualization and plotting utilities for the MIDI generation app."""

from typing import List, Tuple
import warnings

import matplotlib.pyplot as plt
import streamlit as st

from .presets import LAYER_TYPES

# Suppress font warnings
warnings.filterwarnings("ignore", message="Glyph.*missing from current font")
plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']


def plot_midi_layers(
    layers: List[dict], width: int = 12, height: int = 8
) -> plt.Figure:
    """Create a comprehensive visualization of multiple MIDI layers."""

    if not layers:
        fig, ax = plt.subplots(figsize=(width, height))
        ax.text(
            0.5,
            0.5,
            "No layers to display",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
            fontsize=16,
            alpha=0.5,
        )
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 127)
        return fig

    fig, ax = plt.subplots(figsize=(width, height))

    # Track min/max values for better visualization
    all_times = []
    all_pitches = []

    for i, layer in enumerate(layers):
        if layer["muted"]:
            continue

        midi_data = layer["midi_data"]
        layer_type = layer["type"]

        # Get color for this layer type
        layer_color = LAYER_TYPES.get(layer_type, {}).get("color", "#888888")

        # Convert color from hex to matplotlib format
        if layer_color.startswith("#"):
            layer_color = layer_color

        # Plot each note as a rectangle
        for note_name, start, duration, velocity in midi_data:
            # Convert note name to MIDI number for plotting
            midi_note = note_name_to_midi_number(note_name)

            # Create rectangle for note
            rect_height = 0.8  # Height of note rectangle
            rect_y = midi_note - rect_height / 2 + i * 0.1  # Slight offset per layer

            # Alpha based on velocity
            alpha = min(1.0, velocity / 127.0 * 0.8 + 0.2)

            rect = plt.Rectangle(
                (start, rect_y),
                duration,
                rect_height,
                facecolor=layer_color,
                alpha=alpha,
                edgecolor="black",
                linewidth=0.5,
            )
            ax.add_patch(rect)

            all_times.extend([start, start + duration])
            all_pitches.append(midi_note)

    if all_times and all_pitches:
        # Set axis limits with some padding
        time_min, time_max = min(all_times), max(all_times)
        pitch_min, pitch_max = min(all_pitches), max(all_pitches)

        ax.set_xlim(0, max(16, time_max + 1))
        ax.set_ylim(max(0, pitch_min - 5), min(127, pitch_max + 5))
    else:
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 127)

    # Customize the plot
    ax.set_xlabel("Time (beats)", fontsize=12)
    ax.set_ylabel("MIDI Note Number", fontsize=12)
    ax.set_title("MIDI Layer Visualization", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)

    # Add layer legend
    legend_elements = []
    for layer in layers:
        if not layer["muted"]:
            layer_type = layer["type"]
            layer_color = LAYER_TYPES.get(layer_type, {}).get("color", "#888888")
            legend_elements.append(
                plt.Rectangle(
                    (0, 0),
                    1,
                    1,
                    facecolor=layer_color,
                    label=f"{layer['title']} ({layer_type})",
                )
            )

    if legend_elements:
        ax.legend(
            handles=legend_elements,
            loc="upper right",
            bbox_to_anchor=(1, 1),
            fontsize=10,
        )

    plt.tight_layout()
    return fig


def note_name_to_midi_number(note_name: str) -> int:
    """Convert note name (e.g., 'C4') to MIDI note number."""
    # Note mapping
    note_to_number = {
        "C": 0,
        "C#": 1,
        "Db": 1,
        "D": 2,
        "D#": 3,
        "Eb": 3,
        "E": 4,
        "F": 5,
        "F#": 6,
        "Gb": 6,
        "G": 7,
        "G#": 8,
        "Ab": 8,
        "A": 9,
        "A#": 10,
        "Bb": 10,
        "B": 11,
    }

    # Extract note and octave
    if len(note_name) > 1 and note_name[-1].isdigit():
        note = note_name[:-1]
        octave = int(note_name[-1])
    else:
        note = note_name
        octave = 4  # Default octave

    # Calculate MIDI note number
    return note_to_number.get(note, 0) + (octave + 1) * 12


def plot_single_layer_analysis(
    layer: dict, width: int = 10, height: int = 6
) -> plt.Figure:
    """Create detailed analysis plot for a single layer."""

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(width, height), height_ratios=[2, 1])

    midi_data = layer["midi_data"]
    analysis = layer["analysis"]

    # Top plot: Note visualization
    for note_name, start, duration, velocity in midi_data:
        midi_note = note_name_to_midi_number(note_name)
        alpha = min(1.0, velocity / 127.0 * 0.8 + 0.2)

        rect = plt.Rectangle(
            (start, midi_note - 0.4),
            duration,
            0.8,
            facecolor="steelblue",
            alpha=alpha,
            edgecolor="black",
            linewidth=0.5,
        )
        ax1.add_patch(rect)

        # Add note labels
        ax1.text(
            start + duration / 2,
            midi_note,
            note_name,
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
        )

    if midi_data:
        all_notes = [note_name_to_midi_number(note[0]) for note in midi_data]
        all_times = [note[1] + note[2] for note in midi_data]

        ax1.set_xlim(0, max(all_times) + 1 if all_times else 16)
        ax1.set_ylim(min(all_notes) - 2, max(all_notes) + 2)

    ax1.set_ylabel("MIDI Note")
    ax1.set_title(f"{layer['title']} - {layer['type']}")
    ax1.grid(True, alpha=0.3)

    # Bottom plot: Velocity over time
    times = [note[1] for note in midi_data]
    velocities = [note[3] for note in midi_data]

    if times and velocities:
        ax2.scatter(times, velocities, c="red", alpha=0.7, s=50)
        ax2.plot(times, velocities, "r-", alpha=0.5, linewidth=1)

    ax2.set_xlabel("Time (beats)")
    ax2.set_ylabel("Velocity")
    ax2.set_ylim(0, 127)
    ax2.grid(True, alpha=0.3)

    # Add analysis text
    analysis_text = (
        f"Notes: {analysis['note_count']} | "
        f"Range: {analysis['pitch_range']:.1f} | "
        f"Avg Vel: {analysis['avg_velocity']:.0f} | "
        f"Duration: {analysis['total_duration']:.1f} beats"
    )

    fig.suptitle(analysis_text, fontsize=10, y=0.02)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)
    return fig


def create_velocity_heatmap(
    layers: List[dict], width: int = 12, height: int = 6
) -> plt.Figure:
    """Create a heatmap showing velocity patterns across layers."""

    if not layers:
        fig, ax = plt.subplots(figsize=(width, height))
        ax.text(
            0.5,
            0.5,
            "No layers to analyze",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
            fontsize=16,
            alpha=0.5,
        )
        return fig

    fig, ax = plt.subplots(figsize=(width, height))

    # Create a grid for velocity visualization
    time_resolution = 0.25  # Quarter beat resolution
    max_time = 16  # 16 beats default

    if layers:
        layer_max_times = []
        for layer in layers:
            if layer["midi_data"]:
                max_layer_time = max(note[1] + note[2] for note in layer["midi_data"])
                layer_max_times.append(max_layer_time)
        if layer_max_times:
            max_time = max(max_time, max(layer_max_times) + 1)

    time_steps = int(max_time / time_resolution)
    velocity_grid = []
    layer_names = []

    for layer in layers:
        if layer["muted"]:
            continue

        layer_names.append(f"{layer['title']}")
        velocity_row = [0] * time_steps

        for note_name, start, duration, velocity in layer["midi_data"]:
            start_step = int(start / time_resolution)
            end_step = int((start + duration) / time_resolution)

            for step in range(start_step, min(end_step + 1, time_steps)):
                velocity_row[step] = max(velocity_row[step], velocity)

        velocity_grid.append(velocity_row)

    if velocity_grid:
        import numpy as np

        # Create heatmap
        heatmap_data = np.array(velocity_grid)
        im = ax.imshow(
            heatmap_data,
            cmap="YlOrRd",
            aspect="auto",
            vmin=0,
            vmax=127,
            interpolation="nearest",
        )

        # Set labels
        ax.set_yticks(range(len(layer_names)))
        ax.set_yticklabels(layer_names)

        # Set x-axis to show time
        x_ticks = range(0, time_steps, int(1 / time_resolution))  # Every beat
        x_labels = [str(i) for i in range(0, max_time, 1)]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels)

        ax.set_xlabel("Time (beats)")
        ax.set_title("Layer Velocity Heatmap")

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Velocity")

    plt.tight_layout()
    return fig

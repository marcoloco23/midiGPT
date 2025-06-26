"""Audio synthesis and playback utilities for MIDI preview."""

import io
import tempfile
from typing import List, Tuple, Optional

import numpy as np
import pretty_midi
import soundfile as sf
from scipy.signal import butter, lfilter


def note_name_to_frequency(note_name: str) -> float:
    """Convert note name (e.g., 'C4') to frequency in Hz."""
    # Note mapping to semitones from C
    note_to_semitone = {
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

    # Calculate frequency: A4 = 440 Hz
    # Formula: f = 440 * 2^((n-69)/12) where n is MIDI note number
    semitones_from_c = note_to_semitone.get(note, 0)
    midi_note = (octave + 1) * 12 + semitones_from_c
    frequency = 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

    return frequency


def generate_sine_wave(
    frequency: float, duration: float, sample_rate: int = 22050, velocity: int = 100
) -> np.ndarray:
    """Generate a sine wave for a given frequency and duration."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Basic sine wave
    wave = np.sin(2 * np.pi * frequency * t)

    # Apply velocity scaling (0-127 -> 0-1)
    amplitude = velocity / 127.0

    # Apply envelope (ADSR - simple version)
    envelope = create_envelope(len(wave), sample_rate)
    wave = wave * envelope * amplitude * 0.3  # Scale down to prevent clipping

    return wave


def create_envelope(
    length: int,
    sample_rate: int,
    attack: float = 0.01,
    decay: float = 0.1,
    sustain: float = 0.7,
    release: float = 0.2,
) -> np.ndarray:
    """Create an ADSR envelope for natural sound."""
    envelope = np.ones(length)

    # Convert times to samples
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)

    # Attack phase
    if attack_samples > 0 and attack_samples < length:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay phase
    decay_end = min(attack_samples + decay_samples, length)
    if decay_samples > 0 and decay_end > attack_samples:
        envelope[attack_samples:decay_end] = np.linspace(
            1, sustain, decay_end - attack_samples
        )

    # Sustain phase (handled automatically)
    if decay_end < length - release_samples:
        envelope[decay_end : length - release_samples] = sustain

    # Release phase
    if release_samples > 0 and release_samples < length:
        envelope[-release_samples:] = np.linspace(
            envelope[-release_samples], 0, release_samples
        )

    return envelope


def synthesize_layer_type(
    layer_type: str,
    frequency: float,
    duration: float,
    sample_rate: int = 22050,
    velocity: int = 100,
) -> np.ndarray:
    """Generate audio with different synthesis based on layer type."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    amplitude = velocity / 127.0 * 0.3

    if "bassline" in layer_type.lower() or "bass" in layer_type.lower():
        # Bass: Lower frequencies with some harmonics
        wave = (
            np.sin(2 * np.pi * frequency * t)
            + 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
            + 0.1 * np.sin(2 * np.pi * frequency * 3 * t)
        )

        # Low-pass filter for bass
        nyquist = sample_rate // 2
        cutoff = min(800, nyquist - 1)  # Low-pass at 800Hz
        b, a = butter(2, cutoff / nyquist, btype="low")
        wave = lfilter(b, a, wave)

    elif "lead" in layer_type.lower():
        # Lead: Brighter sound with harmonics
        wave = (
            np.sin(2 * np.pi * frequency * t)
            + 0.5 * np.sin(2 * np.pi * frequency * 2 * t)
            + 0.3 * np.sin(2 * np.pi * frequency * 3 * t)
            + 0.1 * np.sin(2 * np.pi * frequency * 4 * t)
        )

    elif "chord" in layer_type.lower():
        # Chords: Softer, pad-like sound
        wave = (
            0.8 * np.sin(2 * np.pi * frequency * t)
            + 0.4 * np.sin(2 * np.pi * frequency * 1.5 * t)
            + 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
        )

    else:
        # Default: Simple sine wave
        wave = np.sin(2 * np.pi * frequency * t)

    # Apply envelope and amplitude
    envelope = create_envelope(len(wave), sample_rate)
    return wave * envelope * amplitude


def midi_data_to_audio(
    midi_data: List[Tuple[str, float, float, int]],
    layer_type: str = "melody",
    sample_rate: int = 22050,
    bpm: float = 120.0,
) -> Tuple[np.ndarray, int]:
    """Convert MIDI data to audio array."""

    if not midi_data:
        # Return 1 second of silence
        return np.zeros(sample_rate), sample_rate

    # Calculate total duration in seconds
    beats_per_second = bpm / 60.0
    max_time_beats = max(start + duration for _, start, duration, _ in midi_data)
    total_duration = max_time_beats / beats_per_second + 1.0  # Add 1 second buffer

    # Create output buffer
    audio_length = int(total_duration * sample_rate)
    audio = np.zeros(audio_length)

    for note_name, start_beats, duration_beats, velocity in midi_data:
        try:
            # Convert timing from beats to seconds
            start_time = start_beats / beats_per_second
            duration_time = duration_beats / beats_per_second

            # Convert note to frequency
            frequency = note_name_to_frequency(note_name)

            # Generate the note audio
            note_audio = synthesize_layer_type(
                layer_type, frequency, duration_time, sample_rate, velocity
            )

            # Calculate sample positions
            start_sample = int(start_time * sample_rate)
            end_sample = start_sample + len(note_audio)

            # Add to audio buffer (with bounds checking)
            if start_sample < audio_length and end_sample > 0:
                # Adjust for bounds
                audio_start = max(0, start_sample)
                audio_end = min(audio_length, end_sample)
                note_start = max(0, -start_sample)
                note_end = note_start + (audio_end - audio_start)

                if note_end <= len(note_audio):
                    audio[audio_start:audio_end] += note_audio[note_start:note_end]

        except Exception as e:
            print(f"Warning: Skipping note {note_name}: {e}")
            continue

    # Normalize to prevent clipping
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio)) * 0.8

    return audio, sample_rate


def audio_to_bytes(audio: np.ndarray, sample_rate: int, format: str = "wav") -> bytes:
    """Convert audio array to bytes for streaming/download."""

    # Create a bytes buffer
    buffer = io.BytesIO()

    try:
        # Write audio to buffer
        sf.write(buffer, audio, sample_rate, format=format.upper())
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        print(f"Error converting audio to bytes: {e}")
        # Return empty WAV file
        empty_audio = np.zeros(sample_rate)  # 1 second of silence
        buffer = io.BytesIO()
        sf.write(buffer, empty_audio, sample_rate, format="WAV")
        buffer.seek(0)
        return buffer.getvalue()


def create_layer_preview(
    midi_data: List[Tuple[str, float, float, int]],
    layer_type: str = "melody",
    duration_limit: float = 30.0,
    bpm: float = 120.0,
) -> bytes:
    """Create an audio preview of a MIDI layer (limited duration for web playback)."""

    if not midi_data:
        return audio_to_bytes(np.zeros(22050), 22050)  # 1 second silence

    # Limit duration for web preview
    beats_per_second = bpm / 60.0
    max_beats = duration_limit * beats_per_second

    # Filter notes that start within the time limit
    limited_midi = [
        (note, start, duration, velocity)
        for note, start, duration, velocity in midi_data
        if start < max_beats
    ]

    if not limited_midi:
        return audio_to_bytes(np.zeros(22050), 22050)

    # Generate audio
    audio, sample_rate = midi_data_to_audio(limited_midi, layer_type, bpm=bpm)

    # Convert to bytes
    return audio_to_bytes(audio, sample_rate)


def create_mix_preview(
    layers: List[dict], duration_limit: float = 30.0, bpm: float = 120.0
) -> bytes:
    """Create an audio preview of multiple MIDI layers mixed together."""

    if not layers:
        return audio_to_bytes(np.zeros(22050), 22050)

    sample_rate = 22050
    beats_per_second = bpm / 60.0
    max_beats = duration_limit * beats_per_second

    # Calculate total duration
    all_midi_data = []
    for layer in layers:
        if layer.get("muted", False):
            continue
        midi_data = layer.get("midi_data", [])
        all_midi_data.extend(midi_data)

    if not all_midi_data:
        return audio_to_bytes(np.zeros(sample_rate), sample_rate)

    # Calculate audio length
    max_time_beats = min(
        max_beats, max(start + duration for _, start, duration, _ in all_midi_data)
    )
    total_duration = max_time_beats / beats_per_second + 1.0
    audio_length = int(total_duration * sample_rate)
    mixed_audio = np.zeros(audio_length)

    # Mix each layer
    for layer in layers:
        if layer.get("muted", False):
            continue

        midi_data = layer.get("midi_data", [])
        layer_type = layer.get("type", "melody")

        if not midi_data:
            continue

        # Filter for duration limit
        limited_midi = [
            (note, start, duration, velocity)
            for note, start, duration, velocity in midi_data
            if start < max_beats
        ]

        if limited_midi:
            layer_audio, _ = midi_data_to_audio(
                limited_midi, layer_type, sample_rate, bpm
            )

            # Mix into the main audio (with length matching)
            mix_length = min(len(mixed_audio), len(layer_audio))
            mixed_audio[:mix_length] += layer_audio[:mix_length]

    # Normalize the mix
    if np.max(np.abs(mixed_audio)) > 0:
        mixed_audio = mixed_audio / np.max(np.abs(mixed_audio)) * 0.8

    return audio_to_bytes(mixed_audio, sample_rate)

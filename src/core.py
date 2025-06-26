"""Core utilities shared by both CLI and Streamlit app.

This module centralises anything that needs to be reused across
entry-points so we avoid code duplication.
"""
from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from midiutil import MIDIFile
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

# ---------------------------------------------------------------------------
# Model definitions
# ---------------------------------------------------------------------------


class Note(BaseModel):
    """Single note representation returned by the LLM."""

    pitch: str = Field(description="Note name with octave, e.g. C#4")
    # Use float timings to allow 16th-note (0.25 beat) or triplet resolutions.
    start: float = Field(ge=0, description="Start time in beats (float)")
    duration: float = Field(gt=0, description="Duration in beats (float)")
    # Allow dynamic expression – defaults to a typical bass velocity.
    velocity: int = Field(default=100, ge=1, le=127, description="Velocity 1-127")


class MidiResponse(BaseModel):
    """Complete structured response returned by the LLM."""

    title: str = Field(
        description="Short descriptive title for the midi layer, suitable for filename. Standard format: '[layer_type] - [key] - [mood] - [genre]'"
    )
    notes: List[Note] = Field(description="List of notes in the midi layer")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NOTES_TO_MIDI: dict[str, int] = {
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

PROMPT_SYSTEM: str = (
    "You are a talented dance-music composer who understands music theory, groove and MIDI. "
    "Specialise in deep/minimal/tech-house yet feel comfortable borrowing ideas from other sub-genres when it serves the groove. "
    "Your mission: craft an irresistible bassline (8–16 bars) that will work on a club sound-system. "
    "Guidelines:\n"
    "1. Pocket & rhythm: think in 16th-note grids, add syncopation, create tension with spaces and ghost notes.\n"
    "2. Dynamics: vary velocity between 70-120 to accentuate groove.\n"
    "3. Keep the fundamental mostly below C3 but octave jumps are welcome for excitement.\n"
    "4. Optional stylistic inspirations (do NOT simply copy):\n"
    "   • 90s organ house (M1-style plucked chords/bass).\n"
    "   • Modern tech-house warm sub with long sustain followed by percussive stabs.\n"
    "   • Disco / funk walking bass with spacious phrasing and scale climbs.\n"
    "   • Acid 303-flavoured plucks using short overlapping notes to create glide.\n"
    "   • Garage / jungle reese bass with elongated notes and contrasting high-octave blips.\n"
    "5. Ensure the pattern loops cleanly over 4-bar sections.\n"
    "6. Output MUST conform to the JSON schema provided – do NOT wrap in markdown.\n\n"
    "Here is a short example JSON bassline for flavour (use only as inspiration):\n"
    '{"notes": [ {"pitch": "F#1", "start": 0, "duration": 1, "velocity": 105}, {"pitch": "C#2", "start": 1, "duration": 1, "velocity": 105}, {"pitch": "E1", "start": 2.5, "duration": 0.5, "velocity": 118}, {"pitch": "B1", "start": 3, "duration": 1, "velocity": 112}, {"pitch": "F#1", "start": 4, "duration": 1, "velocity": 104}, {"pitch": "C#2", "start": 5, "duration": 1, "velocity": 105}, {"pitch": "E1", "start": 6.5, "duration": 0.5, "velocity": 118}, {"pitch": "B1", "start": 7, "duration": 1, "velocity": 112} ]}\n'
)

# ---------------------------------------------------------------------------
# MIDI helpers
# ---------------------------------------------------------------------------


def note_name_to_midi(note: str) -> int:
    """Convert a pitch string such as 'C#4' into its MIDI integer value."""

    pitch, octave = note[:-1], note[-1]
    if pitch not in NOTES_TO_MIDI:
        raise ValueError(f"Unknown pitch '{pitch}' in note '{note}'.")
    return NOTES_TO_MIDI[pitch] + (int(octave) + 1) * 12


# ---------------------------------------------------------------------------
# OpenAI interaction
# ---------------------------------------------------------------------------


def _model_to_tuples(model: MidiResponse) -> List[Tuple[str, float, float, int]]:
    """Helper to convert a `MidiResponse` model into a plain tuple list."""

    return [(n.pitch, n.start, n.duration, n.velocity) for n in model.notes]


def request_midi(
    prompt: str,
    *,
    api_key: str | None = None,
    model: str = "o1",
    layer_type: str = "bassline",
    existing_layers: List[dict] | None = None,
) -> Tuple[str, List[Tuple[str, float, float, int]]]:
    """Ask the LLM for a MIDI layer (bassline, melody, chords, etc.).

    Returns
    -------
    title : str
        Title generated by the LLM to describe the MIDI layer.
    midi_data : list[tuple]
        Sequence of (note, start, duration, velocity) tuples.

    The function relies on OpenAI's *structured output* feature using
    the very convenient `beta.chat.completions.parse` helper which
    guarantees a JSON response that matches the `MidiResponse` schema.
    """

    # Ensure environment variables are loaded once — harmless if called again.
    load_dotenv()

    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set. Provide it or add to .env")

    # Create layering-aware prompt if we have existing layers
    final_prompt = prompt
    if existing_layers:
        final_prompt = create_layering_prompt(layer_type, prompt, existing_layers)

    client = OpenAI(api_key=api_key)

    response = client.beta.chat.completions.parse(
        model=model,
        response_format=MidiResponse,
        messages=[
            {"role": "system", "content": PROMPT_SYSTEM},
            {"role": "user", "content": final_prompt},
        ],
    )

    try:
        midi_resp = MidiResponse.model_validate(response.choices[0].message.parsed)
    except ValidationError as exc:  # pragma: no cover – should never happen
        raise ValueError(f"Model output failed validation: {exc}") from exc

    return midi_resp.title, _model_to_tuples(midi_resp)


# ---------------------------------------------------------------------------
# MIDI serialisation helpers
# ---------------------------------------------------------------------------


def _write_notes_to_midi(
    midi: MIDIFile,
    midi_data: List[Tuple[str, float, float]] | List[Tuple[str, float, float, int]],
) -> None:
    """Populate an existing `MIDIFile` instance with the supplied data."""

    if not midi_data:
        return

    for data in midi_data:
        try:
            # Support both legacy 3-tuple and new 4-tuple (with velocity).
            if len(data) == 3:
                note, start, duration = data  # type: ignore[misc]
                velocity = 100
            else:
                note, start, duration, velocity = data  # type: ignore[misc]

            # Validate and clamp values
            start = max(0.0, float(start))
            duration = max(0.1, float(duration))  # Minimum duration to avoid issues
            velocity = max(1, min(127, int(velocity)))

            # Convert note to MIDI pitch
            pitch = note_name_to_midi(note)
            pitch = max(0, min(127, pitch))  # Clamp to valid MIDI range

            midi.addNote(
                track=0,
                channel=0,
                pitch=pitch,
                time=start,
                duration=duration,
                volume=velocity,
            )
        except Exception as e:
            # Skip problematic notes rather than crashing
            print(f"Warning: Skipping invalid note data {data}: {e}")
            continue


def generate_midi_file(
    midi_data: List[Tuple[str, float, float]] | List[Tuple[str, float, float, int]],
    output_path: Path | str,
) -> None:
    """Create a `.mid` file at *output_path* containing *midi_data*."""

    midi = MIDIFile(1)
    _write_notes_to_midi(midi, midi_data)

    out = Path(output_path).expanduser().resolve()
    with out.open("wb") as fp:
        midi.writeFile(fp)


def midi_to_bytes(
    midi_data: List[Tuple[str, float, float]] | List[Tuple[str, float, float, int]]
) -> bytes:
    """Return a raw MIDI binary representation for direct download/streaming."""

    midi = MIDIFile(1)
    midi.addTempo(track=0, time=0, tempo=120)  # Add tempo to avoid issues

    _write_notes_to_midi(midi, midi_data)

    buffer = BytesIO()
    try:
        midi.writeFile(buffer)
        return buffer.getvalue()
    except Exception as e:
        print(f"Error creating MIDI file: {e}")
        # Return empty MIDI file if there's an issue
        empty_midi = MIDIFile(1)
        empty_midi.addTempo(track=0, time=0, tempo=120)
        buffer = BytesIO()
        empty_midi.writeFile(buffer)
        return buffer.getvalue()


# ---------------------------------------------------------------------------
# MIDI layering and analysis helpers
# ---------------------------------------------------------------------------


def analyze_midi_data(midi_data: List[Tuple[str, float, float, int]]) -> dict:
    """Analyze MIDI data to extract musical information for layering."""
    if not midi_data:
        return {
            "note_count": 0,
            "total_duration": 0.0,
            "avg_velocity": 0,
            "pitch_range": 0.0,
            "unique_pitches": 0,
            "time_span": 0.0,
            "root_note": "C",
            "notes_used": [],
            "octave_range": (4, 4),
            "tempo_hint": "moderate",
            "velocity_range": (100, 100),
            "rhythmic_complexity": 0.0,
        }

    notes = [note[0] for note in midi_data]
    times = [note[1] for note in midi_data]
    durations = [note[2] for note in midi_data]
    velocities = [note[3] for note in midi_data]

    # Extract key information
    note_names = [note[:-1] for note in notes]  # Remove octave
    unique_notes = list(set(note_names))

    # Determine likely key (simplified)
    note_counts = {note: note_names.count(note) for note in unique_notes}
    root_note = max(note_counts, key=note_counts.get) if note_counts else "C"

    # Calculate timing info
    total_duration = (
        max(time + dur for time, dur in zip(times, durations))
        if times and durations
        else 0
    )
    note_density = len(midi_data) / total_duration if total_duration > 0 else 0

    # Octave range
    octaves = [int(note[-1]) if note[-1].isdigit() else 4 for note in notes]
    octave_range = (min(octaves), max(octaves)) if octaves else (4, 4)

    # MIDI pitch analysis
    try:
        pitches = [note_name_to_midi(note) for note in notes]
        pitch_range = max(pitches) - min(pitches) if pitches else 0
        avg_velocity = sum(velocities) / len(velocities) if velocities else 0
    except:
        pitch_range = 0
        avg_velocity = 100

    return {
        # Required keys for interface compatibility
        "note_count": len(midi_data),
        "total_duration": round(total_duration, 2),
        "avg_velocity": round(avg_velocity, 1),
        "pitch_range": round(pitch_range, 1),
        "unique_pitches": len(unique_notes),
        "time_span": round(total_duration, 2),
        # Additional analysis for layering
        "root_note": root_note,
        "notes_used": unique_notes,
        "note_density": note_density,
        "octave_range": octave_range,
        "tempo_hint": "slow"
        if note_density < 1
        else "fast"
        if note_density > 3
        else "moderate",
        "velocity_range": (min(velocities), max(velocities))
        if velocities
        else (100, 100),
        "rhythmic_complexity": len(set(times)) / len(times) if times else 0,
    }


def create_layering_prompt(
    layer_type: str, base_prompt: str, existing_layers: List[dict]
) -> str:
    """Create a prompt for generating a MIDI layer that complements existing layers."""

    if not existing_layers:
        return base_prompt

    # Analyze existing layers
    layer_info = []
    all_notes = set()
    duration_range = (0, 0)

    for layer in existing_layers:
        analysis = layer.get("analysis", {})
        layer_info.append(
            f"- {layer['type']}: {analysis.get('root_note', 'C')} root, "
            f"octave {analysis.get('octave_range', (2, 3))}, "
            f"{analysis.get('tempo_hint', 'moderate')} pace"
        )

        all_notes.update(analysis.get("notes_used", []))
        layer_duration = analysis.get("total_duration", 8)
        duration_range = (
            min(duration_range[0], layer_duration),
            max(duration_range[1], layer_duration),
        )

    # Create contextual prompt
    context = f"""
EXISTING LAYERS:
{chr(10).join(layer_info)}

MUSICAL CONTEXT:
- Key notes in use: {', '.join(sorted(all_notes))}
- Track duration: {duration_range[1]:.1f} beats
- Harmonic foundation established

LAYERING INSTRUCTIONS for {layer_type.upper()}:
"""

    if layer_type.lower() == "melody":
        context += """
- Create a melodic line that complements the existing bassline
- Use higher octaves (3-5) to sit above the bass
- Focus on memorable hooks and phrases
- Ensure harmonic compatibility with established root notes
- Add rhythmic interest without clashing with existing patterns
"""
    elif layer_type.lower() == "chords":
        context += """
- Create chord progressions that support the existing melody and bass
- Use mid-range octaves (2-4) 
- Provide harmonic foundation without competing with lead elements
- Use sustained notes and chord stabs for rhythmic punctuation
- Complement the established key and note choices
"""
    elif layer_type.lower() == "lead":
        context += """
- Create a lead synth line that cuts through the mix
- Use higher octaves (4-6) for clarity and presence
- Add melodic interest and hooks over the harmonic foundation
- Create call-and-response with existing melodic elements
- Use varied velocity for expression and dynamics
"""
    elif layer_type.lower() == "percussion":
        context += """
- Create rhythmic percussion elements that enhance the groove
- Focus on off-beat elements and polyrhythmic patterns
- Use high octaves (5-7) for percussive hits and stabs
- Add syncopation and ghost notes to increase rhythmic complexity
- Complement but don't compete with the main rhythmic elements
"""

    return base_prompt + context


def combine_midi_layers(layers: List[dict]) -> List[Tuple[str, float, float, int]]:
    """Combine multiple MIDI layers into a single MIDI data structure."""
    combined_data = []

    for layer in layers:
        midi_data = layer.get("midi_data", [])
        layer_type = layer.get("type", "unknown")

        # Add layer-specific adjustments
        for note, start, duration, velocity in midi_data:
            # Adjust velocity based on layer type for better mixing
            if layer_type.lower() == "bassline":
                velocity = max(90, min(120, velocity))  # Keep bass punchy
            elif layer_type.lower() == "melody":
                velocity = max(
                    85, min(110, velocity)
                )  # Melody present but not overpowering
            elif layer_type.lower() == "chords":
                velocity = max(70, min(95, velocity))  # Chords more subtle
            elif layer_type.lower() == "lead":
                velocity = max(100, min(127, velocity))  # Lead prominent

            combined_data.append((note, start, duration, velocity))

    # Sort by start time for proper playback
    return sorted(combined_data, key=lambda x: x[1])

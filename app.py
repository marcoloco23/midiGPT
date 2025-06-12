import io
import string
from typing import List, Tuple

import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv
from mido import MidiFile

from src.core import midi_to_bytes, request_midi

load_dotenv()

# ---------------------------------------------------------------------------
# Streamlit helpers
# ---------------------------------------------------------------------------


def sanitize_filename(filename: str) -> str:
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    sanitized = "".join(c for c in filename if c in valid_chars)
    return sanitized[:255]


def get_api_key() -> str:
    """Return the OpenAI key entered by the user in the sidebar (may be empty)."""

    api_key = st.sidebar.text_input("Enter your OpenAI API key:")
    if "api_key" not in st.session_state or st.session_state["api_key"] != api_key:
        st.session_state["api_key"] = api_key
    return st.session_state["api_key"]


def get_chat_prompt() -> str:
    return st.text_input("Enter your prompt:")


def check_execute_button() -> bool:
    return st.button("Generate MIDI")


def handle_execute_button(api_key: str, chat_prompt: str) -> None:
    if not api_key:
        st.warning("Please provide your OpenAI API key.")
        return

    with st.spinner("Generating MIDI..."):
        midi_data = request_midi(chat_prompt, api_key=api_key)
        midi_bytes = midi_to_bytes(midi_data)
        midi_buffer = io.BytesIO(midi_bytes)

        st.download_button(
            label="Download MIDI File",
            data=midi_bytes,
            file_name=f"{sanitize_filename(chat_prompt)}.mid",
            mime="audio/midi",
        )

        plot_midi(midi_buffer)


def plot_midi(midi_file: io.BytesIO) -> None:
    """Display a rudimentary piano roll for the given MIDI bytes."""

    midi_file.seek(0)
    mid = MidiFile(file=midi_file)

    notes: List[int] = []
    start_times: List[float] = []
    durations: List[float] = []

    current_time = 0.0
    for msg in mid:
        current_time += msg.time
        if not msg.is_meta and msg.channel == 0:
            if msg.type == "note_on" and msg.velocity > 0:
                notes.append(msg.note)
                start_times.append(current_time)
            elif msg.type == "note_off" or (
                msg.type == "note_on" and msg.velocity == 0
            ):
                if start_times:
                    durations.append(current_time - start_times[-1])

    if len(durations) < len(start_times):
        durations.append(current_time - start_times[-1])

    fig, ax = plt.subplots(figsize=(10, 6))

    for note, start, duration in zip(notes, start_times, durations):
        ax.plot([start, start + duration], [note, note], color="black", linewidth=10)

    plt.ylabel("Note value")
    plt.xlabel("Time (s)")
    plt.title("MIDI Visualization")

    st.pyplot(fig)


def main() -> None:
    st.title("midiGPT – Deep-House Bassline Generator")

    api_key = get_api_key()
    chat_prompt = get_chat_prompt()

    if check_execute_button():
        handle_execute_button(api_key, chat_prompt)


if __name__ == "__main__":
    main()

import streamlit as st
import openai
from midiutil import MIDIFile
import base64
from typing import List, Tuple
import numpy as np
from mido import MidiFile
import matplotlib.pyplot as plt

PROMPT = (
    "You are a talented composer who understands music theory and MIDI. "
    "You can generate creative and interesting MIDI sequences as a list of tuples. "
    "Each tuple represents a note, consisting of the note name and octave, the start time, and the duration. "
    "For example, [('C4', 0, 1), ('D4', 1, 1), ('E4', 2, 1)]. "
    "Please generate a sequence of such tuples for a new piece of music."
    "Start the midi sequence using ``` and end it with ```."
    "Make sure the midi sequence just a list of tuples, and nothing else."
    "Don't asign a variable to the midi sequence, just return it."
)

NOTES_TO_MIDI = {
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


def generate_midi(midi_data: List[Tuple[str, int, int]], filename: str) -> None:
    midi = MIDIFile(1)
    for note, start_time, duration in midi_data:
        pitch = note_name_to_midi(note)
        midi.addNote(0, 0, pitch, start_time, duration, 100)
    with open(filename, "wb") as f:
        midi.writeFile(f)


def note_name_to_midi(note: str) -> int:
    pitch, octave = note[:-1], note[-1]
    midi_num = NOTES_TO_MIDI[pitch] + (int(octave) + 1) * 12
    return midi_num


def get_binary_file_downloader_html(bin_file: str, file_label="File") -> str:
    with open(bin_file, "rb") as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{bin_file}">{file_label}</a>'
    return href


def get_api_key() -> str:
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
    else:
        with st.spinner("Generating MIDI..."):
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": chat_prompt},
                ],
                stream=True,
            )

            collected_messages = []
            text_placeholder = st.empty()
            for chunk in response:
                chunk_message = chunk["choices"][0]["delta"].get("content")
                if chunk_message:
                    collected_messages.append(chunk_message)
                    text_placeholder.text("".join(collected_messages))

            midi_data_string = extract_midi_data("".join(collected_messages))
            midi_data = eval(midi_data_string)
            generate_midi(midi_data, "output.mid")

            st.markdown(
                get_binary_file_downloader_html(
                    "output.mid", "Click here to download your MIDI file."
                ),
                unsafe_allow_html=True,
            )

            plot_midi("output.mid")


def extract_midi_data(full_reply_content: str) -> str:
    start = full_reply_content.find("```")
    if full_reply_content[start : start + 9] == "```python":
        start += 9  # If it starts with ```python, offset the start index
    else:
        start += 3  # If it starts with ```, offset the start index by 3
    end = full_reply_content.rfind("```")  # rfind to find the last occurrence
    return full_reply_content[start:end].strip()


def plot_midi(file_path: str) -> None:
    """
    Function to plot MIDI data as a simple piano roll.

    Args:
    file_path : str : Path to the MIDI file.
    """
    mid = MidiFile(file_path)

    notes = []
    start_times = []
    durations = []

    time = 0
    for msg in mid:
        time += msg.time
        if not msg.is_meta and msg.channel == 0:
            if msg.type == "note_on":
                data = msg.bytes()
                notes.append(data[1])
                start_times.append(time)
            elif msg.type == "note_off":
                durations.append(time - start_times[-1])

    # Make sure all notes have a corresponding duration
    if len(durations) < len(start_times):
        durations.append(time - start_times[-1])

    fig, ax = plt.subplots(figsize=(10, 6))

    for i in range(len(notes)):
        ax.plot(
            [start_times[i], start_times[i] + durations[i]],
            [notes[i], notes[i]],
            color="black",
            linewidth=10,
        )

    plt.ylabel("Note value")
    plt.xlabel("Time (s)")
    plt.title(f"MIDI file: {file_path}")

    st.pyplot(fig)


def main() -> None:
    api_key = get_api_key()
    chat_prompt = get_chat_prompt()

    if check_execute_button():
        handle_execute_button(api_key, chat_prompt)


if __name__ == "__main__":
    main()

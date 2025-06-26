import io
import random
import string
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv
from mido import MidiFile

from src.core import midi_to_bytes, request_midi

load_dotenv()

# ---------------------------------------------------------------------------
# Enhanced Presets and Creative Templates
# ---------------------------------------------------------------------------

ARTIST_PRESETS = {
    "🔥 Chris Stussy": {
        "description": "Dutch minimal house with warm analog character and jazz influences",
        "prompts": [
            "Chris Stussy inspired minimal house bassline with warm analog character, subtle jazz influences, and sophisticated groove. Focus on deep sub frequencies and organic timing variations.",
            "Dutch minimal house bass with classic machine drums, smooth bassline flow, and late-night underground vibes channeling Chris Stussy's signature sound.",
            "Minimal house bassline with raw production aesthetics, lush synth colors, and seductive warm grooves in the style of Chris Stussy.",
        ],
    },
    "⚡ Kolter (DJOKO)": {
        "description": "Evolution from deep tech to minimal with breaks and chunky grooves",
        "prompts": [
            "Kolter style minimal bassline with chunky grooves and breaks influences, channeling the evolution from DJOKO's deeper sound to more experimental territory.",
            "Deep minimal tech bass with rolling rhythm, subtle variations, and that signature Kolter driving pulse maintaining hypnotic energy throughout.",
            "Minimal house bassline inspired by Kolter's genre-blending approach, incorporating elements of breaks, old-school samples, and modern production.",
        ],
    },
    "🌊 M High": {
        "description": "Deep minimal house with sophisticated underground aesthetics",
        "prompts": [
            "M High inspired deep minimal house bassline with sophisticated underground aesthetics and refined groove development.",
            "Minimal tech bass channeling M High's approach to deep, driving rhythms with subtle complexity and underground appeal.",
            "Deep minimal bassline with clean production, focused low-end, and the sophisticated minimalism characteristic of M High's style.",
        ],
    },
    "🔊 Gaskin": {
        "description": "Bass-heavy house with UK garage influences and powerful low-end",
        "prompts": [
            "Gaskin style bass-heavy house with powerful sub frequencies, UK garage influences, and that signature Bass Jamz label sound from Newcastle.",
            "Heavy bassline inspired by Gaskin's approach to funky sequences, complex rhythms, and genre-spanning creativity blending house with garage elements.",
            "UK-influenced house bassline with Gaskin's characteristic heavy low-end, intricate melodies, and dynamic groove programming.",
        ],
    },
    "🌟 Obskür": {
        "description": "Irish deep house with emotive, atmospheric qualities",
        "prompts": [
            "Obskür inspired deep house bassline with emotive Dublin underground vibes, atmospheric depth, and sophisticated minimal arrangements.",
            "Irish deep house bass with warm, organic character and the refined minimal aesthetics characteristic of Obskür's sound.",
            "Deep minimal house bassline channeling Obskür's approach to atmospheric house music with emotional depth and underground credibility.",
        ],
    },
    "🎯 Artmann": {
        "description": "Amsterdam-based house with funk elements and PIV label aesthetics",
        "prompts": [
            "Artmann style funky house bassline from Amsterdam with diverse genre influences, tight groove programming, and that signature PIV label sound.",
            "Dutch house bass inspired by Artmann's all-round production approach, blending multiple influences into distinctive groovy basslines.",
            "Amsterdam house bassline with Artmann's characteristic funk elements, precise production, and crossover appeal maintaining underground credibility.",
        ],
    },
    "🌈 Luuk Van Dijk": {
        "description": "Amsterdam house with strong basslines and old-school vision",
        "prompts": [
            "Luuk Van Dijk inspired Amsterdam house bassline with strong low-end, groovy vibe, and clear old-school house vision channeling his signature sound.",
            "Dutch house bass with contagious energy, radiant groove, and the distinctive bassline focus that defines Luuk Van Dijk's productions.",
            "Amsterdam house bassline featuring Luuk Van Dijk's approach to contemporary house with vintage influences, Hot Creations and Solid Grooves aesthetics.",
        ],
    },
    "💥 Sidney Charles": {
        "description": "The Sidney Sound - heavy low-end with chunky drums and physicality",
        "prompts": [
            "Sidney Charles style 'Sidney Sound' bassline with heavy low-end, chunky drums, cavernous frequencies, and hard-hitting rhythms that connect directly with your body.",
            "Rough, dirty house bassline inspired by Sidney Charles' approach to old-school pioneers sound with modern, full and punchy production.",
            "Physical house bassline channeling Sidney Charles' upfront, dark, hard-hitting style designed to get bodies moving on the dancefloor.",
        ],
    },
    "🎵 Marsolo": {
        "description": "Underground house with minimal deep tech influences",
        "prompts": [
            "Marsolo inspired underground house bassline with minimal deep tech influences and contemporary electronic aesthetics.",
            "Deep tech house bass channeling Marsolo's approach to modern minimal arrangements with driving underground energy.",
            "Minimal house bassline with Marsolo's characteristic balance of deep techno elements and house groove fundamentals.",
        ],
    },
    "🎹 Classic Organ House": {
        "description": "90s organ house vibes",
        "prompts": [
            "90s organ house bassline with M1-style plucked bass character and classic house groove.",
            "Retro organ house with warm pad-like sustains and percussive chord stabs.",
            "Classic house organ bass with nostalgic character and timeless groove.",
        ],
    },
    "🌟 Disco Funk": {
        "description": "Disco-influenced walking basslines",
        "prompts": [
            "Disco-funk walking bassline with spacious phrasing and scale climbs, bringing classic groove to modern house.",
            "Funky disco bass with sliding notes and rhythmic variations.",
            "Groove-heavy disco-inspired bassline with dynamic articulation.",
        ],
    },
    "🎮 UK Garage": {
        "description": "UK garage influenced bass patterns",
        "prompts": [
            "UK garage influenced bassline with broken rhythms and reese-style character.",
            "Garage bass with elongated notes contrasted by high-octave percussive hits.",
            "Underground UK garage bassline with complex timing and sub-bass emphasis.",
        ],
    },
}

MOOD_MODIFIERS = [
    "dark and moody",
    "bright and energetic",
    "hypnotic and trippy",
    "warm and organic",
    "cold and mechanical",
    "groovy and funky",
    "mysterious and atmospheric",
    "driving and relentless",
    "playful and bouncy",
    "melancholic and deep",
    "aggressive and punchy",
    "smooth and flowing",
]

KEY_SIGNATURES = [
    "C major",
    "G major",
    "D major",
    "A major",
    "E major",
    "F major",
    "A minor",
    "E minor",
    "B minor",
    "F# minor",
    "C# minor",
    "D minor",
    "G minor",
    "C minor",
    "F minor",
    "Bb minor",
    "Eb minor",
]

TEMPO_RANGES = {
    "Deep House (120-125 BPM)": (120, 125),
    "Tech House (125-130 BPM)": (125, 130),
    "Minimal Techno (128-135 BPM)": (128, 135),
    "Classic House (120-128 BPM)": (120, 128),
    "Progressive House (128-132 BPM)": (128, 132),
}

CREATIVE_ELEMENTS = [
    "syncopated rhythm",
    "ghost notes",
    "octave jumps",
    "sliding bass",
    "staccato hits",
    "legato sustains",
    "polyrhythmic elements",
    "swing feel",
    "triplet subdivisions",
    "off-beat accents",
    "velocity automation",
    "filter sweeps",
    "gliding notes",
    "percussive attacks",
    "sub-bass emphasis",
    "harmonic movement",
]

# ---------------------------------------------------------------------------
# Streamlit helpers
# ---------------------------------------------------------------------------


def sanitize_filename(filename: str) -> str:
    """Create a safe filename from user input."""
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    sanitized = "".join(c for c in filename if c in valid_chars)
    return sanitized[:255]


def get_api_key() -> str:
    """Get OpenAI API key from sidebar."""
    api_key = st.sidebar.text_input("🔑 Enter your OpenAI API key:", type="password")
    if "api_key" not in st.session_state or st.session_state["api_key"] != api_key:
        st.session_state["api_key"] = api_key
    return st.session_state["api_key"]


def generate_random_prompt() -> str:
    """Generate a creative random prompt for bassline generation."""
    preset = random.choice(list(ARTIST_PRESETS.keys()))
    mood = random.choice(MOOD_MODIFIERS)
    key = random.choice(KEY_SIGNATURES)
    elements = random.sample(CREATIVE_ELEMENTS, random.randint(2, 4))

    base_prompt = random.choice(ARTIST_PRESETS[preset]["prompts"])

    return (
        f"{base_prompt} Make it {mood} in {key}, incorporating {', '.join(elements)}."
    )


def create_custom_prompt(
    preset: str,
    user_idea: str,
    mood: str,
    key: str,
    tempo_range: str,
    elements: List[str],
) -> str:
    """Build a custom prompt from user selections."""
    base_prompt = random.choice(ARTIST_PRESETS[preset]["prompts"])

    prompt_parts = [base_prompt]

    if user_idea:
        prompt_parts.append(f"User concept: {user_idea}")

    if mood != "Surprise me":
        prompt_parts.append(f"Make it {mood}")

    if key != "Surprise me":
        prompt_parts.append(f"in {key}")

    if tempo_range != "Surprise me":
        tempo_min, tempo_max = TEMPO_RANGES[tempo_range]
        prompt_parts.append(f"targeting {tempo_min}-{tempo_max} BPM feel")

    if elements:
        prompt_parts.append(f"incorporating {', '.join(elements)}")

    return ". ".join(prompt_parts) + "."


def render_generation_controls() -> Tuple[str, str]:
    """Render the main generation controls and return the prompt and mode."""
    st.markdown("### 🎛️ Creative Controls")

    col1, col2 = st.columns([1, 1])

    with col1:
        generation_mode = st.radio(
            "Generation Mode:",
            ["🎯 Preset + Custom", "🎲 Random Magic", "✍️ Manual Prompt"],
            help="Choose how you want to generate your bassline",
        )

    with col2:
        model_choice = st.selectbox(
            "🤖 AI Model:",
            ["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini"],
            index=1,
            help="Choose the OpenAI model for generation",
        )

    if generation_mode == "🎲 Random Magic":
        st.markdown("### ✨ Random Generation")
        st.info("Click 'Generate Bassline' for a completely random creation!")
        if st.button("🎲 Preview Random Prompt", use_container_width=True):
            st.code(generate_random_prompt())
        return generate_random_prompt(), model_choice

    elif generation_mode == "✍️ Manual Prompt":
        st.markdown("### ✍️ Manual Prompt")
        custom_prompt = st.text_area(
            "Enter your custom prompt:",
            placeholder="Describe the bassline you want...",
            height=100,
        )
        return custom_prompt, model_choice

    else:  # Preset + Custom mode
        st.markdown("### 🎯 Preset Builder")

        col1, col2 = st.columns([1, 1])

        with col1:
            preset = st.selectbox(
                "🎨 Artist/Style Preset:",
                list(ARTIST_PRESETS.keys()),
                help="Choose a style preset as your starting point",
            )

            mood = st.selectbox(
                "🌈 Mood:", ["Surprise me"] + MOOD_MODIFIERS, help="Set the overall vibe"
            )

            key = st.selectbox(
                "🎵 Key Signature:",
                ["Surprise me"] + KEY_SIGNATURES,
                help="Choose a musical key",
            )

        with col2:
            tempo_range = st.selectbox(
                "⚡ Tempo Range:",
                ["Surprise me"] + list(TEMPO_RANGES.keys()),
                help="Target tempo range for the bassline",
            )

            elements = st.multiselect(
                "🎛️ Creative Elements:",
                CREATIVE_ELEMENTS,
                help="Add specific musical elements",
            )

            user_idea = st.text_input(
                "💡 Your Creative Idea:",
                placeholder="Optional: Add your own creative twist...",
                help="Describe any specific ideas you want to incorporate",
            )

        # Show preset description
        st.info(f"**{preset}**: {ARTIST_PRESETS[preset]['description']}")

        prompt = create_custom_prompt(
            preset, user_idea, mood, key, tempo_range, elements
        )

        if st.checkbox("👁️ Preview Prompt"):
            st.code(prompt)

        return prompt, model_choice


def display_generation_history():
    """Display previously generated basslines."""
    if "generation_history" not in st.session_state:
        st.session_state.generation_history = []

    if st.session_state.generation_history:
        st.markdown("### 📚 Generation History")

        for i, (title, prompt, midi_data) in enumerate(
            reversed(st.session_state.generation_history[-5:])
        ):
            with st.expander(f"🎵 {title}"):
                st.markdown(f"**Prompt:** {prompt}")

                # Re-create download button for this generation
                midi_bytes = midi_to_bytes(midi_data)
                st.download_button(
                    label=f"📥 Download {title}",
                    data=midi_bytes,
                    file_name=f"{sanitize_filename(title)}.mid",
                    mime="audio/midi",
                    key=f"download_{i}",
                )


def handle_generate_bassline(api_key: str, prompt: str, model: str) -> None:
    """Handle the bassline generation process."""
    if not api_key:
        st.error("🔑 Please provide your OpenAI API key in the sidebar.")
        return

    if not prompt.strip():
        st.error("📝 Please provide a prompt for generation.")
        return

    try:
        with st.spinner("🎵 Generating your bassline..."):
            title, midi_data = request_midi(prompt, api_key=api_key, model=model)

            if not midi_data:
                st.error("❌ No MIDI data generated. Please try again.")
                return

            # Store in history
            if "generation_history" not in st.session_state:
                st.session_state.generation_history = []

            st.session_state.generation_history.append((title, prompt, midi_data))

            # Create download
            midi_bytes = midi_to_bytes(midi_data)

            st.success(f"🎉 Generated: **{title}**")

            col1, col2 = st.columns([1, 1])

            with col1:
                st.download_button(
                    label="📥 Download MIDI File",
                    data=midi_bytes,
                    file_name=f"{sanitize_filename(title)}.mid",
                    mime="audio/midi",
                    use_container_width=True,
                )

            with col2:
                if st.button("🔄 Generate Another", use_container_width=True):
                    st.rerun()

            # Visualize the bassline
            plot_midi(io.BytesIO(midi_bytes))

            # Show MIDI details
            with st.expander("🔍 MIDI Details"):
                st.write(f"**Total Notes:** {len(midi_data)}")
                st.write(
                    f"**Note Range:** {min(note[0] for note in midi_data)} - {max(note[0] for note in midi_data)}"
                )
                st.write(
                    f"**Duration:** {max(note[1] + note[2] for note in midi_data):.1f} beats"
                )

                if len(midi_data) > 0:
                    st.write("**First 5 notes:**")
                    for i, (note, start, duration, velocity) in enumerate(
                        midi_data[:5]
                    ):
                        st.write(
                            f"  {i+1}. {note} at beat {start} for {duration} beats (vel: {velocity})"
                        )

    except Exception as e:
        st.error(f"❌ Error generating bassline: {str(e)}")


def plot_midi(midi_file: io.BytesIO) -> None:
    """Display an enhanced piano roll visualization."""
    midi_file.seek(0)
    mid = MidiFile(file=midi_file)

    notes: List[int] = []
    start_times: List[float] = []
    durations: List[float] = []
    velocities: List[int] = []

    current_time = 0.0
    note_starts = {}  # Track note starts for note_off events

    for msg in mid:
        current_time += msg.time
        if not msg.is_meta and msg.channel == 0:
            if msg.type == "note_on" and msg.velocity > 0:
                note_starts[msg.note] = (current_time, msg.velocity)
            elif msg.type == "note_off" or (
                msg.type == "note_on" and msg.velocity == 0
            ):
                if msg.note in note_starts:
                    start_time, velocity = note_starts[msg.note]
                    notes.append(msg.note)
                    start_times.append(start_time)
                    durations.append(current_time - start_time)
                    velocities.append(velocity)
                    del note_starts[msg.note]

    # Handle any remaining notes that didn't get a note_off
    for note, (start_time, velocity) in note_starts.items():
        notes.append(note)
        start_times.append(start_time)
        durations.append(0.5)  # Default duration
        velocities.append(velocity)

    if not notes:
        st.warning("⚠️ No notes found in MIDI file")
        return

    fig, ax = plt.subplots(figsize=(12, 8))

    # Create color map based on velocity
    norm_velocities = [
        (v - min(velocities)) / (max(velocities) - min(velocities))
        if max(velocities) > min(velocities)
        else 0.5
        for v in velocities
    ]
    colors = plt.cm.plasma(norm_velocities)

    for note, start, duration, color in zip(notes, start_times, durations, colors):
        ax.barh(
            note,
            duration,
            left=start,
            height=0.8,
            color=color,
            alpha=0.8,
            edgecolor="black",
            linewidth=0.5,
        )

    ax.set_ylabel("MIDI Note Number", fontsize=12)
    ax.set_xlabel("Time (beats)", fontsize=12)
    ax.set_title(
        "🎵 Bassline Visualization (Color = Velocity)", fontsize=14, fontweight="bold"
    )
    ax.grid(True, alpha=0.3)

    # Add note names on y-axis
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    if notes:
        min_note, max_note = min(notes), max(notes)
        y_ticks = list(range(min_note, max_note + 1))
        y_labels = [f"{note_names[note % 12]}{note // 12 - 1}" for note in y_ticks]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)

    plt.tight_layout()
    st.pyplot(fig)


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(
        page_title="midiGPT Pro",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Header
    st.markdown(
        """
    # 🎵 midiGPT Pro
    ### Deep House & Minimal Techno Bassline Generator
    *Powered by AI • Inspired by the underground*
    """
    )

    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        api_key = get_api_key()

        st.markdown("---")
        st.markdown("## 🎯 Quick Actions")

        if st.button("🎲 Lucky Dip", use_container_width=True):
            st.session_state.force_random = True
            st.rerun()

        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.generation_history = []
            st.rerun()

        st.markdown("---")
        st.markdown("## 💡 Tips")
        st.markdown(
            """
        - **Try different presets** for various underground styles
        - **Combine elements** for unique sounds  
        - **Use random generation** for inspiration
        - **Save good basslines** to your DAW
        """
        )

    # Main content
    if getattr(st.session_state, "force_random", False):
        prompt = generate_random_prompt()
        model = "gpt-4o-mini"
        st.session_state.force_random = False
        st.markdown(f"### 🎲 Random Generation")
        st.info(f"**Generated prompt:** {prompt}")
    else:
        prompt, model = render_generation_controls()

    # Generate button
    st.markdown("---")
    if st.button("🎵 Generate Bassline", type="primary", use_container_width=True):
        handle_generate_bassline(api_key, prompt, model)

    # Generation history
    st.markdown("---")
    display_generation_history()


if __name__ == "__main__":
    main()

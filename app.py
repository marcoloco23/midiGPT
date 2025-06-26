"""Main Streamlit application for the MIDI generation app."""

import streamlit as st
from dotenv import load_dotenv

from src.session import init_session_state
from src.interfaces import (
    create_layer_interface,
    layer_analysis_interface,
    mix_export_interface,
)

# Load environment variables
load_dotenv()


def main() -> None:
    """Main application entry point."""

    # Configure Streamlit page
    st.set_page_config(
        page_title="🎵 MidiGPT - AI Music Layer Creator",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    init_session_state()

    # Sidebar with app info
    with st.sidebar:
        st.title("🎵 MidiGPT")
        st.markdown("**AI-Powered Music Layer Creator**")

        st.markdown("---")
        st.markdown("### 🎯 Features")
        st.markdown(
            """
        - **Artist-Inspired Presets** - Generate music in the style of your favorite artists
        - **Layer System** - Build tracks layer by layer with basslines, melodies, chords, and more
        - **Creative Controls** - Fine-tune energy, focus, style, and intensity
        - **Real-time Analysis** - Visualize and analyze your MIDI layers
        - **Professional Export** - Download individual layers or complete mixes
        """
        )

        st.markdown("---")
        st.markdown("### 🎛️ Quick Stats")
        if st.session_state.layers:
            total_layers = len(st.session_state.layers)
            active_layers = len([l for l in st.session_state.layers if not l["muted"]])
            st.metric("Total Layers", total_layers)
            st.metric("Active Layers", active_layers)
        else:
            st.info("No layers created yet")

        st.markdown("---")
        st.markdown("### ℹ️ How to Use")
        st.markdown(
            """
        1. **Select** an artist preset and layer type
        2. **Customize** with creative controls
        3. **Generate** your MIDI layer
        4. **Repeat** to build up your track
        5. **Mix & Export** your final composition
        """
        )

    # Main content area
    st.title("🎵 MidiGPT - AI Music Layer Creator")
    st.markdown(
        "*Create professional MIDI layers with AI-powered generation based on artist styles*"
    )

    # Main interface tabs
    tab1, tab2, tab3 = st.tabs(
        ["🎼 Create Layer", "🎛️ Layer Management", "🎚️ Mix & Export"]
    )

    with tab1:
        create_layer_interface()

    with tab2:
        layer_analysis_interface()

    with tab3:
        mix_export_interface()

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
            "🎵 MidiGPT - Professional AI Music Generation | Built with Streamlit & OpenAI"
            "</div>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()

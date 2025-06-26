"""Streamlit interface components for the MIDI generation app."""

import random
from typing import List, Optional

import streamlit as st
from mido import MidiFile

from .core import request_midi, midi_to_bytes, combine_midi_layers
from .presets import ARTIST_PRESETS, LAYER_TYPES, CREATIVE_CONTROLS
from .session import (
    add_layer,
    remove_layer,
    get_layers_by_type,
    toggle_layer_mute,
    toggle_layer_solo,
    get_active_layers,
    clear_all_layers,
)
from .visualization import (
    plot_midi_layers,
    plot_single_layer_analysis,
    create_velocity_heatmap,
)
from .audio import create_layer_preview, create_mix_preview


def create_layer_interface() -> None:
    """Create the main layer creation interface."""

    st.header("🎵 Create New Layer")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎨 Artist Preset")

        # Artist selection
        selected_artist = st.selectbox(
            "Select Artist Style:",
            options=list(ARTIST_PRESETS.keys()),
            index=0,
            help="Choose an artist whose style will influence the generated MIDI",
        )

        if selected_artist:
            preset = ARTIST_PRESETS[selected_artist]
            st.info(f"**Style:** {preset['description']}")

        # Layer type selection
        layer_type = st.selectbox(
            "Layer Type:",
            options=list(LAYER_TYPES.keys()),
            index=0,
            help="Select the type of musical layer to generate",
        )

        layer_info = LAYER_TYPES[layer_type]
        st.caption(f"{layer_info['icon']} {layer_info['description']}")

    with col2:
        st.subheader("🎛️ Creative Controls")

        # Creative controls
        controls = {}
        for control_name, control_info in CREATIVE_CONTROLS.items():
            controls[control_name] = st.selectbox(
                control_name,
                options=control_info["options"],
                index=control_info["options"].index(control_info["default"]),
                help=control_info["description"],
            )

    # Custom prompt option
    with st.expander("✍️ Custom Prompt (Optional)"):
        custom_prompt = st.text_area(
            "Enter custom prompt:",
            placeholder="Describe the specific musical style or characteristics you want...",
            help="This will override the preset prompts if provided",
        )

    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎼 Generate Layer", type="primary", use_container_width=True):
            with st.spinner("🎵 Generating MIDI layer..."):
                try:
                    # Build prompt
                    if custom_prompt.strip():
                        prompt = custom_prompt.strip()
                    else:
                        # Get appropriate prompt from preset
                        layer_key = (
                            layer_type.split(" ", 1)[1].lower()
                            if " " in layer_type
                            else "bassline"
                        )
                        if layer_key in preset["prompts"]:
                            prompt = random.choice(preset["prompts"][layer_key])
                        else:
                            prompt = random.choice(preset["prompts"]["bassline"])

                    # Add creative controls to prompt
                    control_additions = []
                    for control_name, value in controls.items():
                        if value != CREATIVE_CONTROLS[control_name]["default"]:
                            control_additions.append(
                                f"{control_name.split(' ', 1)[1].lower()}: {value.lower()}"
                            )

                    if control_additions:
                        prompt += f" Style modifiers: {', '.join(control_additions)}."

                    # Generate MIDI
                    existing_layers = get_active_layers()
                    title, midi_data = request_midi(
                        prompt,
                        layer_type=layer_type.split(" ", 1)[1].lower()
                        if " " in layer_type
                        else "bassline",
                        existing_layers=existing_layers,
                    )

                    # Add to session
                    add_layer(layer_type, title, midi_data)

                    st.success(f"✅ Generated: **{title}**")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Generation failed: {str(e)}")


def layer_analysis_interface() -> None:
    """Display layer analysis and management interface."""

    if not st.session_state.layers:
        st.info(
            "🎵 No layers created yet. Use the interface above to generate your first layer!"
        )
        return

    st.header("🎛️ Layer Management")

    # Global controls
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔇 Mute All", use_container_width=True):
            for layer in st.session_state.layers:
                layer["muted"] = True
            st.rerun()

    with col2:
        if st.button("🔊 Unmute All", use_container_width=True):
            for layer in st.session_state.layers:
                layer["muted"] = False
            st.rerun()

    with col3:
        if st.button("🎯 Clear Solo", use_container_width=True):
            for layer in st.session_state.layers:
                layer["solo"] = False
            st.rerun()

    with col4:
        if st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
            if st.session_state.get("confirm_clear", False):
                clear_all_layers()
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm deletion of all layers")

    # Layer list
    st.subheader("📋 Active Layers")

    for layer in st.session_state.layers:
        with st.container():
            col1, col2, col3, col4, col5, col6, col7 = st.columns(
                [2.5, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8]
            )

            with col1:
                # Layer info with color indicator
                layer_color = LAYER_TYPES.get(layer["type"], {}).get("color", "#888888")
                status_icon = "🔇" if layer["muted"] else ("🎯" if layer["solo"] else "🔊")

                st.markdown(
                    f"""
                    <div style="
                        padding: 8px; 
                        border-left: 4px solid {layer_color}; 
                        background-color: rgba(0,0,0,0.1);
                        border-radius: 4px;
                    ">
                        {status_icon} <strong>{layer['title']}</strong><br/>
                        <small>{layer['type']} • {layer['analysis']['note_count']} notes • 
                        {layer['analysis']['total_duration']:.1f} beats</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                if st.button(
                    "🔇",
                    key=f"mute_{layer['id']}",
                    help="Toggle mute",
                    use_container_width=True,
                ):
                    toggle_layer_mute(layer["id"])
                    st.rerun()

            with col3:
                if st.button(
                    "🎯",
                    key=f"solo_{layer['id']}",
                    help="Toggle solo",
                    use_container_width=True,
                ):
                    toggle_layer_solo(layer["id"])
                    st.rerun()

            with col4:
                # Download individual layer
                midi_bytes = midi_to_bytes(layer["midi_data"])
                st.download_button(
                    "💾",
                    data=midi_bytes,
                    file_name=f"{layer['title']}.mid",
                    mime="audio/midi",
                    key=f"download_{layer['id']}",
                    help="Download layer",
                    use_container_width=True,
                )

            with col5:
                # Show analysis
                if st.button(
                    "📊",
                    key=f"analyze_{layer['id']}",
                    help="Show analysis",
                    use_container_width=True,
                ):
                    st.session_state[
                        f'show_analysis_{layer["id"]}'
                    ] = not st.session_state.get(f'show_analysis_{layer["id"]}', False)
                    st.rerun()

            with col6:
                # Audio preview
                if st.button(
                    "🔊",
                    key=f"preview_{layer['id']}",
                    help="Preview audio",
                    use_container_width=True,
                ):
                    with st.spinner("🎵 Generating audio..."):
                        try:
                            audio_bytes = create_layer_preview(
                                layer["midi_data"],
                                layer_type=layer["type"],
                                duration_limit=15.0,  # Limit to 15 seconds for preview
                            )
                            st.audio(audio_bytes, format="audio/wav")
                        except Exception as e:
                            st.error(f"Audio generation failed: {e}")

            with col7:
                if st.button(
                    "🗑️",
                    key=f"delete_{layer['id']}",
                    help="Delete layer",
                    use_container_width=True,
                ):
                    remove_layer(layer["id"])
                    st.rerun()

            # Show detailed analysis if requested
            if st.session_state.get(f'show_analysis_{layer["id"]}', False):
                st.markdown("---")

                analysis = layer["analysis"]

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Notes", analysis["note_count"])
                with col2:
                    st.metric("Duration", f"{analysis['total_duration']:.1f} beats")
                with col3:
                    st.metric("Avg Velocity", f"{analysis['avg_velocity']:.0f}")
                with col4:
                    st.metric("Pitch Range", f"{analysis['pitch_range']:.1f}")

                # Individual layer plot
                fig = plot_single_layer_analysis(layer)
                st.pyplot(fig)

            st.markdown("---")


def mix_export_interface() -> None:
    """Interface for mixing and exporting the complete track."""

    if not st.session_state.layers:
        return

    st.header("🎚️ Mix & Export")

    # Visualization options
    viz_option = st.selectbox(
        "📊 Visualization:", ["Layer Overview", "Velocity Heatmap", "None"], index=0
    )

    if viz_option != "None":
        active_layers = get_active_layers()

        if viz_option == "Layer Overview":
            if active_layers:
                fig = plot_midi_layers(active_layers, width=14, height=8)
                st.pyplot(fig)
            else:
                st.info("🔇 All layers are muted")

        elif viz_option == "Velocity Heatmap":
            if active_layers:
                fig = create_velocity_heatmap(active_layers, width=14, height=6)
                st.pyplot(fig)
            else:
                st.info("🔇 All layers are muted")

    # Audio Preview Section
    st.subheader("🔊 Audio Preview")

    col1, col2 = st.columns(2)

    with col1:
        # Preview mix of active layers
        active_layers = get_active_layers()
        if active_layers:
            if st.button(
                "🎵 Preview Mix (Active Layers)",
                use_container_width=True,
                type="primary",
            ):
                with st.spinner("🎵 Generating mix audio..."):
                    try:
                        audio_bytes = create_mix_preview(
                            active_layers,
                            duration_limit=20.0,  # Limit to 20 seconds for mix preview
                        )
                        st.audio(audio_bytes, format="audio/wav")
                        st.success(
                            f"🎧 Playing mix of {len(active_layers)} active layers"
                        )
                    except Exception as e:
                        st.error(f"Mix audio generation failed: {e}")
        else:
            st.info("🔇 No active layers to preview")

    with col2:
        # Preview all layers
        if st.session_state.layers:
            if st.button("🎼 Preview All Layers", use_container_width=True):
                with st.spinner("🎵 Generating full mix audio..."):
                    try:
                        # Temporarily unmute all for full preview
                        all_layers = [
                            dict(layer, muted=False)
                            for layer in st.session_state.layers
                        ]
                        audio_bytes = create_mix_preview(
                            all_layers, duration_limit=20.0
                        )
                        st.audio(audio_bytes, format="audio/wav")
                        st.success(
                            f"🎧 Playing mix of all {len(st.session_state.layers)} layers"
                        )
                    except Exception as e:
                        st.error(f"Full mix audio generation failed: {e}")

    # Export options
    st.subheader("💾 Export Options")

    col1, col2 = st.columns(2)

    with col1:
        # Export active layers
        active_layers = get_active_layers()
        if active_layers:
            combined_midi = combine_midi_layers(active_layers)
            combined_bytes = midi_to_bytes(combined_midi)

            st.download_button(
                "🎼 Download Mix (Active Layers)",
                data=combined_bytes,
                file_name="midi_mix.mid",
                mime="audio/midi",
                type="primary",
                use_container_width=True,
                help=f"Download combined MIDI with {len(active_layers)} active layers",
            )
        else:
            st.info("🔇 No active layers to export")

    with col2:
        # Export all layers
        if st.session_state.layers:
            all_midi = combine_midi_layers(st.session_state.layers)
            all_bytes = midi_to_bytes(all_midi)

            st.download_button(
                "📁 Download All Layers",
                data=all_bytes,
                file_name="midi_all_layers.mid",
                mime="audio/midi",
                use_container_width=True,
                help=f"Download all {len(st.session_state.layers)} layers combined",
            )

    # Layer statistics
    if st.session_state.layers:
        st.subheader("📈 Mix Statistics")

        total_layers = len(st.session_state.layers)
        active_layers = get_active_layers()
        muted_layers = [l for l in st.session_state.layers if l["muted"]]
        solo_layers = [l for l in st.session_state.layers if l["solo"]]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Layers", total_layers)
        with col2:
            st.metric("Active Layers", len(active_layers))
        with col3:
            st.metric("Muted Layers", len(muted_layers))
        with col4:
            st.metric("Solo Layers", len(solo_layers))

        # Layer type breakdown
        layer_types = {}
        for layer in st.session_state.layers:
            layer_type = layer["type"]
            if layer_type not in layer_types:
                layer_types[layer_type] = 0
            layer_types[layer_type] += 1

        if layer_types:
            st.markdown("**Layer Types:**")
            type_text = " • ".join(
                [
                    f"{LAYER_TYPES.get(lt, {}).get('icon', '🎵')} {lt}: {count}"
                    for lt, count in layer_types.items()
                ]
            )
            st.markdown(type_text)

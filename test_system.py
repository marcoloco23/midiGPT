from pathlib import Path
import tempfile

from src.core import request_midi, generate_midi_file

SAMPLE_PROMPT = "Groovy minimal house bassline in C minor with syncopation"


def main() -> None:
    # Retrieve MIDI data using the same function as CLI
    midi_data = request_midi(SAMPLE_PROMPT)

    if not midi_data:
        raise RuntimeError("Model returned no notes. Test failed.")

    print(f"Received {len(midi_data)} notes from the model. First 5: {midi_data[:5]}")

    # Write to a temporary file to ensure generation works
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "test.mid"
        generate_midi_file(midi_data, out_path)
        assert (
            out_path.exists() and out_path.stat().st_size > 0
        ), "MIDI file not created"
        print(
            f"✅ Temporary MIDI file created at {out_path} ({out_path.stat().st_size} bytes)"
        )


if __name__ == "__main__":
    main()

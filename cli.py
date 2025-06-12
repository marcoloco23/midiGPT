import argparse
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.core import generate_midi_file, request_midi


def _slugify(text: str) -> str:
    """Return a filesystem-safe slug derived from *text*."""

    slug = re.sub(r"[^a-zA-Z0-9\-]+", "_", text.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "untitled"


def _next_available_path(base: Path) -> Path:
    """Append numeric suffixes until *base* is free, returning the path."""

    if not base.exists():
        return base
    stem, suffix = base.stem, base.suffix
    counter = 1
    while True:
        candidate = base.with_name(f"{stem}_{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def _run_once(prompt: str, model: str, out_dir: Path) -> None:
    """Generate a bassline for *prompt* and write a MIDI file to *out_dir*."""

    title, midi_data = request_midi(prompt=prompt, model=model)
    filename = _slugify(title) + ".mid"
    output_path = _next_available_path(out_dir / filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generate_midi_file(midi_data, output_path)
    print(f"✅ '{title}' saved to {output_path}")


def main() -> None:
    """Interactive CLI for generating basslines via OpenAI."""

    parser = argparse.ArgumentParser(description="Interactive bassline generator")
    parser.add_argument(
        "--model",
        default="o3-mini",
        help="OpenAI model name (default: o3-mini)",
    )
    parser.add_argument(
        "--out-dir",
        default="midi",
        help="Directory where generated .mid files are stored (default: midi)",
    )
    parser.add_argument(
        "prompt",
        nargs=argparse.REMAINDER,
        help="Optional one-off prompt. If supplied, the tool will generate once and exit.",
    )
    args = parser.parse_args()

    load_dotenv()

    out_dir = Path(args.out_dir).expanduser().resolve()

    # One-off mode if prompt words were supplied on the command-line.
    if args.prompt:
        _run_once(" ".join(args.prompt), args.model, out_dir)
        return

    # Interactive REPL mode.
    print(
        "\n🎹 Bassline Generator REPL — type a prompt and press Enter (quit/q to exit)\n"
    )
    try:
        while True:
            try:
                prompt = input("prompt> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if prompt.lower() in {"", "q", "quit", "exit"}:
                break

            try:
                _run_once(prompt, args.model, out_dir)
            except Exception as exc:  # noqa: BLE001
                print(f"❌ Error: {exc}", file=sys.stderr)

    finally:
        print("Goodbye! 👋")


if __name__ == "__main__":
    main()

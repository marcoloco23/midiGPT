# midiGPT

Generate deep minimal house basslines powered by the latest OpenAI models.

## Prerequisites

1. Python 3.9+
2. Create and activate a virtual environment (optional but recommended)
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Streamlit Web App

```bash
streamlit run app.py
```

Enter your OpenAI API key in the sidebar, provide a creative prompt, and click **Generate MIDI**.  
The app will stream the model output, convert it into a `.mid` file, and render a piano-roll preview. You can download the MIDI directly from the interface.

## CLI Usage

```bash
export OPENAI_API_KEY="sk-..."

python cli.py "Funky minimal-house bassline in A minor with syncopated groove" \
              --output my_bassline.mid \
              --model gpt-4o-mini
```

The script will save `my_bassline.mid` in the current directory.

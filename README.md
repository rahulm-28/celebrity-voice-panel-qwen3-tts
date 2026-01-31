# Celebrity Voice Panel

> AI-Generated Tech Discussions with Famous Voices using Qwen3-TTS

![Demo](assets/demo.gif)

## What is this?

Ever wondered what it would sound like if Modi, Amitabh Bachchan, SRK, Jethalal, Morgan Freeman, and Trump had a tech discussion together?

This project uses **Qwen3-TTS** - an open-source voice cloning model - to create hilarious and viral-worthy audio panels where famous personalities discuss any topic you choose!

## Demo

**Topic: "Artificial Intelligence"**

> **Modi**: "Mitron, Artificial Intelligence humara Digital India ka naya adhyay hai."
>
> **Amitabh**: "Artificial Intelligence... yeh aapka final answer hai?"
>
> **SRK**: "Don't underestimate the power of ek chhota sa neural network"
>
> **Jethalal**: "Ae ma mataji! Machine bhi seekh rahi hai?!"
>
> **Morgan Freeman**: "And so, the machines learned to think... one epoch at a time."
>
> **Trump**: "This AI, let me tell you, it's tremendous. The best."

## Quick Start

### Prerequisites

- Python 3.10+
- CUDA-capable GPU (8GB+ VRAM recommended)
- 3-10 second voice samples for each celebrity

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/celebrity-voice-panel.git
cd celebrity-voice-panel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install Flash Attention for faster inference
pip install flash-attn --no-build-isolation
```

### Add Voice Samples

Place 3-10 second `.wav` files in `voices/samples/`:

```
voices/samples/
├── modi.wav
├── amitabh.wav
├── srk.wav
├── jethalal.wav
├── morgan_freeman.wav
└── trump.wav
```

### Run the App

```bash
# Web interface
python app.py

# Or use CLI
python cli.py panel "JavaScript" --characters modi srk jethalal
python cli.py single modi "Mitron, coding seekhiye"
```

## Project Structure

```
celebrity-voice-panel/
├── app.py                  # Gradio web interface
├── cli.py                  # Command-line tool
├── config.py               # Configuration
├── scripts/
│   ├── voice_cloner.py     # Qwen3-TTS wrapper
│   ├── script_generator.py # Dialogue generation
│   └── audio_stitcher.py   # Audio combining
├── prompts/
│   └── character_prompts.json
├── voices/samples/         # Your voice samples
└── outputs/generated/      # Generated audio
```

## Configuration

Edit `config.py` or use environment variables:

```bash
export MODEL_NAME="Qwen/Qwen3-TTS-12Hz-1.7B-Base"
export DEVICE="cuda:0"
```

## Use Cases

- **LinkedIn Content**: Create viral tech commentary
- **YouTube Shorts**: Celebrity reactions to tech news
- **Podcasts**: Multi-voice intro/outros
- **Education**: Make learning fun with famous voices

## Disclaimer

**This is a technology demonstration for educational purposes only.**

- All voices are AI-generated
- Not affiliated with any celebrities
- Do not use to spread misinformation
- Respect intellectual property rights
- Add clear "AI Generated" labels when sharing

## Tech Stack

- **Model**: [Qwen3-TTS-12Hz-1.7B](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base)
- **Framework**: Gradio
- **Audio**: soundfile, numpy

## License

MIT License - See [LICENSE](LICENSE) for details.

## Credits

- [Qwen Team (Alibaba Cloud)](https://github.com/QwenLM/Qwen3-TTS) for the amazing TTS model
- Voice samples sourced from public domain recordings

## Contributing

PRs welcome! Please read contributing guidelines first.

---

**Made with care by [Rahul Mittal](https://linkedin.com/in/rahulm28)**

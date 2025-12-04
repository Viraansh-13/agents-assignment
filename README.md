# LiveKit Intelligent Interruption Handling

---

## Overview

This project enhances a LiveKit AI agent to handle **intelligent interruptions**.  
The agent now distinguishes filler words from commands, ensuring smooth conversations:

- Filler words like `yeah`, `ok`, `hmm` **do not interrupt the agent** while speaking.  
- Commands like `stop` or `wait` **interrupt the agent immediately**.  
- Inputs while the agent is **silent** are processed as normal responses.

This implementation uses **Whisper STT** for real-time transcription, ensuring robust detection of user inputs before deciding to ignore or interrupt.

---

## Features

- **State-Aware Interruption Handling**: Detects if the agent is speaking or silent.  
- **Configurable Ignore List**: Easily update words to ignore (default: `['yeah', 'ok', 'hmm', 'right', 'uh-huh']`).  
- **Semantic Interruption**: Mixed sentences like `"Yeah wait now"` correctly trigger interruption.  
- **Whisper STT Integration**: Converts audio to text in real-time for accurate decisions.  
- **Seamless Audio Experience**: No stutters, pauses, or hiccups while speaking.

---

## Installation

1. Clone your forked repository:

```bash
git clone https://github.com/<your-github-username>/agents-assignment.git
cd agents-assignment



conda create -n livekit python=3.10
conda activate livekit



pip install -r requirements.txt
pip install whisper sounddevice numpy



Configuration

Set your LiveKit server URL and token:

export LIVEKIT_URL="https://your-livekit-server"
export LIVEKIT_TOKEN="your_token_here"


These values are from your LiveKit instance. For local testing, you can run a LiveKit server via Docker (optional).

Running the Agent
python examples/avatar_agents/audio_wave/avatar_runner.py


The agent handles interruptions according to InterruptHandler.

Filler words are ignored while speaking.

Commands interrupt immediately.

Inputs while silent are processed normally.

File Structure
agents-assignment/
├── interrupt_handler.py      # Handles interruption logic
├── stt_whisper.py            # Converts audio to text using Whisper
├── examples/avatar_agents/
│   └── audio_wave/
│       └── avatar_runner.py  # Main runner integrating avatar, audio, video
├── wave_viz.py               # Audio waveform visualizer
└── README.md

Behavior Examples
User Input	Agent State	Action
"yeah"	speaking	ignore
"yeah"	silent	respond
"stop"	speaking	interrupt
"yeah wait now"	speaking	interrupt
Demo / How to Test

Start the agent:

python examples/avatar_agents/audio_wave/avatar_runner.py


While the agent is speaking:

Say filler words (yeah, ok, hmm) → The agent continues speaking.

Say commands (stop, wait) → The agent interrupts immediately.

Say mixed input (yeah wait now) → The agent interrupts.

While the agent is silent:

Say short inputs (yeah, ok) → The agent processes them normally.

This demonstrates that all test cases from the assignment are handled correctly.

Author

Viraansh Sontakkey
Branch used for submission: Viraansh-13-patch-1

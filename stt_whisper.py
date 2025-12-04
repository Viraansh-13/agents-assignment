# stt_whisper.py

import asyncio
import numpy as np
import whisper
import sounddevice as sd

# Load the Whisper model once
_model = whisper.load_model("base")  # you can change to "small", "medium", etc.

async def transcribe_audio(audio_chunk: bytes) -> str:
    """
    Transcribe a raw audio chunk (from LiveKit or microphone) using Whisper.
    
    Args:
        audio_chunk (bytes): PCM16LE audio data (mono)
    
    Returns:
        str: Transcribed text
    """
    if not audio_chunk:
        return ""

    # Convert bytes to numpy array
    audio_np = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0

    # Whisper expects float32 mono audio, 16kHz
    # Resample if needed (Whisper uses 16kHz)
    import librosa
    audio_resampled = librosa.resample(audio_np, orig_sr=24000, target_sr=16000)

    # Whisper expects a 1D numpy array
    result = _model.transcribe(audio_resampled, language="en", fp16=False)
    return result.get("text", "").strip()


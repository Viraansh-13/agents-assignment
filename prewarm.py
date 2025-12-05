# prewarm.py
from livekit.plugins import silero
from livekit.agents import JobProcess


def prewarm(proc: JobProcess):
    """Pre-warm resources for the process (load VAD, etc.)."""
    proc.userdata["vad"] = silero.VAD.load()

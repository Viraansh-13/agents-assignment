# config.py
"""Configuration for interrupt logic. Loadable / overridable via env if needed."""
import os
import re
from typing import Set

# default ignore words (backchannels / filler)
_DEFAULT_IGNORE = {
    "yeah", "yep", "yup", "ok", "okay", "uh-huh", "uhuh", "hmm", "mm-hmm",
    "mm", "mhm", "right", "sure", "y", "yah", "mmhm",
}

# default interrupt words (should immediately interrupt when spoken)
_DEFAULT_INTERRUPT = {
    "stop", "wait", "no", "pause", "hold", "enough", "actually", "stop now"
}

# decision timeout in seconds: how long to wait for partial STT to decide
_DEFAULT_DECISION_TIMEOUT = float(os.getenv("DECISION_TIMEOUT", "0.35"))

# tokenizer regex (keeps alphanumeric + apostrophes)
_WORD_RE = re.compile(r"[A-Za-z0-9']+")


def get_ignore_words() -> Set[str]:
    # could extend to load from env or a JSON file
    return _DEFAULT_IGNORE.copy()


def get_interrupt_words() -> Set[str]:
    return _DEFAULT_INTERRUPT.copy()


def get_decision_timeout() -> float:
    return _DEFAULT_DECISION_TIMEOUT


def get_word_re():
    return _WORD_RE

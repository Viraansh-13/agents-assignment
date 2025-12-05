# tokenizer.py
from typing import List
from .config import get_word_re


def tokenize_text(text: str) -> List[str]:
    """Return lowercase word tokens from a text string."""
    return get_word_re().findall((text or "").lower())

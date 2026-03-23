import pytest
import json
import os

@pytest.fixture
def sample_sandhi_rules():
    return [
        {"pattern": "a + i", "replacement": "e", "description": "Guna Sandhi example"},
        {"pattern": "a + u", "replacement": "o", "description": "Guna Sandhi example"}
    ]

@pytest.fixture
def sample_linguistic_output():
    return {
        "original_text": "Sample text",
        "tokens": ["Sample", "text"],
        "sandhi_applied": False,
        "phonemes": ["s", "ae", "m", "p", "l"],
        "metadata": {}
    }

# --- SECTION FOR DEV 1 FIXTURES ---
# Dev 1: Add your fixtures below this line

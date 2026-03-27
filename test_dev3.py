"""Test script for dev3 audio wrapper"""

from backend.audio.dev3 import generate_audio

test = {
    "f0": [220, 240],
    "durations": [200, 300],
    "raga": "test"
}

print(generate_audio(test))

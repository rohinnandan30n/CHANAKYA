from backend.melodic.dev2 import apply_melody

test = {
    "syllables": ["ra", "ma"],
    "weights": ["L", "G"],
    "chanda": "test"
}

print(apply_melody(test))

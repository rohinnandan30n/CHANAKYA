"""
config.py

Configuration and environment module for the Svara-Chanda melodic backend.
Resolves, loads, and validates Vedic accent rules and Raga definitions.
"""

import json
import logging
import jsonschema
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

VEDIC_ACCENT_RULES_PATH = DATA_DIR / "vedic_accent_rules.json"
RAGA_DEFINITIONS_PATH = DATA_DIR / "raga_definitions.json"

ACCENT_RULES_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "type": "object"
    }
}

RAGA_DEFS_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "type": "object",
        "required": ["arohana", "avarohana", "vadi", "samvadi", "notes"]
    }
}

def _load_and_validate_json(file_path: Path, schema: dict) -> dict:
    if not file_path.exists():
        logger.error(f"Configuration file missing: {file_path}")
        raise FileNotFoundError(f"Missing required configuration file: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        logger.error(f"Invalid JSON in {file_path}: {error}")
        raise ValueError(f"Failed to parse JSON in {file_path}: {error}") from error

    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as error:
        logger.error(f"Schema validation failed for {file_path}: {error.message}")
        raise ValueError(f"Schema validation failed for {file_path}: {error.message}") from error

    logger.info(f"Successfully loaded and validated {file_path.name}")
    return data


ACCENT_RULES: dict = _load_and_validate_json(VEDIC_ACCENT_RULES_PATH, ACCENT_RULES_SCHEMA)
RAGA_DEFS: dict = _load_and_validate_json(RAGA_DEFINITIONS_PATH, RAGA_DEFS_SCHEMA)


def get_accent_rule(context: str) -> dict:
    if context not in ACCENT_RULES:
        logger.error(f"Unknown accent context lookup: '{context}'")
        raise KeyError(f"Accent rule not found for context: '{context}'")
    return ACCENT_RULES[context]


def get_raga(name: str) -> dict:
    if name not in RAGA_DEFS:
        logger.error(f"Unknown raga lookup: '{name}'")
        raise KeyError(f"Raga definition not found for name: '{name}'")
    return RAGA_DEFS[name]


if __name__ == "__main__":
    print("Svara-Chanda Melodic Environment Configuration")
    print("-" * 45)
    print(f"Loaded Accent Rules Count: {len(ACCENT_RULES)}")
    print(f"Loaded Ragas Count: {len(RAGA_DEFS)}")
    if RAGA_DEFS:
        print(f"Available Ragas: {list(RAGA_DEFS.keys())}")

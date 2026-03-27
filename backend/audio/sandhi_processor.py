"""
sandhi_processor.py - Dev 3: Neural Audio Engineer
Applies Sanskrit sandhi rules to SLP1 token list before phonemisation.
Reads sandhi_rules.json (created by Dev 1) - READ ONLY, never edit.
"""

import json
import logging
from typing import List

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def load_sandhi_rules(rules_path: str = "sandhi_rules.json") -> list:
    """Load sandhi rules from JSON file created by Dev 1."""
    with open(rules_path, "r", encoding="utf-8") as f:
        rules = json.load(f)
    logger.debug(f"Loaded {len(rules)} sandhi rules from {rules_path}")
    return rules


def apply_sandhi(tokens: List[str], rules: list = None) -> str:
    """
    Apply Sanskrit sandhi rules to SLP1 token list.

    Args:
        tokens: List of SLP1 tokens (words)
        rules: Loaded from sandhi_rules.json

    Returns:
        Single SLP1 string with sandhi applied
    """
    if rules is None:
        try:
            rules = load_sandhi_rules()
        except Exception:
            rules = []
    if not tokens:
        return ""

    result = list(tokens)

    for i in range(len(result) - 1):
        word = result[i]
        next_word = result[i + 1]

        if not word or not next_word:
            continue

        last_char = word[-1]
        first_char = next_word[0]

        for rule in rules:
            pattern = rule.get("pattern", "")
            replacement = rule.get("replacement", "")
            description = rule.get("description", "")

            if "+" in pattern:
                parts = pattern.split("+")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()

                    left_chars = [c.strip() for c in left.split("/")]
                    right_chars = [c.strip() for c in right.split("/")]

                    if last_char in left_chars and first_char in right_chars:
                        logger.debug(
                            f"Applying rule: {description} | "
                            f"'{word}' + '{next_word}' -> replacing '{last_char}+{first_char}' with '{replacement}'"
                        )
                        result[i] = word[:-1]
                        result[i + 1] = replacement + next_word[1:]
                        break

    final = "".join(result)
    logger.debug(f"Sandhi result: {tokens} -> '{final}'")
    return final


def apply_internal_sandhi(token: str, rules: list) -> str:
    """
    Apply internal sandhi corrections within a single word.

    Args:
        token: Single SLP1 word
        rules: Loaded from sandhi_rules.json

    Returns:
        SLP1 string with internal sandhi applied
    """
    if not token:
        return token

    result = token
    for rule in rules:
        pattern = rule.get("pattern", "")
        replacement = rule.get("replacement", "")
        description = rule.get("description", "")

        if "+" in pattern:
            parts = pattern.split("+")
            if len(parts) == 2:
                left = parts[0].strip().split("/")
                right = parts[1].strip().split("/")

                for l in left:
                    for r in right:
                        combo = l.strip() + r.strip()
                        if combo in result:
                            result = result.replace(combo, replacement, 1)
                            logger.debug(
                                f"Internal sandhi: {description} | '{combo}' -> '{replacement}'"
                            )

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python sandhi_processor.py 'word1 word2 word3'")
        sys.exit(1)

    input_text = sys.argv[1]
    tokens = input_text.strip().split()

    try:
        rules = load_sandhi_rules()
        result = apply_sandhi(tokens, rules)
        print(f"Input:  {tokens}")
        print(f"Output: {result}")
    except FileNotFoundError:
        print("Error: sandhi_rules.json not found. Make sure Dev 1's file is present.")
        sys.exit(1)
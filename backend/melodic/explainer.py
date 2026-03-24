"""
explainer.py

Melodic explanation generator for Svara-Chanda pipeline.

Generates human-readable explanations of melodic choices based on raga rules,
Vedic accent patterns, and metrical constraints.
"""

import os
import json
from typing import Dict, List
from pathlib import Path


def load_xai_templates() -> Dict[str, str]:
    """
    Load explanation templates from xai_prompts.txt.
    
    File format: KEY:\ntemplate_text\n\nKEY2:\ntemplate_text2\n\n...
    
    Returns:
        Dict[str, str]: Template dictionary {key: template_string}
    """
    templates = {}
    
    # Try multiple possible paths
    possible_paths = [
        Path(__file__).resolve().parent.parent / "data" / "xai_prompts.txt",
        Path.cwd() / "backend" / "data" / "xai_prompts.txt",
        "backend/data/xai_prompts.txt",
    ]
    
    template_file = None
    for path in possible_paths:
        if isinstance(path, str):
            path = Path(path)
        if path.exists():
            template_file = path
            break
    
    if not template_file:
        return _get_default_templates()
    
    try:
        with open(template_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse template blocks: KEY:\ntext\n\n
        blocks = content.split("\n\n")
        for block in blocks:
            block = block.strip()
            if not block or ":" not in block:
                continue
            
            lines = block.split("\n", 1)
            key = lines[0].rstrip(":")
            value = lines[1] if len(lines) > 1 else ""
            templates[key.strip()] = value.strip()
        
        return templates
    
    except Exception:
        return _get_default_templates()


def _get_default_templates() -> Dict[str, str]:
    """Fallback templates if file cannot be loaded."""
    return {
        "RAGA_INTRO": "The raga '{raga_name}' is a classical Indian musical framework.",
        "VADI_SAMVADI": "Primary note (vadi): {vadi}, Secondary note (samvadi): {samvadi}",
        "AROHANA_DESC": "Ascending notes (arohana): {arohana}",
        "AVAROHANA_DESC": "Descending notes (avarohana): {avarohana}",
        "CONTOUR_SUMMARY": "Pitch range: {min_freq:.1f}–{max_freq:.1f} Hz, Average: {avg_freq:.1f} Hz",
        "RULES_APPLIED": "Rules applied: {rules_list}",
        "CLOSING": "This explains the melodic transformation following raga principles.",
    }


def _compute_contour_stats(f0_data: List[Dict]) -> Dict[str, float]:
    """
    Compute summary statistics for pitch contour.
    
    Args:
        f0_data (List[Dict]): List with "f0_hz" field
        
    Returns:
        Dict with min_freq, max_freq, avg_freq
    """
    if not f0_data:
        return {"min_freq": 0, "max_freq": 0, "avg_freq": 0}
    
    frequencies = [item.get("f0_hz", 0) for item in f0_data]
    frequencies = [f for f in frequencies if f > 0]
    
    if not frequencies:
        return {"min_freq": 0, "max_freq": 0, "avg_freq": 0}
    
    return {
        "min_freq": min(frequencies),
        "max_freq": max(frequencies),
        "avg_freq": sum(frequencies) / len(frequencies),
    }


def _format_rules_list(rules: List[str]) -> str:
    """Format rules list as bullet points."""
    if not rules:
        return "No rules applied"
    return "\n".join(f"  • {rule}" for rule in rules)


def explain_melodic_choice(
    raga: Dict,
    f0_data: List[Dict]
) -> Dict:
    """
    Generate explanation for melodic choices.
    
    Args:
        raga (Dict): Raga definition with name, arohana, avarohana, vadi, samvadi
        f0_data (List[Dict]): Pitch sequence with f0_hz values
        
    Returns:
        Dict: {raga_name, explanation, raga_rules_applied}
    """
    templates = load_xai_templates()
    raga_name = raga.get("name", "Unknown")
    
    # Extract raga components
    vadi = raga.get("vadi", "Sa")
    samvadi = raga.get("samvadi", "Pa")
    arohana = ", ".join(raga.get("arohana", []))
    avarohana = ", ".join(raga.get("avarohana", []))
    
    # Compute contour statistics
    stats = _compute_contour_stats(f0_data)
    
    # Build rules applied trace
    rules_applied = [
        "Chanda-based raga selection",
        "Scale snapping to arohana/avarohana notes",
        "Accent-derived pitch contour",
        "Mora-based duration shaping",
    ]
    
    # Format explanation from templates
    explanation_parts = []
    
    if "RAGA_INTRO" in templates:
        intro = templates["RAGA_INTRO"].format(raga_name=raga_name)
        explanation_parts.append(intro)
    
    if "VADI_SAMVADI" in templates:
        vadi_section = templates["VADI_SAMVADI"].format(vadi=vadi, samvadi=samvadi)
        explanation_parts.append(vadi_section)
    
    if "AROHANA_DESC" in templates:
        aroh_section = templates["AROHANA_DESC"].format(arohana=arohana)
        explanation_parts.append(aroh_section)
    
    if "AVAROHANA_DESC" in templates:
        avaroh_section = templates["AVAROHANA_DESC"].format(avarohana=avarohana)
        explanation_parts.append(avaroh_section)
    
    if "CONTOUR_SUMMARY" in templates:
        contour_section = templates["CONTOUR_SUMMARY"].format(
            min_freq=stats["min_freq"],
            max_freq=stats["max_freq"],
            avg_freq=stats["avg_freq"],
            syllable_count=len(f0_data)
        )
        explanation_parts.append(contour_section)
    
    if "RULES_APPLIED" in templates:
        rules_section = templates["RULES_APPLIED"].format(
            rules_list=_format_rules_list(rules_applied)
        )
        explanation_parts.append(rules_section)
    
    if "CLOSING" in templates:
        explanation_parts.append(templates["CLOSING"])
    
    full_explanation = "\n\n".join(explanation_parts)
    
    # Try LLM enhancement if API key exists
    if os.getenv("LLM_API_KEY"):
        try:
            full_explanation = _enhance_with_llm(full_explanation)
        except Exception:
            pass  # Fall back to template-only explanation
    
    return {
        "raga_name": raga_name,
        "explanation": full_explanation,
        "raga_rules_applied": rules_applied,
    }


def _enhance_with_llm(template_text: str) -> str:
    """
    Optional LLM enhancement of explanation.
    
    Calls LLM API if LLM_API_KEY environment variable is set.
    Uses simple HTTP POST with requests library.
    
    Args:
        template_text (str): Template-based explanation
        
    Returns:
        str: Enhanced explanation from LLM or original if API fails
    """
    api_key = os.getenv("LLM_API_KEY")
    api_url = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
    
    if not api_key:
        return template_text
    
    try:
        import requests
    except ImportError:
        return template_text
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a Vedic music expert. Enhance the following explanation with musical insights.",
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }
        
        payload["messages"].append({"role": "user", "content": template_text})
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
    
    except Exception:
        pass
    
    return template_text


def test_melodic_explainer():
    """Test melodic explanation generator with sample data."""
    print("=" * 80)
    print("MELODIC EXPLAINER TEST")
    print("=" * 80)
    
    # Sample raga
    sample_raga = {
        "name": "Bhairav",
        "arohana": ["S", "r", "G", "M", "P", "d", "N", "S"],
        "avarohana": ["S", "N", "d", "P", "M", "G", "r", "S"],
        "vadi": "d",
        "samvadi": "r",
    }
    
    # Sample pitch sequence
    sample_f0_data = [
        {"syllable": "a", "f0_hz": 140.0, "duration_ms": 833.33},
        {"syllable": "gnim", "f0_hz": 155.0, "duration_ms": 1666.67},
        {"syllable": "i", "f0_hz": 174.6, "duration_ms": 833.33},
    ]
    
    # Generate explanation
    result = explain_melodic_choice(sample_raga, sample_f0_data)
    
    print("\nGenerated Explanation:")
    print("-" * 80)
    print(result["explanation"])
    print("-" * 80)
    
    print(f"\nRaga Name: {result['raga_name']}")
    print(f"\nRules Applied:")
    for rule in result["raga_rules_applied"]:
        print(f"  • {rule}")
    
    # Verify output structure
    assert "raga_name" in result, "Missing raga_name"
    assert "explanation" in result, "Missing explanation"
    assert "raga_rules_applied" in result, "Missing raga_rules_applied"
    assert isinstance(result["raga_rules_applied"], list), "raga_rules_applied must be list"
    assert len(result["raga_rules_applied"]) > 0, "raga_rules_applied must not be empty"
    
    print("\n" + "=" * 80)
    print("✅ Melodic explainer test PASSED")
    print("=" * 80)


if __name__ == "__main__":
    test_melodic_explainer()

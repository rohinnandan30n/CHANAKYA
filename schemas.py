from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class LinguisticOutput(BaseModel):
    """
    Schema for linguistic processing output.
    """
    original_text: str
    tokens: List[str]
    sandhi_applied: bool
    phonemes: List[str]
    metadata: Dict[str, Any] = {}

class MelodicOutput(BaseModel):
    """
    Schema for melodic generation output.
    """
    linguistic_id: str
    notes: List[str]
    durations: List[float]
    frequencies: List[float]
    tempo: int
    scale: str
    metadata: Dict[str, Any] = {}

# Placeholder for sandhi rules structure
# This will be reflected in sandhi_rules.json
class SandhiRule(BaseModel):
    pattern: str
    replacement: str
    description: Optional[str] = None

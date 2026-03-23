from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class LinguisticOutput(BaseModel):
    """
    Schema for linguistic processing output.
    """
    tokens: List[str]
    syllables: List[List[str]]
    metre: str
    sandhi_applied: List[Any]  # Based on mock returning []

class MelodicOutput(BaseModel):
    """
    Schema for melodic generation output.
    """
    raga: str
    f0_contour: List[float]
    accent_map: List[Any]
    explanation: str

class AudioOutput(BaseModel):
    """
    Schema for audio generation output.
    """
    file_path: str
    duration_ms: int

# Placeholder for sandhi rules structure
class SandhiRule(BaseModel):
    pattern: str
    replacement: str
    description: Optional[str] = None

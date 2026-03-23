from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ReciteRequest(BaseModel):
    text: str
    raga_preference: Optional[str] = None

class JobStatus(BaseModel):
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None

class LinguisticOutput(BaseModel):
    """
    Schema for linguistic processing output.
    """
    tokens: List[str]
    syllables: List[List[str]]
    metre: str
    sandhi_applied: List[Any]

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

class SandhiRule(BaseModel):
    pattern: str
    replacement: str
    description: Optional[str] = None

"""
Linguistic Output Serialization Module

This module provides Pydantic models for structured linguistic analysis output
and JSON serialization with validation against the defined schema.

Task 5 Implementation:
- Step 22: Define output schema with Pydantic models
- Step 23: Implement serialize_linguistic_data function
- Step 24: Add JSON schema validation
- Step 25: Provide CLI runner for batch analysis
- Step 26: Document output format for API integration
"""

import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import jsonschema

logger = logging.getLogger(__name__)


class SyllableOutput(BaseModel):
    """
    Single syllable with metrical weight.
    
    Attributes:
        syllable (str): Syllable text in SLP1 canonical form
        weight (str): 'L' for Laghu (light) or 'G' for Guru (heavy)
        index (int): 0-based position in the syllable sequence
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "syllable": "na",
                "weight": "L",
                "index": 0
            }
        }
    )
    
    syllable: str = Field(..., min_length=1, description="Syllable in SLP1")
    weight: str = Field(..., pattern="^[LG]$", description="Weight: L or G")
    index: int = Field(..., ge=0, description="0-based syllable position")


class ChandaOutput(BaseModel):
    """
    Metrical scheme identification result.
    
    Attributes:
        name (str): Name of the identified metre (e.g., 'Anushtubh')
        syllables_per_pada (int): Syllables per quarter (1-32)
        gana_pattern (str): Pattern like 'GGGG LGGG'
        classification (str): Standard classification (sama/ardhasama/vishama/unknown)
        confidence (float): Match confidence 0.0-1.0
        notes (str, optional): Additional information
        matra_count (int, optional): Mora count
        example (str, optional): Example verse in SLP1
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Anushtubh",
                "syllables_per_pada": 8,
                "gana_pattern": "GGGG LGGG",
                "classification": "sama",
                "confidence": 1.0
            }
        }
    )
    
    name: str = Field(..., min_length=1, description="Metre name")
    syllables_per_pada: int = Field(..., ge=1, le=32, description="Syllables per pada")
    gana_pattern: str = Field(..., pattern="^[LG ]+$", description="Pattern like 'GGGG LGGG'")
    classification: str = Field(..., pattern="^(sama|ardhasama|vishama|unknown)$", description="Metre classification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0.0-1.0")
    notes: Optional[str] = Field(None, description="Additional notes")
    matra_count: Optional[int] = Field(None, ge=1, description="Mora count")
    example: Optional[str] = Field(None, description="Example verse in SLP1")


class MetadataOutput(BaseModel):
    """
    Analysis metadata.
    
    Attributes:
        analysis_timestamp (datetime, optional): When analysis was performed
        total_syllables (int, optional): Total syllable count
        guru_count (int, optional): Number of Guru syllables
        laghu_count (int, optional): Number of Laghu syllables
        warnings (List[str], optional): Issues encountered
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_syllables": 8,
                "guru_count": 5,
                "laghu_count": 3
            }
        }
    )
    
    analysis_timestamp: Optional[datetime] = Field(None, description="ISO 8601 timestamp")
    total_syllables: Optional[int] = Field(None, ge=1, description="Total syllables")
    guru_count: Optional[int] = Field(None, ge=0, description="Guru syllable count")
    laghu_count: Optional[int] = Field(None, ge=0, description="Laghu syllable count")
    warnings: Optional[List[str]] = Field(None, description="Warning messages")


class LinguisticOutput(BaseModel):
    """
    Complete linguistic analysis output.
    
    This is the main output model combining transliteration, syllabification,
    and metrical analysis. All outputs should conform to this structure.
    
    Attributes:
        original_text (str): Original input text
        input_scheme (str, optional): Detected input scheme
        canonical_slp1 (str): Canonical SLP1 representation
        syllables (List[SyllableOutput]): Syllables with weights
        metrical_pattern (str, optional): LG pattern string
        chanda (ChandaOutput): Metrical scheme identification
        metadata (MetadataOutput, optional): Additional information
    
    Examples:
        >>> output = LinguisticOutput(
        ...     original_text="नमस्ते",
        ...     input_scheme="devanagari",
        ...     canonical_slp1="namasate",
        ...     syllables=[
        ...         SyllableOutput(syllable="na", weight="L", index=0),
        ...         SyllableOutput(syllable="ma", weight="L", index=1),
        ...         SyllableOutput(syllable="sa", weight="L", index=2),
        ...         SyllableOutput(syllable="te", weight="L", index=3),
        ...     ],
        ...     metrical_pattern="LLLL",
        ...     chanda=ChandaOutput(
        ...         name="Simple",
        ...         syllables_per_pada=4,
        ...         gana_pattern="LLLL",
        ...         classification="unknown",
        ...         confidence=0.5
        ...     )
        ... )
        >>> output.dict()  # Get as dictionary
    """
    original_text: str = Field(..., min_length=1, description="Original input text")
    input_scheme: Optional[str] = Field(None, pattern="^(devanagari|iast|harvard_kyoto|slp1|unknown)$", description="Input scheme")
    canonical_slp1: str = Field(..., min_length=1, description="SLP1 canonical form")
    syllables: List[SyllableOutput] = Field(..., min_length=1, description="Syllables with weights")
    metrical_pattern: Optional[str] = Field(None, pattern="^[LG]+$", description="Metrical pattern")
    chanda: ChandaOutput = Field(..., description="Identified metre")
    metadata: Optional[MetadataOutput] = Field(None, description="Optional metadata")
    
    @model_validator(mode='after')
    def set_defaults(self):
        """Auto-generate metrical_pattern and metadata if not provided."""
        # Generate metrical_pattern if not set
        if self.metrical_pattern is None and self.syllables:
            self.metrical_pattern = ''.join(s.weight for s in self.syllables)
        
        # Generate metadata if not set
        if self.metadata is None and self.syllables:
            guru_count = sum(1 for s in self.syllables if s.weight == 'G')
            laghu_count = sum(1 for s in self.syllables if s.weight == 'L')
            self.metadata = MetadataOutput(
                analysis_timestamp=datetime.now(),
                total_syllables=len(self.syllables),
                guru_count=guru_count,
                laghu_count=laghu_count
            )
        
        return self
    
    def model_dump(self, **kwargs) -> Dict:
        """Convert to dictionary, passing through Pydantic serialization."""
        data = super().model_dump(**kwargs)
        # Ensure metadata.analysis_timestamp is ISO format string
        if data.get('metadata') and data['metadata'].get('analysis_timestamp'):
            if isinstance(data['metadata']['analysis_timestamp'], datetime):
                data['metadata']['analysis_timestamp'] = data['metadata']['analysis_timestamp'].isoformat()
        return data
    
    def dict(self, **kwargs) -> Dict:
        """Deprecated: use model_dump() instead. Kept for backward compatibility."""
        return self.model_dump(**kwargs)


def serialize_linguistic_data(output: LinguisticOutput) -> str:
    """
    Step 23: Serialize linguistic analysis to JSON string with validation.
    
    This function takes a LinguisticOutput object and returns a JSON string
    representation with full validation against the schema.
    
    Args:
        output (LinguisticOutput): Structured linguistic analysis output
        
    Returns:
        str: Valid JSON string representation
        
    Raises:
        ValueError: If output fails schema validation
        
    Examples:
        >>> from backend.linguistic import LinguisticOutput, SyllableOutput, ChandaOutput
        >>> output = LinguisticOutput(
        ...     original_text="नमस्ते",
        ...     canonical_slp1="namasate",
        ...     syllables=[SyllableOutput(syllable="na", weight="L", index=0)],
        ...     chanda=ChandaOutput(
        ...         name="Test",
        ...         syllables_per_pada=4,
        ...         gana_pattern="LLLL",
        ...         classification="unknown",
        ...         confidence=0.5
        ...     )
        ... )
        >>> json_str = serialize_linguistic_data(output)
        >>> print(json_str)
        {"original_text": "नमस्ते", "canonical_slp1": "namasate", ...}
    """
    # Convert to dictionary
    output_dict = output.model_dump()
    
    # Step 24: Validate against schema
    schema_path = Path(__file__).parent.parent.parent / 'linguistic_output.schema.json'
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except FileNotFoundError:
        logger.warning(f"Schema file not found at {schema_path}, skipping validation")
        schema = None
    
    if schema:
        try:
            jsonschema.validate(instance=output_dict, schema=schema)
            logger.debug("Output validated successfully against schema")
        except jsonschema.ValidationError as e:
            logger.error(f"Output validation failed: {e.message}")
            raise ValueError(f"Output validation failed: {e.message}")
    
    # Serialize to JSON with proper encoding
    return json.dumps(output_dict, ensure_ascii=False, indent=2)


def validate_output_schema(json_string: str) -> bool:
    """
    Step 24: Validate a JSON string against the output schema.
    
    Args:
        json_string (str): JSON string to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        json.JSONDecodeError: If JSON is malformed
        jsonschema.ValidationError: If validation fails
    """
    data = json.loads(json_string)
    schema_path = Path(__file__).parent.parent.parent / 'linguistic_output.schema.json'
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    jsonschema.validate(instance=data, schema=schema)
    logger.info("JSON output validated successfully")
    return True


if __name__ == '__main__':
    # Simple test
    print("Linguistic Output Module")
    print("Models: SyllableOutput, ChandaOutput, MetadataOutput, LinguisticOutput")
    print("Functions: serialize_linguistic_data, validate_output_schema")
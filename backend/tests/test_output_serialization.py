"""
Tests for Task 5: Output Serialization and JSON Schema Validation

Tests the structured JSON output, Pydantic models, and schema validation.
"""

import pytest
import json
from datetime import datetime

from backend.linguistic import (
    SyllableOutput,
    ChandaOutput,
    MetadataOutput,
    LinguisticOutput,
    serialize_linguistic_data,
    validate_output_schema,
)


class TestSyllableOutput:
    """Test SyllableOutput Pydantic model."""
    
    def test_valid_syllable_output(self):
        """Test creating valid syllable output."""
        syll = SyllableOutput(syllable="na", weight="L", index=0)
        assert syll.syllable == "na"
        assert syll.weight == "L"
        assert syll.index == 0
    
    def test_syllable_output_dict(self):
        """Test syllable output as dictionary."""
        syll = SyllableOutput(syllable="ma", weight="G", index=1)
        d = syll.model_dump()
        assert d == {"syllable": "ma", "weight": "G", "index": 1}
    
    def test_invalid_weight_raises(self):
        """Test invalid weight raises validation error."""
        with pytest.raises(ValueError):
            SyllableOutput(syllable="na", weight="X", index=0)
    
    def test_negative_index_raises(self):
        """Test negative index raises validation error."""
        with pytest.raises(ValueError):
            SyllableOutput(syllable="na", weight="L", index=-1)
    
    def test_empty_syllable_raises(self):
        """Test empty syllable raises validation error."""
        with pytest.raises(ValueError):
            SyllableOutput(syllable="", weight="L", index=0)


class TestChandaOutput:
    """Test ChandaOutput Pydantic model."""
    
    def test_valid_chanda_output(self):
        """Test creating valid chanda output."""
        chanda = ChandaOutput(
            name="Anushtubh",
            syllables_per_pada=8,
            gana_pattern="GGGG LGGG",
            classification="sama",
            confidence=1.0
        )
        assert chanda.name == "Anushtubh"
        assert chanda.confidence == 1.0
    
    def test_chanda_with_optional_fields(self):
        """Test chanda with optional fields."""
        chanda = ChandaOutput(
            name="Trishtubh",
            syllables_per_pada=11,
            gana_pattern="GGGG LLGG GLLG",
            classification="sama",
            confidence=0.95,
            notes="11-syllable verse metre",
            matra_count=44,
            example="yajYaM vAmadevAya cakrAM"
        )
        assert chanda.notes is not None
        assert chanda.matra_count == 44
    
    def test_confidence_range(self):
        """Test confidence must be 0.0-1.0."""
        with pytest.raises(ValueError):
            ChandaOutput(
                name="Test",
                syllables_per_pada=8,
                gana_pattern="LLLL",
                classification="unknown",
                confidence=1.5
            )
    
    def test_invalid_classification_raises(self):
        """Test invalid classification raises error."""
        with pytest.raises(ValueError):
            ChandaOutput(
                name="Test",
                syllables_per_pada=8,
                gana_pattern="LLLL",
                classification="invalid",
                confidence=0.5
            )


class TestLinguisticOutput:
    """Test LinguisticOutput Pydantic model."""
    
    @pytest.fixture
    def basic_output(self):
        """Create a basic valid output for testing."""
        return LinguisticOutput(
            original_text="नमस्ते",
            input_scheme="devanagari",
            canonical_slp1="namasate",
            syllables=[
                SyllableOutput(syllable="na", weight="L", index=0),
                SyllableOutput(syllable="ma", weight="L", index=1),
                SyllableOutput(syllable="sa", weight="L", index=2),
                SyllableOutput(syllable="te", weight="L", index=3),
            ],
            chanda=ChandaOutput(
                name="Simple",
                syllables_per_pada=4,
                gana_pattern="LLLL",
                classification="unknown",
                confidence=0.5
            )
        )
    
    def test_basic_output_creation(self, basic_output):
        """Test creating basic linguistic output."""
        assert basic_output.original_text == "नमस्ते"
        assert basic_output.canonical_slp1 == "namasate"
        assert len(basic_output.syllables) == 4
    
    def test_metrical_pattern_auto_generated(self, basic_output):
        """Test metrical pattern is auto-generated from syllables."""
        assert basic_output.metrical_pattern == "LLLL"
    
    def test_metadata_auto_generated(self, basic_output):
        """Test metadata is auto-generated from syllables."""
        assert basic_output.metadata is not None
        assert basic_output.metadata.total_syllables == 4
        assert basic_output.metadata.laghu_count == 4
        assert basic_output.metadata.guru_count == 0
    
    def test_output_as_dict(self, basic_output):
        """Test converting output to dictionary."""
        d = basic_output.model_dump()
        assert d['original_text'] == "नमस्ते"
        assert d['canonical_slp1'] == "namasate"
        assert len(d['syllables']) == 4
        assert d['metrical_pattern'] == "LLLL"
    
    def test_output_with_guru_syllables(self):
        """Test output with mixed Laghu-Guru syllables."""
        output = LinguisticOutput(
            original_text="medhA",
            canonical_slp1="medhA",
            syllables=[
                SyllableOutput(syllable="me", weight="L", index=0),
                SyllableOutput(syllable="dhA", weight="G", index=1),
            ],
            chanda=ChandaOutput(
                name="Test",
                syllables_per_pada=2,
                gana_pattern="LG",
                classification="unknown",
                confidence=0.0
            )
        )
        assert output.metrical_pattern == "LG"
        assert output.metadata.guru_count == 1
        assert output.metadata.laghu_count == 1


class TestSerialization:
    """Test serialization functions."""
    
    @pytest.fixture
    def sample_output(self):
        """Create a sample output for serialization testing."""
        return LinguisticOutput(
            original_text="नमस्ते",
            input_scheme="devanagari",
            canonical_slp1="namasate",
            syllables=[
                SyllableOutput(syllable="na", weight="L", index=0),
                SyllableOutput(syllable="ma", weight="L", index=1),
                SyllableOutput(syllable="sa", weight="L", index=2),
                SyllableOutput(syllable="te", weight="L", index=3),
            ],
            chanda=ChandaOutput(
                name="Anushtubh",
                syllables_per_pada=8,
                gana_pattern="GGGG LGGG",
                classification="sama",
                confidence=1.0
            )
        )
    
    def test_serialize_to_json(self, sample_output):
        """Step 23: Test serialization to JSON string."""
        json_str = serialize_linguistic_data(sample_output)
        assert isinstance(json_str, str)
        # Should be valid JSON
        data = json.loads(json_str)
        assert data['original_text'] == "नमस्ते"
        assert data['canonical_slp1'] == "namasate"
    
    def test_json_contains_required_fields(self, sample_output):
        """Test JSON contains all required fields."""
        json_str = serialize_linguistic_data(sample_output)
        data = json.loads(json_str)
        
        required = ['original_text', 'canonical_slp1', 'syllables', 'chanda']
        for field in required:
            assert field in data, f"Missing required field: {field}"
    
    def test_syllables_in_json(self, sample_output):
        """Test syllables are properly serialized."""
        json_str = serialize_linguistic_data(sample_output)
        data = json.loads(json_str)
        
        assert len(data['syllables']) == 4
        assert data['syllables'][0]['syllable'] == 'na'
        assert data['syllables'][0]['weight'] == 'L'
        assert data['syllables'][0]['index'] == 0
    
    def test_chanda_in_json(self, sample_output):
        """Test chanda is properly serialized."""
        json_str = serialize_linguistic_data(sample_output)
        data = json.loads(json_str)
        
        chanda = data['chanda']
        assert chanda['name'] == 'Anushtubh'
        assert chanda['syllables_per_pada'] == 8
        assert chanda['gana_pattern'] == 'GGGG LGGG'
        assert chanda['confidence'] == 1.0
    
    def test_metadata_in_json(self, sample_output):
        """Test metadata is included in JSON."""
        json_str = serialize_linguistic_data(sample_output)
        data = json.loads(json_str)
        
        assert 'metadata' in data
        assert data['metadata']['total_syllables'] == 4
        assert data['metadata']['laghu_count'] == 4


class TestSchemaValidation:
    """Step 24: Test JSON schema validation."""
    
    @pytest.fixture
    def valid_json(self):
        """Valid JSON conforming to schema."""
        return json.dumps({
            'original_text': 'नमस्ते',
            'canonical_slp1': 'namasate',
            'syllables': [
                {'syllable': 'na', 'weight': 'L', 'index': 0}
            ],
            'input_scheme': 'devanagari',
            'metrical_pattern': 'L',
            'chanda': {
                'name': 'Simple',
                'syllables_per_pada': 1,
                'gana_pattern': 'L',
                'classification': 'unknown',
                'confidence': 0.0
            }
        })
    
    def test_validate_valid_json(self, valid_json):
        """Test validation of valid JSON."""
        assert validate_output_schema(valid_json) is True
    
    def test_validate_invalid_json(self):
        """Test validation of invalid JSON."""
        invalid_json = '{"invalid": "json"}'
        with pytest.raises(Exception):  # jsonschema.ValidationError
            validate_output_schema(invalid_json)
    
    def test_missing_required_field(self):
        """Test JSON missing required fields fails validation."""
        invalid_json = json.dumps({
            'original_text': 'text',
            # Missing canonical_slp1, syllables, chanda
        })
        with pytest.raises(Exception):
            validate_output_schema(invalid_json)


class TestIntegrationWithRunner:
    """Integration tests with the linguistic runner."""
    
    def test_runner_imports(self):
        """Test runner module imports correctly."""
        from backend.linguistic.runner import analyze_verse
        assert callable(analyze_verse)
    
    def test_analyze_simple_verse(self):
        """Test analyzing a simple verse."""
        from backend.linguistic.runner import analyze_verse
        
        json_result = analyze_verse("namasate")
        data = json.loads(json_result)
        
        assert data['original_text'] == "namasate"
        assert data['canonical_slp1'] == "namasate"
        assert 'syllables' in data
        assert 'chanda' in data
    
    def test_analyze_devanagari_verse(self):
        """Test analyzing Devanagari verse."""
        from backend.linguistic.runner import analyze_verse
        
        json_result = analyze_verse("नमस्ते")
        data = json.loads(json_result)
        
        assert 'canonical_slp1' in data
        assert 'syllables' in data
        assert len(data['syllables']) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_single_syllable_output(self):
        """Test output with single syllable."""
        output = LinguisticOutput(
            original_text="अ",
            canonical_slp1="a",
            syllables=[
                SyllableOutput(syllable="a", weight="L", index=0)
            ],
            chanda=ChandaOutput(
                name="Single",
                syllables_per_pada=1,
                gana_pattern="L",
                classification="unknown",
                confidence=0.0
            )
        )
        json_str = serialize_linguistic_data(output)
        data = json.loads(json_str)
        assert data['metrical_pattern'] == "L"
    
    def test_long_verse_output(self):
        """Test output with many syllables."""
        syllables = [
            SyllableOutput(syllable=f"s{i}", weight="L" if i % 2 == 0 else "G", index=i)
            for i in range(32)
        ]
        output = LinguisticOutput(
            original_text="long_verse",
            canonical_slp1="s" * 32,
            syllables=syllables,
            chanda=ChandaOutput(
                name="Long",
                syllables_per_pada=32,
                gana_pattern="L" * 16 + "G" * 16,
                classification="unknown",
                confidence=0.5
            )
        )
        json_str = serialize_linguistic_data(output)
        data = json.loads(json_str)
        assert len(data['syllables']) == 32


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

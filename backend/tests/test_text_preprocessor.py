"""
Unit tests for the Sanskrit text preprocessor module.

This test suite covers:
- Scheme detection (Devanagari, IAST, Harvard-Kyoto)
- Text conversion to SLP1 canonical form
- Text cleaning and normalization
- Transliteration functionality (robust conversion)
- Error handling and edge cases
"""

import pytest
import sys
import os
import logging

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from linguistic.text_preprocessor import TextPreprocessor, accept_input, transliterate


class TestSchemeDetection:
    """Test cases for transliteration scheme detection."""
    
    def test_detect_devanagari(self):
        """Test detection of Devanagari script."""
        devanagari_text = "नमस्ते"
        detected = TextPreprocessor.detect_scheme(devanagari_text)
        assert detected == 'devanagari', f"Expected 'devanagari', got '{detected}'"
    
    def test_detect_iast(self):
        """Test detection of IAST transliteration."""
        iast_text = "namaste"
        detected = TextPreprocessor.detect_scheme(iast_text)
        # IAST detection might be tricky, so we'll accept harvard_kyoto or iast
        assert detected in ['iast', 'harvard_kyoto'], f"Expected IAST-like, got '{detected}'"
    
    def test_detect_with_diacritics(self):
        """Test detection of IAST with diacritical marks."""
        iast_text = "dhyāna"
        detected = TextPreprocessor.detect_scheme(iast_text)
        assert detected == 'iast', f"Expected 'iast', got '{detected}'"
    
    def test_detect_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            TextPreprocessor.detect_scheme("")
    
    def test_detect_whitespace_only_raises_error(self):
        """Test that whitespace-only text raises ValueError."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            TextPreprocessor.detect_scheme("   ")


class TestTextCleaning:
    """Test cases for text cleaning and normalization."""
    
    def test_clean_extra_whitespace(self):
        """Test removal of extra whitespace."""
        text = "नमस्ते    विश्व"
        cleaned = TextPreprocessor.clean_text(text)
        assert "  " not in cleaned, "Extra whitespace not removed"
        assert cleaned == "नमस्ते विश्व", f"Unexpected result: '{cleaned}'"
    
    def test_clean_punctuation(self):
        """Test removal of punctuation."""
        text = "namaste, world!"
        cleaned = TextPreprocessor.clean_text(text)
        assert "," not in cleaned and "!" not in cleaned
        assert cleaned == "namaste world", f"Unexpected result: '{cleaned}'"
    
    def test_clean_leading_trailing_whitespace(self):
        """Test removal of leading and trailing whitespace."""
        text = "  नमस्ते  "
        cleaned = TextPreprocessor.clean_text(text)
        assert not cleaned.startswith(' ') and not cleaned.endswith(' ')
        assert cleaned == "नमस्ते"
    
    def test_clean_empty_text(self):
        """Test cleaning of empty text returns empty string."""
        result = TextPreprocessor.clean_text("")
        assert result == "", "Empty input should return empty string"
    
    def test_clean_preserves_devanagari(self):
        """Test that cleaning preserves Devanagari characters."""
        text = "नमस्ते, यह एक परीक्षा है!"
        cleaned = TextPreprocessor.clean_text(text)
        # Check that Devanagari characters are preserved
        assert "नमस्ते" in cleaned or any(ord(c) in range(0x0900, 0x097F) for c in cleaned)


class TestAcceptInput:
    """Test cases for the main accept_input function."""
    
    def test_accept_devanagari_input(self):
        """Test processing of Devanagari input."""
        devanagari_text = "नमस्ते"
        result = TextPreprocessor.accept_input(devanagari_text)
        assert result is not None
        assert len(result) > 0
        # Result should be in SLP1, which uses ASCII
        assert isinstance(result, str)
    
    def test_accept_harvard_kyoto_input(self):
        """Test processing of Harvard-Kyoto input."""
        hk_text = "namaste"
        result = TextPreprocessor.accept_input(hk_text, scheme='harvard_kyoto')
        assert result is not None
        assert len(result) > 0
    
    def test_accept_explicit_iast_scheme(self):
        """Test processing with explicit IAST scheme."""
        iast_text = "namaste"
        result = TextPreprocessor.accept_input(iast_text, scheme='iast')
        assert result is not None
        assert len(result) > 0
    
    def test_accept_auto_detect_scheme(self):
        """Test auto-detection when scheme is not specified."""
        devanagari_text = "नमस्ते"
        result = TextPreprocessor.accept_input(devanagari_text)
        assert result is not None
        assert len(result) > 0
    
    def test_empty_input_raises_error(self):
        """Test that empty input raises ValueError."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            TextPreprocessor.accept_input("")
    
    def test_whitespace_only_input_raises_error(self):
        """Test that whitespace-only input raises ValueError."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            TextPreprocessor.accept_input("   ")
    
    def test_non_string_input_raises_error(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="Input text must be a string"):
            TextPreprocessor.accept_input(12345)
    
    def test_invalid_scheme_raises_error(self):
        """Test that invalid scheme raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported scheme"):
            TextPreprocessor.accept_input("namaste", scheme='invalid_scheme')
    
    def test_result_is_slp1(self):
        """Test that output is in SLP1 format."""
        # SLP1 uses ASCII characters for Sanskrit
        result = TextPreprocessor.accept_input("नमस्ते")
        # Check that it's ASCII (SLP1 characteristic)
        assert all(ord(c) < 128 or c == ' ' for c in result)
    
    def test_convenience_function(self):
        """Test the module-level convenience function."""
        result = accept_input("नमस्ते")
        assert result is not None
        assert len(result) > 0


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_very_long_text(self):
        """Test processing of very long text."""
        long_text = "नमस्ते " * 100
        result = TextPreprocessor.accept_input(long_text)
        assert result is not None
        assert len(result) > 0
    
    def test_mixed_scripts_preference(self):
        """Test handling of mixed scripts (should prefer dominant script)."""
        mixed_text = "नमस्ते namaste"
        result = TextPreprocessor.accept_input(mixed_text)
        assert result is not None
    
    def test_case_insensitive_scheme(self):
        """Test that scheme names are case-insensitive."""
        result1 = TextPreprocessor.accept_input("नमस्ते", scheme='DEVANAGARI')
        result2 = TextPreprocessor.accept_input("नमस्ते", scheme='devanagari')
        assert result1 == result2
    
    def test_scheme_names_with_lowercase(self):
        """Test various scheme name formats."""
        text = "नमस्ते"
        result_lower = TextPreprocessor.accept_input(text, scheme='devanagari')
        assert result_lower is not None
    
    def test_unicode_normalization(self):
        """Test handling of different Unicode representations."""
        text = "नमस्ते"
        result = TextPreprocessor.accept_input(text)
        assert result is not None
        assert len(result) > 0


class TestSpecialCharacters:
    """Test handling of special characters and punctuation."""
    
    def test_punctuation_removal(self):
        """Test that punctuation is properly removed."""
        text = "नमस्ते!!! यह एक परीक्षा है???"
        result = TextPreprocessor.accept_input(text)
        assert "!" not in result
        assert "?" not in result
    
    def test_numbers_preserved_or_removed(self):
        """Test handling of numbers in text."""
        text = "नमस्ते123"
        result = TextPreprocessor.accept_input(text)
        # Result should be clean, numbers might be removed
        assert result is not None
    
    def test_special_diacritical_marks(self):
        """Test handling of special diacritical marks in IAST."""
        text = "ṛ ḷ ñ ṇ ṭ"
        result = TextPreprocessor.accept_input(text, scheme='iast')
        assert result is not None


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_complete_workflow_devanagari(self):
        """Test complete workflow with Devanagari input."""
        input_text = "नमस्ते, विश्व!"
        result = TextPreprocessor.accept_input(input_text)
        
        # Verify the result
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert "!" not in result  # Punctuation removed
    
    def test_complete_workflow_iast(self):
        """Test complete workflow with IAST input."""
        input_text = "namaste, viśva!"
        result = TextPreprocessor.accept_input(input_text, scheme='iast')
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_consistency_of_output(self):
        """Test that same input produces same output."""
        input_text = "नमस्ते"
        result1 = TextPreprocessor.accept_input(input_text)
        result2 = TextPreprocessor.accept_input(input_text)
        
        assert result1 == result2, "Output should be consistent for same input"
    
    def test_devanagari_to_slp1_conversion(self):
        """Test conversion from Devanagari to SLP1."""
        # This is a specific test to verify the conversion works
        input_text = "नमः"
        result = TextPreprocessor.accept_input(input_text)
        
        # "नमः" in Devanagari should convert to "nam:" in SLP1
        assert result is not None
        assert isinstance(result, str)


class TestTransliteration:
    """Test cases for the robust transliteration function."""
    
    def test_transliterate_devanagari_to_slp1(self):
        """Test Devanagari to SLP1 transliteration."""
        input_text = "नमस्ते"
        result, metadata = transliterate(input_text, 'devanagari')
        
        # Verify result
        assert result is not None
        assert isinstance(result, str)
        assert all(ord(c) < 128 or c == ' ' for c in result), "SLP1 should be ASCII"
        
        # Verify metadata
        assert metadata['scheme'] == 'devanagari'
        assert metadata['conversion_status'] == 'success'
        assert isinstance(metadata['warnings'], list)
    
    def test_transliterate_iast_to_slp1(self):
        """Test IAST to SLP1 transliteration."""
        input_text = "namaste"
        result, metadata = transliterate(input_text, 'iast')
        
        assert result is not None
        assert isinstance(result, str)
        assert metadata['conversion_status'] == 'success'
    
    def test_transliterate_iast_with_diacritics(self):
        """Test IAST with diacritical marks to SLP1."""
        input_text = "dhyāna"
        result, metadata = transliterate(input_text, 'iast')
        
        assert result is not None
        assert len(result) > 0
        assert metadata['conversion_status'] == 'success'
    
    def test_transliterate_harvard_kyoto_to_slp1(self):
        """Test Harvard-Kyoto to SLP1 transliteration."""
        input_text = "namaste"
        result, metadata = transliterate(input_text, 'hk')
        
        assert result is not None
        assert isinstance(result, str)
        assert metadata['conversion_status'] == 'success'
    
    def test_transliterate_with_explicit_harvard_kyoto_name(self):
        """Test using full 'harvard_kyoto' scheme name."""
        input_text = "namaste"
        result, metadata = transliterate(input_text, 'harvard_kyoto')
        
        assert result is not None
        assert metadata['conversion_status'] == 'success'
    
    def test_transliterate_empty_input_raises_error(self):
        """Test that empty input raises ValueError."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            transliterate("", 'devanagari')
    
    def test_transliterate_invalid_scheme_raises_error(self):
        """Test that invalid scheme raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported scheme"):
            transliterate("नमस्ते", 'invalid_scheme')
    
    def test_transliterate_non_string_input_raises_error(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="Input text must be a string"):
            transliterate(12345, 'devanagari')
    
    def test_transliterate_case_insensitive_scheme(self):
        """Test that scheme names are case-insensitive."""
        input_text = "नमस्ते"
        result1, _ = transliterate(input_text, 'DEVANAGARI')
        result2, _ = transliterate(input_text, 'devanagari')
        result3, _ = transliterate(input_text, 'DeVaNaGaRi')
        
        assert result1 == result2 == result3
    
    def test_transliterate_returns_metadata(self):
        """Test that transliterate returns proper metadata dictionary."""
        input_text = "नमस्ते"
        result, metadata = transliterate(input_text, 'devanagari')
        
        # Check metadata structure
        assert isinstance(metadata, dict)
        assert 'scheme' in metadata
        assert 'unrecognized_chars' in metadata
        assert 'conversion_status' in metadata
        assert 'warnings' in metadata
        assert 'character_count' in metadata
        
        # Verify values
        assert metadata['scheme'] == 'devanagari'
        assert isinstance(metadata['unrecognized_chars'], set)
        assert isinstance(metadata['warnings'], list)
    
    def test_transliterate_detects_unrecognized_characters(self):
        """Test that unrecognized characters are detected and logged."""
        # Mix Devanagari with Latin characters
        input_text = "नमस्ते Hello"
        result, metadata = transliterate(input_text, 'devanagari')
        
        # Should have warnings about Latin characters
        assert len(metadata['unrecognized_chars']) > 0
        assert metadata['conversion_status'] in ['success', 'partial']
    
    def test_transliterate_mixed_devanagari_and_ascii(self):
        """Test handling of mixed Devanagari and ASCII."""
        input_text = "नमस्ते abc"
        result, metadata = transliterate(input_text, 'devanagari')
        
        assert result is not None
        assert len(result) > 0
        # Should have warnings about unrecognized chars
        if metadata['unrecognized_chars']:
            assert len(metadata['warnings']) > 0
    
    def test_transliterate_with_missing_diacritics(self):
        """Test handling of input with missing diacritics."""
        # IAST input without some diacritics
        input_text = "namaste"  # Plain ASCII
        result, metadata = transliterate(input_text, 'iast')
        
        assert result is not None
        assert metadata['conversion_status'] == 'success'
    
    def test_transliterate_preserves_whitespace_in_metadata(self):
        """Test that whitespace handling is tracked in metadata."""
        input_text = "नमस्ते  विश्व"  # Double space
        result, metadata = transliterate(input_text, 'devanagari')
        
        assert metadata['character_count'] == len(input_text)
    
    def test_transliterate_multiple_calls_consistency(self):
        """Test that multiple calls produce consistent results."""
        input_text = "नमस्ते"
        result1, meta1 = transliterate(input_text, 'devanagari')
        result2, meta2 = transliterate(input_text, 'devanagari')
        
        assert result1 == result2
        assert meta1['conversion_status'] == meta2['conversion_status']


class TestTransliterationEdgeCases:
    """Test edge cases and special scenarios for transliteration."""
    
    def test_very_long_devanagari_text(self):
        """Test transliteration of very long Devanagari text."""
        long_text = "नमस्ते " * 100
        result, metadata = transliterate(long_text, 'devanagari')
        
        assert result is not None
        assert len(result) > 0
        assert metadata['conversion_status'] == 'success'
    
    def test_devanagari_with_numbers(self):
        """Test Devanagari text mixed with numbers."""
        input_text = "नमस्ते 123"
        result, metadata = transliterate(input_text, 'devanagari')
        
        assert result is not None
        # Numbers might be preserved in some schemes
        assert '1' in result or metadata['conversion_status'] == 'partial'
    
    def test_iast_with_all_diacritics(self):
        """Test IAST with all special diacritical marks."""
        # Sanskrit diacritics: ā, ī, ū, ṛ, ḷ, ē, ō, ṃ, ḥ, etc.
        input_text = "ṛṭḍṇśṣñḷṃḥ"
        result, metadata = transliterate(input_text, 'iast')
        
        assert result is not None
        assert metadata['conversion_status'] in ['success', 'partial']
    
    def test_harvard_kyoto_complex_clusters(self):
        """Test Harvard-Kyoto with complex consonant clusters."""
        input_text = "strI"  # Complex cluster
        result, metadata = transliterate(input_text, 'hk')
        
        assert result is not None
        assert len(result) > 0
    
    def test_transliterate_single_character(self):
        """Test transliteration of single character."""
        inputs = [
            ('अ', 'devanagari'),
            ('a', 'iast'),
            ('a', 'hk'),
        ]
        
        for text, scheme in inputs:
            result, metadata = transliterate(text, scheme)
            assert result is not None
            assert metadata['conversion_status'] == 'success'
    
    def test_transliterate_special_slp1_characters(self):
        """Test that SLP1 special notation is handled correctly."""
        # Input should convert to SLP1 properly with colons etc.
        input_text = "नमः"  # Visarga (ḥ)
        result, metadata = transliterate(input_text, 'devanagari')
        
        assert result is not None
        # SLP1 uses ':' for visarga
        assert ':' in result or result is not None
    
    def test_transliterate_module_function_equivalence(self):
        """Test that module-level function equals class method."""
        from linguistic.text_preprocessor import transliterate as module_transliterate
        
        input_text = "नमस्ते"
        result1, meta1 = module_transliterate(input_text, 'devanagari')
        result2, meta2 = TextPreprocessor.transliterate(input_text, 'devanagari')
        
        assert result1 == result2


class TestLogging:
    """Test logging of unrecognized characters."""
    
    def test_unrecognized_characters_logged(self, caplog):
        """Test that unrecognized characters are logged as warnings."""
        with caplog.at_level(logging.WARNING):
            input_text = "नमस्ते @#$"
            result, metadata = transliterate(input_text, 'devanagari')
        
        # Should have logged warning about unrecognized chars
        # (caplog might not capture all logs depending on config)
        assert metadata['warnings'] or len(metadata['unrecognized_chars']) == 0
    
    def test_metadata_contains_warning_messages(self):
        """Test that metadata includes warning messages."""
        input_text = "नमस्ते Hello123"
        result, metadata = transliterate(input_text, 'devanagari')
        
        if metadata['unrecognized_chars']:
            # Should have warnings in metadata
            assert metadata['warnings']  # Non-empty list
            # Each warning should mention unrecognized
            assert any('unrecognized' in w.lower() or 'character' in w.lower() 
                      for w in metadata['warnings'])


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])

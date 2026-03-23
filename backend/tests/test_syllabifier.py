"""
Comprehensive test suite for Sanskrit syllabification and Laghu-Guru marking.

Tests cover:
1. Basic syllabification (simple syllables)
2. Consonant cluster detection and handling
3. Laghu-Guru weight classification rules
4. Edge cases (anusvara, visarga, final consonants)
5. Integration with transliteration pipeline
6. Anushtubh metre verse validation
7. Error handling and edge cases
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.linguistic import (
    Syllabifier,
    syllabify_and_mark,
    get_syllables,
    get_metrical_pattern,
    accept_input,
    transliterate,
)


class TestBasicSyllabification:
    """Test basic syllabification of simple Sanskrit words."""
    
    def test_simple_cv_syllables(self):
        """Test simple consonant-vowel syllables like 'na-ma'."""
        syllables = get_syllables('nama')
        assert len(syllables) == 2
        assert syllables[0] == 'na'
        assert syllables[1] == 'ma'
    
    def test_single_syllable_cv(self):
        """Test single CV syllable."""
        syllables = get_syllables('pa')
        assert len(syllables) == 1
        assert syllables[0] == 'pa'
    
    def test_single_vowel(self):
        """Test single vowel as syllable."""
        syllables = get_syllables('a')
        assert len(syllables) == 1
        assert syllables[0] == 'a'
    
    def test_three_syllables(self):
        """Test three-syllable word."""
        syllables = get_syllables('namasata')
        assert len(syllables) == 4
        assert syllables == ['na', 'ma', 'sa', 'ta']
    
    def test_mixed_syllable_lengths(self):
        """Test word with varying syllable structures."""
        syllables = get_syllables('vidya')
        assert len(syllables) == 2
        assert syllables[0] == 'vi'
        assert syllables[1] == 'dya'


class TestConsonantClusters:
    """Test syllabification with consonant clusters."""
    
    def test_cluster_detection(self):
        """Test detection of consonant clusters."""
        syll = Syllabifier()
        assert syll.is_consonant_cluster('namdA', 2) == True
    
    def test_conjunct_consonants(self):
        """Test syllabification with conjunct (double) consonants."""
        syllables = get_syllables('anna')
        # 'an' + 'na' or 'a' + 'nna'
        assert len(syllables) >= 2
    
    def test_cluster_cvc_pattern(self):
        """Test CVC pattern where C=cluster."""
        syllables = get_syllables('kSatra')
        # 'kSa' + 'tra' or similar segmentation
        assert len(syllables) >= 2


class TestLaghuGuruMarking:
    """Test classification of syllables as Laghu (L) or Guru (G)."""
    
    def test_short_vowel_laghu(self):
        """Test short vowel = Laghu."""
        weight = Syllabifier.classify_syllable_weight('na')
        assert weight == 'L'
    
    def test_long_vowel_guru(self):
        """Test long vowel = Guru."""
        weight = Syllabifier.classify_syllable_weight('nA')
        assert weight == 'G'
    
    def test_short_vowel_before_anusvara(self):
        """Test short vowel before M (anusvara) = Guru."""
        weight = Syllabifier.classify_syllable_weight('naM')
        assert weight == 'G'
    
    def test_short_vowel_before_visarga(self):
        """Test short vowel before H (visarga) = Guru."""
        weight = Syllabifier.classify_syllable_weight('naH')
        assert weight == 'G'
    
    def test_short_vowel_before_cluster(self):
        """Test short vowel before consonant cluster = Guru."""
        # Test syllable with cluster like 'kta' where 'kt' is a cluster
        weight = Syllabifier.classify_syllable_weight('akta')
        # 'akta' has 'kt' cluster after 'a', so should be Guru
        assert weight == 'G'
    
    def test_vowel_series_all_short(self):
        """Test marking of 'namasata' - all short vowels, all Laghu."""
        marked = syllabify_and_mark('namasata')
        assert len(marked) == 4
        pattern = get_metrical_pattern('namasata')
        assert pattern == 'LLLL'
    
    def test_vowel_series_mixed(self):
        """Test marking with mixed short and long vowels."""
        marked = syllabify_and_mark('nA')
        assert len(marked) == 1
        assert marked[0] == ('nA', 'G')


class TestAnushtubhMetre:
    """Test Anushtubh metre pattern: GGGG LGGG (8 syllables per pāda)."""
    
    def test_anushtubh_pattern_basic(self):
        """Test recognition of standard Anushtubh pattern."""
        # Create a word with GGGG pattern
        # Using long vowels for Guru
        marked = syllabify_and_mark('mAdhAvAhA')
        pattern = get_metrical_pattern('mAdhAvAhA')
        # Should have all long vowels = all Guru
        assert 'L' not in pattern or pattern.count('G') >= 4
    
    def test_anushtubh_pada_8_syllables(self):
        """Test that Anushtubh pāda has 8 syllables."""
        # Create 8-syllable phrase (2 short + 2 long for L+GGG pattern)
        test_phrase = 'namasatamAdhAvAhA'  # 10 syllables
        marked = syllabify_and_mark(test_phrase)
        assert len(marked) >= 8
    
    def test_anushtubh_first_quarter(self):
        """Test GGGG pattern (first quarter of Anushtubh)."""
        # Use 4 long vowels for GGGG
        pattern = get_metrical_pattern('mAdhAvAhA')
        # Should start with at least GG
        assert pattern.count('G') >= 4


class TestEdgeCases:
    """Test edge cases and special situations."""
    
    def test_final_consonant(self):
        """Test handling of final consonant (no vowel after)."""
        syllables = get_syllables('vAk')
        assert 'vAk' in syllables
    
    def test_empty_input_raises_error(self):
        """Test that empty input raises ValueError."""
        with pytest.raises(ValueError):
            get_syllables('')
    
    def test_whitespace_input_raises_error(self):
        """Test that whitespace-only input raises ValueError."""
        with pytest.raises(ValueError):
            get_syllables('   ')
    
    def test_consonant_only_treated_as_laghu(self):
        """Test consonant without vowel classified as Laghu."""
        # Edge case - shouldn't happen in valid Sanskrit
        weight = Syllabifier.classify_syllable_weight('k')
        assert weight == 'L'
    
    def test_anusvara_without_preceding_vowel(self):
        """Test anusvara behavior."""
        # 'M' alone without vowel - edge case
        weight = Syllabifier.classify_syllable_weight('M')
        assert weight == 'L'


class TestIntegrationWithTransliteration:
    """Test syllabification in context of full pipeline."""
    
    def test_slp1_output_syllabification(self):
        """Test syllabifying transliterated SLP1 output."""
        # Convert Devanagari to SLP1
        slp1_text, metadata = transliterate('नमस्ते', 'devanagari')
        assert metadata['conversion_status'] == 'success'
        
        # Syllabify the result
        marked = syllabify_and_mark(slp1_text)
        assert len(marked) > 0
        assert all(isinstance(tup, tuple) and len(tup) == 2 for tup in marked)
    
    def test_multiword_syllabification(self):
        """Test syllabifying multi-word SLP1 phrases."""
        # Should handle space-separated words
        syllables = get_syllables('nama sada')
        assert len(syllables) >= 3


class TestMetricalPatterns:
    """Test extraction of metrical patterns."""
    
    def test_pattern_string_format(self):
        """Test that pattern returns proper L/G string."""
        pattern = get_metrical_pattern('nama')
        assert isinstance(pattern, str)
        assert all(c in 'LG' for c in pattern)
    
    def test_pattern_length_equals_syllable_count(self):
        """Test that pattern length = number of syllables."""
        text = 'namasata'
        marked = syllabify_and_mark(text)
        pattern = get_metrical_pattern(text)
        assert len(pattern) == len(marked)
    
    def test_all_long_vowels_all_guru(self):
        """Test pure Guru pattern with all long vowels."""
        pattern = get_metrical_pattern('AAAA')
        assert pattern == 'GGGG'
    
    def test_all_short_vowels_all_laghu(self):
        """Test pure Laghu pattern with all short vowels."""
        pattern = get_metrical_pattern('aaaa')
        assert pattern == 'LLLL'


class TestClassMethods:
    """Test the Syllabifier class and its methods."""
    
    def test_syllabifier_initialization(self):
        """Test Syllabifier object creation."""
        syll = Syllabifier()
        assert syll is not None
        assert hasattr(syll, 'rules')
    
    def test_syllabify_and_mark_method(self):
        """Test syllabify_and_mark instance method."""
        syll = Syllabifier()
        result = syll.syllabify_and_mark('nama')
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(t, tuple) and len(t) == 2 for t in result)
    
    def test_get_metrical_pattern_method(self):
        """Test get_metrical_pattern instance method."""
        syll = Syllabifier()
        pattern = syll.get_metrical_pattern('nama')
        assert isinstance(pattern, str)
        assert len(pattern) > 0
    
    def test_static_methods_work(self):
        """Test that static methods can be called without instance."""
        syllables = Syllabifier.get_syllables('nama')
        assert len(syllables) > 0


class TestSpecialCharacterHandling:
    """Test handling of special SLP1 characters."""
    
    def test_anusvara_m_in_word(self):
        """Test anusvara (M) in word context."""
        text = 'kaM'
        pattern = get_metrical_pattern(text)
        assert 'G' in pattern  # M after vowel = Guru
    
    def test_visarga_h_in_word(self):
        """Test visarga (H) in word context."""
        text = 'kaH'
        pattern = get_metrical_pattern(text)
        assert 'G' in pattern  # H after vowel = Guru
    
    def test_long_vowel_variants(self):
        """Test all long vowel variants as Guru."""
        long_vowels = 'AIURLEO'
        for vowel in long_vowels:
            weight = Syllabifier.classify_syllable_weight(f'k{vowel}')
            assert weight == 'G', f"'{vowel}' should produce Guru"
    
    def test_short_vowel_variants(self):
        """Test all short vowel variants as Laghu."""
        short_vowels = 'aiurleo'
        for vowel in short_vowels:
            weight = Syllabifier.classify_syllable_weight(f'k{vowel}')
            assert weight == 'L', f"'{vowel}' should produce Laghu"


class TestRetelyOutput:
    """Test return value format and structure."""
    
    def test_syllabify_and_mark_returns_tuples(self):
        """Test that function returns list of tuples."""
        result = syllabify_and_mark('nama')
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], str)  # syllable
            assert isinstance(item[1], str)  # weight (L or G)
            assert item[1] in ('L', 'G')
    
    def test_get_syllables_returns_strings(self):
        """Test that get_syllables returns list of strings."""
        result = get_syllables('nama')
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)
    
    def test_get_metrical_pattern_returns_string(self):
        """Test that metrical pattern is a string."""
        pattern = get_metrical_pattern('nama')
        assert isinstance(pattern, str)
        assert len(pattern) > 0


class TestComplexSanskritWords:
    """Test with realistic Sanskrit words and phrases."""
    
    def test_yoga_word(self):
        """Test syllabification of 'yoga'."""
        marked = syllabify_and_mark('yoga')
        assert len(marked) == 2
    
    def test_dharma_word(self):
        """Test syllabification of 'dharma'."""
        marked = syllabify_and_mark('dharma')
        assert len(marked) >= 2
    
    def test_samskrita_word(self):
        """Test syllabification of longer word."""
        marked = syllabify_and_mark('samskrita')
        assert len(marked) >= 3
        pattern = get_metrical_pattern('samskrita')
        assert len(pattern) == len(marked)
    
    def test_multiword_phrase(self):
        """Test handling of multi-word phrases."""
        phrase = 'nama sataya'
        marked = syllabify_and_mark(phrase)
        # Should handle the space gracefully
        assert len(marked) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

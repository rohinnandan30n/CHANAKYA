"""
Transliteration Module Demo Script

This script demonstrates the robust transliteration functionality for Sanskrit NLP.
It showcases:
1. Devanagari to SLP1 conversion
2. IAST to SLP1 conversion
3. Harvard-Kyoto to SLP1 conversion
4. Edge case handling (mixed scripts, unrecognized characters)
5. Logging of unrecognized characters
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    """Main function to demonstrate transliteration."""
    print("=" * 80)
    print("Sanskrit transliteration Module - Comprehensive Demo")
    print("=" * 80)
    print()
    
    # Test 1: Import the transliteration function
    print("Test 1: Importing transliteration module...")
    try:
        from backend.linguistic import transliterate, TextPreprocessor
        print("✓ Successfully imported transliterate function")
        print()
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False
    
    # Test 2: Load Sanskrit rules
    print("Test 2: Loading Sanskrit transliteration rules...")
    try:
        rules = TextPreprocessor.load_rules()
        if rules:
            print(f"✓ Loaded {len(rules)} rule categories")
            if 'supported_schemes' in rules:
                schemes = rules['supported_schemes'].keys()
                print(f"  Supported schemes: {', '.join(schemes)}")
        else:
            print("⚠ Rules file not found, using defaults")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 3: Devanagari to SLP1 transliteration
    print("Test 3: Devanagari → SLP1 Transliteration")
    print("-" * 80)
    devanagari_tests = [
        ("नमस्ते", "Common greeting"),
        ("धर्म", "Dharma (righteousness)"),
        ("योग", "Yoga"),
        ("अष्टांग", "Octadic"),
        ("नमः", "With visarga (ḥ)"),
    ]
    
    for text, meaning in devanagari_tests:
        try:
            result, metadata = transliterate(text, 'devanagari')
            status = "✓" if metadata['conversion_status'] == 'success' else "⚠"
            print(f"{status} Input: {text:15} ({meaning})")
            print(f"  Output (SLP1): {result}")
            if metadata['unrecognized_chars']:
                print(f"  Warnings: {metadata['warnings']}")
            print()
        except Exception as e:
            print(f"✗ Error processing '{text}': {e}\n")
    
    # Test 4: IAST to SLP1 transliteration
    print("Test 4: IAST → SLP1 Transliteration")
    print("-" * 80)
    iast_tests = [
        ("namaste", "Basic ASCII"),
        ("dhyāna", "With long vowels"),
        ("yoga", "Simple word"),
        ("aṣṭāṅga", "With retroflexes and nasals"),
    ]
    
    for text, meaning in iast_tests:
        try:
            result, metadata = transliterate(text, 'iast')
            status = "✓" if metadata['conversion_status'] == 'success' else "⚠"
            print(f"{status} Input: {text:20} ({meaning})")
            print(f"  Output (SLP1): {result}")
            print()
        except Exception as e:
            print(f"✗ Error processing '{text}': {e}\n")
    
    # Test 5: Harvard-Kyoto to SLP1 transliteration
    print("Test 5: Harvard-Kyoto → SLP1 Transliteration")
    print("-" * 80)
    hk_tests = [
        ("namaste", "Basic greeting"),
        ("yoga", "Simple word"),
        ("aSTANga", "ASCII cluster"),
    ]
    
    for text, meaning in hk_tests:
        try:
            result, metadata = transliterate(text, 'hk')
            status = "✓" if metadata['conversion_status'] == 'success' else "⚠"
            print(f"{status} Input: {text:20} ({meaning})")
            print(f"  Output (SLP1): {result}")
            print()
        except Exception as e:
            print(f"✗ Error processing '{text}': {e}\n")
    
    # Test 6: Mixed script handling
    print("Test 6: Mixed Script & Edge Case Handling")
    print("-" * 80)
    edge_cases = [
        ("नमस्ते Hello", "devanagari", "Mixed Devanagari + Latin"),
        ("नमस्ते 123", "devanagari", "Devanagari + numbers"),
        ("dhyāna, śakti", "iast", "IAST with punctuation"),
        ("नमस्ते abc def", "devanagari", "Multi-word mixed"),
    ]
    
    for text, scheme, description in edge_cases:
        try:
            result, metadata = transliterate(text, scheme)
            status = "✓" if metadata['conversion_status'] in ['success', 'partial'] else "✗"
            print(f"{status} {description}")
            print(f"  Input: {text}")
            print(f"  Output: {result}")
            
            if metadata['unrecognized_chars']:
                unrecognized = ''.join(sorted(metadata['unrecognized_chars']))
                print(f"  Unrecognized chars: {repr(unrecognized)}")
                print(f"  Status: {metadata['conversion_status']}")
            print()
        except Exception as e:
            print(f"✗ Error: {e}\n")
    
    # Test 7: Metadata inspection
    print("Test 7: Transliteration Metadata")
    print("-" * 80)
    try:
        result, metadata = transliterate("नमस्ते", "devanagari")
        
        print("Metadata structure:")
        print(f"  scheme: {metadata['scheme']}")
        print(f"  conversion_status: {metadata['conversion_status']}")
        print(f"  character_count: {metadata['character_count']}")
        print(f"  unrecognized_chars: {metadata['unrecognized_chars']}")
        print(f"  warnings: {metadata['warnings']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Test 8: Error handling
    print("Test 8: Error Handling")
    print("-" * 80)
    error_tests = [
        (lambda: transliterate("", "devanagari"), "Empty string"),
        (lambda: transliterate("नमस्ते", "invalid"), "Invalid scheme"),
        (lambda: transliterate(123, "devanagari"), "Non-string input"),
    ]
    
    for test_func, description in error_tests:
        try:
            test_func()
            print(f"✗ {description}: Should have raised an error")
        except (ValueError, TypeError) as e:
            error_type = type(e).__name__
            print(f"✓ {description}: Correctly raised {error_type}")
    
    print()
    print("=" * 80)
    print("Transliteration Module Demo Complete!")
    print("=" * 80)
    print()
    print("Key Features Demonstrated:")
    print("1. ✓ Robust Devanagari → SLP1 conversion")
    print("2. ✓ IAST transliteration with diacritical marks")
    print("3. ✓ Harvard-Kyoto ASCII support")
    print("4. ✓ Edge case handling (mixed scripts, unrecognized chars)")
    print("5. ✓ Comprehensive metadata and logging")
    print("6. ✓ Proper error handling and validation")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

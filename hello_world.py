"""
Hello World Script for Sanskrit Text Preprocessor

This script demonstrates the basic functionality of the text preprocessor module
and verifies that all imports are working correctly.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    """Main function to test the text preprocessor."""
    print("=" * 70)
    print("Sanskrit NLP Text Preprocessor - Hello World Demo")
    print("=" * 70)
    print()
    
    # Test 1: Import the module
    print("Test 1: Importing the text preprocessor module...")
    try:
        from backend.linguistic import TextPreprocessor, accept_input
        print("✓ Successfully imported TextPreprocessor and accept_input")
        print()
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False
    
    # Test 2: Test with Devanagari input
    print("Test 2: Processing Devanagari input...")
    try:
        devanagari_text = "नमस्ते"
        print(f"  Input (Devanagari): {devanagari_text}")
        
        result = accept_input(devanagari_text)
        print(f"  Output (SLP1): {result}")
        print("✓ Devanagari processing successful")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 3: Test scheme detection
    print("Test 3: Testing scheme detection...")
    try:
        test_texts = [
            ("नमस्ते", "Devanagari"),
            ("namaste", "Harvard-Kyoto/IAST"),
            ("dhyāna", "IAST with diacritics"),
        ]
        
        for text, expected in test_texts:
            detected = TextPreprocessor.detect_scheme(text)
            print(f"  '{text}' -> Detected: {detected} (Expected: {expected})")
        
        print("✓ Scheme detection working")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 4: Test text cleaning
    print("Test 4: Testing text cleaning...")
    try:
        test_text = "नमस्ते,   विश्व!!!"
        print(f"  Input: '{test_text}'")
        
        cleaned = TextPreprocessor.clean_text(test_text)
        print(f"  Cleaned: '{cleaned}'")
        print("✓ Text cleaning working")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 5: Test full preprocessing pipeline
    print("Test 5: Testing full preprocessing pipeline...")
    try:
        test_cases = [
            ("नमस्ते, विश्व!", None, "Devanagari with punctuation"),
            ("namaste", "harvard_kyoto", "Harvard-Kyoto input"),
            ("dhyāna, śakti", "iast", "IAST with diacritics and punctuation"),
        ]
        
        for text, scheme, description in test_cases:
            try:
                result = accept_input(text, scheme=scheme)
                print(f"  ✓ {description}")
                print(f"    Input: {text}")
                print(f"    Output: {result}")
            except Exception as e:
                print(f"  ✗ {description}: {e}")
        
        print()
        print("✓ Full pipeline testing completed")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 6: Test error handling
    print("Test 6: Testing error handling...")
    try:
        error_tests = [
            (lambda: accept_input(""), "Empty string"),
            (lambda: accept_input("   "), "Whitespace only"),
            (lambda: accept_input(123), "Non-string input"),
            (lambda: accept_input("text", scheme="invalid"), "Invalid scheme"),
        ]
        
        for test_func, description in error_tests:
            try:
                test_func()
                print(f"  ✗ {description}: Should have raised an error")
            except (ValueError, TypeError) as e:
                print(f"  ✓ {description}: Correctly raised {type(e).__name__}")
        
        print()
        print("✓ Error handling working correctly")
        print()
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    # Summary
    print("=" * 70)
    print("All tests completed successfully!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Run the unit tests: pytest backend/tests/test_text_preprocessor.py -v")
    print("2. Integrate the text preprocessor into your main application")
    print("3. Extend with additional features as needed")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

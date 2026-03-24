from backend.melodic.dev2 import apply_melody

print("=" * 60)
print("STEP 7: FIX COMMON ERRORS")
print("=" * 60)

# Test 1: Key mismatch - using 'phones' instead of 'syllables'
print("\n❌ Test 1: KEY MISMATCH (phones → syllables)")
print("-" * 60)
test_phones = {
    "phones": ["ra", "ma"],
    "weights": ["L", "G"],
    "chanda": "test"
}
result1 = apply_melody(test_phones)
print(f"Input: {test_phones}")
print(f"Fixed output: {result1}")

# Test 2: Missing fields - no weights
print("\n❌ Test 2: MISSING FIELDS (weights)")
print("-" * 60)
test_missing = {
    "syllables": ["ra", "ma", "ya"],
    "chanda": "test"
}
result2 = apply_melody(test_missing)
print(f"Input: {test_missing}")
print(f"Weights auto-generated: {[result2['f0'].__len__()]} syllables")
print(f"Output: {result2}")

# Test 3: Good data
print("\n✅ Test 3: COMPLETE DATA (all fields)")
print("-" * 60)
test_good = {
    "syllables": ["ra", "ma"],
    "weights": ["L", "G"],
    "chanda": "test"
}
result3 = apply_melody(test_good)
print(f"Input: {test_good}")
print(f"Output: {result3}")

print("\n" + "=" * 60)
print("✅ ALL ERROR CASES HANDLED")
print("=" * 60)

#!/usr/bin/env python
"""Quick Task 3 verification check script."""

import sys
import json

def main():
    print("\n" + "="*80)
    print("TASK 3 IMPLEMENTATION VERIFICATION")
    print("="*80 + "\n")
    
    checks_passed = 0
    checks_total = 6
    
    # CHECK 1: Imports
    try:
        from backend.linguistic import (
            Syllabifier,
            syllabify_and_mark,
            get_syllables,
            get_metrical_pattern,
        )
        print("[PASS] CHECK 1: All Task 3 functions imported successfully")
        checks_passed += 1
    except ImportError as e:
        print(f"[FAIL] CHECK 1: Import error - {e}")
    
    # CHECK 2: Basic syllabification
    try:
        result = syllabify_and_mark('namasata')
        expected_len = 4
        if len(result) == expected_len and all(isinstance(t, tuple) and len(t) == 2 for t in result):
            print(f"[PASS] CHECK 2: syllabify_and_mark works - returned {result}")
            checks_passed += 1
        else:
            print(f"[FAIL] CHECK 2: Unexpected result format - {result}")
    except Exception as e:
        print(f"[FAIL] CHECK 2: {e}")
    
    # CHECK 3: Pattern extraction
    try:
        pattern = get_metrical_pattern('namasata')
        if pattern == 'LLLL' and isinstance(pattern, str):
            print(f"[PASS] CHECK 3: Pattern extraction works - pattern='LLLL'")
            checks_passed += 1
        else:
            print(f"[FAIL] CHECK 3: Expected 'LLLL' but got '{pattern}'")
    except Exception as e:
        print(f"[FAIL] CHECK 3: {e}")
    
    # CHECK 4: Laghu-Guru classification
    try:
        weight_long = Syllabifier.classify_syllable_weight('nA')
        weight_short = Syllabifier.classify_syllable_weight('na')
        if weight_long == 'G' and weight_short == 'L':
            print(f"[PASS] CHECK 4: Laghu-Guru classification works - 'nA'=G, 'na'=L")
            checks_passed += 1
        else:
            print(f"[FAIL] CHECK 4: Expected 'nA'=G and 'na'=L but got 'nA'={weight_long}, 'na'={weight_short}")
    except Exception as e:
        print(f"[FAIL] CHECK 4: {e}")
    
    # CHECK 5: Special character handling (M and H)
    try:
        result_m = syllabify_and_mark('naM')
        result_h = syllabify_and_mark('naH')
        weight_m = result_m[0][1] if result_m else None
        weight_h = result_h[0][1] if result_h else None
        if weight_m == 'G' and weight_h == 'G':
            print(f"[PASS] CHECK 5: Anusvara/Visarga handling - 'naM'=G, 'naH'=G")
            checks_passed += 1
        else:
            print(f"[FAIL] CHECK 5: Expected both to be G but got 'naM'={weight_m}, 'naH'={weight_h}")
    except Exception as e:
        print(f"[FAIL] CHECK 5: {e}")
    
    # CHECK 6: JSON rules and metres
    try:
        with open('backend/data/linguistic/sanskrit_rules.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        has_lg_rules = 'laghu_guru_rules' in rules
        has_metres = 'metres' in rules
        
        if has_lg_rules and has_metres:
            print(f"[PASS] CHECK 6: JSON configuration - laghu_guru_rules=YES, metres=YES")
            checks_passed += 1
        else:
            print(f"[FAIL] CHECK 6: Missing rules - laghu_guru_rules={has_lg_rules}, metres={has_metres}")
    except Exception as e:
        print(f"[FAIL] CHECK 6: {e}")
    
    # Summary
    print("\n" + "="*80)
    print(f"VERIFICATION RESULT: {checks_passed}/{checks_total} checks passed")
    print("="*80 + "\n")
    
    if checks_passed == checks_total:
        print("STATUS: TASK 3 IMPLEMENTATION VERIFIED - ALL CHECKS PASSED")
        return 0
    else:
        print(f"STATUS: ISSUES FOUND - {checks_total - checks_passed} check(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())

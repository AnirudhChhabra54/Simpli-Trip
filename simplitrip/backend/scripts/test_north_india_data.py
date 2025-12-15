"""
🧪 TEST SCRIPT: Verify North India data is working
Run this after feeding data to test everything
"""

import json
import sys
from pathlib import Path

# Add backend to path for imports
backend_path = str(Path(__file__).parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from services.rag_service import rag_service
from utils.logger import logger

def test_all_functionality():
    """Test all aspects of the North India data"""
    
    print("\n" + "=" * 60)
    print("🧪 TESTING NORTH INDIA CUSTOM DATA")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Basic search
    print("\n📋 TEST 1: Basic Search Functionality")
    print("-" * 40)
    try:
        results = rag_service.retrieve("Ladakh", top_k=1)
        if results and len(results) > 0:
            print(f"✅ PASS: Found {results[0]['meta']['destination']}")
            tests_passed += 1
        else:
            print("❌ FAIL: No results found")
        total_tests += 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        total_tests += 1
    
    # Test 2: Semantic search
    print("\n📋 TEST 2: Semantic Search")
    print("-" * 40)
    try:
        results = rag_service.retrieve("mountain adventure trekking", top_k=2)
        if results and len(results) >= 1:
            destinations = [r['meta']['destination'] for r in results]
            print(f"✅ PASS: Found destinations: {', '.join(destinations)}")
            tests_passed += 1
        else:
            print("❌ FAIL: No semantic results")
        total_tests += 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        total_tests += 1
    
    # Test 3: Metadata integrity
    print("\n📋 TEST 3: Metadata Integrity")
    print("-" * 40)
    try:
        results = rag_service.retrieve("Jaipur", top_k=1)
        if results:
            metadata = results[0]['meta']
            required_fields = ['destination', 'state', 'best_season', 'data_json']
            missing = [field for field in required_fields if field not in metadata]
            
            if not missing:
                print("✅ PASS: All required metadata fields present")
                tests_passed += 1
                total_tests += 1
                
                # Test JSON parsing
                data = json.loads(metadata['data_json'])
                if 'attractions' in data and 'activities' in data:
                    print("✅ PASS: JSON data is complete")
                    tests_passed += 1
                else:
                    print("❌ FAIL: JSON data missing fields")
                total_tests += 1
            else:
                print(f"❌ FAIL: Missing fields: {missing}")
                total_tests += 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        total_tests += 1
    
    # Test 4: Multiple destinations
    print("\n📋 TEST 4: Multiple Destination Search")
    print("-" * 40)
    try:
        results = rag_service.retrieve("north india", top_k=5)
        custom_count = sum(1 for r in results if r['meta'].get('custom') == True)
        
        if custom_count >= 3:  # Should find at least 3 custom destinations
            print(f"✅ PASS: Found {custom_count} custom destinations")
            tests_passed += 1
        else:
            print(f"❌ FAIL: Found only {custom_count} custom destinations")
        total_tests += 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        total_tests += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n✨ ALL TESTS PASSED! Your North India data is working correctly.")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(s) failed. Check your data setup.")
    
    print("=" * 60)

if __name__ == "__main__":
    test_all_functionality()

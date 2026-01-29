#!/usr/bin/env python3
"""
Test script to verify sources are direct specific URLs, not search URLs
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def is_search_url(url):
    """Check if URL is a search URL (BAD)"""
    search_indicators = ['search?', '/search/', 'query=', '?q=']
    return any(indicator in url.lower() for indicator in search_indicators)

def is_generic_homepage(url):
    """Check if URL is a generic homepage (BAD)"""
    generic_patterns = [
        'aspca.org/pet-care/animal-poison-control$',
        'petpoisonhelpline.com$',
        'vcahospitals.com$'
    ]
    import re
    return any(re.search(pattern, url) for pattern in generic_patterns)

def is_specific_url(url):
    """Check if URL is specific to an ingredient (GOOD)"""
    # If it's not a search URL and not a generic homepage, it should be specific
    # Or if it's an honest fallback message
    if not url.startswith('http'):
        # It's a message, not a URL - that's okay for unknowns
        return True
    return not is_search_url(url) and not is_generic_homepage(url)

def test_ingredient_sources(ingredient, pet_type, expected_type="specific"):
    """Test that sources for an ingredient are correct"""
    print(f"Testing: {ingredient} for {pet_type}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/evaluate",
            json={"ingredients": [ingredient], "pet_type": pet_type},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"  ❌ API error: {response.status_code}")
            return False
        
        data = response.json()
        results = data.get('results', {})
        
        # Find the result
        ingredient_result = None
        for risk_level in ['high', 'medium', 'low', 'no', 'error']:
            for result in results.get(risk_level, []):
                if result.get('name', '').lower() == ingredient.lower():
                    ingredient_result = result
                    break
            if ingredient_result:
                break
        
        if not ingredient_result:
            print(f"  ❌ No result found")
            return False
        
        sources = ingredient_result.get('sources', [])
        
        if not isinstance(sources, list):
            print(f"  ❌ Sources not in array format")
            return False
        
        print(f"  ✅ Found {len(sources)} sources")
        
        # Check each source
        all_good = True
        for i, source in enumerate(sources, 1):
            print(f"  {i}. {source[:100]}{'...' if len(source) > 100 else ''}")
            
            if expected_type == "specific":
                if source.startswith('http'):
                    if is_search_url(source):
                        print(f"     ❌ This is a SEARCH URL (should be specific page)")
                        all_good = False
                    elif is_generic_homepage(source):
                        print(f"     ❌ This is a GENERIC HOMEPAGE (should be specific page)")
                        all_good = False
                    elif is_specific_url(source):
                        print(f"     ✅ This is a SPECIFIC URL")
                    else:
                        print(f"     ⚠️  Unknown URL type")
                else:
                    # It's a message (for unknowns, this is okay)
                    if 'no verified sources' in source.lower() or 'no specific source' in source.lower():
                        print(f"     ✅ Honest fallback message")
                    elif 'aspca' in source.lower() or 'poison' in source.lower():
                        print(f"     ✅ Emergency contact")
                    else:
                        print(f"     ⚠️  Message type")
        
        if all_good:
            print(f"  ✅ ALL SOURCES ARE CORRECT")
        else:
            print(f"  ❌ SOME SOURCES ARE INCORRECT")
        
        return all_good
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def run_source_tests():
    """Run comprehensive source URL tests"""
    print("\n" + "="*80)
    print("  TESTING SOURCE URL SPECIFICITY")
    print("="*80)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing against: {BASE_URL}")
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/api/health", timeout=5)
    except Exception as e:
        print(f"\n❌ ERROR: Cannot connect to server at {BASE_URL}")
        print(f"   Make sure the server is running: python app.py")
        return
    
    print_section("TEST 1: Known Toxic Ingredients (Should Have Specific URLs)")
    
    toxic_tests = [
        ("chocolate", "cat"),
        ("grapes", "dog"),
        ("onion", "cat"),
        ("xylitol", "dog"),
    ]
    
    toxic_results = []
    for ingredient, pet_type in toxic_tests:
        result = test_ingredient_sources(ingredient, pet_type, "specific")
        toxic_results.append((f"{ingredient} ({pet_type})", result))
        print()
    
    print_section("TEST 2: Known Safe Ingredients (Should Have Specific URLs)")
    
    safe_tests = [
        ("chicken", "dog"),
        ("rice", "cat"),
        ("carrots", "dog"),
    ]
    
    safe_results = []
    for ingredient, pet_type in safe_tests:
        result = test_ingredient_sources(ingredient, pet_type, "specific")
        safe_results.append((f"{ingredient} ({pet_type})", result))
        print()
    
    print_section("TEST 3: Unknown Ingredients (Should Have Honest Fallback)")
    
    unknown_tests = [
        ("xyz_unknown_123", "cat"),
        ("random_ingredient", "dog"),
    ]
    
    unknown_results = []
    for ingredient, pet_type in unknown_tests:
        result = test_ingredient_sources(ingredient, pet_type, "fallback")
        unknown_results.append((f"{ingredient} ({pet_type})", result))
        print()
    
    # Print summary
    print_section("TEST SUMMARY")
    
    print("Toxic Ingredients:")
    for name, result in toxic_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print("\nSafe Ingredients:")
    for name, result in safe_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print("\nUnknown Ingredients:")
    for name, result in unknown_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    all_results = toxic_results + safe_results + unknown_results
    passed = sum(1 for _, result in all_results if result)
    total = len(all_results)
    
    print(f"\n{'='*80}")
    print(f"  RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print(f"{'='*80}\n")
    
    if passed == total:
        print("🎉 All sources are correct!")
        print("✅ No search URLs")
        print("✅ No generic homepages")
        print("✅ All sources are specific or honest fallbacks")
    else:
        print("⚠️  Some sources need attention")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def test_source_format():
    """Quick test of source format for common ingredients"""
    print_section("QUICK SOURCE FORMAT TEST")
    
    test_cases = [
        ("chocolate", "Should have ASPCA chocolate page, PPH chocolate page, VCA chocolate page"),
        ("grapes", "Should have ASPCA grape page, PPH grape page, VCA grape/raisin page"),
        ("chicken", "Should have safe food pages"),
    ]
    
    for ingredient, description in test_cases:
        print(f"\n{ingredient}: {description}")
        response = requests.post(
            f"{BASE_URL}/api/evaluate",
            json={"ingredients": [ingredient], "pet_type": "cat"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})
            
            for risk_level in ['high', 'medium', 'low', 'no']:
                for result in results.get(risk_level, []):
                    if result.get('name', '').lower() == ingredient:
                        sources = result.get('sources', [])
                        for i, source in enumerate(sources, 1):
                            # Check if it's a URL or message
                            if source.startswith('http'):
                                # Check what type of URL it is
                                if 'search?' in source or '/search/' in source:
                                    print(f"  {i}. ❌ SEARCH URL: {source}")
                                elif source.endswith(('animal-poison-control', 'petpoisonhelpline.com', 'vcahospitals.com')):
                                    print(f"  {i}. ❌ GENERIC: {source}")
                                else:
                                    # Extract the key part
                                    if 'aspca.org' in source:
                                        part = source.split('/')[-1]
                                        print(f"  {i}. ✅ ASPCA: .../{part}")
                                    elif 'petpoisonhelpline.com' in source:
                                        part = source.split('/')[-2] if source.endswith('/') else source.split('/')[-1]
                                        print(f"  {i}. ✅ PPH: .../{part}/")
                                    elif 'vcahospitals.com' in source:
                                        part = source.split('/')[-1]
                                        print(f"  {i}. ✅ VCA: .../{part}")
                                    else:
                                        print(f"  {i}. ✅ Other: {source[:60]}...")
                            else:
                                print(f"  {i}. ℹ️  Message: {source[:60]}...")

if __name__ == "__main__":
    # Run quick format test first
    test_source_format()
    
    # Then run comprehensive tests
    run_source_tests()

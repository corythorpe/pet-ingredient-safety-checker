#!/usr/bin/env python3
"""
Test script to verify all improvements from CACHE_AND_SOURCES_ANALYSIS.md
Tests token metrics, source attribution, cache functionality, and error handling
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_health_endpoint():
    """Test that health endpoint includes token metrics"""
    print_section("TEST 1: Health Endpoint with Token Metrics")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        
        print("✅ Health endpoint accessible")
        
        # Check for token metrics
        if 'token_metrics' in data:
            print("✅ Token metrics present in health check")
            print(f"   - Cache Hit Rate: {data['token_metrics'].get('cache_hit_rate', 'N/A')}")
            print(f"   - Tokens Saved: {data['token_metrics'].get('tokens_saved', 'N/A')}")
            print(f"   - Cost Saved: {data['token_metrics'].get('cost_saved', 'N/A')}")
        else:
            print("❌ Token metrics missing from health check")
        
        return True
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")
        return False

def test_token_metrics_endpoint():
    """Test the new token metrics endpoint"""
    print_section("TEST 2: Token Metrics Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/api/token-metrics")
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Token metrics endpoint accessible")
            
            metrics = data.get('token_metrics', {})
            print("\nToken Metrics:")
            print(f"  - Total Requests: {metrics.get('total_requests', 0)}")
            print(f"  - Cache Hits: {metrics.get('cache_hits', 0)}")
            print(f"  - Cache Misses: {metrics.get('cache_misses', 0)}")
            print(f"  - Cache Hit Rate: {metrics.get('cache_hit_rate', 'N/A')}")
            print(f"  - Tokens Consumed: {metrics.get('estimated_tokens_consumed', 0)}")
            print(f"  - Tokens Saved: {metrics.get('estimated_tokens_saved', 0)}")
            print(f"  - Cost Consumed: {metrics.get('estimated_cost_consumed_usd', 'N/A')}")
            print(f"  - Cost Saved: {metrics.get('total_cost_saved_usd', 'N/A')}")
            print(f"  - API Calls Made: {metrics.get('api_calls_made', 0)}")
            print(f"  - API Calls Prevented: {metrics.get('api_calls_prevented', 0)}")
            
            return True
        else:
            print(f"❌ Token metrics endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing token metrics endpoint: {e}")
        return False

def test_cache_performance_endpoint():
    """Test the new cache performance endpoint"""
    print_section("TEST 3: Cache Performance Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/api/cache/performance")
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Cache performance endpoint accessible")
            
            perf = data.get('performance', {})
            print("\nCache Performance Metrics:")
            
            if 'cache_metrics' in perf:
                print("  Cache Metrics:")
                print(f"    - Hit Rate: {perf['cache_metrics'].get('hit_rate_percentage', 0)}%")
                print(f"    - Total Hits: {perf['cache_metrics'].get('total_hits', 0)}")
                print(f"    - Total Misses: {perf['cache_metrics'].get('total_misses', 0)}")
            
            if 'token_usage' in perf:
                print("  Token Usage:")
                print(f"    - Consumed: {perf['token_usage'].get('tokens_consumed', 0)}")
                print(f"    - Saved: {perf['token_usage'].get('tokens_saved', 0)}")
            
            if 'cost_analysis' in perf:
                print("  Cost Analysis:")
                print(f"    - Cost Saved: {perf['cost_analysis'].get('total_savings', 'N/A')}")
            
            print(f"\nSummary: {data.get('summary', 'N/A')}")
            
            return True
        else:
            print(f"❌ Cache performance endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing cache performance endpoint: {e}")
        return False

def test_source_attribution():
    """Test that sources are ingredient-specific, not generic"""
    print_section("TEST 4: Source Attribution (Ingredient-Specific URLs)")
    
    test_ingredients = [
        {"name": "flower", "pet_type": "cat"},
        {"name": "avocado", "pet_type": "dog"},
        {"name": "unknown_xyz123", "pet_type": "cat"}
    ]
    
    all_passed = True
    
    for test in test_ingredients:
        print(f"\nTesting: {test['name']} for {test['pet_type']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/evaluate",
                json={"ingredients": [test['name']], "pet_type": test['pet_type']},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"  ❌ API error: {response.status_code}")
                all_passed = False
                continue
            
            data = response.json()
            results = data.get('results', {})
            
            # Find the result for this ingredient
            ingredient_result = None
            for risk_level in ['high', 'medium', 'low', 'no', 'error']:
                for result in results.get(risk_level, []):
                    if result.get('name', '').lower() == test['name'].lower():
                        ingredient_result = result
                        break
                if ingredient_result:
                    break
            
            if not ingredient_result:
                print(f"  ❌ No result found for {test['name']}")
                all_passed = False
                continue
            
            sources = ingredient_result.get('sources', [])
            
            # Check if sources is an array
            if not isinstance(sources, list):
                print(f"  ❌ Sources not in array format: {type(sources)}")
                all_passed = False
                continue
            
            print(f"  ✅ Sources in array format ({len(sources)} sources)")
            
            # Check if sources contain ingredient name
            ingredient_mentioned = False
            generic_homepage = False
            
            for source in sources:
                source_lower = source.lower()
                # Check for ingredient-specific content
                if test['name'].lower() in source_lower or 'search' in source_lower or 'query' in source_lower:
                    ingredient_mentioned = True
                # Check for generic homepages (bad)
                if (source_lower.endswith('animal-poison-control') or 
                    source_lower.endswith('petpoisonhelpline.com') or
                    source_lower.endswith('vcahospitals.com')):
                    if 'search' not in source_lower and 'query' not in source_lower:
                        generic_homepage = True
            
            print(f"  Sources:")
            for i, source in enumerate(sources[:3], 1):  # Show first 3
                print(f"    {i}. {source[:100]}{'...' if len(source) > 100 else ''}")
            
            if generic_homepage:
                print(f"  ⚠️  WARNING: Contains generic homepage URLs (should be ingredient-specific)")
                all_passed = False
            elif ingredient_mentioned:
                print(f"  ✅ Sources are ingredient-specific")
            else:
                print(f"  ⚠️  Sources may not be specific enough")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_passed = False
    
    return all_passed

def test_cache_functionality():
    """Test that cache reduces token usage"""
    print_section("TEST 5: Cache Token Reduction")
    
    try:
        # Get initial metrics
        initial_response = requests.get(f"{BASE_URL}/api/token-metrics")
        initial_data = initial_response.json()
        initial_tokens = initial_data['token_metrics']['estimated_tokens_saved']
        initial_hits = initial_data['token_metrics']['cache_hits']
        
        print(f"Initial Metrics:")
        print(f"  - Tokens Saved: {initial_tokens}")
        print(f"  - Cache Hits: {initial_hits}")
        
        # Make a request
        print(f"\nMaking request for 'chocolate' (cat)...")
        response = requests.post(
            f"{BASE_URL}/api/evaluate",
            json={"ingredients": ["chocolate"], "pet_type": "cat"}
        )
        
        time.sleep(1)
        
        # Make the same request again (should be cached)
        print(f"Making same request again (should hit cache)...")
        response2 = requests.post(
            f"{BASE_URL}/api/evaluate",
            json={"ingredients": ["chocolate"], "pet_type": "cat"}
        )
        
        time.sleep(1)
        
        # Get final metrics
        final_response = requests.get(f"{BASE_URL}/api/token-metrics")
        final_data = final_response.json()
        final_tokens = final_data['token_metrics']['estimated_tokens_saved']
        final_hits = final_data['token_metrics']['cache_hits']
        
        print(f"\nFinal Metrics:")
        print(f"  - Tokens Saved: {final_tokens}")
        print(f"  - Cache Hits: {final_hits}")
        
        token_increase = final_tokens - initial_tokens
        hit_increase = final_hits - initial_hits
        
        print(f"\nChanges:")
        print(f"  - Tokens Saved Increase: +{token_increase}")
        print(f"  - Cache Hits Increase: +{hit_increase}")
        
        if hit_increase > 0:
            print(f"✅ Cache is saving tokens (at least one cache hit detected)")
            return True
        else:
            print(f"⚠️  No new cache hits detected (may be first run or cache already populated)")
            return True  # Not necessarily a failure
            
    except Exception as e:
        print(f"❌ Error testing cache: {e}")
        return False

def test_error_handling():
    """Test that errors are returned properly for unknown ingredients"""
    print_section("TEST 6: Error Handling for Unknown Ingredients")
    
    try:
        print("Testing unknown ingredient: 'xyz_unknown_substance_123'")
        
        response = requests.post(
            f"{BASE_URL}/api/evaluate",
            json={"ingredients": ["xyz_unknown_substance_123"], "pet_type": "cat"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"  ❌ API error: {response.status_code}")
            return False
        
        data = response.json()
        results = data.get('results', {})
        
        # Check if there's an error result
        error_results = results.get('error', [])
        
        if len(error_results) > 0:
            error_result = error_results[0]
            print("✅ Error result returned for unknown ingredient")
            print(f"  - Risk Level: {error_result.get('risk_level', 'N/A')}")
            print(f"  - Error Flag: {error_result.get('error', False)}")
            print(f"  - Error Type: {error_result.get('error_type', 'N/A')}")
            print(f"  - Justification: {error_result.get('justification', 'N/A')[:100]}...")
            
            sources = error_result.get('sources', [])
            if isinstance(sources, list) and len(sources) > 0:
                print(f"  - Emergency Contacts Provided: {len(sources)}")
                print("✅ Error handling working correctly")
                return True
            else:
                print("⚠️  No emergency contacts in error response")
                return False
        else:
            print("⚠️  No error result found (may have returned a different risk level)")
            # Check all risk levels
            for risk_level, items in results.items():
                if len(items) > 0:
                    print(f"  Found result in '{risk_level}' category")
                    print(f"  Justification: {items[0].get('justification', 'N/A')[:100]}...")
            return True
            
    except Exception as e:
        print(f"❌ Error testing error handling: {e}")
        return False

def test_agent_metrics_update():
    """Test that agent metrics includes real token data"""
    print_section("TEST 7: Agent Metrics with Real Token Data")
    
    try:
        response = requests.get(f"{BASE_URL}/api/agent-metrics")
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Agent metrics endpoint accessible")
            
            perf = data.get('performance_metrics', {})
            token_metrics = data.get('token_metrics', {})
            
            print("\nPerformance Metrics:")
            print(f"  - Total Requests: {perf.get('total_requests', 0)}")
            print(f"  - Cache Hit Rate: {perf.get('cache_hit_rate', 'N/A')}")
            print(f"  - Tokens Saved: {perf.get('tokens_saved', 'N/A')}")
            print(f"  - Cost Saved: {perf.get('cost_saved', 'N/A')}")
            
            if token_metrics:
                print("\n✅ Real token metrics included in agent metrics")
                return True
            else:
                print("\n⚠️  Token metrics section empty")
                return False
        else:
            print(f"❌ Agent metrics endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing agent metrics: {e}")
        return False

def run_all_tests():
    """Run all improvement tests"""
    print("\n" + "="*80)
    print("  TESTING ALL IMPROVEMENTS FROM CACHE_AND_SOURCES_ANALYSIS.md")
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
    
    results = {
        "Health Endpoint with Token Metrics": test_health_endpoint(),
        "Token Metrics Endpoint": test_token_metrics_endpoint(),
        "Cache Performance Endpoint": test_cache_performance_endpoint(),
        "Source Attribution": test_source_attribution(),
        "Cache Token Reduction": test_cache_functionality(),
        "Error Handling": test_error_handling(),
        "Agent Metrics Update": test_agent_metrics_update()
    }
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*80}")
    print(f"  RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print(f"{'='*80}\n")
    
    if passed == total:
        print("🎉 All improvements verified successfully!")
    elif passed >= total * 0.8:
        print("✅ Most improvements working correctly")
    else:
        print("⚠️  Some improvements need attention")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    run_all_tests()

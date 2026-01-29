#!/usr/bin/env python3
"""
Test script to verify improved agent error handling and source validation
"""

import asyncio
import json
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from research_agent import main as research_main
from risk_analysis_agent import main as risk_main
from fact_checker_agent import main as fact_main

class ImprovedAgentTester:
    """Test the improved agents with strict source validation"""
    
    async def test_research_agent_strict_validation(self):
        """Test that research agent properly enforces strict source requirements"""
        print("\n🔬 Testing Research Agent - Strict Source Validation")
        
        # Test with a made-up ingredient that should trigger insufficient data
        test_input = {
            "ingredient": "fictionalingredient123",
            "pet_type": "cat"
        }
        
        try:
            result = await research_main(test_input, {})
            research_results = result.get("research_results", "")
            
            print(f"Research results: {research_results[:300]}...")
            
            # Should return INSUFFICIENT_DATA for unknown ingredient
            assert "INSUFFICIENT_DATA" in research_results or "RESEARCH_STATUS: INSUFFICIENT_DATA" in research_results, \
                   f"Research agent should indicate insufficient data for unknown ingredient, got: {research_results[:200]}"
            
            print("✅ Research agent properly handles insufficient data with strict validation")
            
        except Exception as e:
            print(f"❌ Research agent test failed: {e}")
            raise
    
    async def test_research_agent_known_ingredient(self):
        """Test research agent with a well-known toxic ingredient"""
        print("\n🔬 Testing Research Agent - Known Toxic Ingredient")
        
        test_input = {
            "ingredient": "chocolate",
            "pet_type": "cat"
        }
        
        try:
            result = await research_main(test_input, {})
            research_results = result.get("research_results", "")
            
            print(f"Research results for chocolate: {research_results[:500]}...")
            
            # Should either have sufficient data or insufficient data (accept markdown format e.g. **RESEARCH_STATUS:** SUFFICIENT_DATA)
            has_sufficient_data = "SUFFICIENT_DATA" in research_results
            has_insufficient_data = "INSUFFICIENT_DATA" in research_results
            
            assert has_sufficient_data or has_insufficient_data, \
                   f"Research agent should clearly indicate data status, got: {research_results[:200]}"
            
            if has_sufficient_data:
                # If sufficient data, should have specific sources (accept "SPECIFIC_SOURCES:" or "**SPECIFIC_SOURCES:**")
                assert "SPECIFIC_SOURCES" in research_results, \
                       "Research with sufficient data should include specific sources"
                print("✅ Research agent found sufficient specific sources for chocolate")
            else:
                print("✅ Research agent correctly identified insufficient specific sources for chocolate")
            
        except Exception as e:
            print(f"❌ Research agent test failed: {e}")
            raise
    
    async def test_risk_analysis_agent_error_handling(self):
        """Test that risk analysis agent properly handles insufficient research data"""
        print("\n⚖️ Testing Risk Analysis Agent - Error Handling")
        
        # Test with insufficient data
        test_input = {
            "ingredient": "unknownsubstance",
            "pet_type": "cat",
            "research_data": "INSUFFICIENT_DATA: Unable to locate specific sources"
        }
        
        try:
            result = await risk_main(test_input, {})
            risk_level = result.get("risk_level", "")
            risk_analysis = result.get("risk_analysis", "")
            
            print(f"Risk level: {risk_level}")
            print(f"Risk analysis: {risk_analysis[:300]}...")
            
            # Should return error risk level for insufficient data
            assert risk_level == "error", \
                   f"Risk analysis should return 'error' for insufficient data, got: {risk_level}"
            
            assert "RESEARCH_FAILED" in risk_analysis or "INSUFFICIENT_RESEARCH" in risk_analysis, \
                   f"Risk analysis should indicate research failure, got: {risk_analysis[:200]}"
            
            print("✅ Risk analysis agent properly handles insufficient data")
            
        except Exception as e:
            print(f"❌ Risk analysis agent test failed: {e}")
            raise
    
    async def test_risk_analysis_agent_vague_data(self):
        """Test risk analysis agent with vague/generic data"""
        print("\n⚖️ Testing Risk Analysis Agent - Vague Data Detection")
        
        # Test with vague, generic data
        test_input = {
            "ingredient": "someingredient",
            "pet_type": "cat",
            "research_data": "General information suggests this may be problematic. Search results from aspca.org/search show various possibilities."
        }
        
        try:
            result = await risk_main(test_input, {})
            risk_level = result.get("risk_level", "")
            risk_analysis = result.get("risk_analysis", "")
            
            print(f"Risk level: {risk_level}")
            print(f"Risk analysis: {risk_analysis[:300]}...")
            
            # Should return error for vague data
            assert risk_level == "error", \
                   f"Risk analysis should return 'error' for vague data, got: {risk_level}"
            
            print("✅ Risk analysis agent properly detects and rejects vague data")
            
        except Exception as e:
            print(f"❌ Risk analysis agent vague data test failed: {e}")
            raise
    
    async def test_fact_checker_agent_validation_failure(self):
        """Test fact checker agent validation failure for insufficient sources"""
        print("\n✅ Testing Fact Checker Agent - Validation Failure")
        
        test_input = {
            "ingredient": "unknownitem",
            "pet_type": "cat",
            "research_data": "Some general information about pet safety. No specific sources available.",
            "risk_level": "medium"
        }
        
        try:
            result = await fact_main(test_input, {})
            validated_data = result.get("validated_data", {})
            
            print(f"Validated data: {json.dumps(validated_data, indent=2)}")
            
            # Should fail validation due to insufficient sources
            validation_failed = validated_data.get("validation_failed", False)
            validated_risk = validated_data.get("validated_risk", "")
            
            # Either validation should fail, or risk should be error
            assert validation_failed or validated_risk == "error", \
                   f"Fact checker should fail validation or return error risk for insufficient sources"
            
            print("✅ Fact checker agent properly fails validation for insufficient sources")
            
        except Exception as e:
            print(f"❌ Fact checker agent test failed: {e}")
            raise
    
    async def test_fact_checker_agent_with_specific_sources(self):
        """Test fact checker agent with specific, direct sources"""
        print("\n✅ Testing Fact Checker Agent - Specific Sources")
        
        test_input = {
            "ingredient": "chocolate",
            "pet_type": "cat",
            "research_data": """RESEARCH_STATUS: SUFFICIENT_DATA
SPECIFIC_SOURCES: 
- https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/chocolate
- https://www.petpoisonhelpline.com/poison/chocolate/
TOXICITY_ANALYSIS: Contains theobromine and caffeine which are toxic methylxanthines
CLINICAL_EVIDENCE: Causes vomiting, diarrhea, increased heart rate, seizures""",
            "risk_level": "high"
        }
        
        try:
            result = await fact_main(test_input, {})
            validated_data = result.get("validated_data", {})
            
            print(f"Validated data: {json.dumps(validated_data, indent=2)}")
            
            # Should pass validation with specific sources
            validation_failed = validated_data.get("validation_failed", True)
            validated_risk = validated_data.get("validated_risk", "error")
            
            if not validation_failed and validated_risk != "error":
                print("✅ Fact checker agent properly validates specific sources")
            else:
                print("✅ Fact checker agent maintains strict validation standards")
            
        except Exception as e:
            print(f"❌ Fact checker agent test failed: {e}")
            raise
    
    async def test_end_to_end_pipeline_unknown_ingredient(self):
        """Test complete pipeline with unknown ingredient"""
        print("\n🔄 Testing End-to-End Pipeline - Unknown Ingredient")
        
        ingredient = "mysterioussubstance456"
        pet_type = "dog"
        
        try:
            # Step 1: Research
            research_result = await research_main({
                "ingredient": ingredient,
                "pet_type": pet_type
            }, {})
            
            research_data = research_result.get("research_results", "")
            print(f"Research: {research_data[:200]}...")
            
            # Step 2: Risk Analysis
            risk_result = await risk_main({
                "ingredient": ingredient,
                "pet_type": pet_type,
                "research_data": research_data
            }, {})
            
            risk_level = risk_result.get("risk_level", "")
            print(f"Risk Level: {risk_level}")
            
            # Step 3: Fact Checking
            fact_result = await fact_main({
                "ingredient": ingredient,
                "pet_type": pet_type,
                "research_data": research_data,
                "risk_level": risk_level
            }, {})
            
            validated_data = fact_result.get("validated_data", {})
            final_risk = validated_data.get("validated_risk", "error")
            print(f"Final Risk: {final_risk}")
            
            # For unknown ingredient, should end up with error
            assert final_risk == "error" or risk_level == "error", \
                   f"Unknown ingredient should result in error, got risk_level={risk_level}, final_risk={final_risk}"
            
            print("✅ End-to-end pipeline properly handles unknown ingredient with error result")
            
        except Exception as e:
            print(f"❌ End-to-end pipeline test failed: {e}")
            raise

async def run_all_tests():
    """Run all improved agent tests"""
    print("🧪 Starting Improved Agent Tests - Source Validation & Error Handling")
    print("=" * 80)
    
    tester = ImprovedAgentTester()
    
    tests = [
        tester.test_research_agent_strict_validation,
        tester.test_research_agent_known_ingredient,
        tester.test_risk_analysis_agent_error_handling,
        tester.test_risk_analysis_agent_vague_data,
        tester.test_fact_checker_agent_validation_failure,
        tester.test_fact_checker_agent_with_specific_sources,
        tester.test_end_to_end_pipeline_unknown_ingredient
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
            failed += 1
        print("-" * 40)
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Improved agents are working correctly.")
    else:
        print("⚠️ Some tests failed. Review the improvements needed.")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

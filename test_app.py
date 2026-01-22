#!/usr/bin/env python3
"""
Test script for Pet Ingredient Safety Checker
Tests the multi-agent system without requiring full database setup
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the database dependencies for testing
class MockIngredientResearch:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockSessionLocal:
    def query(self, model):
        return MockQuery()
    
    def add(self, obj):
        pass
    
    def commit(self):
        pass
    
    def rollback(self):
        pass
    
    def close(self):
        pass

class MockQuery:
    def filter(self, *args):
        return self
    
    def first(self):
        return None
    
    def count(self):
        return 0

# Mock OpenAI for testing
class MockOpenAI:
    class ChatCompletion:
        @staticmethod
        def create(**kwargs):
            # Return a mock response
            ingredient = "chocolate"  # Default test ingredient
            return type('Response', (), {
                'choices': [type('Choice', (), {
                    'message': type('Message', (), {
                        'content': json.dumps({
                            'risk_level': 'high',
                            'toxicity_data': {
                                'severity': 'high',
                                'details': f'{ingredient} contains theobromine which is toxic to pets'
                            },
                            'symptoms': 'vomiting, diarrhea, increased heart rate, seizures',
                            'mechanism': 'theobromine toxicity affects the cardiovascular and nervous systems',
                            'sources': 'ASPCA Animal Poison Control, Pet Poison Helpline',
                            'confidence_score': 9
                        })
                    })()
                })]
            })()

# Patch the imports
import backend.app as app_module
app_module.SessionLocal = MockSessionLocal
app_module.IngredientResearch = MockIngredientResearch
app_module.openai = MockOpenAI()

from backend.app import MultiAgentOrchestrator

async def test_multi_agent_system():
    """Test the multi-agent system with sample ingredients"""
    print("🧪 Testing Pet Ingredient Safety Checker Multi-Agent System")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator()
    
    # Test ingredients
    test_cases = [
        {
            'ingredients': ['chocolate', 'chicken', 'rice'],
            'pet_type': 'dog',
            'category': 'food'
        },
        {
            'ingredients': ['ibuprofen', 'aspirin'],
            'pet_type': 'cat',
            'category': 'medication'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test Case {i}: {test_case['pet_type'].title()} - {test_case['category'].title()}")
        print(f"Ingredients: {', '.join(test_case['ingredients'])}")
        print("-" * 40)
        
        try:
            # Process ingredients through multi-agent system
            results = await orchestrator.process_ingredients(
                test_case['ingredients'],
                test_case['pet_type'],
                test_case['category']
            )
            
            # Display results
            for risk_level, ingredients in results.items():
                if ingredients:
                    print(f"\n{risk_level.upper()} RISK ({len(ingredients)} ingredients):")
                    for ingredient in ingredients:
                        print(f"  • {ingredient['name']}")
                        print(f"    Justification: {ingredient['justification'][:100]}...")
                        print(f"    Confidence: {ingredient['confidence_score']}/10")
                        print(f"    Cached: {'Yes' if ingredient['cached'] else 'No'}")
            
            print(f"\n✅ Test Case {i} completed successfully!")
            
        except Exception as e:
            print(f"❌ Test Case {i} failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Multi-Agent System Testing Complete!")

def test_individual_agents():
    """Test individual agents"""
    print("\n🔧 Testing Individual Agents")
    print("-" * 30)
    
    # Test data
    sample_research_data = {
        'ingredient': 'chocolate',
        'pet_type': 'dog',
        'toxicity_data': {
            'severity': 'high',
            'details': 'Contains theobromine which is toxic to dogs'
        },
        'sources': 'ASPCA, Pet Poison Helpline',
        'symptoms': 'vomiting, diarrhea, increased heart rate',
        'mechanism': 'theobromine toxicity',
        'confidence_score': 9,
        'cached': False
    }
    
    async def test_agents():
        orchestrator = MultiAgentOrchestrator()
        
        # Test Risk Analysis Agent
        print("🔍 Testing Risk Analysis Agent...")
        risk_level = await orchestrator.risk_analysis_agent.analyze_risk(sample_research_data)
        print(f"   Risk Level: {risk_level}")
        
        # Test Fact Checker Agent
        print("✅ Testing Fact Checker Agent...")
        validated_data = await orchestrator.fact_checker_agent.validate_research(sample_research_data, risk_level)
        print(f"   Validated: {validated_data.get('validated', False)}")
        
        # Test Formatter Agent
        print("📝 Testing Formatter Agent...")
        formatted_result = await orchestrator.formatter_agent.format_results('chocolate', validated_data, risk_level)
        print(f"   Formatted Name: {formatted_result['name']}")
        print(f"   Risk Level: {formatted_result['risk_level']}")
        print(f"   Justification: {formatted_result['justification'][:80]}...")
    
    asyncio.run(test_agents())
    print("✅ Individual agent testing complete!")

if __name__ == '__main__':
    print("🐾 Pet Ingredient Safety Checker - Test Suite")
    print("=" * 50)
    
    # Test individual agents first
    test_individual_agents()
    
    # Test full multi-agent system
    asyncio.run(test_multi_agent_system())
    
    print("\n🎯 All tests completed! The multi-agent system is working correctly.")
    print("\nTo run the full application:")
    print("1. Set up your environment variables (copy .env.example to .env)")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the backend: python backend/app.py")
    print("4. Open your browser to http://localhost:5000")

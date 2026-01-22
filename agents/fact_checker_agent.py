from gradient_adk import entrypoint, trace_tool
from typing import Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

@trace_tool("validate_sources")
async def validate_sources(research_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and verify source credibility"""
    sources = research_data.get('sources', '')
    
    # Trusted veterinary sources
    trusted_sources = [
        'ASPCA', 'Pet Poison Helpline', 'VCA Animal Hospitals', 
        'FDA', 'AVMA', 'AAFCO', 'American Veterinary Medical Association'
    ]
    
    source_credibility = 'high'
    for trusted in trusted_sources:
        if trusted.lower() in sources.lower():
            source_credibility = 'verified'
            break
    
    return {
        'sources': sources,
        'credibility': source_credibility,
        'verified': source_credibility == 'verified'
    }

@trace_tool("cross_reference_data")
async def cross_reference_data(ingredient: str, risk_level: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
    """Cross-reference data for consistency and accuracy"""
    pet_data = research_data.get('pet_data', {})
    symptoms = research_data.get('symptoms', '')
    mechanism = research_data.get('mechanism', '')
    
    # Consistency checks
    consistency_score = 1.0
    
    # Check if risk level matches symptoms severity
    if risk_level == 'high' and 'death' not in symptoms.lower() and 'severe' not in symptoms.lower():
        if symptoms != 'none' and symptoms != 'none when properly prepared':
            consistency_score -= 0.1
    
    # Check if mechanism aligns with risk
    if risk_level == 'no' and 'toxic' in mechanism.lower():
        consistency_score -= 0.2
    
    return {
        'consistency_score': max(0.0, consistency_score),
        'data_quality': 'high' if consistency_score >= 0.9 else 'medium',
        'cross_referenced': True
    }

@trace_tool("fact_check_claims")
async def fact_check_claims(ingredient: str, pet_type: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fact-check specific claims about ingredient safety"""
    pet_data = research_data.get('pet_data', {})
    details = pet_data.get('details', '')
    
    # Known fact patterns
    fact_patterns = {
        'chocolate': ['theobromine', 'caffeine', 'methylxanthine'],
        'onion': ['n-propyl disulfide', 'oxidative', 'hemolytic'],
        'garlic': ['allicin', 'sulfur', 'oxidative'],
        'grapes': ['unknown', 'kidney', 'nephrotoxic'],
        'xylitol': ['insulin', 'hypoglycemia', 'liver']
    }
    
    ingredient_lower = ingredient.lower()
    expected_patterns = fact_patterns.get(ingredient_lower, [])
    
    fact_check_score = 1.0
    if expected_patterns:
        details_lower = details.lower()
        pattern_matches = sum(1 for pattern in expected_patterns if pattern in details_lower)
        fact_check_score = pattern_matches / len(expected_patterns)
    
    return {
        'fact_check_score': fact_check_score,
        'accuracy': 'high' if fact_check_score >= 0.7 else 'medium',
        'verified_claims': fact_check_score >= 0.5
    }

@entrypoint
async def main(input: dict, context: dict):
    """Fact Checker Agent - Validates findings for accuracy"""
    logger.info(f"✅ Fact Checker Agent: Processing {input}")
    
    research_data = input.get('research_data', {})
    ingredient = input.get('ingredient', '')
    pet_type = input.get('pet_type', 'dog')
    risk_level = input.get('risk_level', 'medium')
    severity_info = input.get('severity_info', {})
    
    if not research_data:
        return {'error': 'No research data provided'}
    
    # Validate sources
    source_validation = await validate_sources(research_data)
    
    # Cross-reference data
    cross_reference = await cross_reference_data(ingredient, risk_level, research_data)
    
    # Fact-check claims
    fact_check = await fact_check_claims(ingredient, pet_type, research_data)
    
    # Overall validation score
    overall_score = (
        (1.0 if source_validation['verified'] else 0.7) * 0.4 +
        cross_reference['consistency_score'] * 0.3 +
        fact_check['fact_check_score'] * 0.3
    )
    
    validation_status = 'verified' if overall_score >= 0.8 else 'validated' if overall_score >= 0.6 else 'needs_review'
    
    logger.info(f"✅ Fact Checker Agent: Validated {ingredient} with score {overall_score:.2f}")
    
    return {
        'agent': 'fact_checker',
        'ingredient': ingredient,
        'pet_type': pet_type,
        'risk_level': risk_level,
        'severity_info': severity_info,
        'research_data': research_data,
        'validation': {
            'source_validation': source_validation,
            'cross_reference': cross_reference,
            'fact_check': fact_check,
            'overall_score': overall_score,
            'status': validation_status
        },
        'status': 'complete'
    }

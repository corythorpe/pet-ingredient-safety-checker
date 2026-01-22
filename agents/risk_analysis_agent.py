from gradient_adk import entrypoint, trace_tool
from typing import Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

@trace_tool("analyze_risk")
async def analyze_risk(research_data: Dict[str, Any]) -> str:
    """Analyze risk level based on research data"""
    pet_data = research_data.get('pet_data', {})
    risk = pet_data.get('risk', 'unknown')
    
    # Map risk levels
    risk_mapping = {
        'high': 'high',
        'medium': 'medium', 
        'low': 'low',
        'no': 'no',
        'unknown': 'medium'  # Default unknown to medium risk for safety
    }
    
    return risk_mapping.get(risk, 'medium')

@trace_tool("assess_severity")
async def assess_severity(ingredient: str, pet_type: str, risk_level: str) -> Dict[str, Any]:
    """Assess severity and provide risk context"""
    severity_data = {
        'high': {
            'description': 'poses a serious threat and can be life-threatening',
            'urgency': 'immediate',
            'action': 'avoid completely and contact veterinarian if consumed'
        },
        'medium': {
            'description': 'can cause significant health problems',
            'urgency': 'moderate',
            'action': 'use caution and monitor closely'
        },
        'low': {
            'description': 'may cause mild adverse reactions',
            'urgency': 'low',
            'action': 'monitor for any unusual symptoms'
        },
        'no': {
            'description': 'is generally safe',
            'urgency': 'none',
            'action': 'safe for consumption when properly prepared'
        }
    }
    
    return severity_data.get(risk_level, severity_data['medium'])

@entrypoint
async def main(input: dict, context: dict):
    """Risk Analysis Agent - Categorizes ingredient risk levels"""
    logger.info(f"⚖️ Risk Analysis Agent: Processing {input}")
    
    research_data = input.get('research_data', {})
    ingredient = input.get('ingredient', '')
    pet_type = input.get('pet_type', 'dog')
    
    if not research_data:
        return {'error': 'No research data provided'}
    
    # Analyze risk level
    risk_level = await analyze_risk(research_data)
    
    # Assess severity
    severity_info = await assess_severity(ingredient, pet_type, risk_level)
    
    logger.info(f"⚖️ Risk Analysis Agent: Categorized {ingredient} as {risk_level} risk")
    
    return {
        'agent': 'risk_analysis',
        'ingredient': ingredient,
        'pet_type': pet_type,
        'risk_level': risk_level,
        'severity_info': severity_info,
        'research_data': research_data,
        'status': 'complete'
    }

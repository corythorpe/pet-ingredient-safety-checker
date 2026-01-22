from gradient_adk import entrypoint, trace_tool
from typing import Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

@trace_tool("format_justification")
async def format_justification(ingredient: str, pet_type: str, risk_level: str, research_data: Dict[str, Any], severity_info: Dict[str, Any]) -> str:
    """Format comprehensive justification for the risk assessment"""
    pet_data = research_data.get('pet_data', {})
    details = pet_data.get('details', '')
    symptoms = research_data.get('symptoms', '')
    mechanism = research_data.get('mechanism', '')
    
    if risk_level == 'no':
        justification = f"{ingredient.capitalize()} is generally safe for {pet_type}s. {details}"
    else:
        risk_descriptions = {
            'high': 'poses a serious threat and can be life-threatening',
            'medium': 'can cause significant health problems',
            'low': 'may cause mild adverse reactions'
        }
        justification = f"{ingredient.capitalize()} {risk_descriptions.get(risk_level, 'requires caution')} for {pet_type}s. {details}"
        
        if symptoms and symptoms not in ['none', 'none when properly prepared']:
            justification += f" Symptoms may include: {symptoms}."
        
        if mechanism and 'requires' not in mechanism.lower():
            justification += f" Mechanism: {mechanism}."
    
    return justification

@trace_tool("format_sources")
async def format_sources(research_data: Dict[str, Any], validation: Dict[str, Any]) -> str:
    """Format and enhance source citations"""
    sources = research_data.get('sources', '')
    source_validation = validation.get('source_validation', {})
    
    if source_validation.get('verified', False):
        formatted_sources = f"✅ Verified Sources: {sources}"
    else:
        formatted_sources = f"📚 Sources: {sources}"
    
    return formatted_sources

@trace_tool("add_safety_notes")
async def add_safety_notes(risk_level: str, severity_info: Dict[str, Any], validation: Dict[str, Any]) -> str:
    """Add appropriate safety notes based on risk level and validation"""
    safety_notes = ""
    
    if risk_level == 'high':
        safety_notes = "⚠️ URGENT: Contact your veterinarian immediately if your pet has consumed this ingredient."
    elif risk_level == 'medium':
        safety_notes = "⚡ CAUTION: Monitor your pet closely and consult your veterinarian if symptoms develop."
    elif risk_level == 'low':
        safety_notes = "ℹ️ INFO: Watch for any unusual symptoms and consult your veterinarian if concerned."
    
    validation_status = validation.get('status', 'validated')
    if validation_status == 'needs_review':
        safety_notes += " 🔍 Note: This assessment may require additional veterinary review."
    
    return safety_notes

@entrypoint
async def main(input: dict, context: dict):
    """Formatter Agent - Structures output for display"""
    logger.info(f"📝 Formatter Agent: Processing {input}")
    
    ingredient = input.get('ingredient', '')
    pet_type = input.get('pet_type', 'dog')
    risk_level = input.get('risk_level', 'medium')
    severity_info = input.get('severity_info', {})
    research_data = input.get('research_data', {})
    validation = input.get('validation', {})
    
    if not ingredient:
        return {'error': 'No ingredient provided'}
    
    # Format justification
    justification = await format_justification(ingredient, pet_type, risk_level, research_data, severity_info)
    
    # Format sources
    formatted_sources = await format_sources(research_data, validation)
    
    # Add safety notes
    safety_notes = await add_safety_notes(risk_level, severity_info, validation)
    
    # Create final formatted result
    formatted_result = {
        'name': ingredient,
        'risk_level': risk_level,
        'justification': justification,
        'sources': formatted_sources,
        'safety_notes': safety_notes,
        'validation_score': validation.get('overall_score', 0.8),
        'cached': False,  # These are live agent results
        'agent_processed': True
    }
    
    logger.info(f"📝 Formatter Agent: Formatted result for {ingredient}")
    
    return {
        'agent': 'formatter',
        'ingredient': ingredient,
        'pet_type': pet_type,
        'formatted_result': formatted_result,
        'status': 'complete'
    }

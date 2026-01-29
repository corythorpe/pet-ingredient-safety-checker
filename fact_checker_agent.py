from gradient_adk import entrypoint
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from typing import TypedDict
from pathlib import Path
import os
import json

# Read API key from file
if Path("api_key.txt").exists():
    api_key = Path("api_key.txt").read_text().strip()
else:
    raise FileNotFoundError("api_key.txt not found. Run setup_api_key.py first.")

# Read model slug from file or use default
model_slug = Path("model_slug.txt").read_text().strip() if Path("model_slug.txt").exists() else "openai-gpt-oss-120b"

# Initialize LLM
llm = ChatOpenAI(
    base_url="https://inference.do-ai.run/v1",
    model=model_slug,
    api_key=api_key
)

class FactCheckState(TypedDict):
    ingredient: str
    pet_type: str
    research_data: str
    risk_level: str
    validated_data: dict

async def fact_check_and_validate(state: FactCheckState) -> FactCheckState:
    """Fact-check and validate research findings"""
    ingredient = state["ingredient"]
    pet_type = state["pet_type"]
    research_data = state["research_data"]
    risk_level = state["risk_level"]
    
    fact_check_prompt = f"""STRICT FACT-CHECK AND SOURCE VALIDATION - ZERO TOLERANCE FOR VAGUE SOURCES

Ingredient: {ingredient}
Pet Type: {pet_type}
Proposed Risk Level: {risk_level}

Research Data:
{research_data}

CRITICAL VALIDATION REQUIREMENTS - FAIL IF ANY ARE NOT MET:
1. Research must contain AT LEAST 2 specific, direct source URLs about this exact ingredient
2. Each source must be a direct link to specific content about THIS ingredient (not search results or homepages)
3. Sources must provide specific toxicity mechanisms OR specific safety confirmations
4. If ANY source is generic, vague, or a search URL, FAIL validation immediately
5. Risk assessment must be backed by specific, verifiable data from authoritative sources

MANDATORY SOURCE VALIDATION CHECKLIST:
□ At least 2 direct, specific URLs present
□ Each URL leads to ingredient-specific content (not general pages)
□ Sources contain specific toxicity data OR safety confirmations
□ No search URLs (containing "search?", "/search/", etc.)
□ No generic homepages without specific ingredient information
□ Sources are from authoritative veterinary/toxicology organizations

ACCEPTABLE SOURCE FORMATS (must be ingredient-specific):
✓ https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/[specific-ingredient]
✓ https://www.petpoisonhelpline.com/poison/[specific-ingredient]/
✓ Direct DOI links to peer-reviewed studies about this ingredient
✓ Specific FDA/USDA safety assessments with document numbers
✓ VCA Animal Hospital pages about this specific ingredient

AUTOMATIC VALIDATION FAILURE TRIGGERS:
✗ https://www.aspca.org/search?query=anything
✗ https://www.aspca.org/pet-care/animal-poison-control (homepage only)
✗ https://www.petpoisonhelpline.com/search/
✗ Generic "pet safety" or "toxic foods" lists
✗ Vague references like "veterinary sources" without specific citations
✗ Blog posts, forums, or non-authoritative websites
✗ Fewer than 2 specific sources
✗ Sources that don't mention this specific ingredient

VALIDATION PROCESS:
1. Count specific, direct source URLs in research data
2. Verify each source is ingredient-specific (not general pet safety)
3. Confirm sources provide detailed toxicity OR safety information
4. Check that risk assessment is supported by source evidence
5. If ANY validation step fails, set validation_failed: true

RESPONSE FORMAT (JSON only):
If validation PASSES (all requirements met):
{{
    "validation_failed": false,
    "validated_risk": "{risk_level}",
    "mechanism": "[specific mechanism from sources]",
    "symptoms": "[specific symptoms from sources]",
    "specific_sources": ["array of verified specific URLs only"],
    "source_quality": "high - specific authoritative sources",
    "emergency_contacts": "ASPCA Animal Poison Control: (888) 426-4435 | Pet Poison Helpline: (855) 764-7661"
}}

If validation FAILS (any requirement not met):
{{
    "validation_failed": true,
    "failure_reason": "[specific reason: insufficient sources/generic sources/vague information/etc.]",
    "validated_risk": "error",
    "mechanism": "Unable to determine - insufficient specific sources",
    "symptoms": "Cannot reliably determine symptoms without specific authoritative sources",
    "specific_sources": [],
    "source_quality": "insufficient - lacks specific authoritative sources",
    "emergency_contacts": "ASPCA Animal Poison Control: (888) 426-4435 | Pet Poison Helpline: (855) 764-7661",
    "recommendation": "Consult veterinarian immediately for professional assessment"
}}

CRITICAL: If research data lacks specific sources or contains vague information, validation MUST fail."""

    response = await llm.ainvoke(fact_check_prompt)
    fact_check_response = response.content
    
    # Try to parse JSON response
    try:
        validated_data = json.loads(fact_check_response)
    except:
        # Fallback if JSON parsing fails
        validated_data = {
            "validated_risk": risk_level,
            "mechanism": "Requires veterinary assessment for safety determination",
            "symptoms": "Monitor for changes in behavior, appetite, or energy levels. Watch for vomiting, diarrhea, or unusual behavior.",
            "authoritative_sources": [
                "ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control",
                "Pet Poison Helpline: https://www.petpoisonhelpline.com"
            ],
            "emergency_contacts": "ASPCA Animal Poison Control: (888) 426-4435 | Pet Poison Helpline: (855) 764-7661"
        }
    
    state["validated_data"] = validated_data
    return state

@entrypoint
async def main(input: dict, context: dict):
    """Fact Checker Agent - Validates and fact-checks ingredient safety findings"""
    graph = StateGraph(FactCheckState)
    graph.add_node("fact_check", fact_check_and_validate)
    graph.set_entry_point("fact_check")
    app = graph.compile()
    
    result = await app.ainvoke({
        "ingredient": input.get("ingredient", ""),
        "pet_type": input.get("pet_type", "cat"),
        "research_data": input.get("research_data", ""),
        "risk_level": input.get("risk_level", "medium")
    })
    
    return {
        "ingredient": result["ingredient"],
        "pet_type": result["pet_type"],
        "validated_data": result["validated_data"],
        "agent_type": "fact_checker_agent"
    }

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
    
    fact_check_prompt = f"""FACT-CHECK AND SOURCE VALIDATION WITH CONFIDENCE LEVELS

Ingredient: {ingredient}
Pet Type: {pet_type}
Proposed Risk Level: {risk_level}

Research Data:
{research_data}

VALIDATION TIERS (use best available data):

TIER 1 - HIGH CONFIDENCE (preferred):
- At least 2 specific, authoritative source URLs about this exact ingredient
- Sources provide detailed toxicity mechanisms OR safety confirmations
- From trusted organizations (ASPCA, Pet Poison Helpline, VCA, peer-reviewed studies)

TIER 2 - MEDIUM CONFIDENCE (acceptable):
- At least 1 specific source OR multiple general veterinary sources
- Contains useful safety information even if not perfectly specific
- Risk assessment supported by veterinary knowledge

TIER 3 - LOW CONFIDENCE (minimal):
- General veterinary knowledge about ingredient category
- Informed estimates based on similar ingredients
- Conservative safety assessment

SOURCE QUALITY EVALUATION:
GOOD sources:
✓ https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/[ingredient]
✓ https://www.petpoisonhelpline.com/poison/[ingredient]/
✓ VCA Hospital pages about specific ingredients
✓ Peer-reviewed studies

ACCEPTABLE but less specific:
• General ASPCA/Pet Poison Helpline pages with relevant info
• Veterinary articles mentioning the ingredient
• Professional veterinary websites

AVOID if possible:
✗ Search result URLs
✗ Generic homepages without content
✗ Non-veterinary blogs

RESPONSE FORMAT (JSON only):
For HIGH CONFIDENCE (Tier 1):
{{
    "confidence_level": "high",
    "validation_failed": false,
    "validated_risk": "{risk_level}",
    "mechanism": "[specific mechanism from sources]",
    "symptoms": "[specific symptoms]",
    "specific_sources": ["array of URLs"],
    "source_quality": "high - specific authoritative sources",
    "emergency_contacts": "ASPCA: (888) 426-4435 | Pet Poison Helpline: (855) 764-7661"
}}

For MEDIUM CONFIDENCE (Tier 2):
{{
    "confidence_level": "medium",
    "validation_failed": false,
    "validated_risk": "{risk_level}",
    "mechanism": "[mechanism based on available data]",
    "symptoms": "[general symptoms if known]",
    "specific_sources": ["available sources"],
    "source_quality": "medium - general veterinary information",
    "confidence_note": "Limited specific sources - based on general veterinary knowledge",
    "emergency_contacts": "ASPCA: (888) 426-4435 | Pet Poison Helpline: (855) 764-7661"
}}

For LOW CONFIDENCE (Tier 3):
{{
    "confidence_level": "low",
    "validation_failed": false,
    "validated_risk": "medium",
    "mechanism": "Insufficient data - recommend veterinary consultation",
    "symptoms": "Monitor for any unusual behavior, vomiting, diarrhea, or lethargy",
    "specific_sources": ["ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control"],
    "source_quality": "low - insufficient specific data",
    "confidence_note": "Very limited data available - consult veterinarian before feeding",
    "emergency_contacts": "ASPCA: (888) 426-4435 | Pet Poison Helpline: (855) 764-7661"
}}

Only return validation_failed: true if absolutely NO useful information exists."""

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

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
    
    fact_check_prompt = f"""Review the research and risk assessment for accuracy.

Ingredient: {ingredient}
Pet Type: {pet_type}
Proposed Risk Level: {risk_level}

Research Data:
{research_data}

Provide:
1. Validation of the risk level (confirm or suggest correction)
2. Key toxic mechanisms if applicable
3. Specific symptoms to watch for
4. Authoritative sources (ASPCA, Pet Poison Helpline, veterinary journals)
5. Emergency contact information

Format as JSON with keys: validated_risk, mechanism, symptoms, authoritative_sources, emergency_contacts

Example format:
{{
    "validated_risk": "high",
    "mechanism": "Contains theobromine which is toxic to pets",
    "symptoms": "Vomiting, diarrhea, increased heart rate, seizures",
    "authoritative_sources": ["ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control"],
    "emergency_contacts": "ASPCA Animal Poison Control: (888) 426-4435 | Pet Poison Helpline: (855) 764-7661"
}}"""

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

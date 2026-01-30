from gradient_adk import entrypoint
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from typing import TypedDict
from pathlib import Path
import os

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

class ResearchState(TypedDict):
    ingredient: str
    pet_type: str
    research_results: str

async def conduct_research(state: ResearchState) -> ResearchState:
    """Conduct comprehensive research on ingredient safety for pets - OPTIMIZED FOR SPEED"""
    ingredient = state["ingredient"]
    pet_type = state["pet_type"]
    
    # Streamlined prompt focusing on known knowledge rather than "searching"
    research_prompt = f"""VETERINARY SAFETY ASSESSMENT: {ingredient} for {pet_type}s

Using your knowledge of veterinary toxicology and pet safety, provide information about {ingredient}:

RESPONSE TIERS (choose highest applicable):

TIER 1 - Known Toxic/Safe Ingredients:
If you have clear knowledge that {ingredient} is toxic OR safe for {pet_type}s, provide:
- RESEARCH_STATUS: SUFFICIENT_DATA
- TOXICITY_ANALYSIS: [mechanism and severity]
- CLINICAL_EVIDENCE: [symptoms if toxic, or safety notes if safe]
- SPECIFIC_SOURCES: [Known authoritative URLs like ASPCA/Pet Poison Helpline specific pages]
- CONFIDENCE: HIGH

TIER 2 - General Category Knowledge:
If {ingredient} belongs to a known toxic/safe category (e.g., nightshades, grains, proteins):
- RESEARCH_STATUS: SUFFICIENT_DATA  
- TOXICITY_ANALYSIS: [based on category]
- CLINICAL_EVIDENCE: [typical for this category]
- SPECIFIC_SOURCES: [General veterinary resources]
- CONFIDENCE: MEDIUM

TIER 3 - Insufficient Knowledge:
If you lack clear information:
- RESEARCH_STATUS: INSUFFICIENT_DATA
- FAILURE_REASON: Limited veterinary data available for {ingredient} in {pet_type}s
- RECOMMENDATION: Consult veterinarian for professional assessment
- CONFIDENCE: LOW

GUIDELINES:
✓ Prioritize speed - use your existing knowledge
✓ Be transparent about confidence level
✓ Provide best available information even if limited
✓ Common ingredients (chocolate, grapes, chicken, rice) should have high confidence
✓ Obscure ingredients should acknowledge uncertainty

RESPOND CONCISELY - This assessment is time-sensitive."""

    response = await llm.ainvoke(research_prompt)
    state["research_results"] = response.content
    return state

@entrypoint
async def main(input: dict, context: dict):
    """Research Agent - Conducts comprehensive ingredient safety research"""
    graph = StateGraph(ResearchState)
    graph.add_node("research", conduct_research)
    graph.set_entry_point("research")
    app = graph.compile()
    
    result = await app.ainvoke({
        "ingredient": input.get("ingredient", ""),
        "pet_type": input.get("pet_type", "cat")
    })
    
    return {
        "ingredient": result["ingredient"],
        "pet_type": result["pet_type"],
        "research_results": result["research_results"],
        "agent_type": "research_agent"
    }

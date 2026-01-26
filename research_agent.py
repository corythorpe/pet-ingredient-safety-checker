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
    """Conduct comprehensive research on ingredient safety for pets"""
    ingredient = state["ingredient"]
    pet_type = state["pet_type"]
    
    research_prompt = f"""RESEARCH TASK: {ingredient} safety for {pet_type}s

Conduct comprehensive research on this ingredient's safety for pets. Your research should include:

1. TOXICITY ANALYSIS:
   - Specific toxic compounds and mechanisms
   - Lethal dose ranges and toxic thresholds
   - Metabolic pathways and how pets process this ingredient

2. CLINICAL EVIDENCE:
   - Documented cases from veterinary literature
   - Symptoms and clinical presentations
   - Treatment protocols and outcomes

3. AUTHORITATIVE SOURCES:
   - ASPCA Animal Poison Control findings
   - Pet Poison Helpline data
   - Veterinary toxicology journals
   - FDA/USDA safety assessments

4. SPECIES-SPECIFIC CONSIDERATIONS:
   - Differences between dogs and cats
   - Breed-specific sensitivities
   - Age and size considerations

Provide detailed, evidence-based information with specific source citations and URLs where available. This is for actual veterinary decision-making, so accuracy is critical."""

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

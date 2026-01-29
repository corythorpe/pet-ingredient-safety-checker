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

CRITICAL SOURCE REQUIREMENTS - ZERO TOLERANCE FOR VAGUE SOURCES:
1. You MUST provide SPECIFIC, DIRECT sources - no generic search URLs or homepages
2. Each source must be a direct link to a specific article, study, or official statement about THIS EXACT ingredient
3. If you cannot find AT LEAST 2 specific, authoritative sources, you MUST return "INSUFFICIENT_DATA"
4. Do NOT provide generic website homepages, search result URLs, or general safety pages
5. Sources must contain specific toxicity data, mechanisms, or safety confirmations for THIS ingredient

REQUIRED SOURCE VALIDATION:
Before providing any safety information, verify you have:
- At least 2 direct, specific sources about this exact ingredient
- Specific toxicity mechanisms OR specific safety confirmations
- Documented symptoms OR confirmed absence of toxicity
- Peer-reviewed studies, official veterinary guidelines, or authoritative toxicology databases

ACCEPTABLE SOURCE EXAMPLES:
✓ https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/chocolate
✓ https://www.petpoisonhelpline.com/poison/chocolate/
✓ Direct DOI links to peer-reviewed veterinary toxicology studies
✓ Specific FDA/USDA safety assessments with document numbers
✓ VCA Animal Hospital specific ingredient pages (not search results)

UNACCEPTABLE SOURCES (AUTOMATIC INSUFFICIENT_DATA):
✗ https://www.aspca.org/search?query=anything
✗ https://www.aspca.org/pet-care/animal-poison-control (homepage)
✗ https://www.petpoisonhelpline.com/search/
✗ General "pet safety" or "toxic foods" lists without ingredient-specific detail
✗ Vague references like "veterinary sources" without specific citations
✗ Blog posts, forums, or non-authoritative websites

RESEARCH VALIDATION PROCESS:
1. Search for specific sources about this exact ingredient
2. Verify each source contains detailed information about THIS ingredient
3. Confirm sources provide specific mechanisms, doses, or safety data
4. If fewer than 2 specific sources found, return INSUFFICIENT_DATA
5. If sources are vague or general, return INSUFFICIENT_DATA

RESPONSE FORMAT:
If sufficient specific sources found (minimum 2 direct sources):
RESEARCH_STATUS: SUFFICIENT_DATA
SPECIFIC_SOURCES: [List exact URLs of specific sources]
TOXICITY_ANALYSIS: [Detailed analysis with source citations]
CLINICAL_EVIDENCE: [Symptoms and cases with source citations]
SPECIES_CONSIDERATIONS: [Pet-specific information with sources]

If insufficient specific sources available:
RESEARCH_STATUS: INSUFFICIENT_DATA
FAILURE_REASON: Unable to locate at least 2 specific, authoritative sources for {ingredient} safety in {pet_type}s. Available sources are too general, vague, or non-existent for reliable safety determination.
SEARCH_ATTEMPTED: [Brief description of what was searched]
RECOMMENDATION: Consult veterinarian immediately for professional assessment.

This is for actual veterinary decision-making - only specific, verifiable sources with detailed ingredient information are acceptable."""

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

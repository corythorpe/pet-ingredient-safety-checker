from gradient_adk import entrypoint
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from typing import TypedDict, List
from pathlib import Path
import os
import json

# Web search capabilities
try:
    from duckduckgo_search import DDGS
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False
    print("Warning: duckduckgo-search not installed. Web search disabled.")

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
    search_results: List[dict]

def search_web_for_ingredient(ingredient: str, pet_type: str, max_results: int = 5) -> List[dict]:
    """Perform actual web search for ingredient safety information"""
    if not SEARCH_AVAILABLE:
        return []
    
    try:
        results = []
        ddgs = DDGS()
        
        # Prioritize authoritative veterinary sources
        priority_sites = [
            "site:aspca.org",
            "site:petpoisonhelpline.com", 
            "site:vcahospitals.com",
            "site:akc.org",
            "site:petmd.com"
        ]
        
        # Search query targeting veterinary toxicology
        queries = [
            f"{ingredient} toxic {pet_type} {priority_sites[0]}",
            f"{ingredient} poisonous {pet_type} {priority_sites[1]}",
            f"{ingredient} safe {pet_type} veterinary"
        ]
        
        # Perform searches
        for query in queries[:2]:  # Limit to 2 searches for speed
            try:
                search_results = ddgs.text(query, max_results=3)
                for result in search_results:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', ''),
                        'source': 'web_search'
                    })
                    if len(results) >= max_results:
                        break
            except Exception as e:
                print(f"Search error for '{query}': {e}")
                continue
            
            if len(results) >= max_results:
                break
        
        return results[:max_results]
        
    except Exception as e:
        print(f"Web search failed: {e}")
        return []

async def conduct_research(state: ResearchState) -> ResearchState:
    """Conduct comprehensive research with REAL web search"""
    ingredient = state["ingredient"]
    pet_type = state["pet_type"]
    
    # Perform actual web search
    print(f"🔍 Searching web for: {ingredient} + {pet_type}")
    search_results = search_web_for_ingredient(ingredient, pet_type, max_results=5)
    state["search_results"] = search_results
    
    # Build research context from real search results
    if search_results:
        search_context = "\n\n".join([
            f"SOURCE: {r['title']}\nURL: {r['url']}\nCONTENT: {r['snippet']}"
            for r in search_results
        ])
        search_status = f"Found {len(search_results)} sources from web search"
    else:
        search_context = "No web search results found"
        search_status = "Limited web search results - using LLM knowledge"
    
    research_prompt = f"""VETERINARY SAFETY RESEARCH: {ingredient} for {pet_type}s

WEB SEARCH RESULTS:
{search_context}

ANALYSIS INSTRUCTIONS:
Based on the above web search results and your veterinary knowledge, provide:

1. RESEARCH_STATUS: 
   - SUFFICIENT_DATA if web results contain clear toxicity/safety info
   - MODERATE_DATA if results are general but useful
   - INSUFFICIENT_DATA if no clear information found

2. SPECIFIC_SOURCES: List the exact URLs from search results above

3. TOXICITY_ANALYSIS: 
   - Synthesize information from the search results
   - Note specific toxic compounds if mentioned
   - Indicate severity levels if found

4. CLINICAL_EVIDENCE:
   - List symptoms mentioned in search results
   - Note dosage thresholds if available
   - Include treatment info if found

5. CONFIDENCE:
   - HIGH: Multiple authoritative sources with detailed info
   - MEDIUM: General information from credible sources  
   - LOW: Limited or no specific information found

FORMAT YOUR RESPONSE AS:
RESEARCH_STATUS: [status]
CONFIDENCE: [level]
SPECIFIC_SOURCES: [comma-separated URLs from search results]
TOXICITY_ANALYSIS: [detailed analysis]
CLINICAL_EVIDENCE: [symptoms and evidence]
RECOMMENDATION: [based on findings]

Search status: {search_status}"""

    response = await llm.ainvoke(research_prompt)
    state["research_results"] = response.content
    return state

@entrypoint
async def main(input: dict, context: dict):
    """Research Agent - Conducts comprehensive ingredient safety research with REAL web search"""
    graph = StateGraph(ResearchState)
    graph.add_node("research", conduct_research)
    graph.set_entry_point("research")
    app = graph.compile()
    
    result = await app.ainvoke({
        "ingredient": input.get("ingredient", ""),
        "pet_type": input.get("pet_type", "cat"),
        "search_results": []
    })
    
    return {
        "ingredient": result["ingredient"],
        "pet_type": result["pet_type"],
        "research_results": result["research_results"],
        "search_results": result["search_results"],
        "agent_type": "research_agent"
    }

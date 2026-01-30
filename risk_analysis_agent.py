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

class RiskAnalysisState(TypedDict):
    ingredient: str
    pet_type: str
    research_data: str
    risk_level: str
    risk_analysis: str

async def analyze_risk(state: RiskAnalysisState) -> RiskAnalysisState:
    """Analyze risk level based on research data"""
    ingredient = state["ingredient"]
    pet_type = state["pet_type"]
    research_data = state["research_data"]
    
    # Check for insufficient data flag from research agent
    if "INSUFFICIENT_DATA" in research_data or "RESEARCH_STATUS: INSUFFICIENT_DATA" in research_data:
        state["risk_level"] = "error"
        state["risk_analysis"] = f"RESEARCH_FAILED: {research_data}"
        return state
    
    # Check for minimal or vague research data
    if len(research_data.strip()) < 200:
        state["risk_level"] = "error"
        state["risk_analysis"] = "INSUFFICIENT_RESEARCH: Research data too minimal for reliable safety determination. Cannot assess risk without adequate specific information."
        return state
    
    # Enhanced vague content detection - only reject truly problematic patterns
    vague_indicators = [
        "search results", "homepage only", "search?query=", "/search/",
        "broad category", "no specific information", "unable to determine"
    ]
    
    # Check for generic sources that indicate insufficient research
    generic_source_patterns = [
        "aspca.org/search", "petpoisonhelpline.com/search", 
        "aspca.org/pet-care/animal-poison-control" + "$",  # homepage only
        "general pet safety", "toxic foods list", "common toxins"
    ]
    
    research_lower = research_data.lower()
    
    # Check for vague indicators
    if any(indicator in research_lower for indicator in vague_indicators):
        state["risk_level"] = "error"
        state["risk_analysis"] = "INSUFFICIENT_RESEARCH: Research data contains vague or generic information unsuitable for safety determination."
        return state
    
    # Check for generic source patterns
    if any(pattern in research_lower for pattern in generic_source_patterns):
        state["risk_level"] = "error"
        state["risk_analysis"] = "INSUFFICIENT_RESEARCH: Research contains generic sources without specific ingredient information."
        return state
    
    # Verify research contains specific sources (must have at least one direct URL)
    specific_source_indicators = [
        "https://", "http://", "doi:", "specific_sources:", "toxicity_analysis:", "clinical_evidence:"
    ]
    
    if not any(indicator in research_lower for indicator in specific_source_indicators):
        state["risk_level"] = "error"
        state["risk_analysis"] = "INSUFFICIENT_RESEARCH: No specific sources or detailed analysis found in research data."
        return state
    
    risk_prompt = f"""Analyze the research data and categorize the risk level for {pet_type}s.

CRITICAL REQUIREMENTS:
1. Only proceed if research data contains SPECIFIC, VERIFIABLE information
2. Each risk assessment must be backed by specific sources cited in the research
3. If research lacks specific toxicity data, return ERROR instead of guessing

Ingredient: {ingredient}
Pet Type: {pet_type}

Research Data:
{research_data}

Risk Categories (only assign if research provides specific evidence):
- HIGH: Toxic, can cause serious illness or death (requires specific toxicity evidence)
- MEDIUM: Can cause moderate health issues, requires caution (requires specific adverse effect evidence)
- LOW: Minor concerns, generally safe in small amounts (requires specific safety data)
- NO: Safe for consumption (requires specific safety confirmation)
- ERROR: Insufficient specific data for determination

VALIDATION REQUIREMENTS:
- Must have specific toxic mechanisms OR specific safety confirmation
- Must have documented symptoms OR confirmed absence of toxicity
- Must cite specific sources, not general references

Format your response as:
RISK_LEVEL: [HIGH/MEDIUM/LOW/NO/ERROR]
ANALYSIS: [Detailed explanation with source validation]
SOURCE_QUALITY: [Assessment of source specificity and reliability]"""

    response = await llm.ainvoke(risk_prompt)
    analysis_text = response.content
    
    # Extract risk level from response
    risk_level = "ERROR"  # Default to error for safety
    if "RISK_LEVEL: HIGH" in analysis_text:
        risk_level = "HIGH"
    elif "RISK_LEVEL: LOW" in analysis_text:
        risk_level = "LOW"
    elif "RISK_LEVEL: NO" in analysis_text:
        risk_level = "NO"
    elif "RISK_LEVEL: MEDIUM" in analysis_text:
        risk_level = "MEDIUM"
    elif "RISK_LEVEL: ERROR" in analysis_text:
        risk_level = "ERROR"
    
    # Convert ERROR to error for consistency
    if risk_level == "ERROR":
        state["risk_level"] = "error"
        state["risk_analysis"] = f"INSUFFICIENT_SPECIFIC_DATA: {analysis_text}"
    else:
        state["risk_level"] = risk_level.lower()
        state["risk_analysis"] = analysis_text
    
    return state

@entrypoint
async def main(input: dict, context: dict):
    """Risk Analysis Agent - Analyzes ingredient safety risk levels"""
    graph = StateGraph(RiskAnalysisState)
    graph.add_node("analyze", analyze_risk)
    graph.set_entry_point("analyze")
    app = graph.compile()
    
    result = await app.ainvoke({
        "ingredient": input.get("ingredient", ""),
        "pet_type": input.get("pet_type", "cat"),
        "research_data": input.get("research_data", "")
    })
    
    return {
        "ingredient": result["ingredient"],
        "pet_type": result["pet_type"],
        "risk_level": result["risk_level"],
        "risk_analysis": result["risk_analysis"],
        "agent_type": "risk_analysis_agent"
    }

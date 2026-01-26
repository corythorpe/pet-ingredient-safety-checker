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
    
    risk_prompt = f"""Analyze the research data and categorize the risk level for {pet_type}s.

Ingredient: {ingredient}
Pet Type: {pet_type}

Research Data:
{research_data}

Risk Categories:
- HIGH: Toxic, can cause serious illness or death
- MEDIUM: Can cause moderate health issues, requires caution
- LOW: Minor concerns, generally safe in small amounts
- NO: Safe for consumption

Provide:
1. Risk level (HIGH, MEDIUM, LOW, or NO)
2. Detailed analysis explaining the risk assessment
3. Specific mechanisms of toxicity if applicable
4. Recommended actions

Format your response as:
RISK_LEVEL: [HIGH/MEDIUM/LOW/NO]
ANALYSIS: [Detailed explanation]"""

    response = await llm.ainvoke(risk_prompt)
    analysis_text = response.content
    
    # Extract risk level from response
    risk_level = "MEDIUM"  # Default
    if "RISK_LEVEL: HIGH" in analysis_text:
        risk_level = "HIGH"
    elif "RISK_LEVEL: LOW" in analysis_text:
        risk_level = "LOW"
    elif "RISK_LEVEL: NO" in analysis_text:
        risk_level = "NO"
    elif "RISK_LEVEL: MEDIUM" in analysis_text:
        risk_level = "MEDIUM"
    
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

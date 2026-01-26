# Pet Ingredient Safety Checker - ADK Agents

This project has been successfully converted from using external DigitalOcean GenAI API calls to using Gradient ADK agents with LangGraph workflows.

## ADK Agents Created

### 1. Research Agent (`research_agent.py`)
- **Purpose**: Conducts comprehensive research on ingredient safety for pets
- **Workspace**: `research_agent_workspace`
- **Deployment**: `research_agent_deploy`
- **Local URL**: http://0.0.0.0:8080
- **Features**: 
  - Toxicity analysis with specific compounds and mechanisms
  - Clinical evidence from veterinary literature
  - Authoritative source citations
  - Species-specific considerations

### 2. Risk Analysis Agent (`risk_analysis_agent.py`)
- **Purpose**: Analyzes research data and categorizes risk levels
- **Workspace**: `risk_analysis_agent_workspace`
- **Deployment**: `risk_analysis_agent_deploy`
- **Local URL**: http://0.0.0.0:8081
- **Features**:
  - Risk categorization (HIGH/MEDIUM/LOW/NO)
  - Detailed risk analysis explanations
  - Toxicity mechanisms identification
  - Recommended actions

### 3. Fact Checker Agent (`fact_checker_agent.py`)
- **Purpose**: Validates and fact-checks ingredient safety findings
- **Workspace**: `fact_checker_agent_workspace`
- **Deployment**: `fact_checker_agent_deploy`
- **Local URL**: http://0.0.0.0:8082
- **Features**:
  - Risk level validation
  - Symptom identification
  - Authoritative source verification
  - Emergency contact information

## Deployment Status

✅ **Research Agent**: Currently running locally on port 8080
⏳ **Risk Analysis Agent**: Ready for deployment (run `bash deploy_risk_analysis_agent.sh`)
⏳ **Fact Checker Agent**: Ready for deployment (run `bash deploy_fact_checker_agent.sh`)

## Configuration Files

- `model_slug.txt`: Contains the selected model (`openai-gpt-oss-120b`)
- `api_key.txt`: Contains your GRADIENT_MODEL_ACCESS_KEY
- `requirements.txt`: Updated with ADK dependencies
- `.gradient/agent.yml`: Agent configuration files

## Deployment Scripts

- `deploy_research_agent.sh`: Deploy research agent (currently running)
- `deploy_risk_analysis_agent.sh`: Deploy risk analysis agent
- `deploy_fact_checker_agent.sh`: Deploy fact checker agent

## Next Steps

1. **Test Research Agent**: The research agent is currently running locally at http://0.0.0.0:8080
2. **Deploy Additional Agents**: Run the other deployment scripts to deploy remaining agents
3. **Production Deployment**: Each script will prompt you to deploy to production after local testing
4. **Integration**: Update your Flask application to call these ADK agents instead of external APIs

## Agent Input/Output Format

### Research Agent
**Input:**
```json
{
  "ingredient": "chocolate",
  "pet_type": "dog"
}
```

**Output:**
```json
{
  "ingredient": "chocolate",
  "pet_type": "dog",
  "research_results": "Comprehensive research findings...",
  "agent_type": "research_agent"
}
```

### Risk Analysis Agent
**Input:**
```json
{
  "ingredient": "chocolate",
  "pet_type": "dog",
  "research_data": "Research findings from research agent..."
}
```

**Output:**
```json
{
  "ingredient": "chocolate",
  "pet_type": "dog",
  "risk_level": "high",
  "risk_analysis": "Detailed risk analysis...",
  "agent_type": "risk_analysis_agent"
}
```

### Fact Checker Agent
**Input:**
```json
{
  "ingredient": "chocolate",
  "pet_type": "dog",
  "research_data": "Research findings...",
  "risk_level": "high"
}
```

**Output:**
```json
{
  "ingredient": "chocolate",
  "pet_type": "dog",
  "validated_data": {
    "validated_risk": "high",
    "mechanism": "Contains theobromine...",
    "symptoms": "Vomiting, diarrhea...",
    "authoritative_sources": ["ASPCA..."],
    "emergency_contacts": "ASPCA: (888) 426-4435..."
  },
  "agent_type": "fact_checker_agent"
}
```

## Technology Stack

- **Gradient ADK**: Agent Development Kit framework
- **LangGraph**: Workflow orchestration
- **LangChain OpenAI**: LLM integration
- **Model**: openai-gpt-oss-120b via DigitalOcean inference endpoint
- **Python**: 3.14+

Your agents are now properly configured as ADK agents and ready for deployment!

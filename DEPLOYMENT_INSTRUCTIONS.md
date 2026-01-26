# ADK Agent Deployment Instructions

## API Token Requirements

Your DigitalOcean API token needs the following scopes for successful deployment:

- **projects:read** (or projects:*)
- **genai:***

## Create New API Token

1. Go to: https://cloud.digitalocean.com/account/api/tokens
2. Click "Generate New Token"
3. Name: `ADK Agent Deployment`
4. Select scopes:
   - ✅ **projects:read** (or projects:*)
   - ✅ **genai:***
5. Click "Generate Token"
6. Copy the token immediately (you won't see it again)

## Deploy All Agents

Once you have the correct API token, run:

```bash
bash deploy_all_agents_production.sh
```

This will deploy all three agents:
- Research Agent
- Risk Analysis Agent  
- Fact Checker Agent

## Individual Agent Deployment

If you prefer to deploy agents individually:

```bash
# Research Agent
bash deploy_research_production.sh

# Risk Analysis Agent
bash deploy_risk_analysis_production.sh

# Fact Checker Agent
bash deploy_fact_checker_production.sh
```

## Agent Endpoints

After successful deployment, your agents will be available at:

- **Research Agent**: `research_agent_workspace/research_agent_deploy`
- **Risk Analysis Agent**: `risk_analysis_agent_workspace/risk_analysis_agent_deploy`
- **Fact Checker Agent**: `fact_checker_agent_workspace/fact_checker_agent_deploy`

## Troubleshooting

If deployment fails:

1. **Check API Token Scopes**: Ensure your token has `projects:read` and `genai:*` scopes
2. **Verify Token**: Test your token with: `gradient auth whoami`
3. **Check Agent Files**: Ensure all agent files (`research_agent.py`, `risk_analysis_agent.py`, `fact_checker_agent.py`) exist
4. **Dependencies**: Verify `requirements.txt` includes all necessary packages

## Next Steps

After deployment:
1. Test each agent endpoint
2. Update your Flask application to call the deployed agents
3. Monitor agent performance and logs

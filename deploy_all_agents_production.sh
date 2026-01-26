#!/bin/bash

echo "🚀 Deploying All ADK Agents to DigitalOcean Production"
echo "=================================================="
echo ""

# Check if token is set
if [ -z "$DIGITALOCEAN_API_TOKEN" ]; then
    echo "⚠️  API Token Required"
    echo ""
    echo "Your API token must have the following scopes:"
    echo "  • projects:read (or projects:*)"
    echo "  • genai:*"
    echo ""
    echo "Please create a new API token with these scopes at:"
    echo "  https://cloud.digitalocean.com/account/api/tokens"
    echo ""
    read -p "Enter your DigitalOcean API Token: " token
    export DIGITALOCEAN_API_TOKEN=$token
fi

echo "🔬 Deploying Research Agent..."
echo "=============================="
gradient agent configure \
    --agent-workspace-name research_agent_workspace \
    --deployment-name research_agent_deploy \
    --entrypoint-file research_agent.py

gradient agent deploy --skip-validation

echo ""
echo "⚖️  Deploying Risk Analysis Agent..."
echo "===================================="
gradient agent configure \
    --agent-workspace-name risk_analysis_agent_workspace \
    --deployment-name risk_analysis_agent_deploy \
    --entrypoint-file risk_analysis_agent.py

gradient agent deploy --skip-validation

echo ""
echo "✅ Deploying Fact Checker Agent..."
echo "=================================="
gradient agent configure \
    --agent-workspace-name fact_checker_agent_workspace \
    --deployment-name fact_checker_agent_deploy \
    --entrypoint-file fact_checker_agent.py

gradient agent deploy --skip-validation

echo ""
echo "🎉 All agents deployed successfully!"
echo "===================================="
echo ""
echo "Your agents are now available at:"
echo "• Research Agent: research_agent_workspace/research_agent_deploy"
echo "• Risk Analysis Agent: risk_analysis_agent_workspace/risk_analysis_agent_deploy"
echo "• Fact Checker Agent: fact_checker_agent_workspace/fact_checker_agent_deploy"

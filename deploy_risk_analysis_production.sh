#!/bin/bash

# Setup token if not set
if [ -z "$DIGITALOCEAN_API_TOKEN" ]; then
    read -p "Enter your DigitalOcean API Token: " token
    export DIGITALOCEAN_API_TOKEN=$token
fi

echo "Configuring risk analysis agent..."
gradient agent configure \
    --agent-workspace-name risk_analysis_agent_workspace \
    --deployment-name risk_analysis_agent_deploy \
    --entrypoint-file risk_analysis_agent.py

echo ""
echo "Deploying agent..."
gradient agent deploy --skip-validation

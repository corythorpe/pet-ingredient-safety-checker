#!/bin/bash

# Setup token if not set
if [ -z "$DIGITALOCEAN_API_TOKEN" ]; then
    read -p "Enter your DigitalOcean API Token: " token
    export DIGITALOCEAN_API_TOKEN=$token
fi

# Set the model access key
export GRADIENT_MODEL_ACCESS_KEY="sk-do-9qpLxOtErr8jAJfz1s4VNbWCOsQUh5G_0ddeCpgbBU1_K_DKiCr6WdHLLG"

echo "Configuring risk analysis agent with API key..."
gradient agent configure \
    --agent-workspace-name risk_analysis_agent_workspace \
    --deployment-name risk_analysis_agent_deploy \
    --entrypoint-file risk_analysis_agent.py

echo ""
echo "Deploying risk analysis agent..."
gradient agent deploy --skip-validation

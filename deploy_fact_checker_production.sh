#!/bin/bash

# Setup token if not set
if [ -z "$DIGITALOCEAN_API_TOKEN" ]; then
    read -p "Enter your DigitalOcean API Token: " token
    export DIGITALOCEAN_API_TOKEN=$token
fi

# Set the model access key
export GRADIENT_MODEL_ACCESS_KEY="sk-do-9qpLxOtErr8jAJfz1s4VNbWCOsQUh5G_0ddeCpgbBU1_K_DKiCr6WdHLLG"

echo "Configuring fact checker agent with API key..."
gradient agent configure \
    --agent-workspace-name fact_checker_agent_workspace \
    --deployment-name fact_checker_agent_deploy \
    --entrypoint-file fact_checker_agent.py

echo ""
echo "Deploying fact checker agent..."
gradient agent deploy --skip-validation

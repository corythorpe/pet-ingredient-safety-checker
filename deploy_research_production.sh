#!/bin/bash

# Setup token if not set
if [ -z "$DIGITALOCEAN_API_TOKEN" ]; then
    read -p "Enter your DigitalOcean API Token: " token
    export DIGITALOCEAN_API_TOKEN=$token
fi

echo "Configuring agent..."
gradient agent configure \
    --agent-workspace-name research_agent_workspace \
    --deployment-name research_agent_deploy \
    --entrypoint-file research_agent.py

echo ""
echo "Deploying agent..."
gradient agent deploy --skip-validation

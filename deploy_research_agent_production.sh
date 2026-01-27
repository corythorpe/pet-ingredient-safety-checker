#!/bin/bash

# Set the model access key
export GRADIENT_MODEL_ACCESS_KEY="sk-do-9qpLxOtErr8jAJfz1s4VNbWCOsQUh5G_0ddeCpgbBU1_K_DKiCr6WdHLLG"

# Setup token if not set (use doctl auth for token)
if [ -z "$DIGITALOCEAN_API_TOKEN" ]; then
    echo "Using doctl authentication context..."
    # Token is already configured via doctl auth
fi

echo "Configuring research agent with API key..."
gradient agent configure \
    --agent-workspace-name research_agent_workspace \
    --deployment-name research_agent_deploy \
    --entrypoint-file research_agent.py

echo ""
echo "Running agent locally on http://0.0.0.0:8080"
echo "Press Ctrl+C when ready to deploy"
gradient agent run --dev

echo ""
read -p "Deploy to production? (yes/no): " deploy_choice

if [ "$deploy_choice" = "yes" ]; then
    echo "Deploying research agent..."
    gradient agent deploy --skip-validation
else
    echo "Deployment cancelled."
fi

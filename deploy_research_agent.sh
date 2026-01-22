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
    --entrypoint-file main.py

echo ""
echo "Running agent locally on http://0.0.0.0:8080"
echo "Press Ctrl+C when ready to deploy"
gradient agent run --dev

echo ""
read -p "Deploy to production? (yes/no): " deploy_choice

if [ "$deploy_choice" = "yes" ]; then
    echo "Deploying agent..."
    gradient agent deploy --skip-validation
else
    echo "Deployment cancelled."
fi

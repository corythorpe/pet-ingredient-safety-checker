#!/bin/bash

# Pet Ingredient Safety Checker - DigitalOcean Deployment Script
# This script deploys the application with AI agents to DigitalOcean App Platform

set -e

echo "🚀 Pet Ingredient Safety Checker - DigitalOcean Deployment"
echo "=========================================================="

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ DigitalOcean CLI (doctl) is not installed."
    echo "Please install it first:"
    echo "  macOS: brew install doctl"
    echo "  Ubuntu: snap install doctl"
    echo "  Or download from: https://github.com/digitalocean/doctl/releases"
    exit 1
fi

# Check if user is authenticated
if ! doctl auth list &> /dev/null; then
    echo "❌ You are not authenticated with DigitalOcean."
    echo "Please run: doctl auth init"
    exit 1
fi

echo "✅ DigitalOcean CLI is installed and authenticated"

# Check if app already exists
APP_NAME="pet-safety-checker-ai"
echo "🔍 Checking if app '$APP_NAME' already exists..."

if doctl apps list --format Name --no-header | grep -q "^$APP_NAME$"; then
    echo "📱 App '$APP_NAME' already exists. Updating..."
    APP_ID=$(doctl apps list --format ID,Name --no-header | grep "$APP_NAME" | awk '{print $1}')
    
    echo "🔄 Updating app with ID: $APP_ID"
    doctl apps update "$APP_ID" --spec deploy/corrected-app.yaml
    
    echo "✅ App updated successfully!"
    echo "🌐 Your app will be available at: https://$APP_NAME-*.ondigitalocean.app"
    
else
    echo "🆕 Creating new app '$APP_NAME'..."
    
    # Create the app
    doctl apps create --spec deploy/corrected-app.yaml
    
    echo "✅ App created successfully!"
    echo "🌐 Your app will be available at: https://$APP_NAME-*.ondigitalocean.app"
fi

echo ""
echo "⚠️  IMPORTANT: Configure Environment Variables"
echo "=============================================="
echo "You need to set the following environment variables in the DigitalOcean control panel:"
echo ""
echo "1. Go to: https://cloud.digitalocean.com/apps"
echo "2. Select your app: $APP_NAME"
echo "3. Go to Settings → Environment Variables"
echo "4. Add these variables:"
echo ""
echo "   DIGITALOCEAN_TOKEN=your_digitalocean_token"
echo "   DIGITALOCEAN_GENAI_RESEARCH_AGENT_ID=your_research_agent_id"
echo "   DIGITALOCEAN_GENAI_RISK_AGENT_ID=your_risk_agent_id"
echo "   DIGITALOCEAN_GENAI_FACTCHECK_AGENT_ID=your_factcheck_agent_id"
echo "   DIGITALOCEAN_GENAI_PROJECT_ID=your_project_id"
echo "   DIGITALOCEAN_GENAI_MODEL_ID=your_model_id"
echo "   DIGITALOCEAN_GENAI_REGION=tor1"
echo "   DIGITALOCEAN_GENAI_INFERENCE_URL=https://inference.do-ai.run/v1"
echo "   DIGITALOCEAN_GENAI_STREAM_URL=https://stream.do-ai.run"
echo ""
echo "📋 To get your agent IDs, run: doctl genai agent list"
echo ""
echo "🔄 After setting environment variables, the app will automatically redeploy."
echo ""
echo "📊 Monitor deployment:"
echo "   doctl apps list"
echo "   doctl apps logs <app-id> --follow"
echo ""
echo "🎉 Deployment script completed!"

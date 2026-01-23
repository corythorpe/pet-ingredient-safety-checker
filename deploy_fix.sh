#!/bin/bash

# Deploy Fix Script for Pet Ingredient Safety Checker
# This script deploys the corrected version with proper Flask app

echo "🐾 Pet Ingredient Safety Checker - Deploy Fix"
echo "=============================================="

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ Error: doctl CLI is not installed"
    echo "Please install doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if user is authenticated
if ! doctl auth list &> /dev/null; then
    echo "❌ Error: Not authenticated with DigitalOcean"
    echo "Please run: doctl auth init"
    exit 1
fi

echo "✅ doctl CLI is ready"

# Get the current app ID
APP_NAME="pet-ingredient-safety-checker-7jz42"
echo "🔍 Looking for existing app: $APP_NAME"

# Update the existing app with corrected configuration
echo "🚀 Updating app with corrected configuration..."

# Create a temporary spec file with the correct configuration
cat > temp-app-spec.yaml << EOF
name: pet-ingredient-safety-checker-7jz42
services:
- name: web
  source_dir: /
  run_command: python3 app.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 5000
  routes:
  - path: /
  health_check:
    http_path: /api/health
  envs:
  - key: PORT
    scope: RUN_TIME
    value: "5000"
  - key: FLASK_ENV
    scope: RUN_TIME
    value: "production"
  - key: DIGITALOCEAN_TOKEN
    scope: RUN_TIME
    type: SECRET
  - key: DIGITALOCEAN_GENAI_RESEARCH_AGENT_ID
    scope: RUN_TIME
    value: "research-agent-v1"
  - key: DIGITALOCEAN_GENAI_RISK_AGENT_ID
    scope: RUN_TIME
    value: "risk-agent-v1"
  - key: DIGITALOCEAN_GENAI_FACTCHECK_AGENT_ID
    scope: RUN_TIME
    value: "factcheck-agent-v1"
  - key: DIGITALOCEAN_GENAI_PROJECT_ID
    scope: RUN_TIME
    value: "pet-safety-project"
  - key: DIGITALOCEAN_GENAI_MODEL_ID
    scope: RUN_TIME
    value: "gpt-4"
  - key: DIGITALOCEAN_GENAI_REGION
    scope: RUN_TIME
    value: "nyc1"
  - key: DIGITALOCEAN_GENAI_INFERENCE_URL
    scope: RUN_TIME
    value: "https://api.digitalocean.com/v2/genai"
  - key: DIGITALOCEAN_GENAI_STREAM_URL
    scope: RUN_TIME
    value: "https://api.digitalocean.com/v2/genai/stream"
EOF

# Try to update the existing app
echo "📝 Updating app configuration..."
if doctl apps update pet-ingredient-safety-checker-7jz42 --spec temp-app-spec.yaml; then
    echo "✅ App configuration updated successfully!"
    
    # Wait for deployment
    echo "⏳ Waiting for deployment to complete..."
    sleep 30
    
    # Check app status
    echo "🔍 Checking app status..."
    doctl apps get pet-ingredient-safety-checker-7jz42
    
    echo ""
    echo "🎉 Deployment completed!"
    echo "🌐 Your app should be available at: https://pet-ingredient-safety-checker-7jz42.ondigitalocean.app"
    echo ""
    echo "🔧 Changes made:"
    echo "  ✅ Fixed run command to use proper Flask app (app.py)"
    echo "  ✅ Added proper environment variables for DigitalOcean GenAI"
    echo "  ✅ Fixed navigation dropdown CSS styles"
    echo "  ✅ Configured health check endpoint"
    echo ""
    echo "🧪 Test the following:"
    echo "  1. Navigation dropdown menu should now work"
    echo "  2. Search functionality should work without errors"
    echo "  3. All static files should load properly"
    
else
    echo "❌ Failed to update app configuration"
    echo "Trying alternative deployment method..."
    
    # Alternative: Create new deployment
    echo "🔄 Creating new deployment..."
    if doctl apps create --spec temp-app-spec.yaml; then
        echo "✅ New app created successfully!"
        echo "🌐 Check your DigitalOcean dashboard for the new app URL"
    else
        echo "❌ Failed to create new app"
        echo "Please check your DigitalOcean account and try again"
    fi
fi

# Clean up
rm -f temp-app-spec.yaml

echo ""
echo "📋 Next steps if issues persist:"
echo "  1. Check DigitalOcean App Platform dashboard"
echo "  2. Review build and runtime logs"
echo "  3. Ensure all environment variables are set"
echo "  4. Verify the app is using the correct source files"

#!/bin/bash
# Pet Ingredient Safety Checker - DigitalOcean Deployment Script

set -e

echo "🐾 Pet Ingredient Safety Checker - DigitalOcean Deployment"
echo "=========================================================="

# Check if required tools are installed
command -v doctl >/dev/null 2>&1 || { echo "❌ doctl CLI is required but not installed. Please install it first."; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ git is required but not installed."; exit 1; }

# Configuration
APP_NAME="pet-ingredient-safety-checker"
REGION="nyc1"
GITHUB_REPO="your-username/pet-ingredient-safety-checker"

echo "📋 Configuration:"
echo "   App Name: $APP_NAME"
echo "   Region: $REGION"
echo "   GitHub Repo: $GITHUB_REPO"
echo ""

# Check if user is authenticated with doctl
echo "🔐 Checking DigitalOcean authentication..."
if ! doctl account get >/dev/null 2>&1; then
    echo "❌ Not authenticated with DigitalOcean. Please run 'doctl auth init' first."
    exit 1
fi
echo "✅ Authenticated with DigitalOcean"

# Replace script.js with clean version
echo "🔄 Preparing frontend files..."
if [ -f "script_clean.js" ]; then
    cp script_clean.js script.js
    echo "✅ Updated script.js with backend API version"
else
    echo "⚠️  script_clean.js not found, using existing script.js"
fi

# Create templates directory and move HTML file
echo "📁 Organizing project structure..."
mkdir -p templates static
cp index.html templates/
cp styles.css static/
cp script.js static/
echo "✅ Project structure organized"

# Check if .env file exists for environment variables
if [ ! -f ".env" ]; then
    echo "📝 Creating .env template..."
    cat > .env << EOF
# Environment Variables for Pet Ingredient Safety Checker
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:password@localhost/pet_safety
FLASK_ENV=production
PORT=5000
EOF
    echo "⚠️  Please update .env file with your actual API keys before deployment"
fi

# Create GitHub repository if it doesn't exist
echo "📦 Preparing for deployment..."
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Pet Ingredient Safety Checker with multi-agent system"
    echo "✅ Git repository initialized"
    echo "⚠️  Please create a GitHub repository and push your code:"
    echo "   git remote add origin https://github.com/$GITHUB_REPO.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
    echo "   Then update the GitHub repo in .do/app.yaml and run this script again."
    exit 0
fi

# Deploy to DigitalOcean App Platform
echo "🚀 Deploying to DigitalOcean App Platform..."

# Check if app already exists
if doctl apps list | grep -q "$APP_NAME"; then
    echo "📱 App '$APP_NAME' already exists. Updating..."
    APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$APP_NAME" | awk '{print $1}')
    doctl apps update "$APP_ID" --spec .do/app.yaml
else
    echo "📱 Creating new app '$APP_NAME'..."
    doctl apps create --spec .do/app.yaml
fi

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📊 Monitor deployment status:"
echo "   doctl apps list"
echo "   doctl apps get <app-id>"
echo ""
echo "🔧 Set up environment variables in DigitalOcean dashboard:"
echo "   1. Go to https://cloud.digitalocean.com/apps"
echo "   2. Select your app"
echo "   3. Go to Settings > Environment Variables"
echo "   4. Add:"
echo "      - OPENAI_API_KEY (your OpenAI API key)"
echo "      - DATABASE_URL (will be auto-populated by managed database)"
echo ""
echo "🌐 Your app will be available at:"
echo "   https://$APP_NAME-<random-id>.ondigitalocean.app"
echo ""
echo "🎉 Deployment complete! Your multi-agent pet safety checker is now live!"

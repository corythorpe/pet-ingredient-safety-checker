#!/bin/bash

# Deploy Pet Ingredient Safety Checker Fixes
# This script deploys the corrected version with dropdown navigation and search fixes

echo "🚀 Deploying Pet Ingredient Safety Checker fixes..."

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl CLI not found. Please install it first."
    exit 1
fi

# Create deployment package
echo "📦 Creating deployment package..."
tar -czf pet-safety-fixes.tar.gz \
    app.py \
    index.html \
    script.js \
    styles.css \
    requirements.txt \
    static/ \
    templates/ \
    agents/ \
    .env.example \
    Dockerfile

echo "✅ Deployment package created: pet-safety-fixes.tar.gz"

# Deploy to DigitalOcean App Platform
echo "🌊 Deploying to DigitalOcean App Platform..."

# Update the app using the existing app spec
doctl apps update pet-ingredient-safety-checker --spec deploy/real-system.yaml

echo "✅ Deployment initiated!"
echo ""
echo "🔍 Monitor deployment status:"
echo "doctl apps list"
echo "doctl apps get pet-ingredient-safety-checker"
echo ""
echo "🌐 Once deployed, your app will be available at:"
echo "https://pet-ingredient-safety-checker-7jz42.ondigitalocean.app"
echo ""
echo "🎯 Key fixes deployed:"
echo "  ✅ Fixed missing dropdown navigation"
echo "  ✅ Fixed search functionality errors"
echo "  ✅ Updated JavaScript with proper dropdown handling"
echo "  ✅ Fixed static file serving"
echo "  ✅ Enhanced ingredient parsing"
echo ""
echo "🧪 Test the fixes:"
echo "  1. Check dropdown navigation appears in header"
echo "  2. Test search with ingredients like 'chocolate, chicken, grapes'"
echo "  3. Verify navigation links work (Admin Dashboard, How It Works)"
echo "  4. Confirm search results display properly"

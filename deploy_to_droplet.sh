#!/bin/bash
# Deploy Pet Ingredient Safety Checker to DigitalOcean Droplet

DROPLET_IP="137.184.146.14"

echo "🐾 Deploying Pet Ingredient Safety Checker to $DROPLET_IP"

# Create a tarball of our application
tar -czf pet-safety-app.tar.gz \
    backend/ \
    static/ \
    templates/ \
    requirements.txt \
    Dockerfile \
    simple_server.py \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude="venv" \
    --exclude=".git"

echo "✅ Application packaged successfully"

# Copy application to droplet
scp -o StrictHostKeyChecking=no pet-safety-app.tar.gz root@$DROPLET_IP:/tmp/

# Deploy on droplet
ssh -o StrictHostKeyChecking=no root@$DROPLET_IP << 'EOF'
set -e

echo "🚀 Setting up Pet Ingredient Safety Checker..."

# Update system
apt-get update
apt-get install -y python3 python3-pip

# Extract application
cd /opt
tar -xzf /tmp/pet-safety-app.tar.gz
cd /opt

# Install Python dependencies
pip3 install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/pet-safety.service << 'SERVICE'
[Unit]
Description=Pet Ingredient Safety Checker
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt
ExecStart=/usr/bin/python3 simple_server.py
Restart=always
Environment=PYTHONPATH=/opt

[Install]
WantedBy=multi-user.target
SERVICE

# Start the service
systemctl daemon-reload
systemctl enable pet-safety
systemctl start pet-safety

echo "✅ Pet Ingredient Safety Checker deployed successfully!"
echo "🌐 Application is running on port 5000"

# Check service status
systemctl status pet-safety --no-pager
EOF

echo "🎉 Deployment completed!"
echo "🌐 Your application is now live at: http://$DROPLET_IP:5000"

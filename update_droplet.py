#!/usr/bin/env python3
"""
Update the droplet with our latest changes
"""

import os
import subprocess
import tempfile
import shutil

DROPLET_IP = "137.184.146.14"

def create_deployment_package():
    """Create a deployment package with our updated files"""
    print("📦 Creating deployment package...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    app_dir = os.path.join(temp_dir, "pet-safety-app")
    os.makedirs(app_dir)
    
    # Copy files to temp directory
    files_to_copy = [
        ("templates/", "templates/"),
        ("static/", "static/"),
        ("simple_server.py", "simple_server.py"),
        ("requirements.txt", "requirements.txt")
    ]
    
    for src, dst in files_to_copy:
        src_path = os.path.join(".", src)
        dst_path = os.path.join(app_dir, dst)
        
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
    
    # Create tarball
    tarball_path = os.path.join(temp_dir, "pet-safety-update.tar.gz")
    subprocess.run([
        "tar", "-czf", tarball_path, "-C", temp_dir, "pet-safety-app"
    ], check=True)
    
    return tarball_path

def deploy_to_droplet(tarball_path):
    """Deploy the package to the droplet"""
    print(f"🚀 Deploying to droplet {DROPLET_IP}...")
    
    # Copy tarball to droplet
    subprocess.run([
        "scp", "-o", "StrictHostKeyChecking=no", 
        tarball_path, f"root@{DROPLET_IP}:/tmp/pet-safety-update.tar.gz"
    ], check=True)
    
    # Deploy on droplet
    deploy_script = """
set -e
echo "🔄 Updating Pet Ingredient Safety Checker..."

# Stop existing service
systemctl stop pet-safety || true

# Extract new version
cd /opt
rm -rf pet-safety-app-old
mv pet-safety-app pet-safety-app-old || true
tar -xzf /tmp/pet-safety-update.tar.gz
cd pet-safety-app

# Install any new dependencies
pip3 install -r requirements.txt

# Update systemd service
cat > /etc/systemd/system/pet-safety.service << 'SERVICE'
[Unit]
Description=Pet Ingredient Safety Checker
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/pet-safety-app
ExecStart=/usr/bin/python3 simple_server.py
Restart=always
Environment=PYTHONPATH=/opt/pet-safety-app

[Install]
WantedBy=multi-user.target
SERVICE

# Restart service
systemctl daemon-reload
systemctl start pet-safety
systemctl enable pet-safety

echo "✅ Pet Ingredient Safety Checker updated successfully!"
systemctl status pet-safety --no-pager
"""
    
    subprocess.run([
        "ssh", "-o", "StrictHostKeyChecking=no",
        f"root@{DROPLET_IP}", deploy_script
    ], check=True)

def main():
    print("🐾 Pet Ingredient Safety Checker - Deployment Update")
    print("=" * 55)
    
    try:
        # Create deployment package
        tarball_path = create_deployment_package()
        
        # Deploy to droplet
        deploy_to_droplet(tarball_path)
        
        print("\n🎉 Deployment completed successfully!")
        print(f"🌐 Your updated application is live at: http://{DROPLET_IP}:5000")
        print("\n✨ Changes included:")
        print("  • Removed ingredient category requirement")
        print("  • Enhanced ingredient parsing for any text format")
        print("  • Updated placeholder text")
        print("  • Simplified user interface")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

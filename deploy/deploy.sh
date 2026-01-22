#!/bin/bash
# DigitalOcean Deployment Script for Pet Ingredient Safety Checker

set -e

echo "🐾 Pet Ingredient Safety Checker - DigitalOcean Deployment"
echo "=========================================================="

# Configuration
APP_NAME="pet-ingredient-safety-checker"
REGION="nyc1"  # Change to your preferred region
SIZE="s-1vcpu-1gb"  # Adjust based on your needs

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    print_error "doctl CLI is not installed. Please install it first:"
    echo "  brew install doctl  # macOS"
    echo "  snap install doctl  # Ubuntu"
    echo "  Or download from: https://github.com/digitalocean/doctl/releases"
    exit 1
fi

# Check if user is authenticated
if ! doctl account get &> /dev/null; then
    print_error "Not authenticated with DigitalOcean. Please run:"
    echo "  doctl auth init"
    exit 1
fi

print_status "Checking DigitalOcean authentication..."
ACCOUNT_EMAIL=$(doctl account get --format Email --no-header)
print_success "Authenticated as: $ACCOUNT_EMAIL"

# Function to deploy using App Platform
deploy_app_platform() {
    print_status "Deploying to DigitalOcean App Platform..."
    
    # Check if app spec exists
    if [ ! -f "deploy/digitalocean-app.yaml" ]; then
        print_error "App spec file not found: deploy/digitalocean-app.yaml"
        exit 1
    fi
    
    # Create or update the app
    if doctl apps list --format Name --no-header | grep -q "^${APP_NAME}$"; then
        print_status "Updating existing app: $APP_NAME"
        APP_ID=$(doctl apps list --format ID,Name --no-header | grep "$APP_NAME" | awk '{print $1}')
        doctl apps update "$APP_ID" --spec deploy/digitalocean-app.yaml
    else
        print_status "Creating new app: $APP_NAME"
        doctl apps create --spec deploy/digitalocean-app.yaml
    fi
    
    print_success "App deployment initiated!"
    print_status "Monitor deployment progress:"
    echo "  doctl apps list"
    echo "  doctl apps get <app-id>"
}

# Function to deploy using Droplet + Docker
deploy_droplet() {
    print_status "Deploying to DigitalOcean Droplet..."
    
    # Create droplet if it doesn't exist
    if ! doctl compute droplet list --format Name --no-header | grep -q "^${APP_NAME}$"; then
        print_status "Creating new droplet: $APP_NAME"
        doctl compute droplet create "$APP_NAME" \
            --image docker-20-04 \
            --size "$SIZE" \
            --region "$REGION" \
            --ssh-keys $(doctl compute ssh-key list --format ID --no-header | head -1) \
            --wait
        
        print_success "Droplet created successfully!"
    else
        print_status "Using existing droplet: $APP_NAME"
    fi
    
    # Get droplet IP
    DROPLET_IP=$(doctl compute droplet list --format Name,PublicIPv4 --no-header | grep "$APP_NAME" | awk '{print $2}')
    print_status "Droplet IP: $DROPLET_IP"
    
    # Deploy application
    print_status "Deploying application to droplet..."
    
    # Create deployment script
    cat > /tmp/deploy_to_droplet.sh << 'EOF'
#!/bin/bash
set -e

# Update system
sudo apt-get update
sudo apt-get install -y git

# Clone or update repository
if [ -d "/opt/pet-safety-checker" ]; then
    cd /opt/pet-safety-checker
    sudo git pull
else
    sudo git clone https://github.com/your-username/pet-ingredient-safety-checker.git /opt/pet-safety-checker
    cd /opt/pet-safety-checker
fi

# Build and run with Docker
sudo docker build -t pet-safety-checker .
sudo docker stop pet-safety-checker || true
sudo docker rm pet-safety-checker || true

sudo docker run -d \
    --name pet-safety-checker \
    --restart unless-stopped \
    -p 80:5000 \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -e DATABASE_URL="$DATABASE_URL" \
    -e FLASK_ENV=production \
    pet-safety-checker

echo "Deployment completed successfully!"
EOF

    # Copy and execute deployment script
    scp /tmp/deploy_to_droplet.sh root@$DROPLET_IP:/tmp/
    ssh root@$DROPLET_IP "chmod +x /tmp/deploy_to_droplet.sh && /tmp/deploy_to_droplet.sh"
    
    print_success "Application deployed to: http://$DROPLET_IP"
}

# Function to setup database
setup_database() {
    print_status "Setting up PostgreSQL database..."
    
    # Check if database exists
    if ! doctl databases list --format Name --no-header | grep -q "pet-safety-db"; then
        print_status "Creating PostgreSQL database..."
        doctl databases create pet-safety-db \
            --engine pg \
            --version 15 \
            --size db-s-1vcpu-1gb \
            --region "$REGION" \
            --num-nodes 1
        
        print_success "Database created successfully!"
        print_warning "Database is being provisioned. This may take a few minutes."
    else
        print_status "Using existing database: pet-safety-db"
    fi
    
    # Get database connection details
    print_status "Database connection details:"
    doctl databases connection pet-safety-db --format URI --no-header
}

# Function to setup domain and SSL
setup_domain() {
    read -p "Enter your domain name (or press Enter to skip): " DOMAIN_NAME
    
    if [ -n "$DOMAIN_NAME" ]; then
        print_status "Setting up domain: $DOMAIN_NAME"
        
        # Add domain to DigitalOcean
        if ! doctl compute domain list --format Name --no-header | grep -q "^${DOMAIN_NAME}$"; then
            doctl compute domain create "$DOMAIN_NAME"
            print_success "Domain added to DigitalOcean"
        fi
        
        # Get droplet IP for DNS setup
        if [ -n "$DROPLET_IP" ]; then
            print_status "Creating DNS records..."
            doctl compute domain records create "$DOMAIN_NAME" \
                --record-type A \
                --record-name @ \
                --record-data "$DROPLET_IP" \
                --record-ttl 300
            
            doctl compute domain records create "$DOMAIN_NAME" \
                --record-type A \
                --record-name www \
                --record-data "$DROPLET_IP" \
                --record-ttl 300
            
            print_success "DNS records created!"
            print_status "Your application will be available at: https://$DOMAIN_NAME"
        fi
    fi
}

# Main deployment menu
echo ""
echo "Choose deployment method:"
echo "1) DigitalOcean App Platform (Recommended - Managed)"
echo "2) DigitalOcean Droplet with Docker (Self-managed)"
echo "3) Setup Database Only"
echo "4) Setup Domain and SSL"
echo ""
read -p "Enter your choice (1-4): " CHOICE

case $CHOICE in
    1)
        deploy_app_platform
        ;;
    2)
        setup_database
        deploy_droplet
        setup_domain
        ;;
    3)
        setup_database
        ;;
    4)
        setup_domain
        ;;
    *)
        print_error "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
print_success "Deployment process completed!"
echo ""
echo "Next steps:"
echo "1. Set up your environment variables (OPENAI_API_KEY, DATABASE_URL, SECRET_KEY)"
echo "2. Configure your domain DNS if using a custom domain"
echo "3. Monitor your application logs and performance"
echo ""
echo "Useful commands:"
echo "  doctl apps list                    # List all apps"
echo "  doctl apps logs <app-id>           # View app logs"
echo "  doctl compute droplet list         # List droplets"
echo "  doctl databases list               # List databases"
echo ""

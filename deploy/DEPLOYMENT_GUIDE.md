# 🚀 DigitalOcean Deployment Guide
## Pet Ingredient Safety Checker - Multi-Agent Application

This guide provides step-by-step instructions for deploying your Pet Ingredient Safety Checker application to DigitalOcean infrastructure.

## 📋 Prerequisites

### 1. DigitalOcean Account Setup
- Active DigitalOcean account with billing enabled
- DigitalOcean CLI (`doctl`) installed and authenticated
- SSH key added to your DigitalOcean account

### 2. Required API Keys
- **OpenAI API Key**: For AI-powered ingredient analysis
- **Secret Key**: For Flask session security (generate a strong random key)

### 3. Repository Setup
- Code pushed to a Git repository (GitHub, GitLab, etc.)
- Repository URL updated in deployment configurations

## 🎯 Deployment Options

### Option 1: DigitalOcean App Platform (Recommended)
**Best for**: Managed deployment with automatic scaling and SSL

```bash
# Run the deployment script
./deploy/deploy.sh

# Choose option 1 when prompted
# The script will:
# - Create/update your app on App Platform
# - Set up PostgreSQL database
# - Configure environment variables
# - Enable automatic deployments
```

**Benefits:**
- ✅ Fully managed infrastructure
- ✅ Automatic SSL certificates
- ✅ Built-in monitoring and logging
- ✅ Auto-scaling capabilities
- ✅ Zero-downtime deployments

### Option 2: DigitalOcean Droplet + Docker
**Best for**: Full control over the server environment

```bash
# Run the deployment script
./deploy/deploy.sh

# Choose option 2 when prompted
# The script will:
# - Create a Docker-enabled droplet
# - Set up PostgreSQL database
# - Deploy your application with Docker
# - Configure domain and SSL (optional)
```

**Benefits:**
- ✅ Full server control
- ✅ Custom configurations
- ✅ Direct SSH access
- ✅ Cost-effective for stable workloads

## 🔧 Manual Deployment Steps

### Step 1: Install DigitalOcean CLI

**macOS:**
```bash
brew install doctl
```

**Ubuntu/Debian:**
```bash
snap install doctl
```

**Other platforms:**
Download from: https://github.com/digitalocean/doctl/releases

### Step 2: Authenticate with DigitalOcean

```bash
doctl auth init
# Follow the prompts to enter your API token
```

### Step 3: Update Configuration Files

**Update `deploy/digitalocean-app.yaml`:**
```yaml
# Replace with your actual repository
github:
  repo: your-username/pet-ingredient-safety-checker
  branch: main
```

**Update `deploy/deploy.sh`:**
```bash
# Set your preferred region and size
REGION="nyc1"  # or nyc3, sfo3, ams3, sgp1, lon1, fra1, tor1, blr1
SIZE="s-1vcpu-1gb"  # or larger based on your needs
```

### Step 4: Deploy the Application

**For App Platform:**
```bash
# Create the app
doctl apps create --spec deploy/digitalocean-app.yaml

# Or update existing app
doctl apps update <app-id> --spec deploy/digitalocean-app.yaml
```

**For Droplet deployment:**
```bash
# Run the full deployment script
./deploy/deploy.sh
```

### Step 5: Configure Environment Variables

**App Platform (via Control Panel):**
1. Go to DigitalOcean Control Panel → Apps
2. Select your app → Settings → Environment Variables
3. Add the following variables:

```
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://username:password@host:port/database
FLASK_ENV=production
SECRET_KEY=your_super_secret_key_here
```

**Droplet (via SSH):**
```bash
# SSH into your droplet
ssh root@your_droplet_ip

# Set environment variables
export OPENAI_API_KEY="your_openai_api_key_here"
export DATABASE_URL="postgresql://username:password@host:port/database"
export FLASK_ENV="production"
export SECRET_KEY="your_super_secret_key_here"

# Restart the application
docker restart pet-safety-checker
```

## 🗄️ Database Setup

### Automatic Setup (Recommended)
The deployment script automatically creates a PostgreSQL database:

```bash
./deploy/deploy.sh
# Choose option 3 for database setup only
```

### Manual Database Setup
```bash
# Create PostgreSQL database
doctl databases create pet-safety-db \
  --engine pg \
  --version 15 \
  --size db-s-1vcpu-1gb \
  --region nyc1 \
  --num-nodes 1

# Get connection details
doctl databases connection pet-safety-db
```

## 🌐 Domain and SSL Configuration

### Using App Platform (Automatic SSL)
1. Go to DigitalOcean Control Panel → Apps
2. Select your app → Settings → Domains
3. Add your custom domain
4. Update your DNS records as instructed

### Using Droplet (Manual SSL)
```bash
# The deployment script can help set up DNS records
./deploy/deploy.sh
# Choose option 4 for domain setup

# For SSL, consider using Let's Encrypt with Nginx
```

## 📊 Monitoring and Maintenance

### View Application Logs
```bash
# App Platform
doctl apps logs <app-id> --follow

# Droplet
ssh root@your_droplet_ip
docker logs -f pet-safety-checker
```

### Monitor Performance
```bash
# List all apps
doctl apps list

# Get app details
doctl apps get <app-id>

# List droplets
doctl compute droplet list

# Database metrics
doctl databases list
```

### Update Application
```bash
# App Platform (automatic on git push)
git push origin main

# Droplet (manual update)
ssh root@your_droplet_ip
cd /opt/pet-safety-checker
git pull
docker build -t pet-safety-checker .
docker restart pet-safety-checker
```

## 🔒 Security Best Practices

### Environment Variables
- ✅ Never commit API keys to version control
- ✅ Use DigitalOcean's secret management
- ✅ Rotate keys regularly
- ✅ Use strong, unique secret keys

### Database Security
- ✅ Enable SSL connections
- ✅ Use strong passwords
- ✅ Restrict database access to your app only
- ✅ Regular backups (automatic with managed databases)

### Application Security
- ✅ Keep dependencies updated
- ✅ Enable HTTPS only
- ✅ Implement rate limiting
- ✅ Monitor for security vulnerabilities

## 💰 Cost Optimization

### App Platform Pricing
- **Basic**: $5/month (512MB RAM, 1 vCPU)
- **Professional**: $12/month (1GB RAM, 1 vCPU)
- **Database**: $15/month (1GB RAM, 1 vCPU, 10GB storage)

### Droplet Pricing
- **Basic**: $6/month (1GB RAM, 1 vCPU, 25GB SSD)
- **Regular**: $12/month (2GB RAM, 1 vCPU, 50GB SSD)
- **Database**: $15/month (managed PostgreSQL)

### Cost-Saving Tips
- 🔹 Start with smaller instances and scale up as needed
- 🔹 Use managed databases for automatic backups and maintenance
- 🔹 Monitor usage and optimize based on actual traffic
- 🔹 Consider reserved instances for predictable workloads

## 🆘 Troubleshooting

### Common Issues

**Deployment Fails:**
```bash
# Check app logs
doctl apps logs <app-id>

# Verify environment variables
doctl apps get <app-id>
```

**Database Connection Issues:**
```bash
# Test database connectivity
doctl databases connection pet-safety-db

# Check firewall rules
doctl databases firewalls list pet-safety-db
```

**SSL Certificate Issues:**
```bash
# For App Platform, SSL is automatic
# For droplets, check Nginx configuration
ssh root@your_droplet_ip
nginx -t
systemctl status nginx
```

### Getting Help
- 📖 DigitalOcean Documentation: https://docs.digitalocean.com/
- 💬 Community Forums: https://www.digitalocean.com/community/
- 🎫 Support Tickets: Available with paid plans
- 📧 Application Support: Check the main README.md

## 🎉 Post-Deployment Checklist

- [ ] Application is accessible via HTTPS
- [ ] Database connection is working
- [ ] Environment variables are set correctly
- [ ] SSL certificate is valid
- [ ] Monitoring and logging are configured
- [ ] Backup strategy is in place
- [ ] Domain DNS is properly configured
- [ ] Performance testing completed
- [ ] Security scan performed
- [ ] Team access and permissions configured

## 📞 Support

For deployment-specific issues:
1. Check the application logs first
2. Verify all environment variables are set
3. Test database connectivity
4. Review DigitalOcean status page
5. Contact DigitalOcean support if infrastructure issues persist

Your Pet Ingredient Safety Checker is now ready to help pet owners worldwide! 🐾

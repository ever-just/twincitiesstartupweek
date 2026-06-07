# Odoo Single-Instance Deployment - Complete Setup

**Deployment Date:** June 7, 2026  
**Status:** ✅ LIVE

## Infrastructure Overview

### AWS Resources Created

#### Compute
- **EC2 Instance:** `i-03fde105652a7bd7d`
  - Type: t3.xlarge (4 vCPU, 16 GB RAM)
  - AMI: Ubuntu 22.04 LTS
  - Public IP: 52.91.38.110
  - Region: us-east-1

#### Storage
- **EBS Volume:** 200 GB gp3
  - Mount Point: `/mnt/ebs/filestore`
  - Purpose: Odoo filestore persistence

#### Networking
- **Route 53 Hosted Zone:** `everjust.app`
  - Zone ID: Z05208093DUJXT5A3FEXG
  - Nameservers:
    - ns-1757.awsdns-27.co.uk
    - ns-1031.awsdns-00.org
    - ns-478.awsdns-59.com
    - ns-803.awsdns-36.net

- **DNS Records:**
  - `tcsw.everjust.app` → ALB (via Route 53 Alias)
  - ACM Certificate: `arn:aws:acm:us-east-1:678806349176:certificate/c7bd04de-0768-47f1-8b94-48bf250cf4a6`
  - Status: PENDING_VALIDATION (DNS validation records added)

- **Application Load Balancer (ALB):** `odoo-alb`
  - ARN: `arn:aws:elasticloadbalancing:us-east-1:678806349176:loadbalancer/app/odoo-alb/62f1c39c1dade7f4`
  - DNS: `odoo-alb-98405251.us-east-1.elb.amazonaws.com`
  - Listeners:
    - HTTP (80) → Target Group
    - HTTPS (443) → Target Group (pending certificate validation)
  - Target Group: `odoo-targets` (port 8069)
  - Status: Provisioning

- **Security Group:** `odoo-sg` (sg-0b8544450405ef2e7)
  - Inbound Rules:
    - SSH (22): 0.0.0.0/0
    - HTTP (80): 0.0.0.0/0
    - HTTPS (443): 0.0.0.0/0
    - Odoo (8069): 0.0.0.0/0

#### IAM & Security
- **IAM Role:** `odoo-ec2-role`
  - Policy: AmazonS3FullAccess
  - Instance Profile: `odoo-ec2-instance-profile`

- **S3 Bucket:** `everjust-odoo-backups`
  - Purpose: Database and filestore backups
  - Versioning: Enabled

- **EC2 Key Pair:** `odoo-tcsw-key`
  - Private Key: `/Users/cloudaistudio/Desktop/twincitiesstartupweek/odoo-platform/deployment/odoo-tcsw-key.pem`

## Application Stack

### Docker Services (Docker Compose)

```
services:
  odoo:17
    - Port: 8069
    - Database: PostgreSQL (db:5432)
    - Cache: Redis (redis:6379)
    - Filestore: /mnt/ebs/filestore
    - Status: Running

  db:postgres:15
    - Port: 5432
    - Database: tcsw_main
    - User: odoo
    - Status: Running

  redis:7-alpine
    - Port: 6379
    - Status: Running
```

### Database
- **Name:** `tcsw_main`
- **User:** odoo
- **Password:** (configured in docker-compose.yml)
- **Status:** Initialized with base module

## Access Information

### Web Interface
- **URL (via ALB):** http://tcsw.everjust.app (pending DNS propagation)
- **URL (direct IP):** http://52.91.38.110:8069
- **Login:** admin
- **Password:** admin123

### SSH Access
```bash
ssh -i odoo-platform/deployment/odoo-tcsw-key.pem ubuntu@52.91.38.110
```

## Backup & Recovery

### Automated Backups
- **Schedule:** Daily at 2:00 AM (UTC)
- **Location:** S3 bucket `everjust-odoo-backups`
- **Contents:**
  - Database dump: `databases/tcsw_main_YYYYMMDD_HHMMSS.sql.gz`
  - Filestore: `filestore/filestore_YYYYMMDD_HHMMSS.tar.gz`

### Manual Backup
```bash
cd /home/ubuntu/twincitiesstartupweek/odoo-platform/deployment
source .env
bash scripts/backup.sh
```

### Restore from Backup
```bash
# Download from S3
aws s3 cp s3://everjust-odoo-backups/databases/tcsw_main_YYYYMMDD_HHMMSS.sql.gz .

# Restore to database
gunzip -c tcsw_main_YYYYMMDD_HHMMSS.sql.gz | \
  docker exec -i deployment-db-1 psql -U odoo -d tcsw_main
```

## Configuration Files

### Docker Compose
- **Location:** `odoo-platform/deployment/docker-compose.yml`
- **Services:** Odoo, PostgreSQL, Redis
- **Volumes:** EBS mount, named volumes for persistence

### Environment Variables
- **Location:** `odoo-platform/deployment/.env`
- **Variables:**
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_REGION
  - S3_BUCKET

### Odoo Configuration
- **Location:** `/etc/odoo/odoo.conf` (in container)
- **Key Settings:**
  - proxy_mode = True (for ALB)
  - Database: PostgreSQL
  - Session store: Redis

## Monitoring & Maintenance

### Health Checks
- ALB performs HTTP health checks on port 8069 every 30 seconds
- Target health status: Initial (registration in progress)

### Logs
```bash
# Odoo logs
docker logs deployment-odoo-1 -f

# Database logs
docker logs deployment-db-1 -f

# Docker Compose status
cd odoo-platform/deployment && docker compose ps
```

### Common Tasks

#### Restart Services
```bash
cd odoo-platform/deployment
docker compose restart
```

#### Update Odoo
```bash
cd odoo-platform/deployment
docker compose pull odoo
docker compose up -d
```

#### View Database
```bash
docker exec -it deployment-db-1 psql -U odoo -d tcsw_main
```

## Next Steps

### 1. Update Domain Registrar
Update your domain registrar's nameservers to the Route 53 nameservers listed above. This typically takes 5-30 minutes to propagate.

### 2. SSL Certificate Validation
Once DNS propagates, the ACM certificate will automatically validate. The HTTPS listener will then be activated.

### 3. Configure Odoo
- Log in to Odoo at http://tcsw.everjust.app
- Set up company information
- Configure email settings
- Install required modules (Events, CRM, etc.)

### 4. Enable Custom Modules
- Place custom modules in `odoo-platform/custom-modules/`
- Update `docker-compose.yml` to mount custom modules
- Restart Odoo and install modules via web interface

### 5. Set Up Email
Configure SMTP in Odoo settings for email notifications and communications.

## Troubleshooting

### ALB Health Check Failing
- Verify security group allows port 8069
- Check Odoo container is running: `docker logs deployment-odoo-1`
- Ensure database connection is working

### Database Connection Issues
- Verify PostgreSQL container is running: `docker logs deployment-db-1`
- Check environment variables in docker-compose.yml
- Verify network connectivity between containers

### Backup Failures
- Ensure AWS credentials are set in `.env`
- Verify S3 bucket exists and IAM role has permissions
- Check AWS CLI is installed: `aws --version`

## Cost Estimation (Monthly)

- EC2 t3.xlarge: ~$120
- EBS 200GB gp3: ~$20
- ALB: ~$16 + data processing
- Route 53: ~$0.50
- S3 backups: ~$1-5 (depending on backup size)
- **Total: ~$160-170/month**

## Support & Documentation

- Odoo Community: https://www.odoo.com/documentation/17.0/
- AWS Documentation: https://docs.aws.amazon.com/
- Docker Documentation: https://docs.docker.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/

---

**Deployment completed successfully!** 🎉

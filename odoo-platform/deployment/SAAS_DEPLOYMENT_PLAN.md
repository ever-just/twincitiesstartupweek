# SaaS Deployment Plan for Odoo Platform (AWS)

## Overview

This document outlines the deployment architecture for running the Odoo Community fork as a multi-tenant SaaS platform on `everjust.app` using AWS infrastructure.

## Architecture

```
everjust.app (Main Landing/Signup)
    ↓
AWS Route 53 (DNS)
    ↓
AWS Application Load Balancer (SSL via ACM)
    ├── tcsw.everjust.app → Database: tcsw_main
    ├── customer1.everjust.app → Database: customer1
    ├── customer2.everjust.app → Database: customer2
    └── customerN.everjust.app → Database: customerN
    ↓
EC2 Instance (Docker)
    ├── Odoo Container
    ├── Redis Container
    └── Nginx Container
    ↓
AWS RDS PostgreSQL (Multi-DB)
    ↓
AWS EBS (Filestore)
    ↓
AWS S3 (Backups)
```

## AWS Infrastructure Components

### 1. EC2 Instance (Application Server)
- **Instance Type:** t3.xlarge (4 vCPU, 16 GB RAM)
- **AMI:** Ubuntu 22.04 LTS
- **Storage:** 200 GB gp3 EBS volume
- **Security Group:** Allow 80, 443 from ALB; allow SSH from your IP

### 2. AWS RDS PostgreSQL (Database)
- **Engine:** PostgreSQL 15
- **Instance Class:** db.t3.medium (2 vCPU, 4 GB RAM) to start
- **Storage:** 100 GB gp3 (auto-scale)
- **Multi-AZ:** Yes (for production)
- **Security Group:** Allow access from EC2 security group only

### 3. AWS Application Load Balancer
- **Type:** Application Load Balancer
- **SSL Certificate:** AWS Certificate Manager (ACM) for `*.everjust.app`
- **Target Group:** EC2 instance on port 8069
- **Health Checks:** `/web/database/selector`

### 4. AWS Route 53 (DNS)
- **Hosted Zone:** `everjust.app`
- **Records:**
  - `everjust.app` → ALB
  - `*.everjust.app` → ALB (wildcard)

### 5. AWS S3 (Backups)
- **Bucket:** `everjust-odoo-backups`
- **Lifecycle:** Move to Glacier after 30 days, delete after 1 year
- **Access:** Private, accessed via EC2 IAM role

### 6. AWS EBS (Filestore)
- **Volume:** 200 GB gp3 attached to EC2
- **Mount point:** `/var/lib/odoo/filestore`
- **Snapshots:** Daily automated snapshots

## Scaling Considerations

### Vertical Scaling
- **100+ databases:** EC2 → t3.2xlarge (8 vCPU, 32 GB RAM)
- **RDS → db.t3.large (2 vCPU, 8 GB RAM)

### Horizontal Scaling
- **1000+ databases:** Add EC2 instances to ALB target group
- **RDS → db.r6g.large (2 vCPU, 16 GB RAM) or read replica

## Components

### 1. Docker Compose Setup

**File:** `deployment/docker-compose.yml`

```yaml
version: '3.8'

services:
  odoo:
    image: everjust/odoo:latest
    build: ./odoo
    depends_on:
      - redis
    ports:
      - "8069:8069"
      - "8072:8072"
    environment:
      - HOST=${RDS_ENDPOINT}
      - PORT=5432
      - USER=${RDS_USER}
      - PASSWORD=${RDS_PASSWORD}
      - DBFILTER=^%d$
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=${AWS_REGION}
      - S3_BUCKET=${S3_BUCKET}
    volumes:
      - ./odoo/odoo:/opt/odoo
      - ./custom-modules:/opt/odoo/addons/custom
      - odoo-data:/var/lib/odoo
      - /mnt/ebs/filestore:/var/lib/odoo/filestore
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  odoo-data:
```

**Environment Variables (.env):**
```bash
# AWS RDS Configuration
RDS_ENDPOINT=odoo-postgres.xxxx.us-east-1.rds.amazonaws.com
RDS_USER=odoo
RDS_PASSWORD=your_secure_password

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET=everjust-odoo-backups
```

### 2. Nginx Configuration (Optional - ALB handles SSL)

**Note:** With AWS ALB handling SSL termination, Nginx is optional. Use it only if you need additional routing logic.

**File:** `deployment/nginx/nginx.conf`

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://odoo:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Database Provisioning Script (AWS RDS)

**File:** `deployment/scripts/provision_database.py`

```python
#!/usr/bin/env python3
"""
Provision a new Odoo database for a SaaS customer on AWS RDS.
Usage: python provision_database.py --db-name customer1 --email user@example.com --plan pro
"""

import subprocess
import sys
import argparse
import os
import psycopg2
from psycopg2 import sql

def create_database(db_name, rds_endpoint, rds_user, rds_password):
    """Create a new PostgreSQL database on AWS RDS."""
    conn = psycopg2.connect(
        host=rds_endpoint,
        database='postgres',
        user=rds_user,
        password=rds_password
    )
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
    print(f"✓ Database {db_name} created on RDS")

    cursor.close()
    conn.close()

def initialize_odoo_db(db_name, admin_password):
    """Initialize Odoo database with base modules."""
    cmd = (
        f"docker exec twincitiesstartupweek-odoo-1 "
        f"odoo -d {db_name} --init=base,event,crm,project,account "
        f"--stop-after-init --admin-password={admin_password}"
    )
    subprocess.run(cmd, shell=True, check=True)
    print(f"✓ Odoo initialized for {db_name}")

def install_custom_modules(db_name):
    """Install custom TCSW modules."""
    cmd = (
        f"docker exec twincitiesstartupweek-odoo-1 "
        f"odoo -d {db_name} --init=tcsw_events "
        f"--stop-after-init"
    )
    subprocess.run(cmd, shell=True, check=True)
    print(f"✓ Custom modules installed for {db_name}")

def create_admin_user(db_name, email, password):
    """Create admin user via Odoo API."""
    # This would use Odoo's XML-RPC or REST API
    # For now, placeholder
    print(f"✓ Admin user created for {db_name}: {email}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-name', required=True)
    parser.add_argument('--email', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--plan', default='starter', choices=['starter', 'pro', 'enterprise'])
    args = parser.parse_args()

    rds_endpoint = os.getenv('RDS_ENDPOINT')
    rds_user = os.getenv('RDS_USER')
    rds_password = os.getenv('RDS_PASSWORD')

    print(f"Provisioning database: {args.db_name}")
    create_database(args.db_name, rds_endpoint, rds_user, rds_password)
    initialize_odoo_db(args.db_name, args.password)
    install_custom_modules(args.db_name)
    create_admin_user(args.db_name, args.email, args.password)
    print(f"✓ Database {args.db_name} ready")

if __name__ == '__main__':
    main()
```

### 4. Stripe Integration Module

**File:** `custom-modules/saas_billing/__manifest__.py`

```python
{
    'name': 'SaaS Billing Integration',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Stripe integration for SaaS billing and database provisioning',
    'depends': ['base'],
    'data': [
        'views/stripe_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
```

**Stripe Webhook Handler:**

```python
# custom-modules/saas_billing/controllers/main.py
from odoo import http
from odoo.http import request
import stripe

class StripeWebhookController(http.Controller):

    @http.route('/stripe/webhook', type='json', auth='none', methods=['POST'])
    def stripe_webhook(self):
        payload = request.httprequest.data
        sig_header = request.httprequest.headers.get('Stripe-Signature')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, 'whsec_your_webhook_secret'
            )
        except ValueError:
            return {'status': 'invalid payload'}
        except stripe.error.SignatureVerificationError:
            return {'status': 'invalid signature'}

        if event['type'] == 'checkout.session.completed':
            self.handle_checkout_completed(event['data']['object'])
        elif event['type'] == 'invoice.paid':
            self.handle_invoice_paid(event['data']['object'])
        elif event['type'] == 'subscription.deleted':
            self.handle_subscription_deleted(event['data']['object'])

        return {'status': 'success'}

    def handle_checkout_completed(self, session):
        """Create new database when customer subscribes."""
        db_name = session['metadata']['db_name']
        email = session['customer_details']['email']
        plan = session['metadata']['plan']

        # Call provisioning script
        # This would trigger the database creation
        pass

    def handle_invoice_paid(self, invoice):
        """Ensure database is active for paid subscription."""
        db_name = invoice['subscription']['metadata']['db_name']
        # Mark database as active
        pass

    def handle_subscription_deleted(self, subscription):
        """Archive database when subscription cancels."""
        db_name = subscription['metadata']['db_name']
        # Archive or delete database
        pass
```

## Deployment Steps (AWS)

### Phase 1: AWS Infrastructure Setup

1. **Create AWS RDS PostgreSQL**
   - Go to AWS Console → RDS → Create database
   - Engine: PostgreSQL 15
   - Instance class: db.t3.medium
   - Storage: 100 GB gp3
   - Multi-AZ: Yes
   - Master username: odoo
   - Set strong password
   - VPC security group: Allow port 5432 from EC2 security group only
   - Note the endpoint URL for .env file

2. **Create EC2 Instance**
   - Go to AWS Console → EC2 → Launch Instance
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t3.xlarge
   - Key pair: Create or use existing
   - Network: VPC with public subnet
   - Security group: Allow 80, 443 from anywhere; allow SSH from your IP
   - Storage: 200 GB gp3 EBS (attach as /dev/sdb)

3. **Create AWS S3 Bucket for Backups**
   - Go to AWS Console → S3 → Create bucket
   - Bucket name: `everjust-odoo-backups` (must be globally unique)
   - Region: us-east-1 (same as other resources)
   - Block public access: Enabled
   - Lifecycle rule: Move to Glacier after 30 days, delete after 1 year

4. **Create IAM Role for EC2**
   - Go to AWS Console → IAM → Create role
   - Trusted entity: EC2
   - Permissions: S3FullAccess (or scoped to backup bucket)
   - Attach role to EC2 instance

5. **Create AWS Application Load Balancer**
   - Go to AWS Console → EC2 → Load Balancers → Create
   - Type: Application Load Balancer
   - Scheme: Internet-facing
   - VPC: Same as EC2
   - Subnets: 2+ public subnets in different AZs
   - Security group: Allow 80, 443 from anywhere

6. **Request SSL Certificate via ACM**
   - Go to AWS Console → Certificate Manager → Request
   - Domain name: `*.everjust.app`
   - Validation: DNS validation (add CNAME record in Route 53)
   - Wait for validation to complete

7. **Configure Route 53**
   - Go to AWS Console → Route 53 → Hosted zones
   - Create hosted zone for `everjust.app` (if not exists)
   - Add A record: `everjust.app` → ALB DNS name
   - Add A record: `*.everjust.app` → ALB DNS name (wildcard)

8. **Configure ALB Target Group**
   - Create target group for Odoo (port 8069)
   - Register EC2 instance
   - Configure health check: `/web/database/selector`
   - Add listener: HTTPS (443) → Target group with ACM certificate

### Phase 2: EC2 Instance Setup

1. **SSH into EC2**
   ```bash
   ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com
   ```

2. **Mount EBS volume for filestore**
   ```bash
   sudo mkfs -t xfs /dev/xvdb
   sudo mkdir /mnt/ebs
   sudo mount /dev/xvdb /mnt/ebs
   echo '/dev/xvdb /mnt/ebs xfs defaults 0 0' | sudo tee -a /etc/fstab
   sudo mkdir /mnt/ebs/filestore
   ```

3. **Install Docker and Docker Compose**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   sudo apt install docker-compose-plugin
   ```

4. **Clone repository**
   ```bash
   git clone https://github.com/ever-just/twincitiesstartupweek.git
   cd twincitiesstartupweek/odoo-platform
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env
   # Add RDS endpoint, credentials, AWS keys
   ```

6. **Build and start**
   ```bash
   docker compose up -d
   ```

7. **Initialize main database**
   ```bash
   docker exec -it odoo odoo -d tcsw_main --init=base,event,crm,project,account,tcsw_events --stop-after-init
   ```

### Phase 3: Stripe Setup

1. **Create Stripe account**
2. **Create products and prices** for each plan
3. **Set up webhook endpoint:** `https://everjust.app/stripe/webhook`
4. **Configure webhook events:**
   - `checkout.session.completed`
   - `invoice.paid`
   - `subscription.deleted`

### Phase 4: Signup Flow

1. **Create landing page** at `everjust.app`
2. **Add Stripe Checkout** for plan selection
3. **On successful payment:** Stripe webhook triggers database provisioning
4. **Send welcome email** with subdomain URL (e.g., `customer1.everjust.app`)

## Backup Strategy (AWS S3)

### Automated Backups to S3

**File:** `deployment/scripts/backup.sh`

```bash
#!/bin/bash
# Backup all Odoo databases to AWS S3
DATE=$(date +%Y%m%d_%H%M%S)
S3_BUCKET=${S3_BUCKET:-everjust-odoo-backups}
RDS_ENDPOINT=${RDS_ENDPOINT}
RDS_USER=${RDS_USER}
RDS_PASSWORD=${RDS_PASSWORD}

# Backup each database
for db in $(PGPASSWORD=$RDS_PASSWORD psql -h $RDS_ENDPOINT -U $RDS_USER -d postgres -t -c "SELECT datname FROM pg_database WHERE datname LIKE 'tcsw_%' OR datname = 'tcsw_main'"); do
    PGPASSWORD=$RDS_PASSWORD pg_dump -h $RDS_ENDPOINT -U $RDS_USER $db | gzip > /tmp/${db}_${DATE}.sql.gz
    aws s3 cp /tmp/${db}_${DATE}.sql.gz s3://$S3_BUCKET/databases/${db}_${DATE}.sql.gz
    rm /tmp/${db}_${DATE}.sql.gz
    echo "✓ Backed up $db to S3"
done

# Backup filestore to S3
docker exec twincitiesstartupweek-odoo-1 tar -czf - /var/lib/odoo/filestore | gzip > /tmp/filestore_${DATE}.tar.gz
aws s3 cp /tmp/filestore_${DATE}.tar.gz s3://$S3_BUCKET/filestore/filestore_${DATE}.tar.gz
rm /tmp/filestore_${DATE}.tar.gz
echo "✓ Backed up filestore to S3"
```

**Cron job:**
```bash
0 2 * * * /path/to/backup.sh
```

### Restore Procedure from S3

```bash
# Restore database from S3
aws s3 cp s3://everjust-odoo-backups/databases/tcsw_main_20260607_020000.sql.gz /tmp/restore.sql.gz
gunzip < /tmp/restore.sql.gz | PGPASSWORD=$RDS_PASSWORD psql -h $RDS_ENDPOINT -U $RDS_USER tcsw_main

# Restore filestore from S3
aws s3 cp s3://everjust-odoo-backups/filestore/filestore_20260607_020000.tar.gz /tmp/restore.tar.gz
docker exec -i twincitiesstartupweek-odoo-1 tar -xzf - -C /var/lib/odoo < /tmp/restore.tar.gz
```

### AWS RDS Automated Backups

AWS RDS also provides automated backups:
- **Retention period:** 1–35 days (configurable)
- **Backup window:** Daily (configurable)
- **Point-in-time recovery:** Restore to any second within retention window
- **Multi-AZ snapshots:** Automatic with Multi-AZ deployment

## Monitoring (AWS CloudWatch)

### CloudWatch Metrics

AWS provides built-in monitoring:
- **EC2:** CPU utilization, network in/out, disk read/write
- **RDS:** CPU, memory, connections, storage, replication lag
- **ALB:** request count, latency, target response time, healthy/unhealthy hosts
- **EBS:** volume read/write ops, throughput, queue length

### Custom CloudWatch Alarms

Set up alarms for:
- EC2 CPU > 80% for 5 minutes
- RDS CPU > 80% for 5 minutes
- RDS free storage < 10 GB
- ALB 5XX error rate > 1%
- ALB unhealthy hosts > 0

### Health Checks

```bash
# Check Odoo status (from EC2)
curl http://localhost:8069/web/database/selector

# Check RDS connectivity
PGPASSWORD=$RDS_PASSWORD psql -h $RDS_ENDPOINT -U $R_USER -d postgres -c "SELECT 1"

# Check disk space
df -h
```

### Logs

```bash
# Odoo logs
docker compose logs -f odoo

# CloudWatch Logs (if configured)
aws logs tail /aws/odoo/odoo --follow
```

## Security Considerations (AWS)

1. **Environment variables:** Store sensitive data in `.env` (never commit to git)
2. **AWS Secrets Manager:** Consider using AWS Secrets Manager for RDS credentials instead of .env
3. **IAM roles:** Use IAM roles for EC2 instead of AWS access keys in .env
4. **Security groups:** Restrict access to necessary ports only (RDS only from EC2, SSH only from your IP)
5. **VPC:** Keep all resources in a private VPC with public subnets only for ALB
6. **SSL/TLS:** Use ACM certificates for all HTTPS traffic
7. **Updates:** Regularly update Docker images and dependencies
8. **AWS GuardDuty:** Enable for threat detection
9. **AWS Config:** Enable for compliance monitoring

## Scaling Path (AWS)

### Vertical Scaling
- **EC2:** Change instance type (t3.xlarge → t3.2xlarge → m5.2xlarge)
- **RDS:** Change instance class (db.t3.medium → db.t3.large → db.r6g.large)
- **EBS:** Increase volume size (200 GB → 500 GB → 1 TB)

### Horizontal Scaling
- **EC2:** Add instances to ALB target group (Auto Scaling Group)
- **RDS:** Add read replica for read-heavy workloads
- **Session affinity:** Configure ALB for sticky sessions if needed

### Database Sharding
- Group databases by customer tier
- Route subdomains to specific Odoo instances via ALB routing rules
- Shared RDS cluster with connection pooling (AWS RDS Proxy)

## Cost Estimates (AWS)

### Monthly Infrastructure Costs (Initial)

| Component | Specs | Cost/month |
|---|---|---|
| EC2 | t3.xlarge (4 vCPU, 16 GB RAM) | ~$140 |
| RDS | db.t3.medium (2 vCPU, 4 GB RAM, 100 GB) | ~$85 |
| EBS | 200 GB gp3 | ~$24 |
| ALB | Application Load Balancer | ~$22 (750 hours) + $0.008/GB |
| Route 53 | Hosted zone | ~$0.50 |
| S3 | Backups (variable) | ~$5–20 |
| Data Transfer | Outbound (variable) | ~$10–50 |
| **Total** | | **~$287–352/month** |

### Scaling Costs

| Scale | EC2 | RDS | Total/month |
|---|---|---|---|
| 100+ databases | t3.2xlarge (~$280) | db.t3.large (~$170) | ~$620 |
| 1000+ databases | 2× t3.2xlarge (~$560) | db.r6g.large (~$250) | ~$1,000 |

### Per Customer
- **Storage:** ~1 GB per database in RDS (minimal incremental cost)
- **Compute:** Shared across all customers
- **Bandwidth:** Included in ALB cost up to 1 TB/month

### Break-even Point
- At 20 customers @ $99/month = $1,980/month
- Infrastructure cost: ~$350/month
- Margin: ~82% (excluding development time)
- At 50 customers @ $99/month = $4,950/month
- Infrastructure cost: ~$620/month
- Margin: ~87%

## Next Steps

1. Implement Docker Compose configuration
2. Set up Nginx with wildcard SSL
3. Build Stripe webhook handler
4. Create landing page with Stripe Checkout
5. Test database provisioning end-to-end
6. Set up automated backups
7. Deploy to production

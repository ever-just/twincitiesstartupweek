# Single-Instance Deployment Plan for Odoo Platform (AWS)

## Overview

This document outlines the deployment architecture for running the Odoo Community fork as a single-instance platform for Twin Cities Startup Week on AWS.

## Architecture

```
tcsw.everjust.app
    ↓
AWS Route 53 (DNS)
    ↓
AWS Application Load Balancer (SSL via ACM)
    ↓
EC2 Instance (Docker)
    ├── Odoo Container
    ├── Redis Container
    └── PostgreSQL Container
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

### 2. AWS Application Load Balancer (Optional)
- **Type:** Application Load Balancer
- **SSL Certificate:** AWS Certificate Manager (ACM) for `tcsw.everjust.app`
- **Target Group:** EC2 instance on port 8069
- **Health Checks:** `/web/database/selector`
- **Note:** For single instance, you can skip ALB and use EC2 directly with ACM

### 3. AWS Route 53 (DNS)
- **Hosted Zone:** `everjust.app`
- **Record:** `tcsw.everjust.app` → ALB or EC2 public IP

### 4. AWS S3 (Backups)
- **Bucket:** `everjust-odoo-backups`
- **Lifecycle:** Move to Glacier after 30 days, delete after 1 year
- **Access:** Private, accessed via EC2 IAM role

### 5. AWS EBS (Filestore)
- **Volume:** 200 GB gp3 attached to EC2
- **Mount point:** `/var/lib/odoo/filestore`
- **Snapshots:** Daily automated snapshots

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
      - db
      - redis
    ports:
      - "8069:8069"
      - "8072:8072"
    environment:
      - HOST=db
      - PORT=5432
      - USER=odoo
      - PASSWORD=odoo
      - DB_NAME=tcsw_main
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

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_DB=tcsw_main
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres-data:
  odoo-data:
```

**Environment Variables (.env):**
```bash
# AWS S3 Configuration (for backups)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET=everjust-odoo-backups
```

### 2. Nginx Configuration (Optional)

**Note:** If not using ALB, use Nginx for SSL termination on EC2.

**File:** `deployment/nginx/nginx.conf`

```nginx
server {
    listen 80;
    server_name tcsw.everjust.app;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tcsw.everjust.app;

    ssl_certificate /etc/nginx/ssl/tcsw.everjust.app.crt;
    ssl_certificate_key /etc/nginx/ssl/tcsw.everjust.app.key;

    location / {
        proxy_pass http://odoo:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Deployment Steps (AWS - Single Instance)

### Phase 1: AWS Infrastructure Setup

1. **Create EC2 Instance**
   - Go to AWS Console → EC2 → Launch Instance
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t3.xlarge (4 vCPU, 16 GB RAM)
   - Key pair: Create or use existing
   - Network: VPC with public subnet
   - Security group: Allow 80, 443 from anywhere; allow SSH from your IP
   - Storage: 200 GB gp3 EBS (attach as /dev/sdb)

2. **Create AWS S3 Bucket for Backups**
   - Go to AWS Console → S3 → Create bucket
   - Bucket name: `everjust-odoo-backups` (must be globally unique)
   - Region: us-east-1
   - Block public access: Enabled
   - Lifecycle rule: Move to Glacier after 30 days, delete after 1 year

3. **Create IAM Role for EC2**
   - Go to AWS Console → IAM → Create role
   - Trusted entity: EC2
   - Permissions: S3FullAccess (or scoped to backup bucket)
   - Attach role to EC2 instance

4. **Request SSL Certificate via ACM (Optional)**
   - Go to AWS Console → Certificate Manager → Request
   - Domain name: `tcsw.everjust.app`
   - Validation: DNS validation (add CNAME record in Route 53)
   - Wait for validation to complete

5. **Configure Route 53 (Optional)**
   - Go to AWS Console → Route 53 → Hosted zones
   - Create hosted zone for `everjust.app` (if not exists)
   - Add A record: `tcsw.everjust.app` → EC2 public IP or ALB DNS name

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
   # Add AWS S3 keys for backups
   ```

6. **Build and start**
   ```bash
   docker compose up -d
   ```

7. **Initialize database**
   ```bash
   docker exec -it odoo odoo -d tcsw_main --init=base,event,crm,project,account,tcsw_events --stop-after-init
   ```

8. **Access Odoo**
   - Go to `http://your-ec2-public-ip:8069`
   - Create admin user
   - Install tcsw_events module from Apps menu

## Backup Strategy (AWS S3)

### Automated Backups to S3

**File:** `deployment/scripts/backup.sh`

```bash
#!/bin/bash
# Backup Odoo database and filestore to AWS S3
DATE=$(date +%Y%m%d_%H%M%S)
S3_BUCKET=${S3_BUCKET:-everjust-odoo-backups}

# Backup database
docker exec twincitiesstartupweek-db-1 pg_dump -U odoo tcsw_main | gzip > /tmp/tcsw_main_${DATE}.sql.gz
aws s3 cp /tmp/tcsw_main_${DATE}.sql.gz s3://$S3_BUCKET/databases/tcsw_main_${DATE}.sql.gz
rm /tmp/tcsw_main_${DATE}.sql.gz
echo "✓ Backed up database to S3"

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
gunzip < /tmp/restore.sql.gz | docker exec -i twincitiesstartupweek-db-1 psql -U odoo tcsw_main

# Restore filestore from S3
aws s3 cp s3://everjust-odoo-backups/filestore/filestore_20260607_020000.tar.gz /tmp/restore.tar.gz
docker exec -i twincitiesstartupweek-odoo-1 tar -xzf - -C /var/lib/odoo < /tmp/restore.tar.gz
```

### EBS Snapshots

Configure automated EBS snapshots via AWS Console:
- Volume: 200 GB EBS attached to EC2
- Schedule: Daily at 2 AM
- Retention: 7 snapshots (7 days)

## Monitoring (AWS CloudWatch)

### CloudWatch Metrics

AWS provides built-in monitoring:
- **EC2:** CPU utilization, network in/out, disk read/write
- **EBS:** volume read/write ops, throughput, queue length

### Custom CloudWatch Alarms

Set up alarms for:
- EC2 CPU > 80% for 5 minutes
- EBS free storage < 20 GB

### Health Checks

```bash
# Check Odoo status (from EC2)
curl http://localhost:8069/web/database/selector

# Check PostgreSQL
docker exec twincitiesstartupweek-db-1 pg_isready -U odoo

# Check disk space
df -h
```

### Logs

```bash
# Odoo logs
docker compose logs -f odoo

# Database logs
docker compose logs -f db
```

## Security Considerations (AWS)

1. **Environment variables:** Store sensitive data in `.env` (never commit to git)
2. **IAM roles:** Use IAM roles for EC2 instead of AWS access keys in .env
3. **Security groups:** Restrict access to necessary ports only (SSH only from your IP)
4. **SSL/TLS:** Use ACM certificates for HTTPS traffic
5. **Updates:** Regularly update Docker images and dependencies
6. **Database passwords:** Use strong, unique passwords in .env

## Scaling Path (AWS)

### Vertical Scaling
- **EC2:** Change instance type (t3.xlarge → t3.2xlarge → m5.2xlarge)
- **EBS:** Increase volume size (200 GB → 500 GB → 1 TB)

## Cost Estimates (AWS)

### Monthly Infrastructure Costs

| Component | Specs | Cost/month |
|---|---|---|
| EC2 | t3.xlarge (4 vCPU, 16 GB RAM) | ~$140 |
| EBS | 200 GB gp3 | ~$24 |
| Route 53 (optional) | Hosted zone | ~$0.50 |
| S3 | Backups (variable) | ~$5–20 |
| Data Transfer | Outbound (variable) | ~$10–50 |
| **Total** | | **~$180–235/month** |

### Scaling Costs

| Scale | EC2 | EBS | Total/month |
|---|---|---|---|
| Growth | t3.2xlarge (~$280) | 500 GB (~$60) | ~$390 |

## Next Steps

1. Create EC2 instance on AWS
2. Set up S3 bucket for backups
3. Configure IAM role for EC2
4. SSH into EC2 and install Docker
5. Clone repository and configure .env
6. Start Docker Compose
7. Initialize Odoo database
8. Set up automated backups
9. Configure SSL (optional)

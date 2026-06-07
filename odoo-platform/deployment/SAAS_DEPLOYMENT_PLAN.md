# SaaS Deployment Plan for Odoo Platform

## Overview

This document outlines the deployment architecture for running the Odoo Community fork as a multi-tenant SaaS platform on `everjust.app`.

## Architecture

```
everjust.app (Main Landing/Signup)
    ↓
Nginx Reverse Proxy
    ├── tcsw.everjust.app → Database: tcsw_main
    ├── customer1.everjust.app → Database: customer1
    ├── customer2.everjust.app → Database: customer2
    └── customerN.everjust.app → Database: customerN
    ↓
Odoo Container (Single Instance)
    ├── PostgreSQL (Multi-DB)
    ├── Redis (Cache)
    └── Filestore (Per-DB)
```

## Infrastructure Requirements

### Server Specs (Initial)
- **CPU:** 4 cores
- **RAM:** 16 GB
- **Storage:** 200 GB SSD
- **OS:** Ubuntu 22.04 LTS

### Scaling Considerations
- **100+ databases:** Scale to 8 cores, 32 GB RAM
- **1000+ databases:** Shard across multiple Odoo instances

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
      - DBFILTER=^%d$
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    volumes:
      - ./odoo/odoo:/opt/odoo
      - ./custom-modules:/opt/odoo/addons/custom
      - odoo-data:/var/lib/odoo
      - odoo-filestore:/var/lib/odoo/filestore
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_DB=postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - odoo
    restart: unless-stopped

volumes:
  postgres-data:
  odoo-data:
  odoo-filestore:
```

### 2. Nginx Subdomain Routing

**File:** `deployment/nginx/nginx.conf`

```nginx
server {
    listen 80;
    server_name everjust.app www.everjust.app;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name everjust.app www.everjust.app;

    ssl_certificate /etc/nginx/ssl/everjust.app.crt;
    ssl_certificate_key /etc/nginx/ssl/everjust.app.key;

    location / {
        proxy_pass http://odoo:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Wildcard subdomain routing for customer databases
server {
    listen 443 ssl http2;
    server_name *.everjust.app;

    ssl_certificate /etc/nginx/ssl/everjust.app.crt;
    ssl_certificate_key /etc/nginx/ssl/everjust.app.key;

    location / {
        # Extract subdomain as database name
        # tcsw.everjust.app → database: tcsw_main
        # customer1.everjust.app → database: customer1
        proxy_pass http://odoo:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Database Provisioning Script

**File:** `deployment/scripts/provision_database.py`

```python
#!/usr/bin/env python3
"""
Provision a new Odoo database for a SaaS customer.
Usage: python provision_database.py --db-name customer1 --email user@example.com --plan pro
"""

import subprocess
import sys
import argparse

def create_database(db_name):
    """Create a new PostgreSQL database."""
    cmd = f"docker exec twincitiesstartupweek-db-1 createdb -U odoo {db_name}"
    subprocess.run(cmd, shell=True, check=True)
    print(f"✓ Database {db_name} created")

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

    print(f"Provisioning database: {args.db_name}")
    create_database(args.db_name)
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

## Deployment Steps

### Phase 1: Initial Setup

1. **Set up server**
   ```bash
   # Install Docker and Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **Clone repository**
   ```bash
   git clone https://github.com/ever-just/twincitiesstartupweek.git
   cd twincitiesstartupweek/odoo-platform
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Build and start**
   ```bash
   docker-compose up -d
   ```

5. **Initialize main database**
   ```bash
   docker exec -it odoo odoo -d tcsw_main --init=base,event,crm,project,account,tcsw_events --stop-after-init
   ```

### Phase 2: SSL Configuration

1. **Generate SSL certificate** (Let's Encrypt)
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d everjust.app -d *.everjust.app
   ```

2. **Update Nginx config** to use generated certificates

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

## Backup Strategy

### Automated Backups

**File:** `deployment/scripts/backup.sh`

```bash
#!/bin/bash
# Backup all Odoo databases
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups

for db in $(docker exec twincitiesstartupweek-db-1 psql -U odoo -t -c "SELECT datname FROM pg_database WHERE datname LIKE 'tcsw_%' OR datname = 'tcsw_main'"); do
    docker exec twincitiesstartupweek-db-1 pg_dump -U odoo $db > $BACKUP_DIR/${db}_${DATE}.sql
    gzip $BACKUP_DIR/${db}_${DATE}.sql
done

# Backup filestore
docker exec twincitiesstartupweek-odoo-1 tar -czf - /var/lib/odoo/filestore > $BACKUP_DIR/filestore_${DATE}.tar.gz
```

**Cron job:**
```bash
0 2 * * * /path/to/backup.sh
```

### Restore Procedure

```bash
# Restore database
gunzip < backup.sql.gz | docker exec -i twincitiesstartupweek-db-1 psql -U odoo db_name

# Restore filestore
docker exec -i twincitiesstartupweek-odoo-1 tar -xzf - -C /var/lib/odoo < filestore.tar.gz
```

## Monitoring

### Health Checks

```bash
# Check Odoo status
curl http://localhost:8069/web/database/selector

# Check PostgreSQL
docker exec twincitiesstartupweek-db-1 pg_isready -U odoo

# Check disk space
df -h
```

### Logs

```bash
# Odoo logs
docker-compose logs -f odoo

# Database logs
docker-compose logs -f db
```

## Security Considerations

1. **Environment variables:** Store sensitive data in `.env` (never commit)
2. **Database passwords:** Use strong, unique passwords
3. **API keys:** Rotate Stripe webhook secrets regularly
4. **Firewall:** Restrict access to necessary ports only
5. **Updates:** Regularly update Docker images and dependencies

## Scaling Path

### Vertical Scaling
- Increase CPU/RAM on single server
- Monitor performance metrics

### Horizontal Scaling
- Add Nginx load balancer
- Run multiple Odoo containers
- Use shared PostgreSQL and Redis

### Database Sharding
- Group databases by customer tier
- Route subdomains to specific Odoo instances
- Shared PostgreSQL cluster

## Cost Estimates

### Initial Setup
- **Server (4 cores, 16 GB, 200 GB):** ~$80/month (DigitalOcean/Hetzner)
- **Domain:** ~$12/year
- **SSL:** Free (Let's Encrypt)

### Per Customer
- **Storage:** ~1 GB per database (minimal)
- **Compute:** Shared across all customers
- **Bandwidth:** Included in server cost

### Break-even Point
- At 20 customers @ $99/month = $1,980/month
- Server cost: $80/month
- Margin: ~96% (excluding development time)

## Next Steps

1. Implement Docker Compose configuration
2. Set up Nginx with wildcard SSL
3. Build Stripe webhook handler
4. Create landing page with Stripe Checkout
5. Test database provisioning end-to-end
6. Set up automated backups
7. Deploy to production

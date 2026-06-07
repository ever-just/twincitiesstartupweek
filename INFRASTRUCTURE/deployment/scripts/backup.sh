#!/bin/bash
# Backup Odoo database and filestore to AWS S3
DATE=$(date +%Y%m%d_%H%M%S)
S3_BUCKET=${S3_BUCKET:-everjust-odoo-backups}

# Backup database
docker exec deployment-db-1 pg_dump -U odoo tcsw_main | gzip > /tmp/tcsw_main_${DATE}.sql.gz
aws s3 cp /tmp/tcsw_main_${DATE}.sql.gz s3://$S3_BUCKET/databases/tcsw_main_${DATE}.sql.gz
rm /tmp/tcsw_main_${DATE}.sql.gz
echo "✓ Backed up database to S3"

# Backup filestore to S3
docker exec deployment-odoo-1 tar -czf - /var/lib/odoo/filestore | gzip > /tmp/filestore_${DATE}.tar.gz
aws s3 cp /tmp/filestore_${DATE}.tar.gz s3://$S3_BUCKET/filestore/filestore_${DATE}.tar.gz
rm /tmp/filestore_${DATE}.tar.gz
echo "✓ Backed up filestore to S3"

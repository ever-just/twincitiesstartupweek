# Platform Upgrade Plan: Odoo 17 → 19

**Current:** Odoo 17 (Community) on AWS EC2, Docker  
**Target:** Odoo 19 (Community)  
**Path:** 17 → 18 → 19 (two hops — direct 17→19 is not supported)  
**Estimated time:** 4–6 hours total across both hops  
**Risk level:** Low — custom modules are simple, clean, no deprecated API patterns

---

## Why two hops

Odoo does not support skipping major versions. The database migration scripts only handle one version step at a time. 17 → 18 first, test fully, then 18 → 19.

---

## Pre-flight: before touching anything

### 1. Verify custom module compatibility

No deprecated patterns were found in our modules (`tcsw_branding`, `tcsw_events`). Both use current API patterns. No changes needed before starting.

Run this to double-check before each hop:

```bash
grep -r "api\.multi\|api\.one\|fields\.binary\.related" INFRASTRUCTURE/custom-modules/
```

No output = clean.

### 2. Take a full backup

```bash
ssh -i INFRASTRUCTURE/deployment/odoo-tcsw-key.pem ubuntu@52.91.38.110

# On the server:
cd ~/twincitiesstartupweek/INFRASTRUCTURE/deployment
docker exec deployment-db-1 pg_dump -U odoo odoo > /home/ubuntu/backup_odoo17_$(date +%Y%m%d).sql
```

Store this backup off-server (download it locally) before proceeding.

### 3. Spin up a staging clone

Do NOT upgrade production directly. Clone the database into a staging environment first.

```bash
# On the server — create a staging DB from the backup
docker exec deployment-db-1 psql -U odoo -c "CREATE DATABASE odoo_staging TEMPLATE odoo;"
```

---

## Hop 1: 17 → 18

### Step 1 — Run the official upgrade script against staging

Odoo provides a free upgrade script for Community (on-premise). This handles schema migration and data transformation:

```bash
# On the server, inside the container or with psql access:
python3 <(curl -s https://upgrade.odoo.com/upgrade) test \
  -d odoo_staging \
  -t 18.0
```

This sends your database to Odoo's upgrade platform and returns a migrated copy. It does NOT touch your production database.

### Step 2 — Swap the Docker image to 18 for staging

In `docker-compose.yml`, temporarily change the image for a staging container:

```yaml
# docker-compose.staging.yml
services:
  odoo:
    image: odoo:18
    ...
    volumes:
      - ./custom-modules:/mnt/extra-addons
    environment:
      - DB_NAME=odoo_staging
```

```bash
docker compose -f docker-compose.staging.yml up -d
```

### Step 3 — Test staging on 18

Check these specifically:

- [ ] Login works
- [ ] CRM pipeline loads — all 67 sponsor opps present
- [ ] Contacts load — 68 orgs, 600 speakers
- [ ] Events load — 8 events with registrations intact
- [ ] tcsw_branding module active (check Settings > Apps)
- [ ] tcsw_events module active
- [ ] Email marketing campaigns still present
- [ ] Projects and tasks intact

### Step 4 — Upgrade production to 18

Once staging passes:

```bash
# Take a fresh production backup first
docker exec deployment-db-1 pg_dump -U odoo odoo > /home/ubuntu/backup_pre18_$(date +%Y%m%d).sql

# Run the upgrade script on the production DB
python3 <(curl -s https://upgrade.odoo.com/upgrade) production \
  -d odoo \
  -t 18.0

# Update docker-compose.yml: image: odoo:17 → image: odoo:18
# Then restart
docker compose down
docker compose up -d
```

Production is now on 18. Verify it works before proceeding to hop 2.

---

## Hop 2: 18 → 19

Repeat the same process with `odoo_staging` refreshed from the now-18 production database.

### Step 1 — Refresh staging from production 18 backup

```bash
docker exec deployment-db-1 pg_dump -U odoo odoo > /home/ubuntu/backup_odoo18.sql
docker exec deployment-db-1 psql -U odoo -c "DROP DATABASE odoo_staging;"
docker exec deployment-db-1 psql -U odoo -c "CREATE DATABASE odoo_staging TEMPLATE odoo;"
```

### Step 2 — Run upgrade script to 19

```bash
python3 <(curl -s https://upgrade.odoo.com/upgrade) test \
  -d odoo_staging \
  -t 19.0
```

### Step 3 — Test staging on 19

Same checklist as hop 1, plus verify the new 19 features work:

- [ ] AI assistant accessible (Settings)
- [ ] Kanban views render correctly for CRM and Events
- [ ] Drag-and-drop in list views works
- [ ] No broken views or missing fields in tcsw_events or tcsw_branding

### Step 4 — Upgrade production to 19

```bash
# Fresh backup
docker exec deployment-db-1 pg_dump -U odoo odoo > /home/ubuntu/backup_pre19_$(date +%Y%m%d).sql

# Upgrade script on production DB
python3 <(curl -s https://upgrade.odoo.com/upgrade) production \
  -d odoo \
  -t 19.0

# Update docker-compose.yml: image: odoo:18 → image: odoo:19
docker compose down
docker compose up -d
```

---

## Rollback plan

If anything goes wrong at any point:

```bash
# Stop the new container
docker compose down

# Restore the backup
docker exec deployment-db-1 psql -U odoo -c "DROP DATABASE odoo;"
docker exec deployment-db-1 psql -U odoo -c "CREATE DATABASE odoo;"
cat /home/ubuntu/backup_pre18_YYYYMMDD.sql | docker exec -i deployment-db-1 psql -U odoo odoo

# Revert docker-compose.yml image tag
# Restart
docker compose up -d
```

---

## Timing recommendation

**Do not run this upgrade during active TCSW production work.**  
Best window: a quiet weekday morning with 3–4 hours blocked. Both hops in one session if staging looks clean.

| Phase | Time estimate |
|---|---|
| Pre-flight backup + staging setup | 30 min |
| Hop 1: 17 → 18 (staging + test + production) | 90 min |
| Hop 2: 18 → 19 (staging + test + production) | 90 min |
| Post-upgrade verification | 30 min |
| **Total** | **~4 hours** |

---

## What changes after upgrade to 19

Things the team will notice:

- **AI assistant** — accessible from the top bar; can answer questions about CRM data and contacts in natural language
- **Faster Kanban** — sponsor pipeline board will be more responsive
- **Drag-and-drop sorting** in list views (contacts, sessions, etc.)
- **Compact view options** — less white space, more data visible at once
- UI is otherwise familiar — no workflow changes

Things that stay the same:

- All data, contacts, events, CRM pipelines
- TCSW branding (tcsw_branding module carries over)
- Custom event fields (tcsw_events module carries over)
- URL and server setup unchanged

# INFRASTRUCTURE — everjust.app

The operational platform for TCSW 2026, running at **[tcsw.everjust.app](https://tcsw.everjust.app)**.

This is the event management system: CRM, contacts, sponsor pipeline, event registration, project ops, and email marketing — all under TCSW branding.

## Platform

Self-hosted on AWS EC2 via Docker Compose. Access at `https://tcsw.everjust.app`.

| What | Detail |
|---|---|
| **URL** | https://tcsw.everjust.app |
| **Login** | company@everjust.org |
| **Modules active** | Events, CRM, Project, Email Marketing, Website |
| **Data loaded** | 68 orgs, 600 speakers, 8 events, 67 CRM opps |

## Structure

```
INFRASTRUCTURE/
├── custom-modules/
│   ├── tcsw_branding/     # TCSW theme, colors, login page (removes default branding)
│   └── tcsw_events/       # Custom event types, sponsor tiers, CRM pipeline
├── deployment/
│   ├── docker-compose.yml # Full stack: app + database + proxy
│   ├── .env.example       # Environment variable template
│   └── scripts/
│       └── backup.sh      # Automated database backup
└── README.md
```

## Deployment

```bash
# SSH to server
ssh -i deployment/odoo-tcsw-key.pem ubuntu@52.91.38.110

# Restart platform
cd ~/twincitiesstartupweek/INFRASTRUCTURE/deployment
docker compose restart

# View logs
docker compose logs -f
```

## Custom Modules

### tcsw_branding
Removes default platform branding and applies TCSW identity: primary `#E8452C`, dark `#1A1A2E`, accent `#F5A623`. Covers backend, login page, and frontend event pages.

### tcsw_events
Extends the Events and CRM modules for startup week: multi-day event types, sponsor tier tracking, session/speaker relationships, and volunteer roles.

## Adding New Modules

1. Create module folder in `custom-modules/`
2. Required files: `__manifest__.py`, `__init__.py`, `models/`, `views/`, `security/`
3. Restart the platform — module will appear in Apps

# Odoo Platform for Twin Cities Startup Week

This directory contains a fork of Odoo Community Edition with customizations for event management, specifically designed for multi-day, multi-venue startup week events and SaaS deployment.

## Structure

```
odoo-platform/
├── odoo/                    # Forked Odoo Community repository
├── custom-modules/          # Custom Odoo modules
│   └── tcsw_events/        # TCSW-specific event configuration
├── deployment/              # Docker compose and deployment scripts
└── docs/                    # Odoo-specific documentation
```

## Fork Information

- **Upstream:** https://github.com/odoo/odoo
- **Fork:** https://github.com/ever-just/odoo
- **License:** LGPL-3.0 (Community Edition)
- **Branch:** main (shallow clone for initial setup)

## Custom Modules

### tcsw_events

Custom module extending Odoo's Events and CRM modules for startup week event management.

**Features:**
- Custom event types for multi-day startup week events
- Partner organization tracking and session submissions
- Sponsor tier management (Platinum, Gold, Silver, Bronze, Supporter)
- Volunteer role and shift tracking
- Enhanced attendee registration fields
- Sponsor/vendor pipeline in CRM

**Installation:**
1. Copy `custom-modules/tcsw_events/` to `odoo/odoo/addons/`
2. Update Odoo addons path configuration
3. Install module from Apps menu

## Development

### Updating from Upstream

To pull latest changes from Odoo Community:

```bash
cd odoo-platform/odoo
git fetch upstream
git merge upstream/main
```

### Creating New Custom Modules

1. Create new module in `custom-modules/`
2. Follow Odoo module structure:
   - `__manifest__.py` (module manifest)
   - `__init__.py` (Python init)
   - `models/` (data models)
   - `views/` (XML views)
   - `security/` (access rights)
   - `i18n/` (translations)
3. Copy to `odoo/odoo/addons/` for testing
4. Install from Apps menu

## Deployment

See `deployment/` for Docker compose configuration and deployment scripts.

## License

- Odoo Community: LGPL-3.0
- Custom modules: LGPL-3.0

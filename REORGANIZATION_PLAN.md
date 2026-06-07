# Repository Reorganization Plan

## Current Structure
```
twincitiesstartupweek/
├── .git/
├── .gitignore
├── README.md
├── TCSW_Sponsors_Master.pdf
├── TCSW_Sponsors_Master.xlsx
├── analysis/
├── data/
├── docs/
├── event-management-research/
├── event-ops/
├── findings/
├── raw/
└── scripts/
```

## Proposed Structure

```
twincitiesstartupweek/
├── .git/
├── .gitignore
├── README.md (updated to reflect new structure)
│
├── archive/                    # Historical data and raw materials
│   ├── raw/                    # Move current raw/ here
│   ├── data/                   # Move current data/ here
│   └── scripts/                # Move current scripts/ here
│
├── operations/                 # Event operations and execution docs
│   ├── event-ops/              # Move current event-ops/ here
│   └── findings/               # Move current findings/ here
│
├── research/                   # All research and analysis
│   ├── analysis/               # Move current analysis/ here
│   ├── docs/                   # Move current docs/ here
│   └── event-management-research/ # Move current event-management-research/ here
│
├── assets/                     # Static assets (PDFs, Excel files)
│   ├── TCSW_Sponsors_Master.pdf
│   └── TCSW_Sponsors_Master.xlsx
│
└── odoo-platform/              # NEW: Odoo fork and customizations
    ├── odoo/                   # Forked Odoo Community repo
    ├── custom-modules/         # Custom Odoo modules for TCSW/SaaS
    │   ├── tcsw_events/        # Custom Events configuration
    │   ├── saas_provisioning/  # Database provisioning automation
    │   └── stripe_billing/      # Stripe integration module
    ├── deployment/             # Docker compose, deployment scripts
    ├── docs/                   # Odoo-specific documentation
    └── README.md               # Odoo platform README
```

## Migration Steps

### Phase 1: Reorganize Existing Content
1. Create new folder structure (archive/, operations/, research/, assets/)
2. Move raw/ → archive/raw/
3. Move data/ → archive/data/
4. Move scripts/ → archive/scripts/
5. Move event-ops/ → operations/event-ops/
6. Move findings/ → operations/findings/
7. Move analysis/ → research/analysis/
8. Move docs/ → research/docs/
9. Move event-management-research/ → research/event-management-research/
10. Move TCSW_Sponsors_Master.pdf → assets/
11. Move TCSW_Sponsors_Master.xlsx → assets/

### Phase 2: Add Odoo Platform
1. Create odoo-platform/ directory
2. Fork odoo/odoo from GitHub to your account
3. Clone fork into odoo-platform/odoo/
4. Create custom-modules/ subdirectory structure
5. Create deployment/ subdirectory
6. Create docs/ subdirectory
7. Write odoo-platform/README.md

### Phase 3: Git Configuration
1. Update .gitignore to exclude Odoo build artifacts
2. Commit reorganization
3. Create git submodules if needed (or just include Odoo directly)

## .gitignore Additions for Odoo

```
# Odoo-specific
odoo-platform/odoo/.git/
odoo-platform/odoo/.local/
odoo-platform/odoo/odoo.egg-info/
odoo-platform/odoo/*.pyc
odoo-platform/odoo/__pycache__/
odoo-platform/odoo/odoo/addons/__pycache__/
odoo-platform/odoo/odoo/addons/*/__pycache__/
odoo-platform/odoo/node_modules/
odoo-platform/odoo/.eslintcache
odoo-platform/odoo/.idea/
odoo-platform/odoo/.vscode/
odoo-platform/odoo/*.log
odoo-platform/odoo/filestore/
odoo-platform/odoo/sessions/
```

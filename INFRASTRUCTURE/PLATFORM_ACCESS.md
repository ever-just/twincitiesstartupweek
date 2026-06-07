# Platform Access — TCSW on EVERJUST.APP

How to reach and manage the TCSW workspace. **No credentials are committed here** — get the admin login from the team password manager.

## Workspace

| | |
|---|---|
| **URL** | https://tcsw.everjust.app |
| **Platform** | EVERJUST.APP (managed multi-tenant SaaS) |
| **Tenant** | `tcsw` (isolated database, isolated data) |
| **Admin account** | stored in password manager |

Sign in at the URL above for the full UI: CRM, Contacts, Events, Projects, Email Marketing.

## Programmatic access (API / MCP)

The workspace speaks the standard Odoo XML-RPC API. Use it for automation, reporting, bulk imports, and AI-agent (MCP) access — no SSH or server access required.

### Endpoints

```
Base URL:   https://tcsw.everjust.app
Database:   tcsw
Common:     https://tcsw.everjust.app/xmlrpc/2/common   # auth, version
Object:     https://tcsw.everjust.app/xmlrpc/2/object   # read/write models
```

### Auth + example (Python)

```python
import xmlrpc.client

URL = "https://tcsw.everjust.app"
DB = "tcsw"
USERNAME = "admin@tcsw.everjust.app"   # from password manager
PASSWORD = "<from-password-manager>"    # never commit

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})

models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

# Example: list the 10 most recent CRM opportunities
opps = models.execute_kw(
    DB, uid, PASSWORD,
    "crm.lead", "search_read",
    [[]],
    {"fields": ["name", "partner_id", "stage_id", "expected_revenue"], "limit": 10},
)
print(opps)
```

### Common models

| Purpose | Model |
|---|---|
| Contacts / orgs | `res.partner` |
| CRM pipeline | `crm.lead` |
| Events | `event.event` |
| Event registrations | `event.registration` |
| Projects | `project.project` / `project.task` |

## Billing

Subscription is managed through the EVERJUST.APP platform (Stripe). Plan: $100/mo including up to 5 users, then $15/user. Billing and seat changes are handled platform-side; no action needed in this repo.

## Operating the platform itself

If you need to change platform behavior (branding, theme, provisioning, pricing, deployment), work in the platform repo — not here:

- **Repo:** https://github.com/ever-just/ww.everjust.app
- It contains the Odoo 19 module overlay (`everjust_brand`, `everjust_theme`), the FastAPI control plane (signup + Stripe + provisioning), and the Docker/Nginx deployment.

## Break-glass server access

For rare host-level maintenance only. The SSH key is kept locally and git-ignored. Routine work should never need this — prefer the UI or the API above.

# INFRASTRUCTURE — Platform Access

TCSW's operational system runs on **EVERJUST.APP**, a managed multi-tenant SaaS platform. TCSW is a tenant on that platform — it is **no longer self-hosted from this repo**.

| What | Detail |
|---|---|
| **Workspace** | https://tcsw.everjust.app |
| **Platform** | EVERJUST.APP (managed SaaS) |
| **Capabilities** | CRM, contacts, sponsor pipeline, event registration, project ops, email marketing |
| **Hosting** | Managed by the platform — no servers to run from this repo |

## What changed

Previously this folder held a full self-hosted Odoo stack (1.3 GB of source, Docker Compose, custom modules, a server key). That setup is **retired**. The platform — branding, theming, multi-tenancy, billing, provisioning, and deployment — now lives in its own repository and is operated as a service.

- **Platform code:** [`ever-just/ww.everjust.app`](https://github.com/ever-just/ww.everjust.app)
- **This folder:** thin access layer only — how TCSW connects to and manages its workspace.

## Access

`PLATFORM_ACCESS.md` documents how to reach the TCSW workspace and manage it programmatically. Credentials are **not stored in this repo** — they live in the team password manager.

### Interactive
Open https://tcsw.everjust.app and sign in with the TCSW admin account.

### Programmatic (MCP / API)
The workspace exposes a standard XML-RPC API for automation and AI-agent access. See `PLATFORM_ACCESS.md` for the connection pattern (endpoints, auth, and example calls). This is how Cascade and other tooling read/write CRM, contacts, and event data without touching any server.

## Structure

```
INFRASTRUCTURE/
├── README.md             # This file
└── PLATFORM_ACCESS.md    # Workspace endpoints + API/MCP access pattern
```

## Server key

The SSH key for the underlying platform host is retained locally for break-glass admin only and is **git-ignored** (never committed). Day-to-day work needs no SSH — use the workspace UI or the API.

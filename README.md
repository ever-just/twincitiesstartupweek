# Twin Cities Startup Week — Operating Repository

TCSW 2026 · September 14–18 · Minneapolis + St. Paul

This repository is the central workspace for the **SMS x BETA partnership** producing Twin Cities Startup Week 2026. It holds historical research on TCSW, active planning and strategy, and the event management platform running at **[tcsw.everjust.app](https://tcsw.everjust.app)**.

---

## What's here

```
BACKGROUND/       Historical research on TCSW (2014-2026)
PLANNING/         Live strategy and operating documents for 2026
INFRASTRUCTURE/   Event management platform (tcsw.everjust.app)
```

---

## BACKGROUND

Comprehensive OSINT research on TCSW: sponsors, speakers, sessions, media, financials, and twelve years of history.

```
BACKGROUND/
├── analysis/         Strategic analysis, master findings, event operations research
├── history/          Year-by-year summaries and Wayback snapshots (2014-2025)
├── sponsors/         Sponsor database (CSV + MD), logos, multi-year history, 2026 targets
├── people/           Speaker database (600+), contacts, organization roster
├── sessions/         Session records by year (CSV + JSON, 2018-2025)
├── investors/        VC firms, MN Cup history, featured startups
├── media/            Press coverage by year, publication, and topic
├── quantitative/     Attendance data, financials, PDFs (2015-2021 recap reports)
├── official-site/    Scraped official website content and assets
└── raw/              Source HTML, JSON, Wayback archives, photos
```

**Key files:**

| File | What it is |
|---|---|
| `BACKGROUND/analysis/master-findings-report.md` | Full OSINT findings — the single best summary of TCSW history |
| `BACKGROUND/analysis/strategic-analysis.md` | SWOT, competitive landscape, opportunity framing |
| `BACKGROUND/sponsors/sponsors-database.csv` | All known sponsors, tiers, and years of involvement |
| `BACKGROUND/sponsors/TCSW_Sponsors_Master.pdf` | Full sponsor master document |
| `BACKGROUND/people/speakers-database.csv` | 600+ speakers across all years |
| `BACKGROUND/sessions/all-sessions.csv` | Every session from 2018-2025 |

**TCSW at a glance:**

| Item | Detail |
|---|---|
| Founded | 2014 |
| Operator | The Beta Group (BETA) — 501(c)(3) |
| Peak attendance | ~17,000-19,000 (2019-2020) |
| 2025 attendance | 1,000+ (leaner format) |
| 2026 dates | September 14-18 |
| Format | Unconference — community-driven programming |
| Website | tcstartupweek.com |

---

## PLANNING

Live operating documents for TCSW 2026. SMS is the proposed end-to-end production and community experience partner.

```
PLANNING/
└── 01-runtime-os/              Liban's live operating system for TCSW 2026
    ├── 01-thesis/              Core argument: why SMS, why now, what we're building
    ├── 02-stakeholders/        SMS team profiles, BETA contacts
    ├── 03-operating-model/     BETA-SMS partnership structure, roles, decision rights
    ├── 05-venues/              Venue pipeline and location architecture
    ├── 06-funding/             Budget model, sponsor pipeline, funding strategy, offer menu
    ├── 09-meetings/            Board-chair prep, Angela/Linda sessions, operating cadence
    └── 11-deliverables/        Decision briefs and proposals for BETA
```

**Start here:**

| File | What it is |
|---|---|
| `PLANNING/01-runtime-os/01-thesis/current-discovery-synthesis.md` | Core frame: the integrated challenge and SMS's answer |
| `PLANNING/01-runtime-os/11-deliverables/angela-linda-decision-brief.md` | Decision brief for BETA — what SMS is asking for |
| `PLANNING/01-runtime-os/11-deliverables/sms-beta-end-to-end-proposal.md` | Full production partnership proposal |
| `PLANNING/01-runtime-os/11-deliverables/sms-team-operating-brief.md` | SMS team structure and operating commitments |
| `PLANNING/01-runtime-os/09-meetings/2026-06-08-board-chair-meeting-prep.md` | June 8 board meeting prep |
| `PLANNING/01-runtime-os/06-funding/sponsor-pipeline.md` | Current sponsor pipeline and prioritization |
| `PLANNING/01-runtime-os/05-venues/venue-pipeline.md` | Venue candidates and location logic |

**Working thesis:**

> SMS proposes to serve as the end-to-end production and community experience partner for TCSW 2026. BETA holds institutional legitimacy and stewards sponsor relationships. SMS carries the production layer: venues, programming, brand, marketing, registration, sponsor experience, and attendee journey.

---

## INFRASTRUCTURE

The event management platform at **[tcsw.everjust.app](https://tcsw.everjust.app)**.

Self-hosted on AWS EC2 via Docker Compose. Manages CRM, contacts, event registration, project ops, sponsor pipeline, and email marketing — all under TCSW branding.

```
INFRASTRUCTURE/
├── custom-modules/
│   ├── tcsw_branding/     TCSW theme, colors, login page
│   └── tcsw_events/       Custom event types, sponsor tiers, CRM pipeline
├── deployment/
│   ├── docker-compose.yml
│   ├── .env.example
│   └── scripts/backup.sh
└── README.md              Platform setup, deployment, and module docs
```

**Platform status:**

| What | Detail |
|---|---|
| URL | https://tcsw.everjust.app |
| Login | company@everjust.org |
| Server | AWS EC2 (us-east-1) |
| Organizations loaded | 68 |
| Speakers loaded | 600 |
| Sponsor pipeline opps | 67 |
| Events configured | 8 |

See `INFRASTRUCTURE/README.md` for deployment and module documentation.

---

## Who built what

| Contributor | Role | Area |
|---|---|---|
| **Weldon** | COO / Research | `BACKGROUND/` — OSINT research, sponsor intelligence, data collection |
| **Liban** | Executive Producer | `PLANNING/` — strategy, proposals, operating OS |
| **everjust.app team** | Infrastructure | `INFRASTRUCTURE/` — platform setup, branding, data import |

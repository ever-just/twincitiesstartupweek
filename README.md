# Twin Cities Startup Week — Research Intelligence Repository

> Comprehensive OSINT research archive covering **Twin Cities Startup Week (TCSW) 2014–2026** — Minnesota's largest startup festival, run by [The Beta Group (BETA)](https://beta.mn), a 501(c)(3) nonprofit.

---

## What's In This Repo

This repository contains structured intelligence gathered on TCSW across three areas:

| Area | Description |
|---|---|
| **`research/`** | All research data, analysis, findings, and planning docs |
| **`scripts/`** | Python scrapers that collected the raw data |
| **`event-management-research/`** | Deep-dive into TCSW's event operations model |

---

## Key Numbers

| Metric | Detail |
|---|---|
| **Years Covered** | 2014–2026 (12 completed editions) |
| **Peak Attendance** | ~17,000–19,000 (2019–2021) |
| **Sessions Archived** | 200+ per peak year |
| **Sponsors Catalogued** | 80+ companies across all tiers and years |
| **Speakers Documented** | 80+ entries (CSV database) |
| **Media Articles Collected** | 50+ articles across 8 publications |
| **Data Sources** | sched.com, Wayback Machine, TCB Magazine, official site, BETA.MN |
| **2026 Event Dates** | September 14–18, Minneapolis + St. Paul |

---

## Research (`research/`)

The core of this repository. Everything lives under a well-structured folder hierarchy.

### Quick Navigation

| Need | File |
|---|---|
| Executive summary of all findings | [`research/findings/MASTER_FINDINGS_REPORT.md`](research/findings/MASTER_FINDINGS_REPORT.md) |
| Year-by-year history 2014–2026 | `research/data_collection/historical_snapshots/TCSW_COMPLETE_TIMELINE.md` |
| Sponsor database (Markdown) | `research/data_collection/sponsors/SPONSORS_DATABASE.md` |
| Sponsor database (CSV) | `research/data_collection/sponsors/SPONSORS_DATABASE.csv` |
| 2026 sponsor targets | `research/data_collection/sponsors/current_sponsors/2026_SPONSORS.md` |
| Fortune 500 deep-dive | `research/data_collection/sponsors/historical_sponsors/FORTUNE500_SPONSORS_2019.md` |
| Speaker database (CSV) | `research/data_collection/speakers_and_sessions/SPEAKERS_DATABASE.csv` |
| All media coverage | `research/data_collection/media_coverage/MEDIA_COVERAGE_DATABASE.md` |
| VC firms + angel investors | `research/data_collection/investors_and_startups/investors/MN_VC_FIRMS.md` |
| MN Cup winners history | `research/data_collection/investors_and_startups/funding_outcomes/MN_CUP_HISTORY.md` |
| SWOT + strategic analysis | [`research/analysis/STRATEGIC_ANALYSIS.md`](research/analysis/STRATEGIC_ANALYSIS.md) |
| Full file index | [`research/INDEX.md`](research/INDEX.md) |

### Folder Structure

```
research/
├── INDEX.md                        ← Start here for navigation
├── findings/
│   └── MASTER_FINDINGS_REPORT.md  ← Executive summary of all research
├── analysis/
│   └── STRATEGIC_ANALYSIS.md      ← SWOT, sponsorship strategy, 2026 priorities
├── data_collection/
│   ├── historical_snapshots/      ← Year summaries: 2015–2025 + master timeline
│   ├── sponsors/                  ← Sponsor DB (all years, all tiers) + 2026 targets
│   ├── speakers_and_sessions/     ← Speaker CSV + recurring events list
│   ├── media_coverage/            ← 50+ articles, organized by year & publication
│   ├── investors_and_startups/    ← VC firms, featured startups, MN Cup history
│   ├── official_website/          ← Scraped 2026 site notes
│   └── social_media/             ← Handles, hashtags, social intelligence
├── raw_data/                      ← Source files: JSON, HTML, XML, ICS from scrapers
├── planning/                      ← OSINT methodology, AI prompts, execution plans
├── tracking/                      ← Research log + source error tracking
└── visualizations/                ← (placeholder for charts/graphs)
```

### Data Completeness

| Category | Completeness | Known Gaps |
|---|---|---|
| Historical Timeline | 90% | 2022, 2024 sparse |
| Sponsors | 85% | 2015–2016 missing |
| Speakers | ~80% (2023/2025), ~40% (pre-2022) | Pre-2022 sparse |
| Media Coverage | 85% | 2015–2017 missing |
| Investors / VCs | 90% | — |
| Featured Startups | 75% | 2025 BETA cohort names not public |
| Analysis + Findings | 100% | Complete |

---

## Key Findings

### About TCSW

- **Founded:** 2014 by The Beta Group (BETA), a Minneapolis-based 501(c)(3)
- **Operator:** [beta.mn](https://beta.mn) — also manages tech.mn and MN startup community programs
- **Format:** Unconference — community-submitted sessions; low production cost, high authenticity
- **Contact:** [Angela.Eifert@BETA.MN](mailto:Angela.Eifert@BETA.MN) (Executive Director)

### Growth Arc

```
2014  →  ~few thousand attendees, 15 events (tech-only)
2018  →  12,000+, 200+ events (first major expansion)
2019  →  17,000+, Fortune 500 title sponsors (Target, Cargill, 3M)
2020  →  ~19,000 VIRTUAL (COVID, 3-week format on Hopin)
2021  →  ~17,000, hybrid return
2023  →  Full in-person; Luminary Arts Center; Optum Cup naming rights
2025  →  1,000+ (intentionally leaner; co-hosted with Communiful)
2026  →  September 14–18; 6 campuses; themed days (AI, Investor, Give Back)
```

### Sponsor Landscape

Major sponsors identified across years:

- **Fortune 500:** Target, Cargill, 3M, Microsoft, AWS, Walmart, Ecolab, Mayo Clinic
- **Financial/VC:** Optum (UnitedHealth), Mairs & Power, US Bank
- **MN VCs:** Groove Capital, Great North Ventures, Matchstick Ventures, Bread & Butter, M25
- **Ecosystem:** DEED, Launch Minnesota, MN Cup (U of MN), Minnestar, Communiful, gener8tor, Techstars

### Signature Events

- **MN Cup Grand Finale** — $400K+ startup competition anchor event
- **Minnedemo** — rapid-fire product demos; fan favorite
- **BETA Showcase** — science-fair format for startups
- **Innovation Crawl** — walking tour of innovative Twin Cities companies
- **BITCon** — Blacks in Technology conference (co-located)
- **Food | Ag Ideas Week** — AgTech track (co-located)
- **MANOVA Summit** — Health innovation (co-located)

---

## Scripts (`scripts/`)

Python scrapers that built this dataset. See [`scripts/README.md`](scripts/README.md) for full usage.

```bash
pip install -r scripts/requirements.txt

# Run all sources
python scripts/scraper.py

# Run a single source
python scripts/scraper.py --source sched      # sched.com sessions (all years)
python scripts/scraper.py --source wayback    # Wayback Machine CDX
python scripts/scraper.py --source tcb        # TCB Magazine articles
python scripts/scraper.py --source official   # tcstartupweek.com (2026)
python scripts/scraper.py --source mncup      # MN Cup winners
```

**Sources scraped:** sched.com (2018–2025), Wayback Machine (2015–2024), TCB Magazine, Start Midwest, tcstartupweek.com, beta.mn, MN Cup, YouTube

> **Note:** sched.com pages are JS-rendered; scraper uses static HTML fallback. BizJournals and Medium block programmatic access.

---

## Event Operations Research (`event-management-research/`)

A standalone deep-dive into how TCSW is operationally run — useful for understanding the event's structure from a production and logistics perspective.

- [`EVENT_OPERATIONS_RESEARCH.md`](event-management-research/EVENT_OPERATIONS_RESEARCH.md)

---

## Methodology

All data was collected via:

1. **sched.com archives** — session/speaker data for 2018, 2023 (most complete years)
2. **Wayback Machine CDX API** — historical homepage snapshots (2015–2017, 2022, 2024)
3. **Public web scraping** — TCB Magazine, Start Midwest, beta.mn, official TCSW site
4. **Manual OSINT** — LinkedIn, Medium, Google, social media; cross-referenced across sources
5. **YouTube data** — Video archive for speaker/session intelligence

Research was conducted in June 2026. Source URLs and access status are logged in [`research/findings/MASTER_FINDINGS_REPORT.md`](research/findings/MASTER_FINDINGS_REPORT.md).

---

## About

This research was compiled to support strategic planning, sponsorship development, and community intelligence for Twin Cities Startup Week 2026.

**TCSW 2026:** September 14–18 — Minneapolis + St. Paul across six campuses.

*For event inquiries: [Angela.Eifert@BETA.MN](mailto:Angela.Eifert@BETA.MN)*

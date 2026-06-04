# Twin Cities Startup Week — Research Intelligence Repository

> Comprehensive OSINT research archive covering **Twin Cities Startup Week (TCSW) 2014–2026** — Minnesota's largest startup festival, run by [The Beta Group (BETA)](https://beta.mn), a 501(c)(3) nonprofit.

---

## At a Glance

| Metric | Detail |
|---|---|
| **Years Covered** | 2014–2026 (12 completed editions) |
| **Peak Attendance** | ~17,000–19,000 (2019–2021) |
| **Sponsors Catalogued** | 80+ companies across all tiers and years |
| **Speakers Documented** | 80+ entries (CSV database) |
| **Media Articles Collected** | 50+ articles across 8 publications |
| **Data Sources** | sched.com, Wayback Machine, TCB Magazine, official site, BETA.MN |
| **2026 Event Dates** | September 14–18, Minneapolis + St. Paul |

---

## Repo Structure

```
twincitiesstartupweek/
│
├── data/                          ← Structured, clean research data
│   ├── sessions/                  ← Session CSVs by year (2018–2025) + all-sessions
│   ├── speakers/                  ← speakers-database.csv (80+ entries)
│   ├── sponsors/                  ← Sponsor DB (CSV + MD), 2026 targets, Fortune 500 deep-dive
│   │   └── logos/                 ← Sponsor + TCSW brand logos (SVG, PNG)
│   ├── investors/                 ← VC firms, featured startups, MN Cup history
│   │   ├── vc-firms/
│   │   ├── startups/
│   │   └── mn-cup/
│   ├── media/                     ← 50+ media articles organized three ways
│   │   ├── by-year/               ← Coverage per event year
│   │   ├── by-publication/        ← TCB Magazine, Star Tribune, Medium
│   │   └── by-topic/              ← Corporate sponsorship, growth history
│   ├── history/                   ← Year summaries (2015–2025) + complete timeline
│   ├── people-and-orgs/           ← Contacts CSV, orgs database, YouTube index
│   ├── social/                    ← Social handles, hashtags, platform intelligence
│   └── official-site/             ← Scraped 2026 site notes + BETA/TCSW brand assets
│
├── raw/                           ← All source files as-scraped (read-only reference)
│   ├── sched/                     ← sched.com HTML, JSON, XML, ICS per year
│   ├── wayback/                   ← Wayback Machine CDX + homepage snapshots
│   ├── media/                     ← TCB, Start Midwest, BETA.MN, MN Cup HTML/JSON
│   └── photos/                    ← YouTube thumbnails + Wayback archive images
│
├── analysis/
│   └── strategic-analysis.md      ← SWOT, sponsorship strategy, 2026 priorities
│
├── findings/
│   └── master-findings-report.md  ← Executive summary of all research
│
├── event-ops/
│   └── event-operations-research.md ← How TCSW is operationally run
│
├── scripts/                       ← Python scrapers that built this dataset
│   ├── scraper.py                 ← Main entry point
│   ├── requirements.txt
│   └── README.md                  ← How to run each scraper
│
└── docs/                          ← Research methodology, planning, logs
    ├── research-log.md            ← Source tracking + error log
    └── [planning docs]            ← OSINT guide, AI prompts, execution plan
```

---

## Quick Navigation

| What you need | File |
|---|---|
| Executive summary of all findings | [`findings/master-findings-report.md`](findings/master-findings-report.md) |
| Year-by-year history 2014–2026 | [`data/history/complete-timeline.md`](data/history/complete-timeline.md) |
| Sponsor database | [`data/sponsors/sponsors-database.md`](data/sponsors/sponsors-database.md) |
| Sponsor database (CSV) | [`data/sponsors/sponsors-database.csv`](data/sponsors/sponsors-database.csv) |
| 2026 sponsor targets | [`data/sponsors/2026-sponsors.md`](data/sponsors/2026-sponsors.md) |
| Fortune 500 sponsors deep-dive | [`data/sponsors/fortune500-2019.md`](data/sponsors/fortune500-2019.md) |
| Speaker database (CSV) | [`data/speakers/speakers-database.csv`](data/speakers/speakers-database.csv) |
| All sessions combined (CSV) | [`data/sessions/all-sessions.csv`](data/sessions/all-sessions.csv) |
| All media coverage | [`data/media/media-coverage-database.md`](data/media/media-coverage-database.md) |
| MN VC firms + investors | [`data/investors/vc-firms/mn-vc-firms.md`](data/investors/vc-firms/mn-vc-firms.md) |
| MN Cup winners history | [`data/investors/mn-cup/mn-cup-history.md`](data/investors/mn-cup/mn-cup-history.md) |
| SWOT + strategic analysis | [`analysis/strategic-analysis.md`](analysis/strategic-analysis.md) |
| Event operations deep-dive | [`event-ops/event-operations-research.md`](event-ops/event-operations-research.md) |
| Research methodology log | [`docs/research-log.md`](docs/research-log.md) |

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

## Data Completeness

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

## Running the Scrapers

```bash
pip install -r scripts/requirements.txt

python scripts/scraper.py                        # run all sources
python scripts/scraper.py --source sched         # sched.com sessions (all years)
python scripts/scraper.py --source wayback       # Wayback Machine CDX
python scripts/scraper.py --source tcb           # TCB Magazine articles
python scripts/scraper.py --source official      # tcstartupweek.com (2026)
python scripts/scraper.py --source mncup         # MN Cup winners
python scripts/scraper.py --dry-run              # preview without writing files
```

> sched.com pages are JS-rendered — the scraper uses the static HTML fallback. BizJournals and Medium block programmatic access and must be read manually.

See [`scripts/README.md`](scripts/README.md) for the full source-to-output mapping.

---

## Methodology

Data was collected via:

1. **sched.com archives** — session/speaker data for 2018 and 2023 (most complete years)
2. **Wayback Machine CDX API** — historical homepage snapshots for 2015–2017, 2022, 2024
3. **Public web scraping** — TCB Magazine, Start Midwest, beta.mn, official TCSW site
4. **Manual OSINT** — LinkedIn, Medium, Google, social media; cross-referenced across sources
5. **YouTube data** — Video archive for speaker/session intelligence

Research completed June 2026. Source URLs and access status logged in [`findings/master-findings-report.md`](findings/master-findings-report.md).

---

**TCSW 2026:** September 14–18 — Minneapolis + St. Paul, six campuses.
*Event inquiries: [Angela.Eifert@BETA.MN](mailto:Angela.Eifert@BETA.MN)*

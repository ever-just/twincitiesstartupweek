# TCSW Data Scraper

Programmatically pulls all known TCSW data sources and saves them into the research repo.

## Setup

```bash
cd scripts
pip install -r requirements.txt
```

## Run All Sources

```bash
python scraper.py
```

## Run One Source

```bash
python scraper.py --source sched       # sched.com (sessions + speakers, all years)
python scraper.py --source wayback     # Wayback Machine CDX (gap years: 2015-2017, 2022, 2024)
python scraper.py --source tcb         # TCB Magazine articles
python scraper.py --source startmidwest # Start Midwest 2025 recap
python scraper.py --source official    # tcstartupweek.com (2026 site)
python scraper.py --source beta        # beta.mn/about
python scraper.py --source mncup       # MN Cup winners page
```

## Dry Run (no writes)

```bash
python scraper.py --dry-run
```

## Output

| Source | Raw data saved to | Structured data saved to |
|---|---|---|
| sched.com | `research/raw_data/sched_YEAR_*.json` | `research/data_collection/speakers_and_sessions/SPEAKERS_DATABASE.csv` |
| Wayback Machine | `research/raw_data/wayback_YEAR_*.json` | `research/data_collection/historical_snapshots/YEAR/YEAR_WAYBACK_SNAPSHOT.md` |
| TCB Magazine | `research/raw_data/tcb_*.html` | `research/data_collection/media_coverage/YEAR_coverage/YEAR_TCB_ARTICLE.md` |
| Start Midwest | `research/raw_data/start_midwest_2025.json` | `research/data_collection/media_coverage/2025_coverage/` |
| Official site | `research/raw_data/official_site_2026.json` | `research/data_collection/official_website/OFFICIAL_SITE_SCRAPED.md` |
| BETA.MN | `research/raw_data/beta_mn_about.json` | — |
| MN Cup | `research/raw_data/mncup.json` | `research/data_collection/investors_and_startups/funding_outcomes/MN_CUP_HISTORY.md` |

## Notes

- Sched.com pages are JavaScript-rendered; the scraper fetches the static HTML fallback. If a year returns 0 sessions, the raw HTML is still saved in `raw_data/` for manual inspection.
- The Wayback CDX API is rate-limited. The scraper adds delays between requests.
- Medium.com blocks programmatic access (403). Those articles must be read manually.
- BizJournals.com requires a subscription; blocked programmatically.

# Data & Sources

Machine-readable datasets behind the synthesis, plus how the research was produced.

## Datasets

These live in the repo under `BACKGROUND/`. Links open the file on GitHub.

| Asset | File | Rows | Contents |
|---|---|---|---|
| Speakers | [`people/speakers-database.csv`](https://github.com/ever-just/twincitiesstartupweek/blob/master/BACKGROUND/people/speakers-database.csv) | 625 | Catalogued speakers across years |
| Organizations | [`people/organizations-database.csv`](https://github.com/ever-just/twincitiesstartupweek/blob/master/BACKGROUND/people/organizations-database.csv) | 53 | Companies and orgs in the ecosystem |
| Sponsor involvement | [`people/sponsor-involvement.csv`](https://github.com/ever-just/twincitiesstartupweek/blob/master/BACKGROUND/people/sponsor-involvement.csv) | 53 | Sponsor participation by year |
| Sessions | [`sessions/all-sessions.csv`](https://github.com/ever-just/twincitiesstartupweek/blob/master/BACKGROUND/sessions/all-sessions.csv) | 398 | Full session catalog (2018, 2023 deepest) |
| YouTube | [`people/youtube-videos.csv`](https://github.com/ever-just/twincitiesstartupweek/blob/master/BACKGROUND/people/youtube-videos.csv) | 303 | Archived TCSW video record |
| Quantitative master | [`quantitative/TCSW_Quantitative_Master.xlsx`](https://github.com/ever-just/twincitiesstartupweek/blob/master/BACKGROUND/quantitative/TCSW_Quantitative_Master.xlsx) | — | Consolidated metrics |
| Sponsor master | [`sponsors/TCSW_Sponsors_Master.xlsx`](https://github.com/ever-just/twincitiesstartupweek/blob/master/BACKGROUND/sponsors/TCSW_Sponsors_Master.xlsx) | — | Consolidated sponsor data |
| Raw captures | [`raw/`](https://github.com/ever-just/twincitiesstartupweek/tree/master/BACKGROUND/raw) | 67 | Source captures (pre-synthesis) |

## Archive map

```
BACKGROUND/
├── README.md                  # In-repo dossier
├── analysis/                  # Master findings, strategic SWOT, operations + platform research
├── history/                   # Year-by-year summaries + complete timeline
├── sponsors/                  # Sponsor database (md/csv/xlsx/pdf), logos, Fortune 500, 2026 tiers
├── investors/                 # VC firms, MN Cup, startups
├── sessions/                  # Session catalogs (csv/json) + recurring signature events
├── people/                    # Speakers, organizations, contacts, sponsor involvement, YouTube
├── media/                     # Coverage database + social intelligence
├── quantitative/              # Consolidated metrics (xlsx/pdf/json) + source PDFs
├── official-site/             # Captures of the live tcstartupweek.com site
└── raw/                       # 67 raw source captures
```

## Methodology

Research used web search, URL content extraction, sched.com archives, and public records. The full process is documented in the repo:

- [`RESEARCH_METHODOLOGY.md`](https://github.com/ever-just/twincitiesstartupweek/blob/master/BACKGROUND/RESEARCH_METHODOLOGY.md)
- [`RESEARCH_PROMPT_TEMPLATE.md`](https://github.com/ever-just/twincitiesstartupweek/blob/master/BACKGROUND/RESEARCH_PROMPT_TEMPLATE.md)
- [`SEARCH_SYNTHESIS_WALKTHROUGH.md`](https://github.com/ever-just/twincitiesstartupweek/blob/master/BACKGROUND/SEARCH_SYNTHESIS_WALKTHROUGH.md)

## Confidence & gaps

All facts derive from public sources: the live site, BETA pages, sched.com archives, regional media (TCB, Star Tribune, Start Midwest), and Medium. Attendance figures for virtual and distributed years are publisher-stated estimates and may be undercounted or rounded. Data gaps remain for **2015, 2016, 2022, and 2024**. The complete source list with access status is in [`analysis/master-findings-report.md`](https://github.com/ever-just/twincitiesstartupweek/blob/master/BACKGROUND/analysis/master-findings-report.md).

# Twin Cities Startup Week Research - Folder Structure

## Complete Directory Tree

```
research/
├── README.md                          # Start here
├── RESEARCH_PLAN.md                   # Initial research strategy
├── RESEARCH_PROMPT.md                 # AI research prompts
├── OSINT_GUIDE.md                     # OSINT methodology
├── AI_AGENT_PROMPTS.md                # AI agent instructions
├── TOOLS_AND_RESOURCES.md             # Tools reference
├── EXECUTION_PLAN.md                  # Day-by-day execution plan
├── FOLDER_STRUCTURE.md                # This file
│
├── data_collection/                   # Raw data collected
│   ├── README.md
│   ├── official_website/              # Current website content
│   │   ├── README.md
│   │   ├── homepage.html
│   │   ├── about.html
│   │   ├── events.html
│   │   ├── sponsors.html
│   │   ├── speakers.html
│   │   ├── schedule.html
│   │   ├── contact.html
│   │   ├── screenshots/
│   │   │   ├── homepage.png
│   │   │   ├── sponsors-page.png
│   │   │   ├── events-page.png
│   │   │   └── [other screenshots]
│   │   ├── downloads/
│   │   │   ├── event-program.pdf
│   │   │   ├── sponsorship-package.pdf
│   │   │   └── [other PDFs]
│   │   └── metadata.json              # Site structure and info
│   │
│   ├── historical_snapshots/          # Wayback Machine archives
│   │   ├── README.md
│   │   ├── 2024/
│   │   │   ├── homepage_2024.html
│   │   │   ├── sponsors_2024.html
│   │   │   ├── events_2024.html
│   │   │   ├── snapshots_2024/
│   │   │   │   ├── jan_2024.png
│   │   │   │   ├── jun_2024.png
│   │   │   │   └── sep_2024.png
│   │   │   └── metadata_2024.json
│   │   ├── 2023/
│   │   │   ├── homepage_2023.html
│   │   │   ├── sponsors_2023.html
│   │   │   ├── events_2023.html
│   │   │   ├── snapshots_2023/
│   │   │   └── metadata_2023.json
│   │   ├── 2022/
│   │   ├── 2021/
│   │   ├── 2020/
│   │   ├── 2019/
│   │   ├── 2018/
│   │   ├── 2017/
│   │   ├── 2016/
│   │   ├── 2015/
│   │   └── archive_index.json         # Index of all snapshots
│   │
│   ├── sponsors/                      # Sponsor information
│   │   ├── README.md
│   │   ├── current_sponsors/
│   │   │   ├── platinum_tier.md
│   │   │   ├── gold_tier.md
│   │   │   ├── silver_tier.md
│   │   │   ├── bronze_tier.md
│   │   │   └── logos/
│   │   │       ├── sponsor1_logo.png
│   │   │       ├── sponsor2_logo.png
│   │   │       └── [all logos]
│   │   ├── historical_sponsors/
│   │   │   ├── 2024_sponsors.md
│   │   │   ├── 2023_sponsors.md
│   │   │   ├── 2022_sponsors.md
│   │   │   ├── 2021_sponsors.md
│   │   │   ├── 2020_sponsors.md
│   │   │   ├── 2019_sponsors.md
│   │   │   ├── 2018_sponsors.md
│   │   │   ├── 2017_sponsors.md
│   │   │   ├── 2016_sponsors.md
│   │   │   └── 2015_sponsors.md
│   │   ├── sponsor_research/
│   │   │   ├── sponsor1_research.md
│   │   │   ├── sponsor2_research.md
│   │   │   └── [individual sponsor files]
│   │   └── press_releases/
│   │       ├── sponsor_announcement_2024.txt
│   │       ├── sponsor_announcement_2023.txt
│   │       └── [press releases]
│   │
│   ├── speakers_and_sessions/         # Speaker and session data
│   │   ├── README.md
│   │   ├── current_speakers/
│   │   │   ├── speaker1_profile.md
│   │   │   ├── speaker2_profile.md
│   │   │   └── [speaker profiles]
│   │   ├── historical_speakers/
│   │   │   ├── 2024_speakers.md
│   │   │   ├── 2023_speakers.md
│   │   │   ├── 2022_speakers.md
│   │   │   ├── 2021_speakers.md
│   │   │   ├── 2020_speakers.md
│   │   │   ├── 2019_speakers.md
│   │   │   ├── 2018_speakers.md
│   │   │   ├── 2017_speakers.md
│   │   │   ├── 2016_speakers.md
│   │   │   └── 2015_speakers.md
│   │   ├── sessions/
│   │   │   ├── 2024_sessions.md
│   │   │   ├── 2023_sessions.md
│   │   │   ├── 2022_sessions.md
│   │   │   └── [session files]
│   │   ├── videos/
│   │   │   ├── speaker1_talk.mp4 (or links)
│   │   │   ├── speaker2_talk.mp4
│   │   │   └── [video files/links]
│   │   ├── presentations/
│   │   │   ├── speaker1_slides.pdf
│   │   │   ├── speaker2_slides.pdf
│   │   │   └── [presentation files]
│   │   └── bios/
│   │       ├── speaker1_bio.txt
│   │       ├── speaker2_bio.txt
│   │       └── [bio files]
│   │
│   ├── media_coverage/                # News and press coverage
│   │   ├── README.md
│   │   ├── 2024_coverage/
│   │   │   ├── articles_2024.md
│   │   │   ├── press_releases_2024.md
│   │   │   ├── blog_posts_2024.md
│   │   │   └── videos_2024.md
│   │   ├── 2023_coverage/
│   │   ├── 2022_coverage/
│   │   ├── 2021_coverage/
│   │   ├── 2020_coverage/
│   │   ├── 2019_coverage/
│   │   ├── 2018_coverage/
│   │   ├── 2017_coverage/
│   │   ├── 2016_coverage/
│   │   ├── 2015_coverage/
│   │   ├── by_publication/
│   │   │   ├── star_tribune/
│   │   │   │   ├── article1.md
│   │   │   │   ├── article2.md
│   │   │   │   └── [articles]
│   │   │   ├── pioneer_press/
│   │   │   ├── techcrunch/
│   │   │   ├── venturebeat/
│   │   │   ├── forbes/
│   │   │   └── [other publications]
│   │   ├── by_topic/
│   │   │   ├── sponsorship_announcements/
│   │   │   ├── speaker_highlights/
│   │   │   ├── attendance_records/
│   │   │   ├── investor_news/
│   │   │   └── [other topics]
│   │   └── archived_articles/
│   │       ├── article1_full_text.txt
│   │       ├── article2_full_text.txt
│   │       └── [full article texts]
│   │
│   ├── social_media/                  # Social media data
│   │   ├── README.md
│   │   ├── linkedin/
│   │   │   ├── company_page.md
│   │   │   ├── posts/
│   │   │   │   ├── 2024_posts.md
│   │   │   │   ├── 2023_posts.md
│   │   │   │   └── [posts by year]
│   │   │   ├── event_pages/
│   │   │   │   ├── 2024_event.md
│   │   │   │   ├── 2023_event.md
│   │   │   │   └── [event pages]
│   │   │   ├── employees/
│   │   │   │   ├── employee1_profile.md
│   │   │   │   ├── employee2_profile.md
│   │   │   │   └── [employee profiles]
│   │   │   └── screenshots/
│   │   │       ├── company_page.png
│   │   │       ├── event_page.png
│   │   │       └── [screenshots]
│   │   ├── twitter/
│   │   │   ├── account_info.md
│   │   │   ├── tweets_2024.md
│   │   │   ├── tweets_2023.md
│   │   │   ├── hashtag_analysis.md
│   │   │   └── screenshots/
│   │   ├── instagram/
│   │   │   ├── account_info.md
│   │   │   ├── posts_2024.md
│   │   │   ├── posts_2023.md
│   │   │   ├── hashtag_analysis.md
│   │   │   └── images/
│   │   └── facebook/
│   │       ├── page_info.md
│   │       ├── events_2024.md
│   │       ├── events_2023.md
│   │       └── screenshots/
│   │
│   ├── documents/                     # Official documents
│   │   ├── README.md
│   │   ├── event_programs/
│   │   │   ├── 2024_program.pdf
│   │   │   ├── 2023_program.pdf
│   │   │   ├── 2022_program.pdf
│   │   │   └── [programs]
│   │   ├── sponsorship_packages/
│   │   │   ├── 2024_sponsorship_package.pdf
│   │   │   ├── 2023_sponsorship_package.pdf
│   │   │   └── [packages]
│   │   ├── media_kits/
│   │   │   ├── 2024_media_kit.pdf
│   │   │   ├── 2023_media_kit.pdf
│   │   │   └── [media kits]
│   │   ├── marketing_materials/
│   │   │   ├── brochures/
│   │   │   ├── flyers/
│   │   │   ├── posters/
│   │   │   └── [marketing files]
│   │   ├── volunteer_info/
│   │   │   ├── volunteer_guide_2024.pdf
│   │   │   ├── volunteer_guide_2023.pdf
│   │   │   └── [volunteer materials]
│   │   ├── registration_materials/
│   │   │   ├── registration_form_2024.pdf
│   │   │   ├── registration_form_2023.pdf
│   │   │   └── [registration forms]
│   │   └── other_documents/
│   │       ├── fact_sheet.pdf
│   │       ├── annual_report.pdf
│   │       └── [other documents]
│   │
│   └── investors_and_startups/        # Investor and startup data
│       ├── README.md
│       ├── investors/
│       │   ├── investor1_profile.md
│       │   ├── investor2_profile.md
│       │   ├── 2024_investors.md
│       │   ├── 2023_investors.md
│       │   └── [investor files]
│       ├── startups/
│       │   ├── startup1_profile.md
│       │   ├── startup2_profile.md
│       │   ├── 2024_startups.md
│       │   ├── 2023_startups.md
│       │   └── [startup files]
│       ├── funding_outcomes/
│       │   ├── funded_startups.md
│       │   ├── funding_announcements.md
│       │   └── success_stories.md
│       └── connections/
│           ├── investor_startup_connections.md
│           └── partnership_data.md
│
├── raw_data/                          # Structured data files
│   ├── README.md
│   ├── sponsors_database.csv
│   ├── sponsors_database.json
│   ├── speakers_database.csv
│   ├── speakers_database.json
│   ├── sessions_database.csv
│   ├── sessions_database.json
│   ├── media_coverage_database.csv
│   ├── media_coverage_database.json
│   ├── investors_database.csv
│   ├── investors_database.json
│   ├── startups_database.csv
│   ├── startups_database.json
│   ├── events_timeline.csv
│   ├── events_timeline.json
│   └── data_dictionary.md
│
├── analysis/                          # Processed insights
│   ├── README.md
│   ├── sponsor_analysis.md
│   │   ├── sponsor_growth_trends.md
│   │   ├── sponsor_industry_breakdown.md
│   │   ├── sponsor_retention_analysis.md
│   │   └── sponsor_tier_analysis.md
│   ├── speaker_analysis.md
│   │   ├── speaker_diversity.md
│   │   ├── speaker_topics.md
│   │   ├── speaker_backgrounds.md
│   │   └── speaker_trends.md
│   ├── event_analysis.md
│   │   ├── attendance_trends.md
│   │   ├── venue_analysis.md
│   │   ├── event_growth.md
│   │   └── format_evolution.md
│   ├── media_analysis.md
│   │   ├── coverage_trends.md
│   │   ├── publication_breakdown.md
│   │   ├── sentiment_analysis.md
│   │   └── reach_analysis.md
│   ├── investor_analysis.md
│   │   ├── investor_participation.md
│   │   ├── investor_diversity.md
│   │   └── funding_outcomes.md
│   ├── startup_analysis.md
│   │   ├── startup_participation.md
│   │   ├── startup_industries.md
│   │   └── post_event_outcomes.md
│   ├── timeline_analysis.md
│   │   ├── year_by_year_summary.md
│   │   ├── major_milestones.md
│   │   └── evolution_narrative.md
│   └── comparative_analysis.md
│       ├── vs_other_startup_weeks.md
│       ├── regional_context.md
│       └── industry_benchmarks.md
│
├── visualizations/                    # Charts and graphs
│   ├── README.md
│   ├── sponsor_visualizations/
│   │   ├── sponsor_growth_chart.png
│   │   ├── sponsor_industry_pie.png
│   │   ├── sponsor_tier_breakdown.png
│   │   └── [other charts]
│   ├── speaker_visualizations/
│   │   ├── speaker_count_by_year.png
│   │   ├── speaker_diversity.png
│   │   ├── topic_cloud.png
│   │   └── [other charts]
│   ├── event_visualizations/
│   │   ├── attendance_trend.png
│   │   ├── event_growth.png
│   │   ├── venue_map.png
│   │   └── [other charts]
│   ├── media_visualizations/
│   │   ├── coverage_timeline.png
│   │   ├── publication_breakdown.png
│   │   ├── sentiment_chart.png
│   │   └── [other charts]
│   └── interactive_dashboards/
│       ├── dashboard_2024.html
│       ├── dashboard_2023.html
│       └── [dashboards]
│
├── findings/                          # Summary reports
│   ├── README.md
│   ├── EXECUTIVE_SUMMARY.md           # High-level overview
│   ├── COMPREHENSIVE_REPORT.md        # Detailed findings
│   ├── METHODOLOGY.md                 # Research methodology
│   ├── DATA_DICTIONARY.md             # Data field definitions
│   ├── SOURCE_BIBLIOGRAPHY.md         # All sources cited
│   ├── GAP_ANALYSIS.md                # Missing data
│   ├── RECOMMENDATIONS.md             # Next steps
│   ├── KEY_INSIGHTS.md                # Major findings
│   ├── TRENDS_AND_PATTERNS.md         # Analysis of trends
│   └── APPENDICES/
│       ├── appendix_a_full_sponsor_list.md
│       ├── appendix_b_full_speaker_list.md
│       ├── appendix_c_media_articles.md
│       ├── appendix_d_timeline.md
│       └── [other appendices]
│
└── tracking/                          # Research progress tracking
    ├── README.md
    ├── research_tracker.csv           # Daily progress log
    ├── sources_checklist.md           # Sources researched
    ├── data_quality_log.md            # Data quality notes
    ├── conflicts_log.md               # Conflicting information
    ├── gaps_log.md                    # Identified gaps
    └── notes.md                       # General notes
```

---

## Folder Descriptions

### `data_collection/`
Raw data collected from all sources. Organized by source type and year.

**Subfolders:**
- `official_website/` - Current website content and structure
- `historical_snapshots/` - Wayback Machine archives by year
- `sponsors/` - All sponsor information
- `speakers_and_sessions/` - Speaker and session data
- `media_coverage/` - News articles and press coverage
- `social_media/` - LinkedIn, Twitter, Instagram, Facebook data
- `documents/` - PDFs, programs, sponsorship packages
- `investors_and_startups/` - Investor and startup participation data

### `raw_data/`
Structured, machine-readable data files (CSV, JSON).

**Files:**
- `sponsors_database.csv/json` - All sponsors with details
- `speakers_database.csv/json` - All speakers with details
- `sessions_database.csv/json` - All sessions with details
- `media_coverage_database.csv/json` - All articles with summaries
- `investors_database.csv/json` - All investors with details
- `startups_database.csv/json` - All startups with details
- `events_timeline.csv/json` - Year-by-year event data
- `data_dictionary.md` - Field definitions

### `analysis/`
Processed insights and analysis of collected data.

**Subfolders:**
- `sponsor_analysis/` - Trends, growth, industry breakdown
- `speaker_analysis/` - Diversity, topics, backgrounds
- `event_analysis/` - Attendance, venue, growth
- `media_analysis/` - Coverage trends, sentiment, reach
- `investor_analysis/` - Participation, diversity, outcomes
- `startup_analysis/` - Participation, industries, outcomes
- `timeline_analysis/` - Year-by-year summary
- `comparative_analysis/` - Benchmarking

### `visualizations/`
Charts, graphs, and interactive dashboards.

**Subfolders:**
- `sponsor_visualizations/` - Charts about sponsors
- `speaker_visualizations/` - Charts about speakers
- `event_visualizations/` - Charts about events
- `media_visualizations/` - Charts about media coverage
- `interactive_dashboards/` - HTML dashboards

### `findings/`
Final reports and summaries.

**Key Files:**
- `EXECUTIVE_SUMMARY.md` - High-level overview
- `COMPREHENSIVE_REPORT.md` - Detailed findings
- `METHODOLOGY.md` - How research was conducted
- `DATA_DICTIONARY.md` - Field definitions
- `SOURCE_BIBLIOGRAPHY.md` - All sources
- `GAP_ANALYSIS.md` - Missing data
- `RECOMMENDATIONS.md` - Next steps
- `KEY_INSIGHTS.md` - Major findings

### `tracking/`
Research progress and quality tracking.

**Files:**
- `research_tracker.csv` - Daily progress log
- `sources_checklist.md` - Sources researched
- `data_quality_log.md` - Quality notes
- `conflicts_log.md` - Conflicting information
- `gaps_log.md` - Identified gaps
- `notes.md` - General notes

---

## File Naming Conventions

### Markdown Files
- `topic_name.md` - Main topic files
- `topic_name_detail.md` - Detailed subtopics
- `YYYY_topic.md` - Year-specific files

### CSV/JSON Files
- `database_name.csv` - CSV format
- `database_name.json` - JSON format
- `database_name_YYYY.csv` - Year-specific data

### Images
- `descriptive_name.png` - PNG screenshots
- `descriptive_name.jpg` - JPG photos
- `chart_name_YYYY.png` - Year-specific charts

### Documents
- `document_type_YYYY.pdf` - Year-specific documents
- `document_type.pdf` - General documents

---

## Data Organization Principles

1. **By Source Type** - Organize by where data came from
2. **By Year** - Organize historical data chronologically
3. **By Category** - Organize by topic/type
4. **By Format** - Separate raw data from analysis
5. **By Status** - Track research progress

---

## How to Use This Structure

### During Research (Phase 2-3)
1. Collect raw data into `data_collection/` folders
2. Save documents and screenshots
3. Track progress in `tracking/`

### During Organization (Phase 4)
1. Extract structured data into `raw_data/`
2. Create CSV/JSON files from collected data
3. Organize by year and category

### During Analysis (Phase 4-5)
1. Create analysis documents in `analysis/`
2. Generate visualizations in `visualizations/`
3. Write reports in `findings/`

### During Reporting (Phase 5)
1. Compile findings in `findings/`
2. Create executive summary
3. Document methodology and sources
4. Create final index

---

## Maintenance & Updates

### Regular Updates
- Update tracking files daily
- Add new data as collected
- Verify data quality
- Document conflicts

### Periodic Reviews
- Weekly: Check progress against plan
- Bi-weekly: Verify data quality
- End of phase: Comprehensive review

### Final Cleanup
- Remove duplicates
- Verify all links
- Check file naming
- Create final index

---

## Storage & Backup

### Local Storage
- Keep all files in `/research/` folder
- Use version control (Git) if available
- Regular backups to external drive

### Cloud Storage (Optional)
- Google Drive for spreadsheets
- Dropbox for file backup
- GitHub for documentation

### Archival
- Keep all raw data
- Archive completed phases
- Maintain source links
- Document access dates


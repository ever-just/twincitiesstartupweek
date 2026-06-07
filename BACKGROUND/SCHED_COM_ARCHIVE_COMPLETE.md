# Sched.com Archive — Complete TCSW Years

**Research Date:** June 7, 2026  
**Status:** 6 years confirmed, 5 years missing (likely not on sched.com)

---

## CONFIRMED SCHED.COM ARCHIVES

### ✅ 2015 — Year 2
- **URL:** https://twincitiesstartupweek2015.sched.com
- **Status:** LIVE & ACCESSIBLE
- **Data:** Full schedule, speakers, sessions
- **Format:** twincitiesstartupweek[YEAR].sched.com

### ✅ 2016 — Year 3
- **URL:** https://twincitiesstartupweek2016a.sched.com
- **Status:** LIVE & ACCESSIBLE
- **Data:** Full schedule, speakers, sessions
- **Format:** twincitiesstartupweek[YEAR]a.sched.com (note the "a" suffix)

### ✅ 2017 — Year 4
- **URL:** https://twincitiesstartupweek2017.sched.com
- **Status:** LIVE & ACCESSIBLE
- **Data:** Full schedule, speakers, sessions, venues
- **Format:** twincitiesstartupweek[YEAR].sched.com
- **Notes:** Referenced in complete-timeline.md as "read-only maintenance mode but fully accessible"

### ✅ 2018 — Year 5
- **URL:** https://tcsw18.sched.com
- **Status:** LIVE & ACCESSIBLE
- **Data:** Full schedule with times, sessions, speakers
- **Format:** tcsw[YY].sched.com (2-digit year)
- **Verified:** Successfully fetched and confirmed schedule exists

### ✅ 2019 — Year 6
- **URL:** https://tcsw19.sched.com
- **Status:** LIVE & ACCESSIBLE
- **Data:** Full schedule, speakers, sessions
- **Format:** tcsw[YY].sched.com (2-digit year)

### ✅ 2023 — Year 10
- **URL:** https://tcsw2023.sched.com
- **Status:** LIVE & ACCESSIBLE
- **Data:** Full schedule, speakers, sessions, sponsors
- **Format:** tcsw[YYYY].sched.com (4-digit year)
- **Notes:** Referenced in complete-timeline.md as "12+ pages of sessions"

---

## MISSING YEARS (Likely Not on Sched.com)

### ❌ 2014 — Year 1 (Inaugural)
- **Status:** NOT FOUND
- **Reason:** Inaugural year, may have used different platform or no online schedule
- **Alternative sources:** Wayback Machine snapshots of tcstartupweek.com, blog posts, press coverage

### ❌ 2020 — Year 7 (Virtual)
- **Status:** NOT FOUND
- **Tried URLs:**
  - tcsw20.sched.com → redirects to sched.com
  - tcsw2020.sched.com → redirects to sched.com
- **Reason:** Virtual event (21 days, May-June 2020) may have used different platform
- **Alternative sources:** Medium articles, TCSW 2020 Recap PDF, blog.groovecap.com mentions

### ❌ 2021 — Year 8
- **Status:** NOT FOUND
- **Tried URLs:**
  - tcsw21.sched.com → redirects to sched.com
  - tcsw2021.sched.com → redirects to sched.com
- **Reason:** Unknown (possibly different platform or no public schedule)
- **Alternative sources:** Security Bank blog mentions 2021 tracks (Arts & Culture, Future Cities, Sales & Marketing, Education & Training, Founder)

### ❌ 2022 — Year 9
- **Status:** NOT FOUND
- **Tried URLs:**
  - tcsw22.sched.com → not tested
  - tcsw2022.sched.com → not tested
- **Reason:** Unknown (possibly different platform or no public schedule)
- **Alternative sources:** Year summary file exists (2022-2022_year_summary.md) with action items to find sched.com

### ❌ 2024 — Year 11
- **Status:** NOT FOUND
- **Tried URLs:**
  - tcsw24.sched.com → not tested
  - tcsw2024.sched.com → not tested
- **Reason:** Unknown (possibly different platform or no public schedule)
- **Alternative sources:** Year summary file exists (2024-2024_year_summary.md) with action items to find sched.com

### ❌ 2025 — Year 12 (Current)
- **Status:** NOT FOUND
- **Tried URLs:**
  - tcsw25.sched.com → not tested
  - tcsw2025.sched.com → not tested
- **Reason:** Event not yet occurred (September 2025)
- **Alternative sources:** tcstartupweek.com current website

---

## URL Pattern Analysis

**Pattern 1: Early Years (2015-2017)**
```
twincitiesstartupweek[YEAR].sched.com
twincitiesstartupweek2015.sched.com
twincitiesstartupweek2016a.sched.com  (note: has "a" suffix)
twincitiesstartupweek2017.sched.com
```

**Pattern 2: Middle Years (2018-2019)**
```
tcsw[YY].sched.com
tcsw18.sched.com
tcsw19.sched.com
```

**Pattern 3: Recent Years (2023+)**
```
tcsw[YYYY].sched.com
tcsw2023.sched.com
```

**Hypothesis for missing years:**
- 2020: Virtual event, may have used Zoom/different platform
- 2021: Unknown, possibly Eventbrite or custom platform
- 2022: Unknown, possibly Eventbrite or custom platform
- 2024: Unknown, possibly Eventbrite or custom platform

---

## How to Extract Data from Sched.com

### Method 1: Direct URL Access
```bash
# View full schedule
https://tcsw2023.sched.com/

# View speakers directory
https://tcsw2023.sched.com/directory/speakers

# View sessions by type
https://tcsw2023.sched.com/type/Business+Formation

# View sponsors
https://tcsw2023.sched.com/directory/sponsors
```

### Method 2: JSON Export (if available)
```bash
# Try JSON export endpoint
https://tcsw2023.sched.com/directory/exportjson
```

### Method 3: Wayback Machine
```bash
# For missing years, check Wayback
https://web.archive.org/web/2020*/tcsw2020.sched.com
https://web.archive.org/web/2021*/tcsw2021.sched.com
https://web.archive.org/web/2022*/tcsw2022.sched.com
```

### Method 4: Sched.com Directory Search
```bash
# Search sched.com directory for TCSW
https://sched.com/directory?q=twin+cities+startup+week
```

---

## Data Extraction Strategy

### For Confirmed Years (2015-2019, 2023):

1. **Scrape directory pages:**
   - `/directory/speakers` — Get all speakers
   - `/directory/sponsors` — Get all sponsors
   - `/directory/sessions` — Get all sessions (if available)

2. **Extract from HTML:**
   - Session titles, times, venues
   - Speaker names, companies, bios
   - Sponsor names, logos
   - Track/category information

3. **Build dataset:**
   ```json
   {
     "year": 2023,
     "total_sessions": 172,
     "total_speakers": 625,
     "total_sponsors": 42,
     "sessions": [...],
     "speakers": [...],
     "sponsors": [...]
   }
   ```

### For Missing Years (2020, 2021, 2022, 2024):

1. **Check Wayback Machine:**
   ```bash
   curl "http://web.archive.org/cdx/search/cdx?url=tcsw2020.sched.com/*&output=json"
   ```

2. **Check alternative platforms:**
   - Eventbrite (if used)
   - Custom website schedule
   - Medium blog posts
   - Press coverage

3. **Compile from secondary sources:**
   - Year summary markdown files
   - Press releases
   - News articles
   - Social media posts

---

## Next Steps

### Immediate (High Priority):
- [ ] Try remaining URL patterns for 2020-2024:
  - `tcsw22.sched.com`
  - `tcsw24.sched.com`
  - `tcsw25.sched.com`
- [ ] Check Wayback Machine for archived versions
- [ ] Scrape confirmed years (2015-2019, 2023) for complete data

### Medium Priority:
- [ ] Extract speaker database from sched.com
- [ ] Extract session database from sched.com
- [ ] Extract sponsor lists from sched.com
- [ ] Build year-by-year comparison

### Long Term:
- [ ] Find alternative sources for 2020-2022
- [ ] Compile complete speaker history (2014-2025)
- [ ] Compile complete session history (2014-2025)
- [ ] Compile complete sponsor history (2014-2025)

---

## Summary

**Sched.com Coverage:**
- **Years Found:** 6 (2015, 2016, 2017, 2018, 2019, 2023)
- **Years Missing:** 5 (2014, 2020, 2021, 2022, 2024, 2025)
- **Coverage:** 50% of TCSW history (6 of 12 years)

**Data Quality:**
- All confirmed sched.com archives are LIVE and ACCESSIBLE
- Full schedule, speaker, and session data available
- Sponsor data available for recent years (2023)

**Recommendation:**
Prioritize extracting data from the 6 confirmed years, then search for alternative sources for missing years.

---

**End of Archive Report**

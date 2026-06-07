"""
scrape_speakers.py
==================
Scrapes sched.com list/descriptions pages for all TCSW years in parallel.
Extracts: sessions, speakers, roles, companies, venues, dates, files, photos.
Saves per-year CSVs and a unified SPEAKERS_DATABASE.csv
"""

import asyncio
import csv
import json
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW      = REPO_ROOT / "research" / "raw_data"
SPEAKERS = REPO_ROOT / "research" / "data_collection" / "speakers_and_sessions"
SPEAKERS.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Encoding": "gzip, deflate",  # explicitly exclude brotli
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

YEARS = {
    2018: "tcsw18",
    2019: "tcsw2019",
    2020: "tcsw2020",
    2021: "tcsw2021",
    2022: "tcsw2022",
    2023: "tcsw2023",
    2024: "tcsw2024",
    2025: "tcsw2025",
}

SEM = asyncio.Semaphore(8)


def parse_descriptions_page(html, year):
    soup = BeautifulSoup(html, "lxml")
    sessions = []

    # sched.com structure:
    #   div.sched-container
    #     span.event  <- title/time/desc
    #     div.sched-container-inner  <- speakers, files, photos
    for container in soup.select("div.sched-container"):
        block = container.select_one("span.event")
        inner = container.select_one("div.sched-container-inner")
        if not block:
            continue

        # Title + URL
        title_link = block.select_one("a.name")
        title_el   = block.select_one(".session-title")
        title      = title_el.get_text(strip=True) if title_el else ""
        url        = title_link.get("href", "") if title_link else ""
        if url and not url.startswith("http"):
            subdomain = YEARS.get(year, f"tcsw{year}")
            url = f"https://{subdomain}.sched.com/{url}"

        # Time + venue
        tp_el = block.select_one(".sched-event-details-timeandplace")
        tp    = tp_el.get_text(separator=" | ", strip=True) if tp_el else ""

        # Track
        type_el = block.select_one(".sched-event-type")
        track   = type_el.get_text(strip=True) if type_el else ""

        # Description
        desc_el = block.select_one(".sched-event-details")
        desc    = ""
        if desc_el:
            for unwanted in desc_el.select(".sched-person-session, .sched-event-details-timeandplace, .sched-event-type"):
                unwanted.decompose()
            desc = desc_el.get_text(separator=" ", strip=True)[:600]

        # Speakers from inner container
        people = []
        search_el = inner or block
        for person in search_el.select(".sched-person-session"):
            # name+title+company are concatenated in the span text
            raw_text = person.get_text(strip=True)
            # Try avatar img alt for clean name
            avatar_el  = person.find("img") or person.find_previous("img")
            avatar_url = avatar_el.get("src", "") if avatar_el else ""
            clean_name = (avatar_el.get("alt", "") or "").strip() if avatar_el else ""
            # role/company from sibling spans
            role_el    = person.find_next_sibling(class_="sched-person-session-role")
            co_el      = person.find_next_sibling(class_="sched-event-details-role-company")
            role       = role_el.get_text(strip=True) if role_el else ""
            company    = co_el.get_text(strip=True) if co_el else ""
            # fallback: split raw_text on comma if no sibling data
            if not role and not company and "," in raw_text:
                parts   = raw_text.split(",", 1)
                clean_name = clean_name or parts[0].strip()
                company    = parts[1].strip()
            name = clean_name or raw_text.split(",")[0].strip()
            people.append({"name": name, "role": role, "company": company, "avatar_url": avatar_url})

        # Files + photos
        files  = [f.get_text(strip=True) for f in search_el.select(".sched-file")]
        photos = [img.get("src","") for img in search_el.select(".sched-event-photo img") if img.get("src")]

        sessions.append({
            "year":        year,
            "title":       title,
            "url":         url,
            "time_place":  tp,
            "track":       track,
            "description": desc,
            "speakers":    "; ".join(p["name"] for p in people),
            "speaker_details": json.dumps(people, ensure_ascii=False),
            "files":       "; ".join(files),
            "photos":      "; ".join(photos),
        })

    return sessions


async def fetch_year(session, year, subdomain):
    url = f"https://{subdomain}.sched.com/list/descriptions"
    cache = RAW / f"sched_descriptions_{year}.html"

    if cache.exists() and cache.stat().st_size > 50000:
        html = cache.read_text(errors="ignore")
        print(f"  {year}: using cache ({cache.stat().st_size // 1024} KB)")
    else:
        # Try /list/descriptions first, fall back to /list/simple
        for endpoint in ["list/descriptions", "list/simple"]:
            attempt_url = f"https://{subdomain}.sched.com/{endpoint}"
            print(f"  {year}: fetching {attempt_url} ...")
            async with SEM:
                try:
                    async with session.get(attempt_url, timeout=aiohttp.ClientTimeout(total=30)) as r:
                        if r.status == 200:
                            html = await r.text(errors="ignore")
                            cache.write_text(html, encoding="utf-8")
                            print(f"  {year}: fetched {len(html)//1024} KB via {endpoint}")
                            break
                        else:
                            print(f"  {year}: HTTP {r.status} on {endpoint}")
                            html = ""
                except Exception as e:
                    print(f"  {year}: error — {e}")
                    html = ""
        if not html:
            return year, []

    sessions = parse_descriptions_page(html, year)
    print(f"  {year}: {len(sessions)} sessions parsed")
    return year, sessions


async def main():
    print("Fetching all TCSW sched.com description pages in parallel...\n")

    connector = aiohttp.TCPConnector(limit=10, ssl=False, enable_cleanup_closed=True)
    async with aiohttp.ClientSession(headers=HEADERS, connector=connector) as session:
        tasks   = [fetch_year(session, year, sub) for year, sub in YEARS.items()]
        results = await asyncio.gather(*tasks)

    all_sessions = []
    all_speakers = {}  # name -> aggregated info

    for year, sessions in sorted(results):
        if not sessions:
            continue

        # Per-year files
        (RAW / f"sessions_{year}.json").write_text(
            json.dumps(sessions, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        year_csv = SPEAKERS / f"sessions_{year}.csv"
        with open(year_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=sessions[0].keys(), extrasaction="ignore")
            w.writeheader()
            w.writerows(sessions)
        print(f"  ✓ sessions_{year}.csv ({len(sessions)} rows)")

        all_sessions.extend(sessions)

        # Accumulate speaker info
        for s in sessions:
            try:
                people = json.loads(s.get("speaker_details") or "[]")
            except Exception:
                people = []
            for p in people:
                name = p.get("name","").strip()
                if not name:
                    continue
                if name not in all_speakers:
                    all_speakers[name] = {
                        "name":          name,
                        "years":         set(),
                        "session_count": 0,
                        "companies":     set(),
                        "roles":         set(),
                        "sessions":      [],
                        "avatar_url":    p.get("avatar_url",""),
                    }
                all_speakers[name]["years"].add(str(year))
                all_speakers[name]["session_count"] += 1
                if p.get("company"): all_speakers[name]["companies"].add(p["company"])
                if p.get("role"):    all_speakers[name]["roles"].add(p["role"])
                all_speakers[name]["sessions"].append(s["title"][:80])

    # Write ALL_SESSIONS
    if all_sessions:
        all_csv = SPEAKERS / "ALL_SESSIONS.csv"
        with open(all_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=all_sessions[0].keys(), extrasaction="ignore")
            w.writeheader()
            w.writerows(all_sessions)
        (RAW / "all_sessions.json").write_text(
            json.dumps(all_sessions, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\n  ✓ ALL_SESSIONS.csv ({len(all_sessions)} rows)")

    # Write SPEAKERS_DATABASE
    speaker_rows = []
    for name, d in sorted(all_speakers.items()):
        speaker_rows.append({
            "name":           name,
            "years_active":   ", ".join(sorted(d["years"])),
            "session_count":  d["session_count"],
            "companies":      " | ".join(sorted(d["companies"])),
            "roles":          " | ".join(sorted(d["roles"])),
            "sample_sessions":"; ".join(d["sessions"][:3]),
            "avatar_url":     d["avatar_url"],
            "email":          "",
            "linkedin":       "",
            "twitter":        "",
            "notes":          "",
        })

    spk_csv = SPEAKERS / "SPEAKERS_DATABASE.csv"
    if speaker_rows:
        with open(spk_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=speaker_rows[0].keys(), extrasaction="ignore")
            w.writeheader()
            w.writerows(speaker_rows)
    else:
        print("  [warn] No speakers found — check if sched.com subdomains are correct")

    (RAW / "speakers_database.json").write_text(
        json.dumps(speaker_rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"  ✓ SPEAKERS_DATABASE.csv ({len(speaker_rows)} unique speakers)")
    print(f"\nDone. Total: {len(all_sessions)} sessions | {len(speaker_rows)} speakers")


if __name__ == "__main__":
    asyncio.run(main())

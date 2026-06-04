"""
Fetch 2019-2022, 2024-2025 sched.com pages from Wayback Machine, then re-run parser.
"""
import asyncio, json
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup
import sys, csv

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW      = REPO_ROOT / "research" / "raw_data"
SPEAKERS = REPO_ROOT / "research" / "data_collection" / "speakers_and_sessions"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
}

# Known good Wayback snapshots for each year's list/descriptions page
WAYBACK_URLS = {
    2019: "https://web.archive.org/web/20191004000000*/tcsw2019.sched.com/list/descriptions",
    2020: "https://web.archive.org/web/20201001000000*/tcsw2020.sched.com/list/descriptions",
    2021: "https://web.archive.org/web/20211001000000*/tcsw2021.sched.com/list/descriptions",
    2022: "https://web.archive.org/web/20221001000000*/tcsw2022.sched.com/list/descriptions",
    2024: "https://web.archive.org/web/20241001000000*/tcsw2024.sched.com/list/descriptions",
    2025: "https://web.archive.org/web/20251001000000*/tcsw2025.sched.com/list/descriptions",
}

# CDX to find best snapshot timestamp
CDX_BASE = "http://web.archive.org/cdx/search/cdx"

SEM = asyncio.Semaphore(4)


async def find_snapshot_url(session, year, subdomain):
    """Query CDX to get the best snapshot timestamp for this year's list/descriptions."""
    target = f"{subdomain}.sched.com/list/descriptions"
    params = f"?url={target}&output=json&fl=timestamp,original&filter=statuscode:200&limit=5&from={year}0901&to={year}1031"
    try:
        async with session.get(CDX_BASE + params, timeout=aiohttp.ClientTimeout(total=20)) as r:
            if r.status != 200:
                return None
            text = await r.text()
            if not text.strip():
                return None
            data = json.loads(text)
            if len(data) <= 1:
                return None
            ts, orig = data[1][0], data[1][1]
            return f"https://web.archive.org/web/{ts}/{orig}"
    except Exception as e:
        print(f"  CDX {year}: {e}")
        return None


async def fetch_wayback_page(session, year, subdomain):
    cache = RAW / f"sched_descriptions_{year}.html"
    if cache.exists() and cache.stat().st_size > 50000:
        print(f"  {year}: already cached")
        return year, cache.read_text(errors="ignore")

    async with SEM:
        wb_url = await find_snapshot_url(session, year, subdomain)
        if not wb_url:
            print(f"  {year}: no Wayback snapshot found")
            return year, None
        print(f"  {year}: fetching {wb_url[:80]}...")
        try:
            async with session.get(wb_url, timeout=aiohttp.ClientTimeout(total=40)) as r:
                if r.status != 200:
                    print(f"  {year}: Wayback returned {r.status}")
                    return year, None
                html = await r.text(errors="ignore")
                cache.write_text(html, encoding="utf-8")
                print(f"  {year}: fetched {len(html)//1024} KB from Wayback")
                return year, html
        except Exception as e:
            print(f"  {year}: fetch error — {e}")
            return year, None


# Import parser from scrape_speakers
sys.path.insert(0, str(Path(__file__).parent))
from scrape_speakers import parse_descriptions_page, YEARS


async def main():
    missing = {y: s for y, s in YEARS.items() if y not in [2018, 2023]}
    connector = aiohttp.TCPConnector(limit=6, ssl=False)
    async with aiohttp.ClientSession(headers=HEADERS, connector=connector) as session:
        tasks = [fetch_wayback_page(session, y, s) for y, s in missing.items()]
        results = await asyncio.gather(*tasks)

    all_new_sessions = []
    for year, html in results:
        if not html:
            continue
        sessions = parse_descriptions_page(html, year)
        print(f"  {year}: {len(sessions)} sessions parsed")
        if sessions:
            all_new_sessions.extend(sessions)
            # Save per-year
            (RAW / f"sessions_{year}.json").write_text(json.dumps(sessions, indent=2), encoding="utf-8")
            ycsv = SPEAKERS / f"sessions_{year}.csv"
            with open(ycsv, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=sessions[0].keys(), extrasaction="ignore")
                w.writeheader(); w.writerows(sessions)
            print(f"  ✓ sessions_{year}.csv")

    if all_new_sessions:
        # Merge into ALL_SESSIONS
        existing = []
        all_csv = SPEAKERS / "ALL_SESSIONS.csv"
        if all_csv.exists():
            with open(all_csv, newline="", encoding="utf-8") as f:
                existing = list(csv.DictReader(f))
        combined = existing + all_new_sessions
        with open(all_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=combined[0].keys(), extrasaction="ignore")
            w.writeheader(); w.writerows(combined)
        print(f"\n  ✓ ALL_SESSIONS.csv updated: {len(combined)} total rows")

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())

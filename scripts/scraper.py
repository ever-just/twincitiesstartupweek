"""
Twin Cities Startup Week — OSINT Data Scraper
=============================================
Programmatically pulls data from all known sources and saves to the research repo.

Sources covered:
  - tcsw2023.sched.com        → sessions, speakers, venues  (2023)
  - tcsw2025.sched.com        → sessions, speakers, venues  (2025)
  - tcstartupweek.com         → official 2026 site content
  - tcbmag.com                → all known TCSW articles
  - start-midwest.com         → 2025 recap article
  - beta.mn/about             → org info
  - carlsonschool.umn.edu/mn-cup → MN Cup winners
  - Wayback Machine CDX API   → archived snapshots for gap years (2015-2022, 2024)

Output locations:
  research/raw_data/           → raw JSON/CSV from each source
  research/data_collection/    → structured markdown files updated with real data

Usage:
  pip install -r requirements.txt
  python scraper.py                  # run all scrapers
  python scraper.py --source sched   # run one source only
  python scraper.py --source wayback
  python scraper.py --source tcb
  python scraper.py --source mncup
  python scraper.py --dry-run        # print what would be saved, no writes
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ─── Paths ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA = REPO_ROOT / "research" / "raw_data"
DATA_COLLECTION = REPO_ROOT / "research" / "data_collection"
SNAPSHOTS = DATA_COLLECTION / "historical_snapshots"
MEDIA = DATA_COLLECTION / "media_coverage"
SPEAKERS_DIR = DATA_COLLECTION / "speakers_and_sessions"
SPONSORS_DIR = DATA_COLLECTION / "sponsors"
MNCUP_DIR = DATA_COLLECTION / "investors_and_startups" / "funding_outcomes"

RAW_DATA.mkdir(parents=True, exist_ok=True)

# ─── Shared helpers ───────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def get(url: str, retries: int = 3, delay: float = 1.5) -> requests.Response | None:
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            print(f"  [warn] {url} attempt {attempt+1} failed: {exc}")
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
    return None


def save_json(data, path: Path, dry_run: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        print(f"  [dry-run] would write {len(json.dumps(data))} bytes → {path}")
        return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ saved {path.relative_to(REPO_ROOT)}")


def save_csv(rows: list[dict], path: Path, dry_run: bool = False) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        print(f"  [dry-run] would write {len(rows)} rows → {path}")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ saved {path.relative_to(REPO_ROOT)} ({len(rows)} rows)")


def save_md(content: str, path: Path, dry_run: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        print(f"  [dry-run] would write {len(content)} chars → {path}")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ saved {path.relative_to(REPO_ROOT)}")


# ─── 1. Sched.com scraper ─────────────────────────────────────────────────────

SCHED_YEARS = {
    2023: "https://tcsw2023.sched.com/",
    2025: "https://tcsw2025.sched.com/",
    2022: "https://tcsw2022.sched.com/",
    2024: "https://tcsw2024.sched.com/",
    2021: "https://tcsw2021.sched.com/",
    2020: "https://tcsw2020.sched.com/",
    2019: "https://tcsw2019.sched.com/",
    2018: "https://tcsw2018.sched.com/",
}


def parse_sched_page(html: str, year: int) -> list[dict]:
    """Parse a sched.com event listing page into a list of session dicts."""
    soup = BeautifulSoup(html, "lxml")
    sessions = []

    for item in soup.select("li.sched-container-item"):
        title_el = item.select_one("span.sched-event-name a, a.sched-event-name")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        url = title_el.get("href", "")
        if url and not url.startswith("http"):
            url = f"https://tcsw{year}.sched.com{url}"

        time_el = item.select_one("span.sched-event-period")
        time_str = time_el.get_text(strip=True) if time_el else ""

        venue_el = item.select_one("span.sched-venue a, span.sched-venue")
        venue = venue_el.get_text(strip=True) if venue_el else ""

        speakers = [
            s.get_text(strip=True)
            for s in item.select("span.sched-person a, a.sched-person")
        ]

        sessions.append(
            {
                "year": year,
                "title": title,
                "time": time_str,
                "venue": venue,
                "speakers": "; ".join(speakers),
                "url": url,
            }
        )

    # Fallback: try the event-list table structure
    if not sessions:
        for row in soup.select("tr.event"):
            title_el = row.select_one("td.title a")
            if not title_el:
                continue
            speakers = [s.get_text(strip=True) for s in row.select("td.presenter a")]
            time_el = row.select_one("td.time")
            venue_el = row.select_one("td.venue")
            sessions.append(
                {
                    "year": year,
                    "title": title_el.get_text(strip=True),
                    "time": time_el.get_text(strip=True) if time_el else "",
                    "venue": venue_el.get_text(strip=True) if venue_el else "",
                    "speakers": "; ".join(speakers),
                    "url": urljoin(f"https://tcsw{year}.sched.com/", title_el.get("href", "")),
                }
            )

    return sessions


def scrape_sched(dry_run: bool = False) -> None:
    print("\n── Scraping sched.com ──")
    all_sessions: list[dict] = []

    for year, url in SCHED_YEARS.items():
        print(f"  Fetching {year}: {url}")
        resp = get(url)
        if not resp:
            print(f"  [skip] Could not reach {url}")
            continue

        sessions = parse_sched_page(resp.text, year)
        if not sessions:
            print(f"  [warn] No sessions parsed from {url} (page may require JS)")
        else:
            print(f"  Found {len(sessions)} sessions for {year}")

        # Save raw HTML
        raw_html_path = RAW_DATA / f"sched_{year}_raw.html"
        if not dry_run:
            raw_html_path.write_text(resp.text, encoding="utf-8")
            print(f"  ✓ raw HTML → {raw_html_path.relative_to(REPO_ROOT)}")

        # Save per-year JSON
        save_json(sessions, RAW_DATA / f"sched_{year}_sessions.json", dry_run)
        all_sessions.extend(sessions)
        time.sleep(1)

    # Master CSV of all sessions
    save_csv(all_sessions, RAW_DATA / "all_sessions.csv", dry_run)

    # Update the speakers CSV in data_collection
    speaker_rows = []
    seen = set()
    for s in all_sessions:
        for name in s["speakers"].split(";"):
            name = name.strip()
            if name and name not in seen:
                seen.add(name)
                speaker_rows.append({"name": name, "year": s["year"], "session": s["title"], "venue": s["venue"]})
    if speaker_rows:
        save_csv(speaker_rows, SPEAKERS_DIR / "SPEAKERS_DATABASE.csv", dry_run)


# ─── 2. Wayback Machine CDX API ──────────────────────────────────────────────

CDX_API = "http://web.archive.org/cdx/search/cdx"
GAP_YEARS = [2015, 2016, 2017, 2022, 2024]
TCSW_DOMAINS = [
    "twincitiesstartupweek.com",
    "tcstartupweek.com",
]


def query_cdx(url: str, year: int) -> list[dict]:
    """Return CDX records for a domain in a given year."""
    params = {
        "url": f"*.{url}/*",
        "output": "json",
        "from": f"{year}0101",
        "to": f"{year}1231",
        "limit": 100,
        "filter": "statuscode:200",
        "fl": "timestamp,original,statuscode,mimetype,length",
        "collapse": "urlkey",
    }
    resp = get(CDX_API + "?" + "&".join(f"{k}={v}" for k, v in params.items()))
    if not resp:
        return []
    try:
        raw = resp.json()
        if len(raw) < 2:
            return []
        keys = raw[0]
        return [dict(zip(keys, row)) for row in raw[1:]]
    except Exception as exc:
        print(f"  [warn] CDX parse error: {exc}")
        return []


def fetch_wayback_snapshot(cdx_record: dict) -> str | None:
    """Fetch HTML content of a Wayback snapshot."""
    ts = cdx_record["timestamp"]
    orig = cdx_record["original"]
    wb_url = f"https://web.archive.org/web/{ts}/{orig}"
    resp = get(wb_url)
    return resp.text if resp else None


def scrape_wayback(dry_run: bool = False) -> None:
    print("\n── Querying Wayback Machine CDX API ──")

    for year in GAP_YEARS:
        print(f"\n  Year {year}:")
        all_records: list[dict] = []

        for domain in TCSW_DOMAINS:
            records = query_cdx(domain, year)
            print(f"    {domain}: {len(records)} snapshots found")
            all_records.extend(records)
            time.sleep(0.5)

        if not all_records:
            print(f"    [skip] No archived snapshots found for {year}")
            continue

        # Save CDX index
        save_json(all_records, RAW_DATA / f"wayback_{year}_cdx.json", dry_run)

        # Fetch the homepage snapshot (first HTML record)
        html_records = [r for r in all_records if "text/html" in r.get("mimetype", "")]
        if not html_records:
            continue

        best = html_records[0]
        print(f"    Fetching best snapshot: {best['original']} @ {best['timestamp']}")
        html = fetch_wayback_snapshot(best)
        if not html:
            continue

        raw_html_path = RAW_DATA / f"wayback_{year}_homepage.html"
        if not dry_run:
            raw_html_path.write_text(html, encoding="utf-8")
            print(f"    ✓ raw HTML → {raw_html_path.relative_to(REPO_ROOT)}")

        # Extract text content and save to year snapshot folder
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(separator="\n", strip=True)
        snapshot_md = (
            f"# TCSW {year} — Archived Website Content\n"
            f"*Source: Wayback Machine | Original: {best['original']} | Captured: {best['timestamp']}*\n\n"
            "---\n\n"
            "## Extracted Text\n\n"
            f"```\n{text[:8000]}\n```\n"
        )
        save_md(snapshot_md, SNAPSHOTS / str(year) / f"{year}_WAYBACK_SNAPSHOT.md", dry_run)
        time.sleep(1.5)


# ─── 3. TCB Magazine article scraper ─────────────────────────────────────────

TCB_ARTICLES = [
    {
        "url": "https://tcbmag.com/twin-cities-startup-week-is-bigger-than-ever/",
        "year": 2018,
        "title": "Twin Cities Startup Week is Bigger Than Ever",
    },
    {
        "url": "https://tcbmag.com/how-to-navigate-twin-cities-startup-week/",
        "year": 2019,
        "title": "How to Navigate Twin Cities Startup Week",
    },
    {
        "url": "https://tcbmag.com/twin-cities-startup-week-goes-virtual/",
        "year": 2020,
        "title": "Twin Cities Startup Week Goes Virtual",
    },
    {
        "url": "https://tcbmag.com/mn-cups-2025-winner-is-acqumen-medical/",
        "year": 2025,
        "title": "MN Cup's 2025 Winner Is AcQumen Medical",
    },
]


def scrape_tcb(dry_run: bool = False) -> None:
    print("\n── Scraping TCB Magazine ──")
    articles = []

    for meta in TCB_ARTICLES:
        print(f"  Fetching: {meta['url']}")
        resp = get(meta["url"])
        if not resp:
            print("  [skip]")
            continue

        soup = BeautifulSoup(resp.text, "lxml")

        # Extract article body text
        body = soup.select_one("article, .entry-content, .post-content, main")
        text = body.get_text(separator="\n", strip=True) if body else soup.get_text(separator="\n", strip=True)

        # Extract publish date
        date_el = soup.select_one("time[datetime], .entry-date, .published")
        date = date_el.get("datetime", date_el.get_text(strip=True)) if date_el else ""

        article = {**meta, "date": date, "text": text[:6000]}
        articles.append(article)

        # Save raw HTML
        slug = urlparse(meta["url"]).path.strip("/").split("/")[-1]
        if not dry_run:
            raw_path = RAW_DATA / f"tcb_{slug}.html"
            raw_path.write_text(resp.text, encoding="utf-8")
            print(f"  ✓ raw HTML → {raw_path.relative_to(REPO_ROOT)}")

        # Save to year media folder
        year = meta["year"]
        md = (
            f"# {meta['title']}\n"
            f"*Source: Twin Cities Business Magazine | {date} | {meta['url']}*\n\n"
            "---\n\n"
            f"{text[:5000]}\n\n"
            f"---\n*Full article: {meta['url']}*\n"
        )
        media_year_dir = MEDIA / f"{year}_coverage"
        media_year_dir.mkdir(parents=True, exist_ok=True)
        save_md(md, media_year_dir / f"{year}_TCB_ARTICLE.md", dry_run)
        time.sleep(1)

    save_json(articles, RAW_DATA / "tcb_articles.json", dry_run)


# ─── 4. Start Midwest 2025 recap ─────────────────────────────────────────────

def scrape_start_midwest(dry_run: bool = False) -> None:
    print("\n── Scraping Start Midwest 2025 recap ──")
    url = "https://www.start-midwest.com/news/recapping-twin-cities-startup-week-2025"
    print(f"  Fetching: {url}")
    resp = get(url)
    if not resp:
        print("  [skip]")
        return

    soup = BeautifulSoup(resp.text, "lxml")
    body = soup.select_one("article, .post-content, main, .content")
    text = body.get_text(separator="\n", strip=True) if body else soup.get_text(separator="\n", strip=True)

    if not dry_run:
        (RAW_DATA / "start_midwest_2025_recap.html").write_text(resp.text, encoding="utf-8")

    md = (
        "# Recapping Twin Cities Startup Week 2025\n"
        f"*Source: Start Midwest | {url}*\n\n"
        "---\n\n"
        f"{text[:6000]}\n\n"
        f"---\n*Full article: {url}*\n"
    )
    save_md(md, MEDIA / "2025_coverage" / "2025_START_MIDWEST_RECAP.md", dry_run)
    save_json({"url": url, "text": text[:8000]}, RAW_DATA / "start_midwest_2025.json", dry_run)


# ─── 5. Official website (2026) ───────────────────────────────────────────────

def scrape_official_site(dry_run: bool = False) -> None:
    print("\n── Scraping official TCSW website ──")
    url = "https://www.tcstartupweek.com/"
    print(f"  Fetching: {url}")
    resp = get(url)
    if not resp:
        print("  [skip]")
        return

    soup = BeautifulSoup(resp.text, "lxml")
    text = soup.get_text(separator="\n", strip=True)

    if not dry_run:
        (RAW_DATA / "official_site_2026.html").write_text(resp.text, encoding="utf-8")

    # Extract key structured data
    data = {
        "url": url,
        "scraped_at": datetime.now().isoformat(),
        "title": soup.title.get_text(strip=True) if soup.title else "",
        "meta_description": "",
        "text_content": text[:5000],
    }
    meta_desc = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
    if meta_desc:
        data["meta_description"] = meta_desc.get("content", "")

    save_json(data, RAW_DATA / "official_site_2026.json", dry_run)
    official_dir = DATA_COLLECTION / "official_website"
    official_dir.mkdir(parents=True, exist_ok=True)
    md = (
        "# TCSW Official Website — Scraped Content (2026)\n"
        f"*Scraped: {data['scraped_at']} | Source: {url}*\n\n"
        "---\n\n"
        f"{text[:4000]}\n"
    )
    save_md(md, official_dir / "OFFICIAL_SITE_SCRAPED.md", dry_run)


# ─── 6. BETA.MN About page ───────────────────────────────────────────────────

def scrape_beta(dry_run: bool = False) -> None:
    print("\n── Scraping BETA.MN ──")
    url = "https://www.beta.mn/about"
    resp = get(url)
    if not resp:
        print("  [skip]")
        return

    soup = BeautifulSoup(resp.text, "lxml")
    text = soup.get_text(separator="\n", strip=True)

    if not dry_run:
        (RAW_DATA / "beta_mn_about.html").write_text(resp.text, encoding="utf-8")

    save_json({"url": url, "scraped_at": datetime.now().isoformat(), "text": text[:5000]},
              RAW_DATA / "beta_mn_about.json", dry_run)
    print(f"  ✓ BETA.MN about page saved")


# ─── 7. MN Cup winners page ──────────────────────────────────────────────────

def scrape_mncup(dry_run: bool = False) -> None:
    print("\n── Scraping MN Cup ──")
    url = "https://carlsonschool.umn.edu/mn-cup"
    resp = get(url)
    if not resp:
        print("  [skip]")
        return

    soup = BeautifulSoup(resp.text, "lxml")
    text = soup.get_text(separator="\n", strip=True)

    if not dry_run:
        (RAW_DATA / "mncup_page.html").write_text(resp.text, encoding="utf-8")

    save_json({"url": url, "scraped_at": datetime.now().isoformat(), "text": text[:6000]},
              RAW_DATA / "mncup.json", dry_run)

    # Append scraped content to MN Cup history file
    scraped_note = (
        "\n\n---\n\n"
        "## Scraped Live Data\n"
        f"*Source: {url} | Scraped: {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        f"{text[:3000]}\n"
    )
    mncup_file = MNCUP_DIR / "MN_CUP_HISTORY.md"
    if not dry_run and mncup_file.exists():
        with open(mncup_file, "a", encoding="utf-8") as f:
            f.write(scraped_note)
        print(f"  ✓ appended live data to {mncup_file.relative_to(REPO_ROOT)}")
    elif dry_run:
        print(f"  [dry-run] would append scraped MN Cup data to {mncup_file.relative_to(REPO_ROOT)}")


# ─── Main ─────────────────────────────────────────────────────────────────────

SCRAPERS = {
    "sched": scrape_sched,
    "wayback": scrape_wayback,
    "tcb": scrape_tcb,
    "startmidwest": scrape_start_midwest,
    "official": scrape_official_site,
    "beta": scrape_beta,
    "mncup": scrape_mncup,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="TCSW OSINT Data Scraper")
    parser.add_argument(
        "--source",
        choices=list(SCRAPERS.keys()) + ["all"],
        default="all",
        help="Which source to scrape (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be saved without writing any files",
    )
    args = parser.parse_args()

    dry_run = args.dry_run
    if dry_run:
        print("DRY RUN — no files will be written\n")

    sources = list(SCRAPERS.keys()) if args.source == "all" else [args.source]

    print(f"Running {len(sources)} scraper(s): {', '.join(sources)}")
    print(f"Output root: {REPO_ROOT}\n")

    for name in sources:
        try:
            SCRAPERS[name](dry_run=dry_run)
        except Exception as exc:
            print(f"  [ERROR] {name} scraper failed: {exc}")
            import traceback
            traceback.print_exc()

    print("\n✅ Done.")


if __name__ == "__main__":
    main()

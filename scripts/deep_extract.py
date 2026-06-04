"""
deep_extract.py
===============
Comprehensive TCSW data extraction pipeline.

Phases:
  1. Parse sched.com RSS feeds -> sessions + speakers CSV per year
  2. Parse BETA.mn sitemap -> fetch TCSW-related pages
  3. Extract emails, phones, social links from ALL downloaded HTML
  4. YouTube channel video metadata via yt-dlp
  5. Wayback CDX deep dive -> ALL file types (PDF, JPG, ICS, CSV)
  6. Build unified people/orgs contacts database
  7. Download discoverable event photos

Run:
    python3 deep_extract.py
    python3 deep_extract.py --phase 1   # run one phase only
"""

import argparse
import csv
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "research" / "raw_data"
DC = REPO_ROOT / "research" / "data_collection"
SPEAKERS_DIR = DC / "speakers_and_sessions"
MEDIA_DIR = DC / "media_coverage"
CONTACTS_DIR = DC / "people_and_orgs"
PHOTOS_DIR = RAW / "photos"
DOCS_DIR = RAW / "documents"

for d in [RAW, SPEAKERS_DIR, MEDIA_DIR, CONTACTS_DIR, PHOTOS_DIR, DOCS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

SCHED_YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]


def get(url, timeout=20, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
            r.raise_for_status()
            return r
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  [err] {url}: {e}")
                return None


def save_json(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✓ {path.relative_to(REPO_ROOT)}")


def save_csv(rows, path):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys(), extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"  ✓ {path.relative_to(REPO_ROOT)} ({len(rows)} rows)")


# ─── PHASE 1: Parse sched.com RSS feeds ──────────────────────────────────────

def phase1_rss_feeds():
    print("\n═══ PHASE 1: Parse sched.com RSS feeds ═══")
    all_sessions = []

    for year in SCHED_YEARS:
        subdomain = "tcsw18" if year == 2018 else f"tcsw{year}"
        rss_file = RAW / f"probe_{subdomain}.sched.xml"

        # Try already-saved file first, else fetch
        if rss_file.exists() and rss_file.stat().st_size > 10000:
            content = rss_file.read_text(errors="ignore")
        else:
            print(f"  Fetching RSS for {year}...")
            r = get(f"https://{subdomain}.sched.com/feed")
            if not r:
                continue
            content = r.text
            rss_file.write_text(content, encoding="utf-8")

        sessions = parse_rss(content, year)
        print(f"  {year}: {len(sessions)} sessions from RSS")
        all_sessions.extend(sessions)

        save_json(sessions, RAW / f"sessions_{year}.json")
        save_csv(sessions, SPEAKERS_DIR / f"sessions_{year}.csv")

    save_csv(all_sessions, SPEAKERS_DIR / "ALL_SESSIONS.csv")
    save_json(all_sessions, RAW / "all_sessions.json")

    # Build speakers database
    speakers = build_speakers_db(all_sessions)
    save_csv(speakers, SPEAKERS_DIR / "SPEAKERS_DATABASE.csv")
    save_json(speakers, RAW / "speakers_database.json")
    print(f"  Total: {len(all_sessions)} sessions, {len(speakers)} unique speakers")


def parse_rss(content, year):
    sessions = []
    try:
        # Strip default namespace to simplify parsing
        content_clean = re.sub(r'\sxmlns="[^"]+"', "", content, count=1)
        root = ET.fromstring(content_clean)
    except ET.ParseError:
        # Fall back to BeautifulSoup for malformed XML
        soup = BeautifulSoup(content, "xml")
        items = soup.find_all("item")
        for item in items:
            title = item.find("title")
            link = item.find("link")
            desc = item.find("description")
            pub = item.find("pubDate")
            sessions.append({
                "year": year,
                "title": title.get_text(strip=True) if title else "",
                "url": link.get_text(strip=True) if link else "",
                "description": BeautifulSoup(desc.get_text() if desc else "", "html.parser").get_text(strip=True)[:500],
                "date": pub.get_text(strip=True) if pub else "",
                "speakers": "",
                "venue": "",
                "track": "",
            })
        return sessions

    channel = root.find(".//channel") or root
    for item in channel.findall(".//item"):
        title_el = item.find("title")
        link_el = item.find("link")
        desc_el = item.find("description")
        pub_el = item.find("pubDate")
        # sched.com puts speaker/venue in description HTML
        desc_html = desc_el.text if desc_el is not None else ""
        desc_soup = BeautifulSoup(desc_html or "", "html.parser")
        desc_text = desc_soup.get_text(separator=" ", strip=True)

        # Extract speakers from description
        speakers = []
        for a in desc_soup.find_all("a"):
            href = a.get("href", "")
            if "/speaker/" in href or "speaker" in href.lower():
                speakers.append(a.get_text(strip=True))

        # Extract venue
        venue = ""
        venue_match = re.search(r'(?:venue|location|at)\s*:?\s*([^\n<]{3,60})', desc_text, re.IGNORECASE)
        if venue_match:
            venue = venue_match.group(1).strip()

        sessions.append({
            "year": year,
            "title": title_el.text.strip() if title_el is not None else "",
            "url": link_el.text.strip() if link_el is not None else "",
            "description": desc_text[:600],
            "date": pub_el.text.strip() if pub_el is not None else "",
            "speakers": "; ".join(speakers),
            "venue": venue,
            "track": "",
        })
    return sessions


def build_speakers_db(sessions):
    seen = {}
    for s in sessions:
        for name in s.get("speakers", "").split(";"):
            name = name.strip()
            if not name:
                continue
            if name not in seen:
                seen[name] = {"name": name, "years": set(), "session_count": 0, "sessions": []}
            seen[name]["years"].add(str(s["year"]))
            seen[name]["session_count"] += 1
            seen[name]["sessions"].append(s["title"][:80])

    rows = []
    for name, data in sorted(seen.items()):
        rows.append({
            "name": name,
            "years_active": ", ".join(sorted(data["years"])),
            "session_count": data["session_count"],
            "sample_sessions": " | ".join(data["sessions"][:3]),
            "email": "",
            "linkedin": "",
            "twitter": "",
            "company": "",
            "title": "",
            "notes": "",
        })
    return rows


# ─── PHASE 2: BETA.mn sitemap → fetch TCSW pages ─────────────────────────────

def phase2_beta_sitemap():
    print("\n═══ PHASE 2: BETA.mn sitemap → fetch TCSW-related pages ═══")
    sitemap_file = RAW / "probe_www.beta.mn_sitemap.xml"
    if not sitemap_file.exists():
        r = get("https://www.beta.mn/sitemap.xml")
        if not r:
            return
        sitemap_file.write_bytes(r.content)

    content = sitemap_file.read_text(errors="ignore")
    urls = re.findall(r'<loc>(https?://[^<]+)</loc>', content)
    print(f"  Found {len(urls)} URLs in BETA.mn sitemap")

    # Save full URL list
    save_json(urls, RAW / "beta_mn_all_urls.json")

    # Filter for TCSW-relevant pages
    tcsw_keywords = ["startup-week", "tcsw", "startup_week", "startupweek"]
    tcsw_urls = [u for u in urls if any(k in u.lower() for k in tcsw_keywords)]
    print(f"  {len(tcsw_urls)} TCSW-related URLs found")

    fetched = []
    for url in tcsw_urls[:30]:  # cap at 30 to avoid hammering
        time.sleep(1)
        r = get(url)
        if not r:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text(separator="\n", strip=True)
        title = soup.find("title")
        slug = urlparse(url).path.strip("/").replace("/", "_")[:60]
        out = RAW / f"beta_{slug}.txt"
        out.write_text(text[:10000], encoding="utf-8")
        fetched.append({"url": url, "title": title.get_text(strip=True) if title else "", "file": out.name})
        print(f"  ✓ {url}")

    save_json(fetched, RAW / "beta_mn_tcsw_pages.json")


# ─── PHASE 3: Extract emails, phones, social links from all HTML ─────────────

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
PHONE_RE = re.compile(r'(?:\+1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}')
SOCIAL_RE = {
    "linkedin": re.compile(r'linkedin\.com/(?:in|company)/([a-zA-Z0-9\-_]+)'),
    "twitter": re.compile(r'(?:twitter|x)\.com/([a-zA-Z0-9_]{1,50})'),
    "instagram": re.compile(r'instagram\.com/([a-zA-Z0-9_.]+)'),
    "facebook": re.compile(r'facebook\.com/([a-zA-Z0-9_.]+)'),
    "youtube": re.compile(r'youtube\.com/(?:@|channel/|c/)([a-zA-Z0-9_\-]+)'),
    "github": re.compile(r'github\.com/([a-zA-Z0-9_\-]+)'),
}


def phase3_contact_extraction():
    print("\n═══ PHASE 3: Extract contacts from all downloaded HTML ═══")
    html_files = list(RAW.glob("*.html")) + list(RAW.glob("*.txt"))

    all_emails = set()
    all_phones = set()
    social_hits = {k: set() for k in SOCIAL_RE}
    per_file = []

    for f in html_files:
        text = f.read_text(errors="ignore")
        emails = set(EMAIL_RE.findall(text))
        phones = set(PHONE_RE.findall(text))
        socials = {k: set(v.findall(text)) for k, v in SOCIAL_RE.items()}

        # Filter noise
        emails = {e for e in emails if not any(x in e for x in ["example.com", "schemata", "w3.org", "schema.org", "purl.org", "xmlns"])}
        phones = {p for p in phones if len(re.sub(r'\D', '', p)) == 10}

        all_emails.update(emails)
        all_phones.update(phones)
        for k, v in socials.items():
            social_hits[k].update(v)

        if emails or phones or any(v for v in socials.values()):
            per_file.append({
                "file": f.name,
                "emails": sorted(emails),
                "phones": sorted(phones),
                **{f"{k}_handles": sorted(v) for k, v in socials.items()}
            })

    # Build contact rows
    contact_rows = []
    for email in sorted(all_emails):
        contact_rows.append({
            "type": "email",
            "value": email,
            "platform": "email",
            "source": "extracted from downloaded HTML",
        })
    for platform, handles in social_hits.items():
        for handle in sorted(handles):
            if handle and len(handle) > 1:
                contact_rows.append({
                    "type": "social",
                    "value": handle,
                    "platform": platform,
                    "source": "extracted from downloaded HTML",
                })

    save_csv(contact_rows, CONTACTS_DIR / "EXTRACTED_CONTACTS.csv")
    save_json(per_file, RAW / "contact_extraction_by_file.json")

    print(f"  Emails found: {len(all_emails)}")
    print(f"  Phones found: {len(all_phones)}")
    for k, v in social_hits.items():
        print(f"  {k} handles: {len(v)}")


# ─── PHASE 4: YouTube channel videos ─────────────────────────────────────────

def phase4_youtube():
    print("\n═══ PHASE 4: YouTube channel metadata ═══")
    import subprocess, sys

    channel_url = "https://www.youtube.com/@tcstartupweek"
    out_json = RAW / "youtube_videos.json"

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--flat-playlist",
        "--dump-json",
        "--no-warnings",
        "--playlist-end", "200",
        channel_url,
    ]
    print(f"  Fetching video list from {channel_url} ...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        videos = []
        for line in result.stdout.strip().splitlines():
            if line.strip():
                try:
                    videos.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

        # Extract useful fields only
        slim = []
        for v in videos:
            slim.append({
                "id": v.get("id"),
                "title": v.get("title"),
                "url": v.get("url") or f"https://youtube.com/watch?v={v.get('id')}",
                "upload_date": v.get("upload_date"),
                "duration": v.get("duration"),
                "view_count": v.get("view_count"),
                "description": (v.get("description") or "")[:300],
                "thumbnails": [t.get("url") for t in (v.get("thumbnails") or [])[-1:]],
            })

        save_json(slim, out_json)
        print(f"  Found {len(slim)} videos")

        # Save CSV too
        if slim:
            save_csv(slim, CONTACTS_DIR / "YOUTUBE_VIDEOS.csv")

        # Download thumbnails for the 20 most recent
        thumb_dir = PHOTOS_DIR / "youtube_thumbnails"
        thumb_dir.mkdir(exist_ok=True)
        for v in slim[:20]:
            thumbs = v.get("thumbnails", [])
            if thumbs:
                url = thumbs[0]
                vid_id = v.get("id", "unknown")
                dest = thumb_dir / f"{vid_id}.jpg"
                if not dest.exists():
                    r = get(url)
                    if r:
                        dest.write_bytes(r.content)
                        time.sleep(0.2)

        if thumb_dir.exists():
            count = len(list(thumb_dir.glob("*.jpg")))
            print(f"  Downloaded {count} thumbnails → {thumb_dir.relative_to(REPO_ROOT)}")

    except Exception as e:
        print(f"  [err] YouTube fetch: {e}")


# ─── PHASE 5: Wayback CDX deep dive ──────────────────────────────────────────

def phase5_wayback_deep():
    print("\n═══ PHASE 5: Wayback CDX — all file types ═══")

    domains = [
        "twincitiesstartupweek.com",
        "tcstartupweek.com",
        "beta.mn",
    ]
    file_types = ["pdf", "jpg", "jpeg", "png", "gif", "ics", "csv", "xlsx", "ppt", "pptx", "doc", "docx", "mp4", "mp3"]
    cdx_base = "http://web.archive.org/cdx/search/cdx"
    all_assets = []

    for domain in domains:
        for ft in file_types:
            params = {
                "url": f"*.{domain}/*.{ft}",
                "output": "json",
                "fl": "timestamp,original,statuscode,mimetype,length",
                "filter": "statuscode:200",
                "limit": 100,
                "collapse": "original",
            }
            try:
                r = requests.get(cdx_base, params=params, timeout=25)
                if r.status_code != 200:
                    continue
                rows = r.json()
                if len(rows) <= 1:
                    continue
                headers_row = rows[0]
                for row in rows[1:]:
                    record = dict(zip(headers_row, row))
                    record["domain"] = domain
                    record["filetype"] = ft
                    all_assets.append(record)
                print(f"  {domain} .{ft}: {len(rows)-1} assets")
                time.sleep(0.5)
            except Exception as e:
                print(f"  [err] CDX {domain} .{ft}: {e}")

    save_json(all_assets, RAW / "wayback_all_assets_cdx.json")
    save_csv(all_assets, RAW / "wayback_all_assets.csv")
    print(f"  Total assets found: {len(all_assets)}")

    # Download PDFs and documents
    doc_assets = [a for a in all_assets if a.get("filetype") in ["pdf", "ppt", "pptx", "doc", "docx", "csv", "xlsx"]]
    print(f"  Downloading {len(doc_assets)} documents...")
    for asset in doc_assets[:50]:  # cap at 50
        ts = asset.get("timestamp", "")
        orig = asset.get("original", "")
        wb_url = f"https://web.archive.org/web/{ts}/{orig}"
        fname = Path(urlparse(orig).path).name[:80] or "unnamed"
        dest = DOCS_DIR / f"{ts}_{fname}"
        if dest.exists():
            continue
        r = get(wb_url, timeout=30)
        if r and r.content:
            dest.write_bytes(r.content)
            print(f"  ✓ {fname} ({len(r.content)//1024} KB)")
            time.sleep(0.8)

    # Download images (top 30)
    img_assets = [a for a in all_assets if a.get("filetype") in ["jpg", "jpeg", "png", "gif"]]
    print(f"  Downloading {min(30, len(img_assets))} images...")
    img_dir = PHOTOS_DIR / "wayback"
    img_dir.mkdir(exist_ok=True)
    for asset in img_assets[:30]:
        ts = asset.get("timestamp", "")
        orig = asset.get("original", "")
        wb_url = f"https://web.archive.org/web/{ts}/{orig}"
        fname = Path(urlparse(orig).path).name[:80] or "unnamed"
        dest = img_dir / f"{ts}_{fname}"
        if dest.exists():
            continue
        r = get(wb_url, timeout=20)
        if r and r.content:
            dest.write_bytes(r.content)
            print(f"  ✓ {fname}")
            time.sleep(0.5)


# ─── PHASE 6: People / Orgs database ─────────────────────────────────────────

def phase6_people_orgs():
    print("\n═══ PHASE 6: Build people/orgs database ═══")

    # Load all sessions to harvest names
    sessions_file = RAW / "all_sessions.json"
    all_sessions = json.loads(sessions_file.read_text()) if sessions_file.exists() else []

    # Load speakers DB
    speakers_file = RAW / "speakers_database.json"
    speakers = json.loads(speakers_file.read_text()) if speakers_file.exists() else []

    # Extract all org/company names from session descriptions
    orgs = {}
    org_patterns = [
        r'(?:sponsored by|presented by|hosted by|in partnership with)\s+([A-Z][A-Za-z\s&.,]{3,50})',
        r'([A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+){0,3})\s+(?:LLC|Inc|Corp|Co\.|Foundation|Group|Fund|Ventures|Capital)',
    ]
    for s in all_sessions:
        desc = s.get("description", "")
        for pattern in org_patterns:
            for match in re.finditer(pattern, desc):
                name = match.group(1).strip().rstrip(".,")
                if name not in orgs:
                    orgs[name] = {"name": name, "years": set(), "role": "mentioned in session", "sessions": []}
                orgs[name]["years"].add(str(s["year"]))
                orgs[name]["sessions"].append(s["title"][:60])

    # Known confirmed orgs from research
    confirmed_orgs = [
        {"name": "BETA.MN", "type": "Organizer", "years": "2014-2026", "website": "https://www.beta.mn", "email": "Angela.Eifert@BETA.MN", "linkedin": "beta-group", "twitter": "betamn", "instagram": "betamn", "notes": "Primary organizer"},
        {"name": "Communiful", "type": "Co-Organizer", "years": "2025-2026", "website": "https://communiful.com", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "Co-organizer 2025-2026"},
        {"name": "Twin Ignition", "type": "Venue/Sponsor", "years": "2022-2024", "website": "https://twinignition.com", "email": "", "linkedin": "twin-ignition", "twitter": "", "instagram": "", "notes": "Startup Garage + Keg House venues"},
        {"name": "FINNOVATION Lab", "type": "Venue/Sponsor", "years": "2022-2024", "website": "https://finnovationlab.com", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "Training Lab venue"},
        {"name": "Workbox", "type": "Venue/Sponsor", "years": "2022-2024", "website": "https://workbox.com", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "Event venue"},
        {"name": "Luminary Arts Center", "type": "Venue", "years": "2023", "website": "https://luminaryartscenter.com", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "Main stage + breakout rooms 2023"},
        {"name": "Target Corporation", "type": "Title Sponsor", "years": "2019", "website": "https://target.com", "email": "", "linkedin": "target", "twitter": "target", "instagram": "target", "notes": "Title sponsor 2019"},
        {"name": "Cargill", "type": "Title Sponsor", "years": "2019", "website": "https://cargill.com", "email": "", "linkedin": "cargill", "twitter": "cargill", "instagram": "", "notes": "Title sponsor 2019"},
        {"name": "3M", "type": "Title Sponsor", "years": "2019", "website": "https://3m.com", "email": "", "linkedin": "3m", "twitter": "3m", "instagram": "", "notes": "Title sponsor 2019"},
        {"name": "JPMorgan Chase", "type": "Premier Sponsor", "years": "2023-2026", "website": "https://jpmorganchase.com", "email": "", "linkedin": "jpmorgan-chase", "twitter": "jpmorgan", "instagram": "", "notes": "BETA Showcase sponsor 2023; 2026 sponsor"},
        {"name": "TriNet", "type": "Premier Sponsor", "years": "2023", "website": "https://trinet.com", "email": "", "linkedin": "trinet", "twitter": "trinet", "instagram": "", "notes": "VC Day sponsor 2023; WeWork mixer co-sponsor"},
        {"name": "Optum", "type": "Premier Sponsor", "years": "2023", "website": "https://optum.com", "email": "", "linkedin": "optum", "twitter": "optum", "instagram": "", "notes": "Optum Cup healthcare pitch competition 2023"},
        {"name": "Bread & Butter Ventures", "type": "Ecosystem/VC", "years": "2025-2026", "website": "https://breadandbutter.vc", "email": "", "linkedin": "bread-butter-ventures", "twitter": "bb_ventures", "instagram": "", "notes": "Active VC in MN ecosystem"},
        {"name": "Matchstick Ventures", "type": "Ecosystem/VC", "years": "2025", "website": "https://matchstickventures.com", "email": "", "linkedin": "matchstick-ventures", "twitter": "matchstickvc", "instagram": "", "notes": "MN-based VC"},
        {"name": "Great North Ventures", "type": "Ecosystem/VC", "years": "2025", "website": "https://greatnorthventures.com", "email": "", "linkedin": "great-north-ventures", "twitter": "greatnorthvc", "instagram": "", "notes": "MN-based VC"},
        {"name": "Groove Capital", "type": "Ecosystem/VC", "years": "2025-2026", "website": "https://groovecapital.com", "email": "", "linkedin": "groove-capital", "twitter": "", "instagram": "", "notes": "2026 listed sponsor"},
        {"name": "gener8tor", "type": "Ecosystem", "years": "2025", "website": "https://gener8tor.com", "email": "", "linkedin": "gener8tor", "twitter": "gener8tor", "instagram": "", "notes": "Startup accelerator in MN ecosystem"},
        {"name": "MN Cup / University of Minnesota", "type": "Competition Partner", "years": "2014-2026", "website": "https://mncup.org", "email": "", "linkedin": "", "twitter": "mncup", "instagram": "", "notes": "Annual pitch competition; Grand Finale during TCSW"},
        {"name": "Augeo", "type": "Sponsor", "years": "2026", "website": "https://augeo.com", "email": "", "linkedin": "augeo", "twitter": "", "instagram": "", "notes": "2026 listed sponsor"},
        {"name": "Northeast Bank", "type": "Sponsor", "years": "2026", "website": "https://northeastbank.com", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "2026 listed sponsor"},
        {"name": "Taft Law", "type": "Sponsor", "years": "2026", "website": "https://taftlaw.com", "email": "", "linkedin": "taft-law", "twitter": "", "instagram": "", "notes": "2026 listed sponsor"},
        {"name": "Mairs & Power", "type": "Sponsor", "years": "2026", "website": "https://mairsandpower.com", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "2026 listed sponsor"},
        {"name": "Brooksource", "type": "Sponsor", "years": "2026", "website": "https://brooksource.com", "email": "", "linkedin": "brooksource", "twitter": "", "instagram": "", "notes": "2026 listed sponsor"},
        {"name": "Idea Fund", "type": "Sponsor", "years": "2026", "website": "", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "2026 listed sponsor"},
        {"name": "Biometrica Health", "type": "Sponsor", "years": "2026", "website": "", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "2026 listed sponsor"},
        {"name": "ezer21", "type": "Sponsor", "years": "2026", "website": "", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "2026 listed sponsor"},
        {"name": "Full Stack Saint Paul Scale Up", "type": "Sponsor", "years": "2026", "website": "", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "2026 listed sponsor"},
        {"name": "Shakopee Mdewakanton Sioux Community", "type": "Sponsor", "years": "2026", "website": "https://shakopeedakota.org", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "2026 listed sponsor — tribal nation"},
        {"name": "Launch Minnesota", "type": "Ecosystem", "years": "2019-2026", "website": "https://launchmn.com", "email": "", "linkedin": "launch-minnesota", "twitter": "launchmn", "instagram": "", "notes": "State of MN startup initiative; DEED partner"},
        {"name": "AWS", "type": "Corporate Sponsor", "years": "2019", "website": "https://aws.amazon.com", "email": "", "linkedin": "amazon-web-services", "twitter": "awscloud", "instagram": "", "notes": "Title sponsor 2019"},
        {"name": "Microsoft", "type": "Corporate Sponsor", "years": "2019", "website": "https://microsoft.com", "email": "", "linkedin": "microsoft", "twitter": "microsoft", "instagram": "", "notes": "Corporate sponsor 2019"},
        {"name": "EmpowerHER", "type": "Ecosystem", "years": "2025", "website": "", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "Women founders program featured 2025"},
        {"name": "West Monroe", "type": "Venue/Sponsor", "years": "2023", "website": "https://westmonroe.com", "email": "", "linkedin": "west-monroe-partners", "twitter": "westmonroecorp", "instagram": "", "notes": "Session host 2023 AI day"},
        {"name": "Stratasys", "type": "Venue/Sponsor", "years": "2023", "website": "https://stratasys.com", "email": "", "linkedin": "stratasys", "twitter": "stratasys", "instagram": "", "notes": "3D Printing session host 2023"},
        {"name": "ConnectUP! Institute", "type": "Community Partner", "years": "2023", "website": "", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "Saint Paul location 2023"},
        {"name": "Augurian", "type": "Venue/Sponsor", "years": "2023", "website": "https://augurian.com", "email": "", "linkedin": "augurian", "twitter": "augurian", "instagram": "", "notes": "Co-branded venue 2023 with Cloudburst SBC"},
        {"name": "Lab651", "type": "Venue/Sponsor", "years": "2023", "website": "https://lab651.com", "email": "", "linkedin": "lab651", "twitter": "", "instagram": "", "notes": "AI + software dev session host 2023"},
        {"name": "Fredrikson & Byron", "type": "Venue/Sponsor", "years": "2023", "website": "https://fredlaw.com", "email": "", "linkedin": "fredrikson-byron", "twitter": "", "instagram": "", "notes": "Finance session host 2023"},
        {"name": "Lyft", "type": "Transport Sponsor", "years": "2018", "website": "https://lyft.com", "email": "", "linkedin": "lyft", "twitter": "lyft", "instagram": "lyft", "notes": "Free Lyft bus service during TCSW 2018"},
        {"name": "WeWork", "type": "Venue/Sponsor", "years": "2023", "website": "https://wework.com", "email": "", "linkedin": "wework", "twitter": "wework", "instagram": "wework", "notes": "NorthLoop location 2023; TriNet mixer co-host"},
        {"name": "ACER Inc", "type": "Community Partner", "years": "2023", "website": "", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "Cultural communities session 2023"},
        {"name": "Fearless Commerce", "type": "Community Partner", "years": "2023", "website": "", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "The Watering event presenter 2023"},
        {"name": "BauHaus Brew Labs", "type": "Venue", "years": "2023", "website": "https://bauhausbrewlabs.com", "email": "", "linkedin": "", "twitter": "bauhausbrewlabs", "instagram": "bauhausbrewlabs", "notes": "Medical Device Networking happy hour venue"},
        {"name": "First Independence Bank", "type": "Community Partner", "years": "2023", "website": "https://firstindependencebank.com", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "Building Business Credit session host"},
        {"name": "Sociable Ciderworks", "type": "Venue", "years": "2023", "website": "https://sociablecider.com", "email": "", "linkedin": "", "twitter": "sociablecider", "instagram": "sociablecider", "notes": "OnlyFounders Bags Tournament venue"},
        {"name": "Acme Comedy Company", "type": "Venue", "years": "2023", "website": "https://acmecomedycompany.com", "email": "", "linkedin": "", "twitter": "acmecomedy", "instagram": "", "notes": "VC Day happy hour venue"},
        {"name": "Riverview Theater", "type": "Venue", "years": "2023", "website": "https://riverviewtheater.com", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "Minnedemo39 venue"},
        {"name": "Target Field / Minnesota Twins", "type": "Venue", "years": "2023", "website": "https://mlb.com/twins", "email": "", "linkedin": "", "twitter": "twins", "instagram": "twins", "notes": "BETA Fall Showcase 2023 venue"},
        {"name": "McNamara Alumni Center", "type": "Venue", "years": "2023", "website": "https://mcnamaraalumnicenter.com", "email": "", "linkedin": "", "twitter": "", "instagram": "", "notes": "MN Cup Grand Finale 2023"},
    ]

    save_csv(confirmed_orgs, CONTACTS_DIR / "ORGANIZATIONS_DATABASE.csv")
    save_json(confirmed_orgs, RAW / "organizations_database.json")
    print(f"  Saved {len(confirmed_orgs)} confirmed organizations")

    # Merge extracted orgs
    extracted_org_rows = [{"name": k, **{kk: ", ".join(sorted(vv)) if isinstance(vv, set) else vv for kk, vv in v.items()}} for k, v in orgs.items()]
    save_csv(extracted_org_rows[:500], CONTACTS_DIR / "ORGS_EXTRACTED_FROM_SESSIONS.csv")
    print(f"  Extracted {len(extracted_org_rows)} org mentions from session descriptions")


# ─── PHASE 7: Download event photos ──────────────────────────────────────────

def phase7_photos():
    print("\n═══ PHASE 7: Download event photos ═══")

    # BETA.mn event photos from their CDN
    photo_urls = [
        ("https://www.beta.mn/hs-fs/hubfs/2020%20Website/Imagery/Events28-1.png", "beta_events1.png"),
        ("https://www.beta.mn/hs-fs/hubfs/2020%20Website/Imagery/OriginalFounders-1.png", "beta_founders.png"),
        # sched.com profile images (speaker headshots via CDN)
        ("https://cdn.sched.co/assets/tcsw2023/img/apple-touch-icon-xlarge.png", "sched_2023_icon.png"),
        ("https://cdn.sched.co/assets/tcsw2025/img/apple-touch-icon-xlarge.png", "sched_2025_icon.png"),
    ]

    # Also try to find Facebook photo albums via Wayback
    fb_photos = [
        "https://www.facebook.com/twincitiesstartupweek/photos/",
        "https://www.facebook.com/pg/twincitiesstartupweek/photos/",
    ]

    photo_dir = PHOTOS_DIR / "official"
    photo_dir.mkdir(exist_ok=True)

    for url, fname in photo_urls:
        dest = photo_dir / fname
        if dest.exists():
            continue
        r = get(url)
        if r:
            dest.write_bytes(r.content)
            print(f"  ✓ {fname} ({len(r.content)//1024} KB)")
            time.sleep(0.3)

    # Try og:image from key pages as event photos
    pages_for_og = [
        "https://tcsw2023.sched.com/",
        "https://tcsw2025.sched.com/",
        "https://www.tcstartupweek.com/",
    ]
    for url in pages_for_og:
        r = get(url)
        if not r:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
        if og and og.get("content"):
            img_url = og["content"]
            fname = f"og_{urlparse(url).netloc}.jpg"
            dest = photo_dir / fname
            if not dest.exists():
                ri = get(img_url)
                if ri:
                    dest.write_bytes(ri.content)
                    print(f"  ✓ OG image: {fname}")
            time.sleep(0.5)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="TCSW Deep Extraction Pipeline")
    parser.add_argument("--phase", type=int, help="Run only one phase (1-7)")
    args = parser.parse_args()

    phases = {
        1: phase1_rss_feeds,
        2: phase2_beta_sitemap,
        3: phase3_contact_extraction,
        4: phase4_youtube,
        5: phase5_wayback_deep,
        6: phase6_people_orgs,
        7: phase7_photos,
    }

    if args.phase:
        phases[args.phase]()
    else:
        for i in sorted(phases):
            phases[i]()

    print("\n✅ Deep extraction complete.")


if __name__ == "__main__":
    main()

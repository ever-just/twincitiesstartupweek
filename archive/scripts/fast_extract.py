"""
fast_extract.py
===============
Fully async parallel TCSW data extraction.
Uses aiohttp with 30 concurrent workers — 20-50x faster than sequential.

Phases (all run in parallel where possible):
  1. Sched RSS feeds -> sessions + speakers (all years simultaneously)
  2. Wayback CDX -> all file types, all domains (parallel domain+filetype queries)
  3. Wayback asset downloads (PDFs, images, docs) - 20 concurrent
  4. Contact/email/phone/social extraction from all HTML
  5. YouTube video metadata
  6. BETA.mn sitemap pages
  7. People/orgs database write

Run:
    python3 fast_extract.py
"""

import asyncio
import csv
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import subprocess, sys

import aiohttp
import aiofiles
from bs4 import BeautifulSoup

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
RAW        = REPO_ROOT / "research" / "raw_data"
DC         = REPO_ROOT / "research" / "data_collection"
SPEAKERS   = DC / "speakers_and_sessions"
CONTACTS   = DC / "people_and_orgs"
PHOTOS     = RAW / "photos"
DOCS       = RAW / "documents"
WB_IMGS    = PHOTOS / "wayback"
YT_THUMBS  = PHOTOS / "youtube_thumbnails"

for d in [RAW, SPEAKERS, CONTACTS, PHOTOS, DOCS, WB_IMGS, YT_THUMBS]:
    d.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
}

# ── Semaphores: tune concurrency per domain ────────────────────────────────────
SEM_GENERAL  = asyncio.Semaphore(30)   # general sites
SEM_WAYBACK  = asyncio.Semaphore(8)    # Wayback is sensitive to bursts
SEM_SCHED    = asyncio.Semaphore(10)
SEM_BETA     = asyncio.Semaphore(5)

SCHED_YEARS  = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

# ── Core async fetch ───────────────────────────────────────────────────────────

async def fetch(session, url, sem=None, timeout=20, binary=False):
    sem = sem or SEM_GENERAL
    async with sem:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), allow_redirects=True) as r:
                if r.status >= 400:
                    return None
                return await r.read() if binary else await r.text(errors="ignore")
        except Exception:
            return None

def save_json(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def save_csv(rows, path):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys(), extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — Sched.com RSS feeds (all years in parallel)
# ═══════════════════════════════════════════════════════════════════════════════

def parse_rss(content, year):
    sessions = []
    try:
        clean = re.sub(r'\sxmlns[^=]*="[^"]+"', "", content)
        root  = ET.fromstring(clean)
        items = root.findall(".//item")
    except ET.ParseError:
        soup  = BeautifulSoup(content, "lxml")
        items = None
        for item in soup.find_all("item"):
            title = item.find("title")
            link  = item.find("link")
            desc  = item.find("description")
            pub   = item.find("pubDate")
            desc_text = BeautifulSoup(desc.get_text() if desc else "", "html.parser").get_text(strip=True)
            sessions.append({
                "year": year, "title": title.get_text(strip=True) if title else "",
                "url": link.get_text(strip=True) if link else "",
                "description": desc_text[:500],
                "date": pub.get_text(strip=True) if pub else "",
                "speakers": "", "venue": "", "track": "",
            })
        return sessions

    for item in items:
        t   = item.find("title")
        l   = item.find("link")
        d   = item.find("description")
        pub = item.find("pubDate")
        desc_html = (d.text or "") if d is not None else ""
        soup_d    = BeautifulSoup(desc_html, "html.parser")
        desc_text = soup_d.get_text(separator=" ", strip=True)
        speakers  = [a.get_text(strip=True) for a in soup_d.find_all("a") if "/speaker/" in (a.get("href") or "")]
        sessions.append({
            "year": year,
            "title": t.text.strip() if t is not None else "",
            "url": l.text.strip() if l is not None else "",
            "description": desc_text[:500],
            "date": pub.text.strip() if pub is not None else "",
            "speakers": "; ".join(speakers),
            "venue": "",
            "track": "",
        })
    return sessions


async def fetch_sched_year(session, year):
    subdomain = "tcsw18" if year == 2018 else f"tcsw{year}"
    # Try cached file
    cached = RAW / f"probe_{subdomain}.sched.xml"
    if cached.exists() and cached.stat().st_size > 5000:
        content = cached.read_text(errors="ignore")
    else:
        url     = f"https://{subdomain}.sched.com/feed"
        content = await fetch(session, url, SEM_SCHED)
        if content:
            cached.write_text(content, encoding="utf-8")
    if not content:
        return year, []
    sessions = parse_rss(content, year)
    return year, sessions


async def phase1_rss(session):
    print("▶ Phase 1: sched.com RSS (all years parallel)...")
    tasks   = [fetch_sched_year(session, y) for y in SCHED_YEARS]
    results = await asyncio.gather(*tasks)

    all_sessions = []
    for year, sessions in results:
        print(f"  {year}: {len(sessions)} sessions")
        all_sessions.extend(sessions)
        if sessions:
            save_json(sessions, RAW / f"sessions_{year}.json")
            save_csv(sessions,  SPEAKERS / f"sessions_{year}.csv")

    save_csv(all_sessions, SPEAKERS / "ALL_SESSIONS.csv")
    save_json(all_sessions, RAW / "all_sessions.json")

    # Speakers DB
    seen = {}
    for s in all_sessions:
        for name in (s.get("speakers") or "").split(";"):
            name = name.strip()
            if not name:
                continue
            if name not in seen:
                seen[name] = {"name": name, "years": set(), "count": 0, "sessions": []}
            seen[name]["years"].add(str(s["year"]))
            seen[name]["count"] += 1
            seen[name]["sessions"].append(s["title"][:80])

    rows = [{"name": n, "years_active": ",".join(sorted(d["years"])),
             "session_count": d["count"], "sample_sessions": " | ".join(d["sessions"][:3]),
             "email": "", "linkedin": "", "twitter": "", "company": "", "notes": ""}
            for n, d in sorted(seen.items())]
    save_csv(rows, SPEAKERS / "SPEAKERS_DATABASE.csv")
    save_json(rows, RAW / "speakers_database.json")
    print(f"  ✓ {len(all_sessions)} sessions | {len(rows)} unique speakers")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — Wayback CDX all file types (parallel domain × filetype)
# ═══════════════════════════════════════════════════════════════════════════════

WB_DOMAINS   = ["twincitiesstartupweek.com", "tcstartupweek.com", "beta.mn"]
WB_FILETYPES = ["pdf", "jpg", "jpeg", "png", "ics", "csv", "xlsx", "ppt", "pptx", "doc", "docx"]

async def cdx_query(session, domain, ft):
    url = "http://web.archive.org/cdx/search/cdx"
    params = (
        f"?url=*.{domain}/*.{ft}&output=json"
        f"&fl=timestamp,original,statuscode,mimetype,length"
        f"&filter=statuscode:200&limit=100&collapse=original"
    )
    async with SEM_WAYBACK:
        try:
            async with session.get(url + params, timeout=aiohttp.ClientTimeout(total=30)) as r:
                if r.status != 200:
                    return domain, ft, []
                data = await r.json(content_type=None)
                if len(data) <= 1:
                    return domain, ft, []
                headers = data[0]
                rows    = [dict(zip(headers, row)) for row in data[1:]]
                for row in rows:
                    row["domain"]   = domain
                    row["filetype"] = ft
                return domain, ft, rows
        except Exception as e:
            return domain, ft, []


async def phase2_wayback_cdx(session):
    print("▶ Phase 2: Wayback CDX — all domains × file types in parallel...")
    tasks   = [cdx_query(session, d, ft) for d in WB_DOMAINS for ft in WB_FILETYPES]
    results = await asyncio.gather(*tasks)

    all_assets = []
    for domain, ft, rows in results:
        if rows:
            print(f"  {domain} .{ft}: {len(rows)} assets")
            all_assets.extend(rows)

    save_json(all_assets, RAW / "wayback_all_assets_cdx.json")
    save_csv(all_assets,  RAW / "wayback_all_assets.csv")
    print(f"  ✓ {len(all_assets)} total Wayback assets catalogued")
    return all_assets


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — Download Wayback assets (parallel, 20 concurrent)
# ═══════════════════════════════════════════════════════════════════════════════

async def download_asset(session, asset):
    ts   = asset.get("timestamp", "")
    orig = asset.get("original", "")
    ft   = asset.get("filetype", "bin")
    wb_url = f"https://web.archive.org/web/{ts}/{orig}"
    fname  = (Path(urlparse(orig).path).name or "unnamed")[:80]
    dest_dir = DOCS if ft in ["pdf","ppt","pptx","doc","docx","csv","xlsx","ics"] else WB_IMGS
    dest = dest_dir / f"{ts}_{fname}"
    if dest.exists():
        return
    data = await fetch(session, wb_url, SEM_WAYBACK, timeout=30, binary=True)
    if data:
        dest.write_bytes(data)


async def phase3_download_assets(session, all_assets):
    print("▶ Phase 3: Downloading Wayback assets (parallel)...")
    docs = [a for a in all_assets if a.get("filetype") in ["pdf","ppt","pptx","doc","docx","csv","xlsx","ics"]]
    imgs = [a for a in all_assets if a.get("filetype") in ["jpg","jpeg","png"]]

    doc_tasks = [download_asset(session, a) for a in docs[:60]]
    img_tasks = [download_asset(session, a) for a in imgs[:40]]
    await asyncio.gather(*(doc_tasks + img_tasks))

    dc = len(list(DOCS.glob("*")))
    ic = len(list(WB_IMGS.glob("*")))
    print(f"  ✓ {dc} documents | {ic} images downloaded")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — Contact extraction from all local HTML
# ═══════════════════════════════════════════════════════════════════════════════

EMAIL_RE  = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
PHONE_RE  = re.compile(r'(?:\+1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}')
SOCIAL_RE = {
    "linkedin":  re.compile(r'linkedin\.com/(?:in|company)/([a-zA-Z0-9\-_%]+)'),
    "twitter":   re.compile(r'(?:twitter|x)\.com/([a-zA-Z0-9_]{2,50})(?:[/?"\s]|$)'),
    "instagram": re.compile(r'instagram\.com/([a-zA-Z0-9_.]+)'),
    "facebook":  re.compile(r'facebook\.com/([a-zA-Z0-9_.]+)'),
    "youtube":   re.compile(r'youtube\.com/(?:@|channel/|c/)([a-zA-Z0-9_\-]+)'),
}
NOISE = {"example.com","schema.org","w3.org","purl.org","xmlns","schemata","yoursite"}

async def phase4_contacts():
    print("▶ Phase 4: Contact extraction from all HTML/text files...")
    files = list(RAW.glob("*.html")) + list(RAW.glob("*.txt")) + list(RAW.glob("*.xml"))

    all_emails = set()
    all_phones = set()
    social     = {k: set() for k in SOCIAL_RE}

    loop = asyncio.get_event_loop()
    def process(f):
        text = f.read_text(errors="ignore")
        emails = {e for e in EMAIL_RE.findall(text) if not any(n in e for n in NOISE)}
        phones = {p for p in PHONE_RE.findall(text) if len(re.sub(r'\D','',p))==10}
        soc    = {k: set(v.findall(text)) for k, v in SOCIAL_RE.items()}
        return emails, phones, soc

    # Run file parsing in thread pool (CPU bound)
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futs = [loop.run_in_executor(pool, process, f) for f in files]
        results = await asyncio.gather(*futs)

    for emails, phones, soc in results:
        all_emails.update(emails)
        all_phones.update(phones)
        for k, v in soc.items():
            social[k].update(v)

    rows = []
    for e in sorted(all_emails):
        rows.append({"type":"email","value":e,"platform":"email"})
    for platform, handles in social.items():
        for h in sorted(handles):
            if h and len(h) > 1:
                rows.append({"type":"social","value":h,"platform":platform})

    save_csv(rows, CONTACTS / "EXTRACTED_CONTACTS.csv")
    print(f"  ✓ {len(all_emails)} emails | {sum(len(v) for v in social.values())} social handles")
    return all_emails, social


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — YouTube videos + thumbnails
# ═══════════════════════════════════════════════════════════════════════════════

async def phase5_youtube(session):
    print("▶ Phase 5: YouTube channel metadata + thumbnails...")
    cmd = [sys.executable, "-m", "yt_dlp", "--flat-playlist", "--dump-json",
           "--no-warnings", "--playlist-end", "300",
           "https://www.youtube.com/@tcstartupweek"]

    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
    )
    stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)

    videos = []
    for line in stdout.decode(errors="ignore").splitlines():
        try:
            v = json.loads(line)
            videos.append({
                "id": v.get("id"), "title": v.get("title"),
                "url": v.get("url") or f"https://youtube.com/watch?v={v.get('id')}",
                "upload_date": v.get("upload_date"), "duration": v.get("duration"),
                "view_count": v.get("view_count"),
                "description": (v.get("description") or "")[:300],
                "thumbnail": next((t["url"] for t in reversed(v.get("thumbnails") or []) if t.get("url")), ""),
            })
        except Exception:
            pass

    save_json(videos, RAW / "youtube_videos.json")
    save_csv(videos,  CONTACTS / "YOUTUBE_VIDEOS.csv")
    print(f"  Found {len(videos)} videos")

    # Download thumbnails in parallel
    async def dl_thumb(v):
        url  = v.get("thumbnail","")
        vid  = v.get("id","x")
        dest = YT_THUMBS / f"{vid}.jpg"
        if url and not dest.exists():
            data = await fetch(session, url, SEM_GENERAL, binary=True)
            if data:
                dest.write_bytes(data)

    await asyncio.gather(*[dl_thumb(v) for v in videos[:50]])
    print(f"  ✓ {len(list(YT_THUMBS.glob('*.jpg')))} thumbnails saved")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6 — BETA.mn sitemap + TCSW pages (parallel)
# ═══════════════════════════════════════════════════════════════════════════════

async def fetch_page_text(session, url):
    html = await fetch(session, url, SEM_BETA)
    if not html:
        return url, None
    soup  = BeautifulSoup(html, "lxml")
    title = soup.find("title")
    text  = soup.get_text(separator="\n", strip=True)
    return url, {"title": title.get_text(strip=True) if title else "", "text": text[:8000]}


async def phase6_beta(session):
    print("▶ Phase 6: BETA.mn sitemap + TCSW pages...")
    sitemap_file = RAW / "probe_www.beta.mn_sitemap.xml"
    if sitemap_file.exists():
        content = sitemap_file.read_text(errors="ignore")
    else:
        content = await fetch(session, "https://www.beta.mn/sitemap.xml", SEM_BETA) or ""

    urls = re.findall(r'<loc>(https?://[^<]+)</loc>', content)
    save_json(urls, RAW / "beta_mn_all_urls.json")

    # Fetch all TCSW-relevant pages in parallel
    kw = ["startup", "tcsw", "event", "beta"]
    tcsw = [u for u in urls if any(k in u.lower() for k in kw)][:25]

    results = await asyncio.gather(*[fetch_page_text(session, u) for u in tcsw])
    saved = []
    for url, data in results:
        if data:
            slug = urlparse(url).path.strip("/").replace("/","_")[:50]
            out  = RAW / f"beta_{slug}.txt"
            out.write_text(data["text"], encoding="utf-8")
            saved.append({"url": url, "title": data["title"], "file": out.name})
            print(f"  ✓ {url}")

    save_json(saved, RAW / "beta_mn_tcsw_pages.json")
    print(f"  ✓ {len(saved)} BETA.mn pages fetched")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 7 — People / Orgs database
# ═══════════════════════════════════════════════════════════════════════════════

CONFIRMED_ORGS = [
    {"name":"BETA.MN","type":"Organizer","years":"2014-2026","website":"https://www.beta.mn","email":"Angela.Eifert@BETA.MN","linkedin":"beta-group","twitter":"betamn","instagram":"betamn","facebook":"betamn","notes":"Primary organizer"},
    {"name":"Communiful","type":"Co-Organizer","years":"2025-2026","website":"https://communiful.com","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"Co-organizer 2025-2026"},
    {"name":"Twin Ignition","type":"Venue/Sponsor","years":"2022-2024","website":"https://twinignition.com","email":"","linkedin":"twin-ignition","twitter":"","instagram":"","facebook":"","notes":"Startup Garage + Keg House venues"},
    {"name":"FINNOVATION Lab","type":"Venue/Sponsor","years":"2022-2024","website":"https://finnovationlab.com","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"Training Lab venue"},
    {"name":"Workbox","type":"Venue/Sponsor","years":"2022-2024","website":"https://workbox.com","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"Event venue"},
    {"name":"Luminary Arts Center","type":"Venue","years":"2023","website":"https://luminaryartscenter.com","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"Main stage + breakout rooms 2023"},
    {"name":"Target Corporation","type":"Title Sponsor","years":"2019","website":"https://target.com","email":"","linkedin":"target","twitter":"target","instagram":"target","facebook":"target","notes":"Title sponsor 2019; logo on all materials"},
    {"name":"Cargill","type":"Title Sponsor","years":"2019","website":"https://cargill.com","email":"","linkedin":"cargill","twitter":"cargill","instagram":"","facebook":"cargill","notes":"Title sponsor 2019"},
    {"name":"3M","type":"Title Sponsor","years":"2019","website":"https://3m.com","email":"","linkedin":"3m","twitter":"3m","instagram":"","facebook":"3M","notes":"Title sponsor 2019"},
    {"name":"JPMorgan Chase","type":"Premier Sponsor","years":"2023-2026","website":"https://jpmorganchase.com","email":"","linkedin":"jpmorgan-chase","twitter":"jpmorgan","instagram":"","facebook":"jpmorganchase","notes":"BETA Showcase sponsor 2023; 2026 listed sponsor"},
    {"name":"TriNet","type":"Premier Sponsor","years":"2023","website":"https://trinet.com","email":"","linkedin":"trinet","twitter":"trinet","instagram":"","facebook":"trinet","notes":"VC Day + WeWork mixer sponsor; branding on stage"},
    {"name":"Optum","type":"Premier Sponsor","years":"2023","website":"https://optum.com","email":"","linkedin":"optum","twitter":"optum","instagram":"","facebook":"optum","notes":"Named Optum Cup healthcare pitch competition"},
    {"name":"AWS","type":"Corporate Sponsor","years":"2019","website":"https://aws.amazon.com","email":"","linkedin":"amazon-web-services","twitter":"awscloud","instagram":"","facebook":"","notes":"Title sponsor 2019"},
    {"name":"Microsoft","type":"Corporate Sponsor","years":"2019","website":"https://microsoft.com","email":"","linkedin":"microsoft","twitter":"microsoft","instagram":"","facebook":"microsoft","notes":"Corporate sponsor 2019"},
    {"name":"Lyft","type":"Transport Sponsor","years":"2018","website":"https://lyft.com","email":"","linkedin":"lyft","twitter":"lyft","instagram":"lyft","facebook":"lyft","notes":"Free Lyft bus shuttle during TCSW 2018"},
    {"name":"Bread & Butter Ventures","type":"Ecosystem/VC","years":"2025-2026","website":"https://breadandbutter.vc","email":"","linkedin":"bread-butter-ventures","twitter":"bb_ventures","instagram":"","facebook":"","notes":"MN VC; 2026 sponsor"},
    {"name":"Matchstick Ventures","type":"Ecosystem/VC","years":"2025","website":"https://matchstickventures.com","email":"","linkedin":"matchstick-ventures","twitter":"matchstickvc","instagram":"","facebook":"","notes":"MN VC"},
    {"name":"Great North Ventures","type":"Ecosystem/VC","years":"2025","website":"https://greatnorthventures.com","email":"","linkedin":"great-north-ventures","twitter":"greatnorthvc","instagram":"","facebook":"","notes":"MN VC"},
    {"name":"Groove Capital","type":"Ecosystem/VC","years":"2025-2026","website":"https://groovecapital.com","email":"","linkedin":"groove-capital","twitter":"","instagram":"","facebook":"","notes":"2026 listed sponsor"},
    {"name":"gener8tor","type":"Ecosystem","years":"2025","website":"https://gener8tor.com","email":"","linkedin":"gener8tor","twitter":"gener8tor","instagram":"","facebook":"gener8tor","notes":"Startup accelerator MN ecosystem"},
    {"name":"MN Cup / University of Minnesota","type":"Competition Partner","years":"2014-2026","website":"https://mncup.org","email":"","linkedin":"","twitter":"mncup","instagram":"","facebook":"mncup","notes":"Annual pitch competition; Grand Finale during TCSW"},
    {"name":"Launch Minnesota","type":"Ecosystem","years":"2019-2026","website":"https://launchmn.com","email":"","linkedin":"launch-minnesota","twitter":"launchmn","instagram":"","facebook":"launchmn","notes":"State of MN startup initiative"},
    {"name":"Augeo","type":"Sponsor","years":"2026","website":"https://augeo.com","email":"","linkedin":"augeo","twitter":"","instagram":"","facebook":"","notes":"2026 sponsor"},
    {"name":"Northeast Bank","type":"Sponsor","years":"2026","website":"https://northeastbank.com","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"2026 sponsor"},
    {"name":"Taft Law","type":"Sponsor","years":"2026","website":"https://taftlaw.com","email":"","linkedin":"taft-law","twitter":"","instagram":"","facebook":"","notes":"2026 sponsor; annual exit planning sessions"},
    {"name":"Mairs & Power","type":"Sponsor","years":"2026","website":"https://mairsandpower.com","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"2026 sponsor"},
    {"name":"Brooksource","type":"Sponsor","years":"2026","website":"https://brooksource.com","email":"","linkedin":"brooksource","twitter":"","instagram":"","facebook":"","notes":"2026 sponsor"},
    {"name":"Shakopee Mdewakanton Sioux Community","type":"Sponsor","years":"2026","website":"https://shakopeedakota.org","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"2026 sponsor — tribal nation"},
    {"name":"Idea Fund","type":"Sponsor","years":"2026","website":"","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"2026 sponsor"},
    {"name":"Biometrica Health","type":"Sponsor","years":"2026","website":"","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"2026 sponsor"},
    {"name":"ezer21","type":"Sponsor","years":"2026","website":"","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"2026 sponsor"},
    {"name":"Full Stack Saint Paul Scale Up","type":"Sponsor","years":"2026","website":"","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"2026 sponsor"},
    {"name":"WeWork","type":"Venue/Sponsor","years":"2023","website":"https://wework.com","email":"","linkedin":"wework","twitter":"wework","instagram":"wework","facebook":"wework","notes":"NorthLoop location 2023"},
    {"name":"Lab651","type":"Venue/Sponsor","years":"2023","website":"https://lab651.com","email":"","linkedin":"lab651","twitter":"","instagram":"","facebook":"","notes":"AI + software session host"},
    {"name":"Augurian","type":"Venue/Sponsor","years":"2023","website":"https://augurian.com","email":"","linkedin":"augurian","twitter":"augurian","instagram":"","facebook":"","notes":"Co-branded Cloudburst SBC venue 2023"},
    {"name":"West Monroe","type":"Venue/Sponsor","years":"2023","website":"https://westmonroe.com","email":"","linkedin":"west-monroe-partners","twitter":"westmonroecorp","instagram":"","facebook":"","notes":"AI Day session host 2023"},
    {"name":"Stratasys","type":"Venue/Sponsor","years":"2023","website":"https://stratasys.com","email":"","linkedin":"stratasys","twitter":"stratasys","instagram":"","facebook":"stratasys","notes":"3D Printing session host 2023"},
    {"name":"Fredrikson & Byron","type":"Venue/Sponsor","years":"2023","website":"https://fredlaw.com","email":"","linkedin":"fredrikson-byron","twitter":"","instagram":"","facebook":"","notes":"Finance session host 2023"},
    {"name":"EmpowerHER","type":"Community Partner","years":"2025","website":"","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"Women founders program 2025"},
    {"name":"ConnectUP! Institute","type":"Community Partner","years":"2023","website":"","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"Saint Paul location 2023"},
    {"name":"ACER Inc","type":"Community Partner","years":"2023","website":"","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"Cultural communities session 2023"},
    {"name":"Fearless Commerce","type":"Community Partner","years":"2023","website":"","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"The Watering event presenter 2023"},
    {"name":"First Independence Bank","type":"Community Partner","years":"2023","website":"https://firstindependencebank.com","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"Business credit session host"},
    {"name":"BauHaus Brew Labs","type":"Venue","years":"2023","website":"https://bauhausbrewlabs.com","email":"","linkedin":"","twitter":"bauhausbrewlabs","instagram":"bauhausbrewlabs","facebook":"","notes":"Medical Device Networking happy hour"},
    {"name":"Sociable Ciderworks","type":"Venue","years":"2023","website":"https://sociablecider.com","email":"","linkedin":"","twitter":"sociablecider","instagram":"sociablecider","facebook":"","notes":"OnlyFounders Bags Tournament venue"},
    {"name":"Acme Comedy Company","type":"Venue","years":"2023","website":"https://acmecomedycompany.com","email":"","linkedin":"","twitter":"acmecomedy","instagram":"","facebook":"acmecomedy","notes":"VC Day happy hour venue"},
    {"name":"Riverview Theater","type":"Venue","years":"2023","website":"https://riverviewtheater.com","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"Minnedemo39 venue"},
    {"name":"Target Field / MN Twins","type":"Venue","years":"2023","website":"https://mlb.com/twins","email":"","linkedin":"","twitter":"twins","instagram":"twins","facebook":"twinsbaseball","notes":"BETA Fall Showcase 2023"},
    {"name":"McNamara Alumni Center","type":"Venue","years":"2023","website":"https://mcnamaraalumnicenter.com","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"MN Cup Grand Finale 2023"},
    {"name":"Woulfe Alumni Hall / U of St Thomas","type":"Venue","years":"2023","website":"https://stthomas.edu","email":"","linkedin":"","twitter":"stthomas","instagram":"stthomas","facebook":"","notes":"gBETA showcase venue 2023"},
    {"name":"IDS Tower / Fulcrum","type":"Venue","years":"2023","website":"","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"Fulcrum HQ 46th floor networking event"},
    {"name":"Northrop / U of Minnesota","type":"Venue","years":"2023","website":"https://northrop.umn.edu","email":"","linkedin":"","twitter":"","instagram":"","facebook":"","notes":"Infrastructure + future sessions 2023"},
    {"name":"Hewing Hotel","type":"Venue","years":"2023","website":"https://hewinghotel.com","email":"","linkedin":"","twitter":"hewinghotel","instagram":"hewinghotel","facebook":"hewinghotel","notes":"AR session venue 2023"},
]

async def phase7_orgs():
    print("▶ Phase 7: Writing people/orgs database...")
    save_csv(CONFIRMED_ORGS, CONTACTS / "ORGANIZATIONS_DATABASE.csv")
    save_json(CONFIRMED_ORGS, RAW / "organizations_database.json")
    print(f"  ✓ {len(CONFIRMED_ORGS)} organizations saved")

    # Also write a sponsor involvement detail file
    involvement = []
    for org in CONFIRMED_ORGS:
        notes = org.get("notes","")
        inv = {
            "organization": org["name"],
            "type": org["type"],
            "years": org["years"],
            "website": org["website"],
            "twitter": org.get("twitter",""),
            "linkedin": org.get("linkedin",""),
            "ad_placement": "yes" if org["type"] in ["Title Sponsor","Premier Sponsor","Corporate Sponsor"] else "unknown",
            "website_listing": "yes" if org["type"] in ["Title Sponsor","Premier Sponsor","Organizer","Co-Organizer"] else "likely",
            "named_event": "yes" if any(x in notes for x in ["Cup","named","Named"]) else "no",
            "venue_sponsor": "yes" if "venue" in org["type"].lower() else "no",
            "transport_sponsor": "yes" if "Transport" in org["type"] else "no",
            "notes": notes,
        }
        involvement.append(inv)

    save_csv(involvement, CONTACTS / "SPONSOR_INVOLVEMENT_DETAIL.csv")
    print(f"  ✓ Sponsor involvement matrix saved")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN — run all phases concurrently where possible
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    start = datetime.now()
    connector = aiohttp.TCPConnector(limit=40, limit_per_host=10, ssl=False)
    async with aiohttp.ClientSession(headers=HEADERS, connector=connector) as session:

        # Phases that don't depend on each other run concurrently
        p1  = phase1_rss(session)
        p4  = phase4_contacts()          # reads local files only
        p5  = phase5_youtube(session)
        p6  = phase6_beta(session)
        p7  = phase7_orgs()

        # Run independent phases all at once
        await asyncio.gather(p1, p4, p5, p6, p7)

        # Phase 2+3 need session but can run after above
        assets = await phase2_wayback_cdx(session)
        await phase3_download_assets(session, assets)

    elapsed = (datetime.now() - start).seconds
    print(f"\n✅ All phases complete in {elapsed}s")
    print(f"   Sessions CSV:    {SPEAKERS / 'ALL_SESSIONS.csv'}")
    print(f"   Speakers DB:     {SPEAKERS / 'SPEAKERS_DATABASE.csv'}")
    print(f"   Orgs DB:         {CONTACTS / 'ORGANIZATIONS_DATABASE.csv'}")
    print(f"   Contacts:        {CONTACTS / 'EXTRACTED_CONTACTS.csv'}")
    print(f"   YouTube:         {CONTACTS / 'YOUTUBE_VIDEOS.csv'}")
    print(f"   Wayback assets:  {RAW / 'wayback_all_assets.csv'}")
    print(f"   Documents:       {DOCS}")
    print(f"   Photos:          {PHOTOS}")


if __name__ == "__main__":
    asyncio.run(main())

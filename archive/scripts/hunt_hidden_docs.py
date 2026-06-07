"""
hunt_hidden_docs.py
===================
Finds hidden/unlisted documents (PDFs, Excel, Word, CSV, PPT) stored on
TCSW / BETA.MN domains — both on live servers and in Wayback Machine.

Also fetches:
- Google Trends search volume for "Twin Cities Startup Week"
- ProPublica 990 financial tables (HTML parse, no JS needed)
- Eventbrite pages for MN Cup / TCSW events (capacity, price, attendee counts)
- YouTube video view counts via YouTube oEmbed / noembed API
- MN Secretary of State nonprofit filing data
- DEED grants search
- pytrends Google Trends data
"""

import asyncio, json, re, time
from pathlib import Path
from datetime import date
import aiohttp
from bs4 import BeautifulSoup

REPO  = Path(__file__).resolve().parent.parent
OUT   = REPO / "data" / "quantitative"
OUT.mkdir(parents=True, exist_ok=True)

TODAY = date.today().isoformat()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}

# Domains to hunt across
DOMAINS = [
    "tcstartupweek.com",
    "twincitiesstartupweek.com",
    "beta.mn",
    "www.beta.mn",
    "info.tcstartupweek.com",
    "info.twincitiesstartupweek.com",
    "tcsw2023.sched.com",
    "tcsw18.sched.com",
]

# Hidden file paths to probe directly on live servers
HIDDEN_PATHS = [
    "/sponsor-prospectus.pdf",
    "/sponsorship-prospectus.pdf",
    "/sponsorship-deck.pdf",
    "/media-kit.pdf",
    "/press-kit.pdf",
    "/impact-report.pdf",
    "/impact-report-2023.pdf",
    "/annual-report.pdf",
    "/annual-report-2023.pdf",
    "/tcsw-2023-recap.pdf",
    "/tcsw-recap.pdf",
    "/2023-impact-report.pdf",
    "/2024-impact-report.pdf",
    "/2025-impact-report.pdf",
    "/files/sponsor-prospectus.pdf",
    "/files/sponsorship.pdf",
    "/assets/sponsor-prospectus.pdf",
    "/assets/docs/sponsor-prospectus.pdf",
    "/wp-content/uploads/sponsor-prospectus.pdf",
    "/wp-content/uploads/tcsw-sponsorship.pdf",
    "/downloads/sponsor-prospectus.pdf",
    "/docs/sponsor-prospectus.pdf",
    "/hubfs/sponsor-prospectus.pdf",
    "/hubfs/tcsw-sponsorship-prospectus.pdf",
    "/hs-fs/hubfs/sponsor-prospectus.pdf",
]

SEM = asyncio.Semaphore(4)


async def fetch(session, url, label="", timeout=15):
    async with SEM:
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=timeout),
                ssl=False, allow_redirects=True
            ) as r:
                if r.status == 200:
                    ct = r.headers.get("Content-Type", "")
                    if "pdf" in ct or "excel" in ct or "spreadsheet" in ct or "word" in ct:
                        body = await r.read()
                        return body, ct, r.status
                    text = await r.text(errors="ignore")
                    return text, ct, r.status
                return None, None, r.status
        except Exception as e:
            return None, None, str(e)


async def fetch_json(session, url, timeout=15):
    async with SEM:
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=timeout),
                ssl=False, headers={**HEADERS, "Accept": "application/json"}
            ) as r:
                if r.status == 200:
                    return await r.json(content_type=None)
                return None
        except Exception:
            return None


# ─────────────────────────────────────────────────────────────────
# 1. WAYBACK CDX — hunt PDFs / Excel / Word / PPT across all domains
# ─────────────────────────────────────────────────────────────────

async def wayback_file_hunt(session):
    print("\n[Wayback] Hunting hidden documents via CDX API...")
    found = []
    mimetypes = [
        "application/pdf",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/csv",
    ]

    for domain in DOMAINS[:5]:  # top 5 domains
        for mime in mimetypes[:4]:  # PDF + Excel priority
            await asyncio.sleep(1.5)  # rate-limit: Wayback CDX is strict
            url = (
                f"http://web.archive.org/cdx/search/cdx"
                f"?url={domain}/*&output=json&fl=timestamp,original,mimetype,length,statuscode"
                f"&filter=mimetype:{re.escape(mime)}"
                f"&filter=statuscode:200"
                f"&collapse=original&limit=50"
            )
            data = await fetch_json(session, url)
            if data and len(data) > 1:
                for row in data[1:]:
                    ts, orig, mt, sz, sc = row
                    entry = {
                        "source": "Wayback CDX",
                        "domain": domain,
                        "url": orig,
                        "mimetype": mt,
                        "size_bytes": sz,
                        "wayback_ts": ts,
                        "wayback_url": f"https://web.archive.org/web/{ts}/{orig}",
                    }
                    found.append(entry)
                    print(f"  FOUND [{mt.split('/')[-1]}] {orig}")

    print(f"  Wayback doc hunt: {len(found)} documents found")
    return found


# ─────────────────────────────────────────────────────────────────
# 2. LIVE SERVER — probe hidden file paths
# ─────────────────────────────────────────────────────────────────

async def probe_live_hidden(session):
    print("\n[Live] Probing hidden document paths on live servers...")
    found = []

    live_domains = [
        "https://tcstartupweek.com",
        "https://www.beta.mn",
        "https://communiful.com",
    ]

    for base in live_domains:
        for path in HIDDEN_PATHS:
            url = base + path
            body, ct, status = await fetch(session, url, f"Live {path}")
            if body and status == 200:
                size = len(body) if isinstance(body, bytes) else len(body.encode())
                print(f"  *** HIT: {url} [{ct}] {size:,} bytes")
                entry = {"source": "Live server", "url": url, "content_type": ct,
                         "size_bytes": size}
                if isinstance(body, bytes):
                    # Save the PDF locally
                    fname = OUT / f"hidden_{base.split('//')[1].split('.')[0]}_{path.strip('/').replace('/','_')}"
                    fname.write_bytes(body)
                    entry["saved_to"] = str(fname)
                found.append(entry)
            await asyncio.sleep(0.3)

    print(f"  Live probe: {len(found)} files found")
    return found


# ─────────────────────────────────────────────────────────────────
# 3. PROPUBLICA 990 — parse HTML financial tables (no JS needed)
# ─────────────────────────────────────────────────────────────────

FILING_URLS = {
    2024: "https://projects.propublica.org/nonprofits/organizations/812227583/202523219349317932/full",
    2023: "https://projects.propublica.org/nonprofits/organizations/812227583/202413189349302391/full",
    2022: "https://projects.propublica.org/nonprofits/organizations/812227583/202402259349302190/full",
    2021: "https://projects.propublica.org/nonprofits/organizations/812227583/202410179349300426/full",
    2020: "https://projects.propublica.org/nonprofits/organizations/812227583/202103199349310690/full",
    2019: "https://projects.propublica.org/nonprofits/organizations/812227583/202043219349301644/full",
    2018: "https://projects.propublica.org/nonprofits/organizations/812227583/201911049349300316/full",
}

async def fetch_990_financials(session):
    print("\n[990] Parsing IRS Form 990 financial data from ProPublica...")
    results = []

    for year, url in FILING_URLS.items():
        await asyncio.sleep(1)
        body, ct, status = await fetch(session, url, f"990 {year}", timeout=12)
        if not body or status != 200:
            print(f"  {year}: HTTP {status}")
            continue

        soup = BeautifulSoup(body, "lxml")
        text = soup.get_text(" ", strip=True)

        # Extract key financials from text
        def find_amount(pattern):
            m = re.search(pattern, text, re.I)
            if m:
                raw = m.group(1).replace(",", "")
                try: return int(float(raw))
                except: return None
            return None

        # 990 line items
        total_rev   = find_amount(r'Total revenue[^$]*\$\s*([\d,]+)')
        total_exp   = find_amount(r'Total (?:functional )?expenses[^$]*\$\s*([\d,]+)')
        net_assets  = find_amount(r'Net assets[^$]*\$\s*([\d,]+)')
        program_exp = find_amount(r'Program service[^$]*\$\s*([\d,]+)')
        grants_rec  = find_amount(r'Grants and.*contributions[^$]*\$\s*([\d,]+)')
        employees   = find_amount(r'Total number.*employees.*?(\d+)')
        volunteers  = find_amount(r'Total number.*volunteers.*?(\d+)')
        comp_high   = find_amount(r'(?:Reed Robinson|Angela Eifert|Nels Pedersen|Cihan Behlivan)[^$]*\$\s*([\d,]+)')

        # Fallback broader patterns
        if not total_rev:
            total_rev = find_amount(r'12\s+Total revenue.*?\$?\s*([\d,]{4,})')
        if not total_exp:
            total_exp = find_amount(r'Total functional expenses.*?\$?\s*([\d,]{4,})')

        # Grab all dollar amounts for manual review
        all_dollars = re.findall(r'\$\s*([\d,]{4,})', text)
        top_amounts = sorted(set(int(x.replace(",","")) for x in all_dollars[:100]
                                 if x.replace(",","").isdigit()), reverse=True)[:15]

        entry = {
            "source": "IRS Form 990 / ProPublica",
            "fiscal_year": year,
            "url": url,
            "total_revenue": total_rev,
            "total_expenses": total_exp,
            "net_assets": net_assets,
            "program_expenses": program_exp,
            "grants_received": grants_rec,
            "employees": employees,
            "volunteers": volunteers,
            "top_executive_comp": comp_high,
            "largest_dollar_amounts_on_form": top_amounts,
        }
        results.append(entry)
        rev_s = f"${total_rev:,}" if total_rev else "N/A"
        exp_s = f"${total_exp:,}" if total_exp else "N/A"
        print(f"  {year}: revenue={rev_s} | expenses={exp_s} | top amounts={top_amounts[:5]}")

    return results


# ─────────────────────────────────────────────────────────────────
# 4. YOUTUBE oEmbed / noembed — get view counts for all 303 videos
# ─────────────────────────────────────────────────────────────────

async def fetch_youtube_views(session):
    print("\n[YouTube] Fetching view counts via noembed API...")
    yt_file = REPO / "raw" / "youtube_videos.json"
    videos  = json.loads(yt_file.read_text())
    results = []
    hit = 0

    for i, v in enumerate(videos):
        vid_id = v.get("id", "")
        if not vid_id:
            continue
        # noembed.com returns title, author, thumbnail — not views
        # But YouTube page embeds view count in og:description or ytInitialData
        # Use YouTube's public /watch page — extract view count from meta tags
        url = f"https://www.youtube.com/watch?v={vid_id}"
        await asyncio.sleep(0.4)
        body, ct, status = await fetch(session, url, f"YT {i}/{len(videos)}", timeout=15)
        if not body or status != 200:
            continue

        # Views in og:description: "X views"
        m = re.search(r'"viewCount":\s*"(\d+)"', body)
        views = int(m.group(1)) if m else None

        # Upload date
        d = re.search(r'"publishDate":\s*"(\d{4}-\d{2}-\d{2})"', body)
        pub_date = d.group(1) if d else v.get("upload_date", "")

        # Like count
        lk = re.search(r'"likeCount":\s*"(\d+)"', body)
        likes = int(lk.group(1)) if lk else None

        if views:
            hit += 1
            results.append({
                "id": vid_id,
                "title": v.get("title", ""),
                "url": url,
                "views": views,
                "likes": likes,
                "published": pub_date,
                "duration_sec": v.get("duration"),
            })
        if i % 30 == 0:
            print(f"  Progress: {i}/{len(videos)}, hits={hit}")

    print(f"  YouTube: {hit}/{len(videos)} view counts retrieved")
    return results


# ─────────────────────────────────────────────────────────────────
# 5. EVENTBRITE — scrape MN Cup + TCSW event pages for capacity/price
# ─────────────────────────────────────────────────────────────────

EVENTBRITE_URLS = [
    ("MN Cup 2025 Grand Finale", "https://www.eventbrite.com/e/2025-mn-cup-grand-finale-tickets-1295771049089"),
    ("MN Cup 2024 Grand Finale", "https://www.eventbrite.com/e/2024-mn-cup-grand-finale-tickets-899333850757"),
    ("TCSW 2023 search", "https://www.eventbrite.com/d/mn--minneapolis/twin-cities-startup-week/?page=1"),
    ("BETA Showcase search", "https://www.eventbrite.com/d/mn--minneapolis/beta-showcase/"),
    ("Minnedemo search", "https://www.eventbrite.com/d/mn--minneapolis/minnedemo/"),
]

async def fetch_eventbrite_events(session):
    print("\n[Eventbrite] Scraping event capacity and ticket data...")
    results = []

    for label, url in EVENTBRITE_URLS:
        body, ct, status = await fetch(session, url, f"EB {label}", timeout=20)
        if not body or status != 200:
            print(f"  {label}: HTTP {status}")
            continue

        soup = BeautifulSoup(body, "lxml")
        text = soup.get_text(" ", strip=True)

        # Capacity
        cap    = re.findall(r'(\d[\d,]*)\s*(?:spots?|tickets?|spaces?|seats?|capacity)', text, re.I)
        sold   = re.findall(r'(\d[\d,]*)\s*(?:sold|attending|going|registered)', text, re.I)
        price  = re.findall(r'\$\s*([\d,.]+)', text)
        date_  = re.findall(r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+\w+\s+\d+,?\s+\d{4}', text)
        # JSON-LD structured data often has exact numbers
        jld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.DOTALL)
        jld_data = []
        for j in jld:
            try: jld_data.append(json.loads(j))
            except: pass

        attendee_count = None
        event_capacity = None
        for j in jld_data:
            if isinstance(j, dict):
                attendee_count = j.get("attendee", {})
                event_capacity = j.get("maximumAttendeeCapacity")
                offer = j.get("offers", {})
                if isinstance(offer, dict):
                    price = [offer.get("price", "")]

        entry = {
            "source": "Eventbrite",
            "label": label,
            "url": url,
            "capacity_mentions": cap[:5],
            "sold_mentions": sold[:5],
            "price_mentions": price[:5],
            "dates_mentioned": date_[:3],
            "json_ld_capacity": event_capacity,
            "json_ld_attendees": str(attendee_count)[:100] if attendee_count else None,
        }
        results.append(entry)
        print(f"  {label}: cap={cap[:3]}, sold={sold[:3]}, price={price[:3]}, ld_cap={event_capacity}")

    return results


# ─────────────────────────────────────────────────────────────────
# 6. GOOGLE TRENDS via pytrends
# ─────────────────────────────────────────────────────────────────

def fetch_google_trends():
    print("\n[Google Trends] Fetching search volume data...")
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw_list = ["Twin Cities Startup Week", "TCSW", "beta.mn"]
        pytrends.build_payload(kw_list, cat=0, timeframe="2014-01-01 2026-06-01", geo="US-MN")
        df = pytrends.interest_over_time()
        if df is not None and not df.empty:
            result = df.reset_index().to_dict(orient="records")
            # Yearly peaks
            df["year"] = df.index.year
            yearly = df.groupby("year")["Twin Cities Startup Week"].max().to_dict()
            print(f"  Google Trends: {len(result)} weekly data points")
            print(f"  Yearly peaks: {yearly}")
            return {"weekly": result, "yearly_peaks": yearly}
    except ImportError:
        print("  pytrends not installed — skipping")
    except Exception as e:
        print(f"  Google Trends error: {e}")
    return {}


# ─────────────────────────────────────────────────────────────────
# 7. MN SECRETARY OF STATE — BETA nonprofit filings
# ─────────────────────────────────────────────────────────────────

async def fetch_mn_sos(session):
    print("\n[MN SoS] Searching Minnesota nonprofit registry...")
    results = []
    urls = [
        "https://mblsportal.sos.state.mn.us/Business/SearchIndex?SearchType=BusinessName&SearchValue=beta+group",
        "https://www.sos.state.mn.us/business-liens/business-filings/",
    ]
    for url in urls:
        body, ct, status = await fetch(session, url, "MN SoS", timeout=20)
        if not body or status != 200:
            continue
        soup = BeautifulSoup(body, "lxml")
        text = soup.get_text(" ", strip=True)
        # Look for filing dates, registration numbers
        filings = re.findall(r'(?:filed|incorporated|registered|formed)[:\s]+(\w+\s+\d{1,2},?\s+\d{4})', text, re.I)
        ein     = re.findall(r'EIN[:\s#]+(\d{2}-\d{7})', text)
        reg_id  = re.findall(r'(?:file\s+number|entity\s+id|registration)[:\s#]+(\d{6,})', text, re.I)
        if filings or reg_id:
            results.append({"source": "MN SoS", "url": url, "filings": filings[:5], "ein": ein, "reg_id": reg_id})
            print(f"  MN SoS: {filings[:3]}, reg={reg_id[:3]}")
    return results


# ─────────────────────────────────────────────────────────────────
# 8. TCSW LIVE SITE — try with corrected headers (fix 421 error)
# ─────────────────────────────────────────────────────────────────

async def fetch_tcsw_stats(session):
    print("\n[TCSW] Fetching live site stats with corrected headers...")
    results = []
    urls = [
        "https://tcstartupweek.com/",
        "https://tcstartupweek.com/about",
        "https://tcstartupweek.com/faq",
        "https://www.tcstartupweek.com/",
        "https://www.beta.mn/",
        "https://www.beta.mn/about",
        "https://www.beta.mn/programs",
        "https://www.beta.mn/accelerator",
        "https://www.beta.mn/showcase",
        "https://www.beta.mn/impact",
        "https://www.beta.mn/blog",
    ]
    for url in urls:
        body, ct, status = await fetch(session, url, f"TCSW {url[-20:]}", timeout=20)
        if not body or status != 200:
            print(f"  {url[-40:]}: HTTP {status}")
            continue
        soup = BeautifulSoup(body, "lxml")
        text = soup.get_text(" ", strip=True)

        att      = re.findall(r'(\d[\d,]+)\+?\s*(?:attendees?|participants?|entrepreneurs?|founders?)', text, re.I)
        evts     = re.findall(r'(\d[\d,]+)\+?\s*(?:events?|sessions?)', text, re.I)
        spk      = re.findall(r'(\d[\d,]+)\+?\s*speakers?', text, re.I)
        money    = re.findall(r'\$\s*(\d[\d,.]+)\s*(?:K|M|thousand|million)?', text, re.I)
        startups = re.findall(r'(\d[\d,]+)\+?\s*startups?', text, re.I)
        years    = re.findall(r'(\d+)\+?\s*years?', text, re.I)
        jobs     = re.findall(r'(\d[\d,]+)\+?\s*jobs?', text, re.I)
        # Stat blocks
        stat_els = soup.select("[class*=stat],[class*=count],[class*=number],[class*=metric],[class*=figure]")
        stats    = [el.get_text(strip=True) for el in stat_els if el.get_text(strip=True)]

        if any([att, evts, spk, money, stats, startups]):
            results.append({
                "source": "TCSW/BETA live", "url": url,
                "attendees": att[:5], "events": evts[:5], "speakers": spk[:5],
                "startups": startups[:5], "dollar_figures": money[:10],
                "years_mentioned": years[:5], "jobs": jobs[:3],
                "stat_elements": stats[:20],
            })
            print(f"  {url[-40:]}: att={att[:3]}, events={evts[:3]}, stats={stats[:4]}, $={money[:4]}")

    return results


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

async def main():
    print("=" * 65)
    print("TCSW HIDDEN DOCS + DEEP QUANTITATIVE EXTRACTION")
    print(f"Started: {TODAY}")
    print("=" * 65)

    import sys
    connector = aiohttp.TCPConnector(limit=6, ssl=False, enable_cleanup_closed=True)
    async with aiohttp.ClientSession(headers=HEADERS, connector=connector) as session:
        # Fast parallel sources first
        print("[Phase 1] Fast parallel sources..."); sys.stdout.flush()
        r_live, r_eb, r_sos, r_probe = await asyncio.gather(
            fetch_tcsw_stats(session),
            fetch_eventbrite_events(session),
            fetch_mn_sos(session),
            probe_live_hidden(session),
        )
        # Wayback (rate-limited, sequential internally)
        print("[Phase 2] Wayback doc hunt..."); sys.stdout.flush()
        r_wb = await wayback_file_hunt(session)
        # 990 (slow external site)
        print("[Phase 3] IRS 990 financials..."); sys.stdout.flush()
        r_990 = await fetch_990_financials(session)
        # YouTube (303 requests, slow)
        print("[Phase 4] YouTube view counts (303 videos)..."); sys.stdout.flush()
        r_yt = await fetch_youtube_views(session)

    # Google Trends (sync)
    r_trends = fetch_google_trends()

    # ── Compile ──────────────────────────────────────────────────
    out = {
        "generated": TODAY,
        "irs_990_financials":    r_990,
        "tcsw_beta_live_site":   r_live,
        "eventbrite_events":     r_eb,
        "mn_sos_filings":        r_sos,
        "wayback_hidden_docs":   r_wb,
        "live_server_hidden":    r_probe,
        "youtube_view_counts":   r_yt,
        "google_trends":         r_trends,
    }

    out_file = OUT / "hidden_docs_and_deep_quant.json"
    out_file.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

    print("\n" + "=" * 65)
    print("RESULTS SUMMARY")
    print("=" * 65)
    print(f"  990 filings parsed:         {len(r_990)}")
    print(f"  Live site pages w/ data:    {len(r_live)}")
    print(f"  Eventbrite events parsed:   {len(r_eb)}")
    print(f"  MN SoS results:             {len(r_sos)}")
    print(f"  Wayback hidden documents:   {len(r_wb)}")
    print(f"  Live hidden files found:    {len(r_probe)}")
    print(f"  YouTube view counts:        {len(r_yt)}")
    print(f"  Google Trends data points:  {len(r_trends.get('weekly', []))}")
    print(f"\n  Output: {out_file}")
    print(f"  Next: python3 build_quant_report.py")


if __name__ == "__main__":
    asyncio.run(main())

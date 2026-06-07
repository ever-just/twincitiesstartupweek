"""
probe_sites.py
==============
Fetches robots.txt, sitemaps, and hidden endpoints from all TCSW-related domains.
Saves everything to research/raw_data/. No shell commands needed.
"""

import requests
import json
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "research" / "raw_data"
RAW.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
}

DOMAINS = [
    "https://www.tcstartupweek.com",
    "https://info.tcstartupweek.com",
    "https://tcsw2023.sched.com",
    "https://tcsw2025.sched.com",
    "https://tcsw2022.sched.com",
    "https://tcsw2024.sched.com",
    "https://tcsw2021.sched.com",
    "https://tcsw2020.sched.com",
    "https://tcsw2019.sched.com",
    "https://tcsw18.sched.com",
    "https://www.beta.mn",
]

EXTRA_PATHS = [
    "/robots.txt",
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/feed",
    "/feed.xml",
    "/rss",
    "/api",
    "/api/session/list",
    "/export/json",
    "/export/ics",
    "/.well-known/security.txt",
]

results = {}

for domain in DOMAINS:
    domain_key = domain.replace("https://", "").replace("/", "_")
    results[domain] = {}
    print(f"\n── {domain}")

    for path in EXTRA_PATHS:
        url = domain + path
        try:
            r = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
            content_type = r.headers.get("Content-Type", "")
            size = len(r.content)
            status = r.status_code

            if status == 200 and size > 100:
                # Save the content
                safe_path = path.strip("/").replace("/", "_") or "root"
                out_file = RAW / f"probe_{domain_key}_{safe_path}"

                if "xml" in content_type or path.endswith(".xml"):
                    out_file = out_file.with_suffix(".xml")
                    out_file.write_bytes(r.content)
                elif "json" in content_type or path.endswith(".json"):
                    out_file = out_file.with_suffix(".json")
                    out_file.write_bytes(r.content)
                elif "text" in content_type:
                    out_file = out_file.with_suffix(".txt")
                    out_file.write_bytes(r.content)
                else:
                    out_file = out_file.with_suffix(".bin")
                    out_file.write_bytes(r.content)

                print(f"  200 {path:35s} {size:>8} bytes  [{content_type[:40]}]  -> {out_file.name}")
                results[domain][path] = {"status": status, "size": size, "content_type": content_type}
            else:
                print(f"  {status} {path}")
                results[domain][path] = {"status": status}

        except Exception as e:
            print(f"  ERR {path}: {e}")
            results[domain][path] = {"error": str(e)}

# Save summary
summary_path = RAW / "probe_summary.json"
summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"\nSummary saved -> {summary_path.relative_to(REPO_ROOT)}")
print("Done.")

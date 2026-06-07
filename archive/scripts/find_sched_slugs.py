"""Find the correct sched.com subdomain slugs for every TCSW year via Wayback CDX."""
import requests, json, re

# Query Wayback for all tcsw*.sched.com URLs
r = requests.get(
    "http://web.archive.org/cdx/search/cdx",
    params={
        "url": "*.sched.com/list/descriptions",
        "output": "json",
        "fl": "timestamp,original",
        "filter": "original:.*tcsw.*",
        "limit": 100,
        "collapse": "original",
    },
    timeout=25,
)
print("Status:", r.status_code, "Len:", len(r.text))
if r.text.strip():
    try:
        data = r.json()
        for row in data[1:]:
            print(row[0][:8], row[1])
    except Exception as e:
        print("Parse error:", e)
        print(r.text[:500])
else:
    print("Empty response")
    # Try alternate approach — check known slugs directly
    slugs = ["tcsw18","tcsw2018","tcsw19","tcsw2019","tcsw20","tcsw2020",
             "tcsw21","tcsw2021","tcsw22","tcsw2022","tcsw23","tcsw2023",
             "tcsw24","tcsw2024","tcsw25","tcsw2025","tcsw2026","tcsw26",
             "tcstartupweek2023","tcstartupweek2024","twincitiesstartupweek2023"]
    print("\nChecking slugs directly...")
    for slug in slugs:
        try:
            resp = requests.get(
                f"https://{slug}.sched.com/list/descriptions",
                headers={"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip, deflate"},
                timeout=8, allow_redirects=False,
            )
            final = requests.get(
                f"https://{slug}.sched.com/",
                headers={"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip, deflate"},
                timeout=8, allow_redirects=True,
            )
            print(f"  {slug}: /list/descriptions={resp.status_code}  homepage_final={final.url[:50]}")
        except Exception as e:
            print(f"  {slug}: ERR {str(e)[:40]}")

import requests
import time
from pathlib import Path

LOGOS_DIR = Path(__file__).resolve().parent.parent / "research" / "data_collection" / "sponsors" / "logos"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}

items = [
    # Official press kit / newsroom CDN sources
    ("https://news.3m.com/image/3M-logo.png", "3M_logo.png", "3M"),
    ("https://www.jpmorganchase.com/content/dam/jpmc/jpmorgan-chase-and-co/logos/jpmc-logo-color.png", "JPMORGAN_logo.png", "JPMorgan Chase"),
    ("https://www.cargill.com/image/1470006163800/cargill-logo.png", "CARGILL_logo.png", "Cargill"),
    ("https://www.trinet.com/content/dam/trinet/logos/trinet-logo.svg", "TRINET_logo.svg", "TriNet"),
    ("https://www.optum.com/content/dam/optum3/optum/en/resources/logos/optum-logo.svg", "OPTUM_logo.svg", "Optum"),
    ("https://groovecapital.com/wp-content/uploads/2021/01/Groove-Capital-Logo.png", "GROOVE_CAPITAL_logo.png", "Groove Capital"),
    ("https://greatnorthventures.com/wp-content/uploads/2020/01/GNV-Logo.png", "GREAT_NORTH_VENTURES_logo.png", "Great North Ventures"),
    ("https://matchstickventures.com/wp-content/uploads/2019/09/Matchstick-Logo.png", "MATCHSTICK_VENTURES_logo.png", "Matchstick Ventures"),
]

for url, fname, label in items:
    dest = LOGOS_DIR / fname
    if dest.exists() and dest.stat().st_size > 200:
        print(f"  skip  {fname}")
        continue
    time.sleep(4)
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        dest.write_bytes(r.content)
        print(f"  OK    {label} ({len(r.content) // 1024} KB) -> {fname}")
    except Exception as e:
        print(f"  ERR   {label}: {e}")

print("done")

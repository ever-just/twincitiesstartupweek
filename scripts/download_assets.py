"""
download_assets.py
==================
Downloads logos, flyers, and documents for the TCSW research repo.

Sources:
  - TCSW / BETA official logos (beta.mn, tcstartupweek.com)
  - Sched.com event imagery
  - Wikimedia Commons SVG logos for major corporate sponsors
  - Historical TCSW logos via Wayback Machine
  - Sched.com event badge/flyer images

Run:
    python3 download_assets.py                  # download everything
    python3 download_assets.py --logos           # only logos
    python3 download_assets.py --flyers          # only flyers / event imagery
    python3 download_assets.py --dry-run         # print what would download
"""

import argparse
import os
import time
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGOS_DIR = REPO_ROOT / "research" / "data_collection" / "sponsors" / "logos"
PRESS_DIR = REPO_ROOT / "research" / "data_collection" / "sponsors" / "press_releases"
DOCS_DIR = REPO_ROOT / "research" / "documents"
FLYERS_DIR = REPO_ROOT / "research" / "documents" / "flyers"
OFFICIAL_MEDIA = REPO_ROOT / "research" / "data_collection" / "official_website" / "assets"

for d in [LOGOS_DIR, PRESS_DIR, DOCS_DIR, FLYERS_DIR, OFFICIAL_MEDIA]:
    d.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def download(url: str, dest: Path, label: str = "", dry_run: bool = False) -> bool:
    """Download a URL to dest file. Returns True on success."""
    if dry_run:
        print(f"  [dry-run] would download → {dest.relative_to(REPO_ROOT)}")
        return True
    if dest.exists() and dest.stat().st_size > 500:
        print(f"  [skip]   already exists: {dest.name}")
        return True
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        size_kb = dest.stat().st_size // 1024
        print(f"  ✓ {label or dest.name} ({size_kb} KB) → {dest.relative_to(REPO_ROOT)}")
        return True
    except Exception as exc:
        print(f"  [error]  {label or url}: {exc}")
        return False


# ─── Logo assets ──────────────────────────────────────────────────────────────

LOGOS = [
    # ── Official TCSW / BETA logos ────────────────────────────────────────────
    {
        "url": "https://www.tcstartupweek.com/assets/tcsw-landing-logo-jDXWmuYM.png",
        "dest": LOGOS_DIR / "TCSW_logo_official_2026.png",
        "label": "TCSW Official Logo (2026)",
    },
    {
        "url": "https://www.beta.mn/hs-fs/hubfs/Startup%20Week/TCSW_Logo_Navy.png",
        "dest": LOGOS_DIR / "TCSW_logo_navy.png",
        "label": "TCSW Logo Navy",
    },
    {
        "url": "https://www.beta.mn/hubfs/Beta%20Logos/BETA%20Logo.svg",
        "dest": LOGOS_DIR / "BETA_logo.svg",
        "label": "BETA.MN Logo (SVG)",
    },
    {
        "url": "https://www.beta.mn/hs-fs/hubfs/Beta%20Logos/Primary_DkGray-Orange.png",
        "dest": LOGOS_DIR / "BETA_logo_primary.png",
        "label": "BETA.MN Primary Logo",
    },
    {
        "url": "https://www.beta.mn/hs-fs/hubfs/Beta%20Logos/Beta-grey.png",
        "dest": LOGOS_DIR / "BETA_logo_grey.png",
        "label": "BETA.MN Grey Logo",
    },
    {
        "url": "https://www.beta.mn/hs-fs/hubfs/Beta%20Logos/TCSW-grey.png",
        "dest": LOGOS_DIR / "TCSW_logo_grey.png",
        "label": "TCSW Grey Logo",
    },
    # ── Sched.com event icons (TCSW branded) ─────────────────────────────────
    {
        "url": "https://cdn.sched.co/assets/tcsw2023/img/apple-touch-icon-xlarge.png",
        "dest": LOGOS_DIR / "TCSW_2023_event_icon.png",
        "label": "TCSW 2023 Event Icon",
    },
    {
        "url": "https://cdn.sched.co/assets/tcsw2025/img/apple-touch-icon-xlarge.png",
        "dest": LOGOS_DIR / "TCSW_2025_event_icon.png",
        "label": "TCSW 2025 Event Icon",
    },
    {
        "url": "https://cdn.sched.co/assets/tcsw2022/img/apple-touch-icon-xlarge.png",
        "dest": LOGOS_DIR / "TCSW_2022_event_icon.png",
        "label": "TCSW 2022 Event Icon",
    },
    # ── Wikimedia Commons: major sponsor SVG logos (free/public domain) ───────
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Target_logo.svg",
        "dest": LOGOS_DIR / "TARGET_logo.svg",
        "label": "Target (Wikimedia Commons)",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/5b/3M_wordmark.svg",
        "dest": LOGOS_DIR / "3M_logo.svg",
        "label": "3M (Wikimedia Commons)",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg",
        "dest": LOGOS_DIR / "MICROSOFT_logo.svg",
        "label": "Microsoft (Wikimedia Commons)",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg",
        "dest": LOGOS_DIR / "AWS_logo.svg",
        "label": "Amazon Web Services (Wikimedia Commons)",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/af/J._P._Morgan_Logo_2008_1.svg",
        "dest": LOGOS_DIR / "JPMORGAN_logo.svg",
        "label": "JPMorgan (Wikimedia Commons)",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e7/Cargill_logo.svg",
        "dest": LOGOS_DIR / "CARGILL_logo.svg",
        "label": "Cargill (Wikimedia Commons)",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a0/TriNet_logo.svg",
        "dest": LOGOS_DIR / "TRINET_logo.svg",
        "label": "TriNet (Wikimedia Commons)",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/6/6a/UnitedHealth_Group_logo.svg",
        "dest": LOGOS_DIR / "OPTUM_UNITEDHEALTH_logo.svg",
        "label": "UnitedHealth / Optum parent (Wikimedia Commons)",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
        "dest": LOGOS_DIR / "AMAZON_logo.svg",
        "label": "Amazon (Wikimedia Commons)",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
        "dest": LOGOS_DIR / "GOOGLE_logo.svg",
        "label": "Google (Wikimedia Commons)",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/51/Minnesota_Twins_Logo.svg",
        "dest": LOGOS_DIR / "MINNESOTA_TWINS_logo.svg",
        "label": "Minnesota Twins (Wikimedia Commons) — venue ref",
    },
]

# ─── Official TCSW site assets ───────────────────────────────────────────────

SITE_ASSETS = [
    # Favicon / site icon from official TCSW site
    {
        "url": "https://www.tcstartupweek.com/favicon.ico",
        "dest": OFFICIAL_MEDIA / "tcsw_favicon.ico",
        "label": "TCSW Favicon",
    },
    # BETA.MN site imagery
    {
        "url": "https://www.beta.mn/hs-fs/hubfs/2020%20Website/Imagery/Events28-1.png",
        "dest": OFFICIAL_MEDIA / "BETA_events_photo.png",
        "label": "BETA.MN Events Photo",
    },
    {
        "url": "https://www.beta.mn/hs-fs/hubfs/2020%20Website/Imagery/OriginalFounders-1.png",
        "dest": OFFICIAL_MEDIA / "BETA_original_founders.png",
        "label": "BETA.MN Original Founders Photo",
    },
]

# ─── Historical TCSW logos via Wayback Machine ───────────────────────────────

WAYBACK_ASSETS = [
    # 2023 sched.com social banner
    {
        "url": "https://web.archive.org/web/20231001000000*/tcsw2023.sched.com",
        "dest": None,  # meta-only entry, just for reference
        "label": "TCSW 2023 Sched Social Banner (Wayback)",
    },
]


def download_logos(dry_run: bool = False) -> None:
    print("\n── Downloading logos ──")
    for item in LOGOS:
        download(item["url"], item["dest"], item["label"], dry_run)
        time.sleep(0.3)


def download_site_assets(dry_run: bool = False) -> None:
    print("\n── Downloading site assets ──")
    for item in SITE_ASSETS:
        download(item["url"], item["dest"], item["label"], dry_run)
        time.sleep(0.3)


def write_asset_index(dry_run: bool = False) -> None:
    """Write an index markdown listing all downloaded assets with metadata."""
    index_lines = [
        "# Downloaded Asset Index",
        f"*Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}*\n",
        "## Logos\n",
        "| File | Source | Status |",
        "|---|---|---|",
    ]
    for item in LOGOS:
        dest = item["dest"]
        if dest is None:
            continue
        status = "✓ Downloaded" if (dest.exists() and not dry_run) else "⏳ Pending"
        rel = dest.relative_to(REPO_ROOT)
        index_lines.append(f"| `{rel}` | {item['label']} | {status} |")

    index_lines += [
        "\n## Site Assets\n",
        "| File | Source | Status |",
        "|---|---|---|",
    ]
    for item in SITE_ASSETS:
        dest = item["dest"]
        status = "✓ Downloaded" if (dest.exists() and not dry_run) else "⏳ Pending"
        rel = dest.relative_to(REPO_ROOT)
        index_lines.append(f"| `{rel}` | {item['label']} | {status} |")

    index_lines += [
        "\n## Notes",
        "- Wikimedia Commons SVG logos are public domain / freely licensed.",
        "- BETA.MN and TCSW logos are © their respective owners; stored for research/reference only.",
        "- Do not redistribute without permission.",
    ]

    index_path = LOGOS_DIR / "ASSET_INDEX.md"
    if not dry_run:
        index_path.write_text("\n".join(index_lines), encoding="utf-8")
        print(f"\n  ✓ Asset index → {index_path.relative_to(REPO_ROOT)}")
    else:
        print(f"\n  [dry-run] would write asset index → {index_path.relative_to(REPO_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="TCSW Asset Downloader")
    parser.add_argument("--logos", action="store_true", help="Download logos only")
    parser.add_argument("--flyers", action="store_true", help="Download site assets only")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    dry_run = args.dry_run
    run_all = not args.logos and not args.flyers

    if dry_run:
        print("DRY RUN — no files will be written\n")

    if run_all or args.logos:
        download_logos(dry_run)

    if run_all or args.flyers:
        download_site_assets(dry_run)

    write_asset_index(dry_run)
    print("\n✅ Done.")


if __name__ == "__main__":
    main()

"""
download_hidden_pdfs.py
=======================
Downloads the BETA.MN HubSpot PDFs found via Wayback CDX.
Deduplicates URLs, downloads live copies, extracts text for quantitative data.
"""

import asyncio, re, json
from pathlib import Path
from urllib.parse import unquote
import aiohttp

REPO = Path(__file__).resolve().parent.parent
PDF_DIR = REPO / "data" / "quantitative" / "pdfs"
PDF_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
}

# Confirmed live PDF URLs from Wayback CDX hunt (deduped, no ?hsLang= variants)
PDF_URLS = [
    # TCSW Recaps
    ("TCSW_2015_year_end_review",  "https://www.beta.mn/hubfs/2020%20Website/How%20to%20Help%20PDFs/2015%20Year%20End%20Review%20(3).pdf"),
    ("TCSW_2017_recap",            "https://www.beta.mn/hubfs/2020%20Website/How%20to%20Help%20PDFs/TCSW17%20Recap.pdf"),
    ("TCSW_2018_recap",            "https://www.beta.mn/hubfs/2020%20Website/How%20to%20Help%20PDFs/TCSW18-recap_ALL_web.pdf"),
    ("TCSW_2018_recap_alt",        "https://www.beta.mn/hubfs/2020%20Website/How%20to%20Help%20PDFs/Beta%202018%20Recap.pdf"),
    ("TCSW_2019_recap",            "https://www.beta.mn/hubfs/2020%20Website/How%20to%20Help%20PDFs/TCSW%202019%20Recap.pdf"),
    ("TCSW_2019_recap_alt",        "https://www.beta.mn/hubfs/2020%20Website/How%20to%20Help%20PDFs/BETA%202019%20Recap.pdf"),
    ("TCSW_2020_recap",            "https://www.beta.mn/hubfs/TCSW-Recap-2020.pdf"),
    ("TCSW_2021_recap",            "https://www.beta.mn/hubfs/TCSW%202021%20Recap.pdf"),
    # BETA Annual Reports / Recaps
    ("BETA_2015_year_end",         "https://www.beta.mn/hubfs/2020%20Website/How%20to%20Help%20PDFs/2015%20Year%20End%20Review%20(3).pdf"),
    ("BETA_2016_annual_report",    "https://www.beta.mn/hubfs/2020%20Website/How%20to%20Help%20PDFs/Beta.MN%202016%20Annaul%20Report%20(1).pdf"),
    ("BETA_2017_review",           "https://www.beta.mn/hubfs/2020%20Website/How%20to%20Help%20PDFs/Beta.mn%202017%20Review.pdf"),
    ("BETA_2020_recap",            "https://www.beta.mn/hubfs/BETA-Recap-2020.pdf"),
    ("BETA_2021_recap",            "https://www.beta.mn/hubfs/BETA-Recap-2021.pdf"),
    ("BETA_2022_metrics",          "https://www.beta.mn/hubfs/BETA-BRAND-2022-METRICS.pdf"),
    # Try additional years / paths
    ("TCSW_2022_recap_try",        "https://www.beta.mn/hubfs/TCSW-Recap-2022.pdf"),
    ("TCSW_2023_recap_try",        "https://www.beta.mn/hubfs/TCSW-Recap-2023.pdf"),
    ("TCSW_2024_recap_try",        "https://www.beta.mn/hubfs/TCSW-Recap-2024.pdf"),
    ("BETA_2023_recap_try",        "https://www.beta.mn/hubfs/BETA-Recap-2023.pdf"),
    ("BETA_2024_recap_try",        "https://www.beta.mn/hubfs/BETA-Recap-2024.pdf"),
    ("sponsor_prospectus_2024",    "https://www.beta.mn/hubfs/TCSW-2024-Sponsorship-Prospectus.pdf"),
    ("sponsor_prospectus_2025",    "https://www.beta.mn/hubfs/TCSW-2025-Sponsorship-Prospectus.pdf"),
    ("sponsor_prospectus_try2",    "https://www.beta.mn/hubfs/TCSW-Sponsorship-Prospectus.pdf"),
    ("impact_report_try",          "https://www.beta.mn/hubfs/BETA-Impact-Report.pdf"),
]

SEM = asyncio.Semaphore(4)


async def download_pdf(session, label, url):
    async with SEM:
        try:
            async with session.get(
                url, headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=20),
                ssl=False, allow_redirects=True
            ) as r:
                if r.status == 200:
                    ct = r.headers.get("Content-Type", "")
                    if "pdf" in ct or "octet" in ct or url.endswith(".pdf"):
                        body = await r.read()
                        out = PDF_DIR / f"{label}.pdf"
                        out.write_bytes(body)
                        print(f"  ✓ {label}: {len(body):,} bytes → {out.name}")
                        return str(out), len(body)
                    else:
                        text = await r.text(errors="ignore")
                        print(f"  ✗ {label}: not PDF ({ct[:40]})")
                        return None, 0
                else:
                    print(f"  ✗ {label}: HTTP {r.status}")
                    return None, 0
        except Exception as e:
            print(f"  ✗ {label}: {e}")
            return None, 0


async def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfminer or pypdf."""
    try:
        import pdfminer.high_level as pml
        import io
        text = pml.extract_text(str(pdf_path))
        return text
    except ImportError:
        pass
    try:
        import pypdf
        reader = pypdf.PdfReader(str(pdf_path))
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    except ImportError:
        pass
    return ""


def extract_numbers(text, label):
    """Pull all quantitative data from PDF text."""
    results = {
        "label": label,
        "attendees":   re.findall(r'(\d[\d,]+)\+?\s*(?:attendees?|participants?|people|entrepreneurs?|founders?)', text, re.I),
        "events":      re.findall(r'(\d[\d,]+)\+?\s*(?:events?|sessions?|talks?|workshops?)', text, re.I),
        "speakers":    re.findall(r'(\d[\d,]+)\+?\s*speakers?', text, re.I),
        "sponsors":    re.findall(r'(\d[\d,]+)\+?\s*sponsors?', text, re.I),
        "startups":    re.findall(r'(\d[\d,]+)\+?\s*(?:startups?|companies|ventures?)', text, re.I),
        "investors":   re.findall(r'(\d[\d,]+)\+?\s*investors?', text, re.I),
        "volunteers":  re.findall(r'(\d[\d,]+)\+?\s*volunteers?', text, re.I),
        "revenue":     re.findall(r'\$\s*([\d,]+(?:\.\d+)?)\s*(?:K|M|thousand|million)?', text, re.I),
        "jobs":        re.findall(r'(\d[\d,]+)\+?\s*jobs?', text, re.I),
        "days":        re.findall(r'(\d+)[\s-]*days?', text, re.I),
        "years":       re.findall(r'(\d+)(?:th|st|nd|rd)\s+(?:annual|year)', text, re.I),
        "venues":      re.findall(r'(\d+)\+?\s*venues?', text, re.I),
        "tracks":      re.findall(r'(\d+)\+?\s*tracks?', text, re.I),
        "cities":      re.findall(r'(\d+)\s*cities', text, re.I),
        "raised":      re.findall(r'\$\s*([\d,]+(?:\.\d+)?)\s*(?:M|million)\s*(?:raised|in funding|funded)', text, re.I),
        "prize_money": re.findall(r'\$\s*([\d,]+(?:\.\d+)?)\s*(?:in prizes?|prize money|awarded)', text, re.I),
        "text_preview": text[:800] if text else "",
    }
    # Trim to top unique values
    for k in list(results.keys()):
        if isinstance(results[k], list):
            results[k] = list(dict.fromkeys(results[k]))[:8]
    return results


async def main():
    print("=" * 60)
    print("DOWNLOADING BETA.MN HIDDEN PDFs")
    print("=" * 60)

    downloaded = []
    connector = aiohttp.TCPConnector(limit=4, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [download_pdf(session, label, url) for label, url in PDF_URLS]
        results = await asyncio.gather(*tasks)

    for (label, url), (path, size) in zip(PDF_URLS, results):
        if path:
            downloaded.append({"label": label, "url": url, "path": path, "size": size})

    print(f"\n✓ Downloaded {len(downloaded)}/{len(PDF_URLS)} PDFs")

    # ── Extract text + quantitative data from each PDF ──────────
    print("\n[Extract] Pulling quantitative data from PDFs...")

    # Install pdfminer if needed
    try:
        import pdfminer.high_level
    except ImportError:
        import subprocess
        subprocess.run(["pip3", "install", "pdfminer.six", "-q"], capture_output=True)

    all_quant = []
    for item in downloaded:
        pdf_path = Path(item["path"])
        text = await extract_text_from_pdf(pdf_path)
        if text:
            quant = extract_numbers(text, item["label"])
            quant["url"] = item["url"]
            quant["size_bytes"] = item["size"]
            all_quant.append(quant)
            print(f"\n  [{item['label']}]")
            for k in ["attendees","events","speakers","sponsors","startups","revenue","prize_money","raised"]:
                if quant.get(k):
                    print(f"    {k}: {quant[k][:5]}")
        else:
            print(f"  [{item['label']}]: could not extract text")

    # Save results
    out_file = REPO / "data" / "quantitative" / "pdf_quantitative_data.json"
    out_file.write_text(json.dumps(all_quant, indent=2, default=str), encoding="utf-8")
    print(f"\n✓ Saved PDF data: {out_file}")
    print(f"  {len(all_quant)} PDFs with extractable text")
    print(f"  PDFs saved to: {PDF_DIR}")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Extract session, speaker, and sponsor data from sched.com archives
for all available TCSW years (2015, 2016, 2017, 2018, 2019, 2023)
"""

import asyncio
import aiohttp
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import sys

# Confirmed sched.com URLs
SCHED_URLS = {
    2015: "https://twincitiesstartupweek2015.sched.com",
    2016: "https://twincitiesstartupweek2016a.sched.com",
    2017: "https://twincitiesstartupweek2017.sched.com",
    2018: "https://tcsw18.sched.com",
    2019: "https://tcsw19.sched.com",
    2023: "https://tcsw2023.sched.com",
}

OUTPUT_DIR = Path("/Users/cloudaistudio/Desktop/twincitiesstartupweek/BACKGROUND/sessions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def fetch(session, url, timeout=15):
    """Fetch URL with error handling"""
    try:
        async with session.get(url, timeout=timeout) as r:
            if r.status == 200:
                return await r.text()
            else:
                print(f"  ⚠️  {url}: HTTP {r.status}")
                return None
    except asyncio.TimeoutError:
        print(f"  ⚠️  {url}: Timeout")
        return None
    except Exception as e:
        print(f"  ⚠️  {url}: {str(e)[:50]}")
        return None


async def extract_speakers(session, year, base_url):
    """Extract speakers from sched.com directory"""
    print(f"\n[{year}] Extracting speakers...", end="", flush=True)
    
    url = f"{base_url}/directory/speakers"
    html = await fetch(session, url)
    if not html:
        print(" FAILED")
        return []
    
    soup = BeautifulSoup(html, "lxml")
    speakers = []
    
    # Look for speaker cards/entries
    for item in soup.find_all(class_=["speaker", "person", "attendee"]):
        name = item.find(class_=["name", "title"])
        if name:
            speaker_data = {
                "name": name.get_text(strip=True),
                "year": year,
            }
            
            # Try to extract company
            company = item.find(class_=["company", "organization"])
            if company:
                speaker_data["company"] = company.get_text(strip=True)
            
            # Try to extract bio/title
            bio = item.find(class_=["bio", "description", "title"])
            if bio:
                speaker_data["bio"] = bio.get_text(strip=True)
            
            speakers.append(speaker_data)
    
    print(f" ✓ {len(speakers)} speakers")
    return speakers


async def extract_sessions(session, year, base_url):
    """Extract sessions from sched.com"""
    print(f"[{year}] Extracting sessions...", end="", flush=True)
    
    url = f"{base_url}/"
    html = await fetch(session, url)
    if not html:
        print(" FAILED")
        return []
    
    soup = BeautifulSoup(html, "lxml")
    sessions = []
    
    # Look for session entries
    for item in soup.find_all(class_=["session", "event", "item"]):
        title = item.find(class_=["title", "name"])
        if title:
            session_data = {
                "title": title.get_text(strip=True),
                "year": year,
            }
            
            # Try to extract time
            time_elem = item.find(class_=["time", "when", "datetime"])
            if time_elem:
                session_data["time"] = time_elem.get_text(strip=True)
            
            # Try to extract venue
            venue = item.find(class_=["venue", "location", "room"])
            if venue:
                session_data["venue"] = venue.get_text(strip=True)
            
            # Try to extract speaker
            speaker = item.find(class_=["speaker", "presenter"])
            if speaker:
                session_data["speaker"] = speaker.get_text(strip=True)
            
            sessions.append(session_data)
    
    print(f" ✓ {len(sessions)} sessions")
    return sessions


async def extract_sponsors(session, year, base_url):
    """Extract sponsors from sched.com directory"""
    print(f"[{year}] Extracting sponsors...", end="", flush=True)
    
    url = f"{base_url}/directory/sponsors"
    html = await fetch(session, url)
    if not html:
        print(" SKIPPED (not available)")
        return []
    
    soup = BeautifulSoup(html, "lxml")
    sponsors = []
    
    # Look for sponsor entries
    for item in soup.find_all(class_=["sponsor", "partner", "exhibitor"]):
        name = item.find(class_=["name", "title"])
        if name:
            sponsor_data = {
                "name": name.get_text(strip=True),
                "year": year,
            }
            
            # Try to extract tier/level
            tier = item.find(class_=["tier", "level", "type"])
            if tier:
                sponsor_data["tier"] = tier.get_text(strip=True)
            
            sponsors.append(sponsor_data)
    
    print(f" ✓ {len(sponsors)} sponsors")
    return sponsors


async def extract_year(session, year, base_url):
    """Extract all data for a single year"""
    print(f"\n{'='*60}")
    print(f"TCSW {year}")
    print(f"{'='*60}")
    
    speakers = await extract_speakers(session, year, base_url)
    sessions = await extract_sessions(session, year, base_url)
    sponsors = await extract_sponsors(session, year, base_url)
    
    # Save individual files
    year_data = {
        "year": year,
        "url": base_url,
        "speakers": speakers,
        "sessions": sessions,
        "sponsors": sponsors,
        "stats": {
            "total_speakers": len(speakers),
            "total_sessions": len(sessions),
            "total_sponsors": len(sponsors),
        }
    }
    
    output_file = OUTPUT_DIR / f"sched_{year}_complete.json"
    output_file.write_text(json.dumps(year_data, indent=2))
    print(f"\n✓ Saved: {output_file.name}")
    
    return year_data


async def main():
    """Main extraction pipeline"""
    print("\n" + "="*60)
    print("SCHED.COM DATA EXTRACTION")
    print("Twin Cities Startup Week (2015-2023)")
    print("="*60)
    
    all_data = {}
    
    async with aiohttp.ClientSession() as session:
        for year in sorted(SCHED_URLS.keys()):
            base_url = SCHED_URLS[year]
            await asyncio.sleep(1.0)  # Rate limiting
            
            try:
                year_data = await extract_year(session, year, base_url)
                all_data[year] = year_data
            except Exception as e:
                print(f"✗ Error extracting {year}: {e}")
    
    # Save master file
    master_file = OUTPUT_DIR / "sched_all_years_complete.json"
    master_file.write_text(json.dumps(all_data, indent=2))
    print(f"\n✓ Master file saved: {master_file.name}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    total_speakers = sum(d["stats"]["total_speakers"] for d in all_data.values())
    total_sessions = sum(d["stats"]["total_sessions"] for d in all_data.values())
    total_sponsors = sum(d["stats"]["total_sponsors"] for d in all_data.values())
    
    print(f"Years extracted: {len(all_data)}")
    print(f"Total speakers: {total_speakers}")
    print(f"Total sessions: {total_sessions}")
    print(f"Total sponsors: {total_sponsors}")
    
    for year in sorted(all_data.keys()):
        stats = all_data[year]["stats"]
        print(f"  {year}: {stats['total_sessions']} sessions, {stats['total_speakers']} speakers, {stats['total_sponsors']} sponsors")


if __name__ == "__main__":
    asyncio.run(main())

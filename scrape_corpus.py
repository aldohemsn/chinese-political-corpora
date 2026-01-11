import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re

BASE_URL = "https://zh.wikisource.org"
PORTAL_URL = "https://zh.wikisource.org/wiki/Portal:%E4%B8%AD%E5%8D%8E%E4%BA%BA%E6%B0%91%E5%85%B1%E5%92%8C%E5%9B%BD%E5%9B%BD%E5%8A%A1%E9%99%A2%E6%94%BF%E5%BA%9C%E5%B7%A5%E4%BD%9C%E6%8A%A5%E5%91%8A"
OUTPUT_FILE = "government_work_reports.jsonl"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, "lxml")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_report_links(soup):
    links = []
    # The structure of the portal page. We look for links relative to Government Work Reports.
    # Usually they are listed by year.
    content_div = soup.find("div", {"class": "mw-parser-output"})
    if not content_div:
        print("Could not find content div")
        return []

    # Find all links that look like work reports
    # Heuristic: link text contains "政府工作报告"
    for a in content_div.find_all("a", href=True):
        text = a.get_text().strip()
        href = a['href']
        
        # Filter for report links. 
        # Note: Some might be "1954年..." or "2024年..."
        if "政府工作报告" in text and not "Portal" in href:
             # Check if it is a red link (page doesn't exist)
            if "redlink=1" in href:
                continue
            
            full_url = BASE_URL + href if href.startswith("/") else href
            links.append({
                "title": text,
                "url": full_url
            })
            
    # Remove duplicates
    unique_links = {v['url']: v for v in links}.values()
    return list(unique_links)

def scrape_report_content(url):
    soup = get_soup(url)
    if not soup:
        return None
    
    # Wikisource content is usually in a div with specific classes
    # We want to extract the main text.
    # Often it is in .mw-parser-output
    content_div = soup.find("div", {"class": "mw-parser-output"})
    
    if not content_div:
        return ""
        
    # Remove some non-content elements if necessary (e.g., navigation templates)
    # This is a basic cleaning
    for tag in content_div.select(".mw-editsection, .navbox, table"):
        tag.decompose()
        
    text = content_div.get_text(separator="\n").strip()
    return text

def main():
    print(f"Fetching portal: {PORTAL_URL}")
    soup = get_soup(PORTAL_URL)
    if not soup:
        print("Failed to fetch portal page.")
        return

    links = extract_report_links(soup)
    print(f"Found {len(links)} potential reports.")

    reports = []
    
    # Sort links by title if possible to have chronological order roughly (optional)
    # links.sort(key=lambda x: x['title'])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for i, link in enumerate(links):
            print(f"[{i+1}/{len(links)}] Scraping: {link['title']} - {link['url']}")
            content = scrape_report_content(link['url'])
            
            if content:
                record = {
                    "title": link['title'],
                    "url": link['url'],
                    "content": content,
                    "year": re.search(r"\d{4}", link['title']).group(0) if re.search(r"\d{4}", link['title']) else None
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                f.flush()
            else:
                print(f"  Empty content for {link['title']}")
            
            # Be polite
            time.sleep(1)

    print(f"Done. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

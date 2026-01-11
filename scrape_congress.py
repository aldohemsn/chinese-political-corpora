import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re

LINKS_FILE = "cpc_congress_links.json"
OUTPUT_FILE = "cpc_congress_reports.jsonl"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        # Handle redirects or errors
        if response.status_code == 404:
            print(f"404 Not Found: {url}")
            return None
        response.raise_for_status()
        return BeautifulSoup(response.content, "lxml")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_report_content(url):
    soup = get_soup(url)
    if not soup:
        return None
    
    content_div = soup.find("div", {"class": "mw-parser-output"})
    if not content_div:
        return ""
        
    # Cleaning
    for tag in content_div.select(".mw-editsection, .navbox, table, .hatnote, .metadata"):
        tag.decompose()
        
    text = content_div.get_text(separator="\n").strip()
    return text

def infer_congress_audit(title):
    cn_nums = {'一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '十':10}
    
    def parse_chinese_num(s):
        if not s: return 0
        if s.isdigit(): return int(s)
        val = 0
        if s.startswith('十'):
            val += 10
            if len(s) > 1:
                val += cn_nums.get(s[1], 0)
        elif '十' in s:
            parts = s.split('十')
            val += cn_nums.get(parts[0], 0) * 10
            if len(parts) > 1 and parts[1]:
                val += cn_nums.get(parts[1], 0)
        else:
            val = cn_nums.get(s, 0)
        return val

    # Pattern 1: 第XX次
    match = re.search(r"第([一二三四五六七八九十]+)次", title)
    if match:
        return parse_chinese_num(match.group(1))
        
    # Pattern 2: (XX大) or （XX大）
    match = re.search(r"[\(（]([一二三四五六七八九十]+)大[\)）]", title)
    if match:
        return parse_chinese_num(match.group(1))

    # Pattern 3: explicit full match checks avoiding partials
    if "一大" in title and "十一" not in title and "二十一" not in title: return 1
    if "二大" in title and "十二" not in title and "二十二" not in title: return 2
    if "三大" in title and "十三" not in title and "二十三" not in title: return 3
    if "四大" in title and "十四" not in title and "二十四" not in title: return 4
    if "五大" in title and "十五" not in title and "二十五" not in title: return 5
    
    return None

def main():
    if not os.path.exists(LINKS_FILE):
        print(f"File {LINKS_FILE} not found.")
        return

    with open(LINKS_FILE, "r") as f:
        links = json.load(f)

    print(f"Found {len(links)} reports to process.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for i, link in enumerate(links):
            print(f"[{i+1}/{len(links)}] Scraping: {link['title']}")
            
            content = scrape_report_content(link['url'])
            congress_num = infer_congress_audit(link['title'])
            
            if content:
                record = {
                    "title": link['title'],
                    "url": link['url'],
                    "content": content,
                    "congress": congress_num,
                    "type": "cpc_congress_report"
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                f.flush()
            else:
                print(f"  Empty content or failed fetch for {link['title']}")
            
            time.sleep(1)

    print(f"Done. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

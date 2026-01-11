import requests
from bs4 import BeautifulSoup
import re
import json
import duckdb
import time

BASE_URL = "https://language.chinadaily.com.cn/19thcpcnationalcongress/2017-10/16/content_32684880.htm"
# Pattern seems to be content_32684880.htm, content_32684880_2.htm, ...

def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def fetch_page(url):
    print(f"Fetching {url}")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        r.encoding = 'utf-8' # Force utf-8
        return r.text
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_english_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # The content seems to be in a specific div. 
    # Based on Chinadaily structure, often #Content or .main_content
    # Let's try to just grab paragraphs in the main body.
    # Inspecting the chunk view: 
    # The text is just paragraphs.
    
    # Try generic 'p' tags inside the main content area if we can find it.
    # Usually 'div#Content' or just standard paragraphs.
    
    # Let's try to target the main content div to avoid nav links.
    # Common IDs: 'Content', 'div_currpage', 'art_content'
    main_div = soup.find(id="Content") or soup.find(class_="main_content") or soup.find(id="div_currpage")
    
    if not main_div:
        # Fallback to body
        main_div = soup.body
        
    ps = main_div.find_all('p')
    
    english_paragraphs = []
    
    for p in ps:
        text = p.get_text().strip()
        if not text:
            continue
            
        # Check if it is the "XII. Making Party..." link or similar nav junk
        if "chinadaily.com.cn" in text:
            continue
            
        # Heuristic: mostly English.
        # If it has significant Chinese, skip.
        if has_chinese(text):
            # Sometimes a line might have both? "Title (Chinese title)"
            # If it's mixed, we might lose it. 
            # But the user provided "Parallel text". usually they are separate paragraphs.
            # Let's assume separate paragraphs for now.
            continue
            
        english_paragraphs.append(text)
        
    return "\n".join(english_paragraphs)

def main():
    collected_text = []
    
    # Page 1
    html = fetch_page(BASE_URL)
    if not html:
        print("Failed to fetch page 1")
        return

    collected_text.append(extract_english_from_html(html))
    
    # Pages 2 ... N
    # We don't know N. We loop until 404.
    page_num = 2
    while True:
        url = BASE_URL.replace(".htm", f"_{page_num}.htm")
        html = fetch_page(url)
        if not html:
            break
        
        text = extract_english_from_html(html)
        if text:
            collected_text.append(text)
        
        page_num += 1
        time.sleep(0.5)
        
    full_text = "\n".join(collected_text)
    
    print(f"Extracted {len(full_text)} characters.")
    
    # Save to JSONL
    record = {
        "title": "Firmly March on the Path of Socialism with Chinese Characteristics and Strive to Complete the Building of a Moderately Prosperous Society in All Respects (18th National Congress)",
        "url": BASE_URL,
        "content": full_text,
        "congress": 18,
        "type": "cpc_congress_report",
        "reference": "Author: Hu Jintao, Agency: China Daily (Bilingual Source), URL: " + BASE_URL
    }
    
    outfile = "report_18_english.jsonl"
    with open(outfile, 'w') as f:
        f.write(json.dumps(record) + "\n")
        

    # Update DB
    con = duckdb.connect("corpus.duckdb")
    print("Updating DuckDB...")
    try:
        # Check if 18th exists?
        # Maybe I inserted a placeholder or failed?
        # I just won't insert duplicates if I can help it, but simple Insert is fine.
        # I can just DELETE WHERE congress=18 first to be safe.
        con.execute("DELETE FROM reports WHERE congress=18 AND type='cpc_congress_report'")
        con.execute(f"INSERT INTO reports (title, url, content, congress, type, reference) SELECT title, url, content, congress, type, reference FROM read_json_auto('{outfile}')")
        print("Success.")
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    main()

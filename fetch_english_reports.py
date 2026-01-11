import requests
from bs4 import BeautifulSoup
import json
import duckdb
import os
import time

# List of reports to fetch
reports = [
    {
        "congress": 7,
        "title": "On Coalition Government (7th National Congress)",
        "url": "https://www.marxists.org/reference/archive/mao/selected-works/volume-3/mswv3_25.htm",
        "author": "Mao Zedong",
        "agency": "Marxists Internet Archive"
    },
    {
        "congress": 8,
        "title": "Political Report to the Eighth National Congress of the CPC",
        "url": "https://www.marxists.org/reference/archive/liu-shaoqi/1956/09/15.htm",
        "author": "Liu Shaoqi",
        "agency": "Marxists Internet Archive"
    },
    {
        "congress": 9,
        "title": "Report to the Ninth National Congress of the CPC",
        "url": "https://www.marxists.org/reference/archive/lin-biao/1969/04/01.htm",
        "author": "Lin Biao",
        "agency": "Marxists Internet Archive"
    },
    {
        "congress": 10,
        "title": "Report to the Tenth National Congress of the CPC",
        "url": "https://www.marxists.org/reference/archive/zhou-enlai/1973/08/24.htm",
        "author": "Zhou Enlai",
        "agency": "Marxists Internet Archive"
    },
    {
        "congress": 16,
        "title": "Build a Well-off Society in an All-Round Way and Create a New Situation in Building Socialism with Chinese Characteristics (16th National Congress)",
        "url": "http://www.china.org.cn/english/features/49007.htm", 
        # Note: 45461 was the feature page, 49007 is often the report text or I will try to find the text in 45461 logic if this fails.
        # Actually I will use a known working URL if possible. 
        # http://www.china.org.cn/english/features/49007.htm is likely correct for full text based on pattern.
        "author": "Jiang Zemin",
        "agency": "China.org.cn"
    },
    {
        "congress": 17,
        "title": "Hold High the Great Banner of Socialism with Chinese Characteristics and Strive for New Victories in Building a Moderately Prosperous Society in All Respects (17th National Congress)",
        "url": "http://www.china.org.cn/english/congress/229611.htm",
        "author": "Hu Jintao",
        "agency": "China.org.cn"
    },
    {
        "congress": 18,
        "title": "Firmly March on the Path of Socialism with Chinese Characteristics and Strive to Complete the Building of a Moderately Prosperous Society in All Respects (18th National Congress)",
        "url": "http://www.china.org.cn/china/18th_cpc_congress/2012-11/17/content_27137540.htm",
        "author": "Hu Jintao",
        "agency": "China.org.cn"
    },
    {
        "congress": 19,
        "title": "Secure a Decisive Victory in Building a Moderately Prosperous Society in All Respects and Strive for the Great Success of Socialism with Chinese Characteristics for a New Era (19th National Congress)",
        "url": "http://www.xinhuanet.com/english/special/2017-11/03/c_136725942.htm",
        "author": "Xi Jinping",
        "agency": "Xinhuanet"
    },
    {
        "congress": 20,
        "title": "Hold High the Great Banner of Socialism with Chinese Characteristics and Strive in Unity to Build a Modern Socialist Country in All Respects (20th National Congress)",
        "url": "https://www.fmprc.gov.cn/eng/zxxx_662805/202210/t20221025_10791908.html",
        "author": "Xi Jinping",
        "agency": "Ministry of Foreign Affairs of PRC"
    }
]

# For 16, I'm not 100% sure on 49007.htm. I found 45461.htm as feature.
# I'll check if 45461 has the text directly or links. 
# But for the script, I will try the specific URL. if it fails (404), I will skip.

RESULTS_FILE = "english_congress_reports.jsonl"

def fetch_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_text(html, agency):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    text = ""
    
    # different sites have different structures
    if "marxists.org" in agency.lower():
        # Usually in <p> tags or body. 
        # Marxists.org is simple HTML.
        # Try to find the main content.
        # Often it's just the body or a specific div.
        # We can just get all text for now and clean up.
        text = soup.get_text(separator="\n")
    elif "china.org.cn" in agency.lower():
        # Often in 'content' div or table structure (older sites).
        # Try finding a large block of text.
        # Usually classes like 'text', 'content', or just pars.
        # Fallback to get_text
        text = soup.get_text(separator="\n")
    elif "xinhuanet" in agency.lower():
        # #p-detail or .main-content
        main = soup.find(id="p-detail") or soup.find(class_="main-content")
        if main:
            text = main.get_text(separator="\n")
        else:
            text = soup.get_text(separator="\n")
    else:
        text = soup.get_text(separator="\n")

    # Basic cleaning
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def main():
    if os.path.exists(RESULTS_FILE):
        os.remove(RESULTS_FILE)

    collected = []
    
    for report in reports:
        print(f"Fetching {report['title']}...")
        html = fetch_content(report['url'])
        
        if html:
            content = extract_text(html, report['agency'])
            
            # Create record
            record = {
                "title": report['title'],
                "url": report['url'],
                "content": content,
                "congress": report['congress'],
                "type": "cpc_congress_report",
                "reference": f"Author: {report['author']}, Agency: {report['agency']}, URL: {report['url']}"
            }
            
            # Append to file
            with open(RESULTS_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
            print(f"Saved {report['title']}")
            collected.append(record)
        else:
            print(f"Failed to fetch {report['title']}")
            
        time.sleep(1) # Be polite

    # Now update DuckDB
    print("Updating DuckDB...")
    db_file = "corpus.duckdb"
    con = duckdb.connect(db_file)
    
    try:
        # Check if table exists
        # We assume 'reports' table exists from previous step.
        # We want to INSERT into it.
        # The schema in 'create_duckdb.py' was: CREATE TABLE reports AS SELECT * FROM read_json_auto(...)
        # We can append using INSERT INTO reports SELECT * FROM read_json_auto('english_congress_reports.jsonl')
        # However, the columns must match. 
        # The existing columns are: title, url, content, congress, type. (Based on jsonl).
        # My new jsonl has: title, url, content, congress, type, reference.
        # "reference" is new.
        # DuckDB handles schema evolution if we use read_json_auto? 
        # If I use INSERT INTO, it expects matching columns.
        # I might need to ALTER TABLE to add 'reference' column first.
        
        # Check columns
        columns = con.execute("DESCRIBE reports").fetchall()
        col_names = [c[0] for c in columns]
        
        if "reference" not in col_names:
            print("Adding 'reference' column to reports table...")
            con.execute("ALTER TABLE reports ADD COLUMN reference VARCHAR")
        
        # Insert
        print(f"Inserting {len(collected)} reports...")
        con.execute(f"INSERT INTO reports SELECT * FROM read_json_auto('{RESULTS_FILE}')")
        
        # Verify
        count = con.execute("SELECT count(*) FROM reports").fetchone()[0]
        print(f"Total reports in DB: {count}")
        
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    main()

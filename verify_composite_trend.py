import duckdb
import pandas as pd
import re

DB_FILE = "corpus.duckdb"

def main():
    con = duckdb.connect(DB_FILE)
    
    print("--- Searching for 'composite' in English Reports (DuckDB) ---")
    
    # Get all English content
    query = """
    SELECT year, substr(content, 1, 50) as title, content 
    FROM reports 
    WHERE (type='cpc_congress_report' OR content LIKE '%Report%')
      AND content REGEXP '[a-zA-Z]{50,}'
    ORDER BY year DESC
    """
    try:
        df = con.execute(query).df()
    except Exception as e:
        # Fallback if REGEXP fails (older duckdb versions)
        print(f"Regex query failed ({e}), trying basic LIKE...")
        query = """
        SELECT year, substr(content, 1, 50) as title, content 
        FROM reports 
        WHERE (type='cpc_congress_report' OR content LIKE '%Report%')
          AND content LIKE '% the %'
        ORDER BY year DESC
        """
        df = con.execute(query).df()

    found_count = 0
    
    for _, row in df.iterrows():
        content = row['content']
        title = row['title'].replace('\n', ' ')
        year = row['year']
        
        # Case insensitive search for 'composite'
        if 'composite' in content.lower():
            # Find all occurrences
            matches = [m.start() for m in re.finditer('composite', content, re.IGNORECASE)]
            
            for start_idx in matches:
                # Extract context window
                start = max(0, start_idx - 40)
                end = min(len(content), start_idx + 40)
                snippet = content[start:end].replace('\n', ' ')
                
                print(f"\n[FOUND] in Year: {year} | Title: {title}...")
                print(f"   Context: \"...{snippet}...\"")
                found_count += 1
                
    if found_count == 0:
        print("\nResult: No instances of 'composite' found in the English reports.")
    else:
        print(f"\nTotal instances found: {found_count}")

    con.close()

if __name__ == "__main__":
    main()

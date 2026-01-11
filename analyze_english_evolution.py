import duckdb
import pandas as pd

DB_FILE = "corpus.duckdb"

def main():
    con = duckdb.connect(DB_FILE)
    
    # Check for relevant terms in English reports
    terms = [
        "comprehensive national power",
        "composite national power",
        "national strength",
        "aggregate power",
        "overall national strength"
    ]
    
    print("--- Searching English Reports in DuckDB ---")
    
    # Get all English reports
    # Note: We filter by type or content heuristics if type isn't perfectly consistent
    query = """
    SELECT year, substr(content, 1, 50) as title, content 
    FROM reports 
    WHERE type='cpc_congress_report' 
       OR content LIKE '%National Congress%' 
       OR content LIKE '%Report to the%'
    """
    df = con.execute(query).df()
    
    found_any = False
    
    for _, row in df.iterrows():
        content = row['content']
        year = row['year']
        title = row['title'].replace('\n', ' ')
        
        # Simple heuristic to ensure it's English
        if not all(ord(c) < 128 for c in title[:10]):
            continue
            
        print(f"\nReport: {title} (Year: {year})")
        
        has_matches = False
        for term in terms:
            if term.lower() in content.lower():
                count = content.lower().count(term.lower())
                print(f"  - found '{term}': {count} times")
                
                # Show snippet
                import re
                matches = [m.start() for m in re.finditer(re.escape(term), content, re.IGNORECASE)]
                for start_idx in matches[:1]: # Show first context
                    start = max(0, start_idx - 50)
                    end = min(len(content), start_idx + len(term) + 50)
                    snippet = content[start:end].replace('\n', ' ')
                    print(f"    Context: ...{snippet}...")
                has_matches = True
                found_any = True
                
        if not has_matches:
            print("  - No matches found for target terms.")

    con.close()
    
    if not found_any:
        print("\nNo terms found in any analyzed English reports.")

if __name__ == "__main__":
    main()

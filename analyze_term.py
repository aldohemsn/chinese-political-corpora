import duckdb
import pandas as pd

DB_FILE = "corpus.duckdb"
TERM = "综合国力"

def main():
    con = duckdb.connect(DB_FILE)
    
    print(f"\n--- Government Work Reports (reports) ---")
    query_count_reports = f"""
    SELECT year, 
           (len(content) - len(replace(content, '{TERM}', ''))) / len('{TERM}') as count
    FROM reports
    WHERE content LIKE '%{TERM}%'
    ORDER BY year ASC
    """
    df_reports = con.execute(query_count_reports).df()
    
    if df_reports.empty:
        print("Term not found in Government Work Reports.")
    else:
        print(df_reports.to_string(index=False))
        print(f"Total occurrences: {df_reports['count'].sum()}")

    print(f"\n--- CPC National Congress Reports (congress_reports) ---")
    query_count_congress = f"""
    SELECT congress, 
           (len(content) - len(replace(content, '{TERM}', ''))) / len('{TERM}') as count
    FROM congress_reports
    WHERE content LIKE '%{TERM}%'
    ORDER BY congress ASC
    """
    df_congress = con.execute(query_count_congress).df()
    
    if df_congress.empty:
        print("Term not found in Congress Reports.")
    else:
        print(df_congress.to_string(index=False))
        print(f"Total occurrences: {df_congress['count'].sum()}")

    print("\n--- Context Samples (Congress Reports) ---")
    query_content = f"SELECT congress, content FROM congress_reports WHERE content LIKE '%{TERM}%' ORDER BY congress DESC"
    results = con.execute(query_content).fetchall()
    
    shown = 0
    for congress, content in results:
        import re
        matches = [m.start() for m in re.finditer(TERM, content)]
        for start_idx in matches:
            if shown >= 5: break
            window_start = max(0, start_idx - 30)
            window_end = min(len(content), start_idx + len(TERM) + 30)
            snippet = content[window_start:window_end].replace('\n', ' ')
            print(f"[Congress {congress}] ...{snippet}...")
            shown += 1
        if shown >= 5: break

    con.close()

if __name__ == "__main__":
    main()

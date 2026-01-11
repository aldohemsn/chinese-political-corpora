import duckdb
import json
import os

JSONL_FILE = "government_work_reports.jsonl"
DB_FILE = "corpus.duckdb"

def main():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    con = duckdb.connect(DB_FILE)
    
    # Create table directly from JSONL
    print(f"Loading {JSONL_FILE} into {DB_FILE}...")
    
    # DuckDB can read JSONL directly
    query = f"""
    CREATE TABLE reports AS 
    SELECT * FROM read_json_auto('{JSONL_FILE}');
    """
    
    con.execute(query)
    
    # Verify
    count = con.execute("SELECT count(*) FROM reports").fetchone()[0]
    print(f"Successfully loaded {count} reports into 'reports' table.")
    
    # Show a sample
    print("Sample report titles:")
    titles = con.execute("SELECT title, year FROM reports ORDER BY year DESC LIMIT 5").fetchall()
    for t in titles:
        print(f"- {t[0]} ({t[1]})")
        
    con.close()

if __name__ == "__main__":
    main()

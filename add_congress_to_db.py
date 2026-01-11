import duckdb
import json
import os

JSONL_FILE = "cpc_congress_reports.jsonl"
DB_FILE = "corpus.duckdb"

def main():
    con = duckdb.connect(DB_FILE)
    
    # Create separate table 'congress_reports'
    print(f"Loading {JSONL_FILE} into {DB_FILE} table 'congress_reports'...")
    
    # Drop if exists to be clean
    con.execute("DROP TABLE IF EXISTS congress_reports")
    
    query = f"""
    CREATE TABLE congress_reports AS 
    SELECT * FROM read_json_auto('{JSONL_FILE}');
    """
    
    con.execute(query)
    
    count = con.execute("SELECT count(*) FROM congress_reports").fetchone()[0]
    print(f"Successfully loaded {count} reports into 'congress_reports' table.")
    
    print("Sample titles:")
    titles = con.execute("SELECT title, congress FROM congress_reports ORDER BY congress DESC LIMIT 5").fetchall()
    for t in titles:
        print(f"- {t[0]} (Congress: {t[1]})")
        
    con.close()

if __name__ == "__main__":
    main()

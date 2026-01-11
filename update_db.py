import duckdb
import json

db_file = "corpus.duckdb"
jsonl_file = "english_congress_reports.jsonl"

con = duckdb.connect(db_file)

try:
    # 1. Check Schema
    print("Checking schema...")
    columns = con.execute("DESCRIBE reports").fetchall()
    col_names = [c[0] for c in columns]
    print(f"Current columns: {col_names}")
    
    if "reference" not in col_names:
        print("Adding 'reference' column...")
        con.execute("ALTER TABLE reports ADD COLUMN reference VARCHAR")
    
    # 2. Insert Data
    print("Inserting data...")
    # usage of read_json_auto might return cols in different order or extra cols?
    # We will explicitely map.
    # The JSONL has: title, url, content, congress, type, reference.
    # The table has: title, url, content, congress, type, year (maybe?), reference.
    # Wait, the original create_duckdb.py said: 
    #   create table reports as select * from read_json_auto...
    #   The government_work_reports.jsonl has 'year'.
    #   The cpc_congress_reports.jsonl has 'congress'.
    #   So the table likely has BOTH 'year' and 'congress' columns (sparse population)?
    #   DuckDB schema inference on UNION or loose json?
    #   Actually, create_duckdb.py only loaded government_work_reports.jsonl ??
    #   Let's check create_duckdb.py again in my memory.
    #   "loading data from a JSONL file (`government_work_reports.jsonl`)..."
    #   It didn't mention cpc_congress_reports.jsonl?
    #   I should verify if cpc reports are even in the DB yet.
    
    # If the DB only has govt reports, then I am adding cpc reports.
    # Checks:
    con.execute("SELECT count(*) FROM reports").fetchall()
    
    # We will try to INSERT with flexible column matching if possible, or build a query.
    # Safest is to read the JSONL into a temp table, then INSERT INTO reports SELECT ... mismatch cols being null.
    
    con.execute("CREATE OR REPLACE TEMP TABLE new_reports AS SELECT * FROM read_json_auto(?)", [jsonl_file])
    
    # Get cols of new_reports
    new_cols = [c[0] for c in con.execute("DESCRIBE new_reports").fetchall()]
    print(f"New data columns: {new_cols}")
    
    # Determine common columns and missing columns in target
    # We need to constructing an INSERT statement that maps fields.
    
    # For now, let's assume we just want to union them.
    # INSERT INTO reports (title, url, content, congress, type, reference)
    # SELECT title, url, content, congress, type, reference FROM new_reports
    

    if "congress" not in col_names:
        print("Adding 'congress' column...")
        con.execute("ALTER TABLE reports ADD COLUMN congress INTEGER")
    
    if "type" not in col_names:
        print("Adding 'type' column...")
        con.execute("ALTER TABLE reports ADD COLUMN type VARCHAR")
        
    con.execute("""
        INSERT INTO reports (title, url, content, congress, type, reference)
        SELECT title, url, content, congress, type, reference FROM new_reports
    """)
    
    print("Insert success.")
    
    # 3. Verify
    count = con.execute("SELECT count(*) FROM reports WHERE type='cpc_congress_report'").fetchone()[0]
    print(f"Total CPC Congress reports in DB: {count}")
    
    # Show sample
    sample = con.execute("SELECT title, congress, reference FROM reports WHERE type='cpc_congress_report' LIMIT 5").fetchall()
    for s in sample:
        print(s)

except Exception as e:
    print(f"Error: {e}")
finally:
    con.close()

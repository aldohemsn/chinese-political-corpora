import duckdb

db_file = "corpus.duckdb"
output_file = "review_18th_congress_report.txt"

con = duckdb.connect(db_file)

try:
    # Fetch the content
    result = con.execute("SELECT content FROM reports WHERE congress=18 AND type='cpc_congress_report'").fetchone()
    
    if result:
        content = result[0]
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Successfully exported 18th Congress report to {output_file}")
        print(f"Content length: {len(content)} characters")
    else:
        print("No report found for 18th Congress.")

except Exception as e:
    print(f"Error: {e}")
finally:
    con.close()

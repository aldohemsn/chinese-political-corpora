# Chinese Political Corpora

This project contains a corpus of Government Work Reports (政府工作报告) from the State Council of the People's Republic of China, scraped from Wikisource.

## Data

*   `government_work_reports.jsonl`: The raw scraped data in JSON Lines format. Each line is a JSON object with:
    *   `title`: The title of the report.
    *   `url`: The Wikisource URL.
    *   `content`: The full text content of the report.
    *   `year`: The year extracting from the title.
*   `corpus.duckdb`: A DuckDB database containing the `reports` table with the same fields.

## Scripts

1.  `scrape_corpus.py`: Scrapes the reports from the [Wikisource Portal](https://zh.wikisource.org/wiki/Portal:%E4%B8%AD%E5%8D%8E%E4%BA%BA%E6%B0%91%E5%85%B1%E5%92%8C%E5%9B%BD%E5%9B%BD%E5%8A%A1%E9%99%A2%E6%94%BF%E5%BA%9C%E5%B7%A5%E4%BD%9C%E6%8A%A5%E5%91%8A).
2.  `create_duckdb.py`: Loads the JSONL file into a DuckDB database.

## Usage

You can query the DuckDB database using the `duckdb` CLI or Python client:

```python
import duckdb

con = duckdb.connect("corpus.duckdb")
df = con.execute("SELECT * FROM reports WHERE year = '2024'").df()
print(df)
```

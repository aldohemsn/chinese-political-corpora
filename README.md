# Chinese Political Corpora

This project contains a corpus of political discourse from the People's Republic of China, scraped from Wikisource. It includes Government Work Reports and National Congress Reports of the Communist Party of China.

## Datasets

The data is provided in JSON Lines (`.jsonl`) format and as a DuckDB database (`corpus.duckdb`).

### 1. Government Work Reports (国务院政府工作报告)
*   **Source:** [Wikisource Portal](https://zh.wikisource.org/wiki/Portal:%E4%B8%AD%E5%8D%8E%E4%BA%BA%E6%B0%91%E5%85%B1%E5%92%8C%E5%9B%BD%E5%9B%BD%E5%8A%A1%E9%99%A2%E6%94%BF%E5%BA%9C%E5%B7%A5%E4%BD%9C%E6%8A%A5%E5%91%8A)
*   **File:** `government_work_reports.jsonl`
*   **Table Name:** `reports`
*   **Content:** Annual reports delivered by the Premier of the State Council (1954–2025).
*   **Fields:** `title`, `url`, `content`, `year`.

### 2. CPC National Congress Reports (中国共产党全国代表大会报告)
*   **Source:** [Wikisource - CPC National Congresses](https://zh.wikisource.org/wiki/Portal:%E4%B8%AD%E5%9B%BD%E5%85%B1%E4%BA%A7%E5%85%9A%E5%85%A8%E5%9B%BD%E4%BB%A3%E8%A1%A8%E5%A4%A7%E4%BC%9A)
*   **File:** `cpc_congress_reports.jsonl`
*   **Table Name:** `congress_reports`
*   **Content:** Political reports delivered at the National Congresses of the CCP (1st–20th).
*   **Fields:** `title`, `url`, `content`, `congress` (integer), `type`.

## Database (`corpus.duckdb`)

The `corpus.duckdb` file contains both datasets in separate tables:
*   `reports`: 72 records.
*   `congress_reports`: 16 records.

## Scripts


### 3. English Translations of Reports
*   **Sources**: China.org.cn, Xinhuanet, Marxists Internet Archive, China Daily.
*   **Table Name**: `reports` (mixed with Government Work Reports, distinguished by `type`).
*   **Content**: English translations of selected CPC National Congress reports (7th, 9th, 16th, 17th, 18th, 19th, 20th).
*   **Fields**: `title`, `url`, `content`, `congress` (integer), `type` ('cpc_congress_report'), `reference`.

## Database (`corpus.duckdb`)

The `corpus.duckdb` file contains:
*   `reports`: Contains Government Work Reports (Chinese) AND English Translations of CPC Congress Reports.
    *   Columns: `title`, `url`, `content`, `year`, `congress`, `type`, `reference`.
*   `congress_reports`: Contains CPC National Congress Reports (Chinese).

## Scripts

### Scraping & English Integration
*   `fetch_english_reports.py`: Scrapes English translations from various official sources.
*   `scrape_18th_congress.py`: Specifically scrapes the 18th Congress report from China Daily (bilingual source).
*   `update_db.py`: Updates the `reports` table schema and inserts the English reports.
*   `export_18th_report.py`: Helper to export the 18th Congress report for review.
*   `scrape_corpus.py`: Scrapes Government Work Reports.
*   `scrape_congress.py`: Scrapes CPC Congress Reports (uses `cpc_congress_links.json`).

### Database Management
*   `create_duckdb.py`: Initializes the database and loads the Government Work Reports.
*   `add_congress_to_db.py`: Adds the Congress Reports to the database.

### Analysis
*   `analyze_term.py`: A script to query the frequency and context of a specific term across both datasets.
    *   Usage: Edit the `TERM` variable in the script and run.
    *   Example: Searching for "综合国力" (Comprehensive National Power).

## Usage Example

```python
import duckdb

con = duckdb.connect("corpus.duckdb")

# Query Government Work Reports
df_gov = con.execute("SELECT year, content FROM reports WHERE year = '2024'").df()

# Query CPC Congress Reports
df_cpc = con.execute("SELECT congress, content FROM congress_reports WHERE congress = 20").df()

print(df_gov.head())
print(df_cpc.head())
```

## Requirements
*   Python 3
*   `duckdb`
*   `pandas`
*   `requests`
*   `beautifulsoup4`
*   `lxml`

Install dependencies:
```bash
pip install -r requirements.txt
```

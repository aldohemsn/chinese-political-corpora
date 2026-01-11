# English Translations of CPC Congress Reports

## Overview
This document tracks the English translations of CPC National Congress reports that have been incorporated into the `corpus.duckdb` database.

## Sourcing
We searched for and retrieved full text translations from official or authoritative sources:
- **China.org.cn**: Official Chinese government portal (English).
- **Xinhuanet**: Official state press agency.
- **Marxists Internet Archive**: Reliable archive for historical texts (Mao, Lin Biao, etc.).
- **Ministry of Foreign Affairs (PRC)**.

## Reports Incorporated

| Congress | Title | Author | Source URL | Status |
|----------|-------|--------|------------|--------|
| **7th** | On Coalition Government | Mao Zedong | [Marxists.org](https://www.marxists.org/reference/archive/mao/selected-works/volume-3/mswv3_25.htm) | Added |
| **8th** | Political Report | Liu Shaoqi | [Marxists.org](https://www.marxists.org/reference/archive/liu-shaoqi/1956/09/15.htm) | Failed (404) |
| **9th** | Report to the Ninth National Congress | Lin Biao | [Marxists.org](https://www.marxists.org/reference/archive/lin-biao/1969/04/01.htm) | Added |
| **10th** | Report to the Tenth National Congress | Zhou Enlai | [Marxists.org](https://www.marxists.org/reference/archive/zhou-enlai/1973/08/24.htm) | Failed (404) |
| **16th** | Build a Well-off Society... | Jiang Zemin | [China.org.cn](http://www.china.org.cn/english/features/49007.htm) | Added |
| **17th** | Hold High the Great Banner... | Hu Jintao | [China.org.cn](http://www.china.org.cn/english/congress/229611.htm) | Added |
| **18th** | Firmly March on the Path... | Hu Jintao | [China Daily](https://language.chinadaily.com.cn/19thcpcnationalcongress/2017-10/16/content_32684880.htm) | Added |
| **19th** | Secure a Decisive Victory... | Xi Jinping | [Xinhuanet](http://www.xinhuanet.com/english/special/2017-11/03/c_136725942.htm) | Added |
| **20th** | Hold High the Great Banner... | Xi Jinping | [FMPRC](https://www.fmprc.gov.cn/eng/zxxx_662805/202210/t20221025_10791908.html) | Added |

## Database Schema Updates
The `reports` table in `corpus.duckdb` was updated to support the new metadata:
- Added `congress` (INTEGER) column.
- Added `type` (VARCHAR) column (e.g., 'cpc_congress_report').
- Added `reference` (VARCHAR) column to store citation metadata (Author/Agency/URL).

## Scripts
- `fetch_english_reports.py`: Used to scrape the content.
- `update_db.py`: Used to update the schema and insert data.

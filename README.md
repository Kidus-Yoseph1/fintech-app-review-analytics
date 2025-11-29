# Fintech Customer Experience Analytics

## Project Goal
To analyze customer satisfaction with mobile banking apps for Commercial Bank of Ethiopia (CBE), Bank of Abyssinia (BOA), and Dashen Bank by scraping, processing, and analyzing user reviews from the Google Play Store.

---

## 🛠️ 1 Data Collection and Preprocessing Methodology

This task focused on acquiring raw data and transforming it into a clean, structured format suitable for downstream NLP analysis .

### 1.1 Data Source and Scraper
* **Source:** Google Play Store reviews.
* **Libraries Used:** `google-play-scraper` (for acquisition) and `pandas` (for cleaning).
* **Target Apps (Package IDs):**
    * **CBE:** `com.combanketh.mobilebanking`
    * **BOA:** `com.boa.boaMobileBanking`
    * **Dashen:** `com.dashen.dashensuperapp`
* **Volume:** 500 reviews were scraped per app (1,500 total raw reviews) to ensure a minimum of 400 clean reviews per bank (1,200 total) remained after cleaning.
* **Scraping Script:** `src/scrape_reviews.py` was executed to fetch the data.

### 1.2 Data Storage and Transformation
The process was split into two stages for modularity:

1.  **Intermediate Storage:** The raw data (a list of dictionaries, including nested metadata) was saved as **`data/raw_reviews.json`**. This preserved the native format from the scraper. During saving, `datetime` objects were converted to ISO strings (`.isoformat()`) to prevent `TypeError` exceptions.
2.  **Preprocessing & Final Output:** The script `src/preprocess_data.py` performed the following cleaning steps:
    * Loaded the JSON data into a Pandas DataFrame.
    * Selected and renamed required columns: `Review Text` (content), `Rating` (score), `Date` (at), `Bank/App Name`, and `Source`.
    * Handled missing data by dropping rows with empty `Review Text`.
    * Removed duplicate reviews based on the combination of `Review Text` and `Date`.
    * Normalized the `Date` column to a simple date format.
    * Saved the final, clean, and tabular output to **`data/processed_data.csv`**.

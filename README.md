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

---

##  2 Data Analysis and NLP Methodology (Task 3)

This task involved applying analytical techniques to the cleaned data and storing the results in a persistent database.

### 2.1 Sentiment Analysis (SA)
* **Tool:** **VADER** (Valence Aware Dictionary and sEntiment Reasoner) from the `nltk` library.
* **Metric:** VADER generated a **`compound_score`** for each review.
* **Classification:** Scores were mapped to categorical **`sentiment`** labels: Positive ($\ge 0.05$), Neutral ($-0.05 < score < 0.05$), and Negative ($\le -0.05$).

### 2.2 Thematic Clustering (Topic Modeling)
* **Tool:** **K-Means Clustering**.
* **Preprocessing:** Text was tokenized, cleaned, and vectorized using **TF-IDF**.
* **Modeling:** K-Means was applied after **PCA** (Principal Component Analysis) reduced the feature space.
* **Output:** Reviews were grouped into 10 distinct **`theme`** clusters.

### 2.3 Database Integration
* **Database:** **PostgreSQL** (using `psycopg2`).
* **Goal:** Store the final structured data for querying.
* **Tables:** `banks` (lookup) and `reviews` (core data with all NLP features).
* **Final Script:** **`src/analyze_and_store.py`** executes the SA, NLP clustering, and inserts all results into the PostgreSQL database.

---

## 📊 3 Visualization and Reporting (Task 4)

This final task retrieves the enriched data from the database to generate visual reports and extract actionable metrics.

### 3.1 Data Acquisition
* **Source:** PostgreSQL database.
* **Process:** The final script executes a `JOIN` query to retrieve all analyzed data from the `reviews` and `banks` tables.

### 3.2 Visualization Artifacts
* **Goal:** Generate 10 distinct, production-ready plots for comprehensive analysis.
* **Libraries:** `matplotlib` and `seaborn`.
* **Output:** All 10 plots are saved as PNG files in the **`reports/figures/`** directory.

| Plot No. | Description | Key Insight |
| :--- | :--- | :--- |
| **1** | Overall Sentiment Distribution | Global sentiment balance. |
| **2** | Sentiment Distribution by Bank | Comparative risk/success across apps. |
| **3** | Average Rating by Bank | Overall perceived quality leadership. |
| **4** | Overall Rating Distribution | Polarity (high 5-star vs. low 1-star volume). |
| **5** | Top 4 Thematic Clusters by Bank | Highest volume complaint areas per bank. |
| **6** | Overall Sentiment Trend Over Time | Longitudinal stability of satisfaction. |
| **7** | Ratings Distribution by Bank | Volatility and dispersion of scores (Box Plot). |
| **8** | Top Negative Themes for BOA | Deep dive into a specific bank's primary failures. |
| **9** | Distribution of Sentiment Scores | Consistency of VADER scoring across banks. |
| **10** | 7-Day Rolling Average Rating Trend | Smoothed metric for detecting service degradation. |


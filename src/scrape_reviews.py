import json
from google_play_scraper import Sort, reviews
from datetime import datetime

# Configuration 
APP_IDS = {
    "Commercial Bank of Ethiopia (CBE)": "com.combanketh.mobilebanking",
    "Bank of Abyssinia (BOA)": "com.boa.boaMobileBanking",
    "Dashen Bank": "com.dashen.dashensuperapp",
}
N_REVIEWS_TO_SCRAPE = 500 
OUTPUT_PATH = "data/raw_reviews.json"

# Data Collection (Scraping) 
def scrape_reviews(app_ids: dict, n_reviews: int) -> list:
    """Scrapes reviews for all defined apps and combines them into a list of dictionaries."""
    all_reviews = []
    
    print("Starting review scraping...")
    for bank_name, app_id in app_ids.items():
        print(f"Scraping {n_reviews} reviews for {bank_name} (ID: {app_id})...")
        
        try:
            result, _ = reviews(
                app_id,
                lang='en',
                country='et',
                sort=Sort.NEWEST,
                count=n_reviews,
                filter_score_with=None 
            )
            
            # Add bank name and source to each review dictionary
            for res in result:
                res['bank_name'] = bank_name
                res['source'] = 'Google Play Store'
                all_reviews.append(res)
                
            print(f"Successfully scraped {len(result)} reviews for {bank_name}.")
            
        except Exception as e:
            print(f"Error scraping {bank_name}: {e}")
            
    print(f"\nTotal raw reviews scraped: {len(all_reviews)}")
    return all_reviews

 
if __name__ == "__main__":
    raw_reviews_data = scrape_reviews(APP_IDS, N_REVIEWS_TO_SCRAPE)
    
    if raw_reviews_data:
        # Convert datetime objects to string format before saving to JSON
        for review in raw_reviews_data:
            if 'at' in review and isinstance(review['at'], datetime):
                # Convert the datetime object to an ISO 8601 string
                review['at'] = review['at'].isoformat()
            # Also convert 'repliedAt' if it exists, as it is also a datetime object
            if 'repliedAt' in review and isinstance(review['repliedAt'], datetime):
                 review['repliedAt'] = review['repliedAt'].isoformat()
        
        # Save the list of dictionaries to a JSON file
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(raw_reviews_data, f, ensure_ascii=False, indent=4)
        
        print(f"\n Scraping Complete. Raw data saved to {OUTPUT_PATH}")
    else:
        print("\n Scraping Failed: Could not retrieve any reviews.")

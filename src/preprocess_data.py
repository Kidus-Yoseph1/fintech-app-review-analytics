import pandas as pd
import json

# Configuration 
INPUT_PATH = "data/raw_reviews.json"
OUTPUT_PATH = "data/processed_data.csv"

# Data Preprocessing 
def preprocess_data(input_path: str, output_path: str):
    """Loads raw JSON data, cleans it, and saves the final CSV."""
    
    print(f"Loading raw data from {input_path}...")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        df = pd.DataFrame(raw_data)
        initial_count = len(df)
        print(f"Raw row count: {initial_count}")
        
    except FileNotFoundError:
        print(f"Error: Raw data file not found at {input_path}. Please run the scraping script first.")
        return
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print("Starting data preprocessing...")
    
    df_clean = df[['content', 'score', 'at', 'bank_name', 'source']].copy()
    df_clean.rename(columns={
        'content': 'Review Text',
        'score': 'Rating',
        'at': 'Date',
        'bank_name': 'Bank/App Name',
        'source': 'Source'
    }, inplace=True)
    
    df_clean.dropna(subset=['Review Text'], inplace=True)
    
   
    df_clean.drop_duplicates(subset=['Review Text', 'Date'], inplace=True)
    
 
    df_clean['Date'] = pd.to_datetime(df_clean['Date']).dt.date
    
    # 5. Save the cleaned data
    final_count = len(df_clean)
    df_clean.to_csv(output_path, index=False)
    
    print(f"Final row count after cleaning: {final_count}")
    print(f"Removed {initial_count - final_count} rows due to missing data or duplicates.")
    print(f"\n Task 1 Preprocessing Complete. Cleaned data saved to {output_path}")
    print("\nData Summary:")
    print(df_clean.groupby('Bank/App Name')['Review Text'].count())


if __name__ == "__main__":
    preprocess_data(INPUT_PATH, OUTPUT_PATH)

import pandas as pd
import nltk
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from nltk.corpus import stopwords
import numpy as np

# Configuration 
INPUT_FILE = "data/processed_data.csv"
OUTPUT_FILE = "data/analyzed_reviews.csv"
N_THEMES = 4 # Targeting 4 themes per bank (within the 3-5 requirement)

ENGLISH_STOP_WORDS = stopwords.words('english')


def clean_text(text):
    """Basic cleaning for text: remove punctuation, lowercase, remove stopwords."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text) 
    tokens = text.split()
    tokens = [word for word in tokens if word not in ENGLISH_STOP_WORDS and len(word) > 2]
    return " ".join(tokens)

def get_sentiment(compound_score):
    """Classifies sentiment based on VADER compound score."""
    if compound_score >= 0.05:
        return 'Positive'
    elif compound_score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

def get_theme_map(model, feature_names, n_top_words=5):
    """Generates a theme name for each topic based on its top 3 words."""
    theme_map = {}
    for topic_idx, topic in enumerate(model.components_):
        # Get top words for the topic
        top_words = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
        # Name the theme using the top 3 descriptive words
        theme_name = " ".join(top_words[:3]).title() 
        theme_map[topic_idx] = theme_name
        
    return theme_map

def run_task2_analysis():
    """Performs Sentiment and Thematic Analysis on review data."""
    print("Starting Task 2: Sentiment and Thematic Analysis...")
    
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found. Ensure Task 1 was run correctly.")
        return
    
    df['Review Text'] = df['Review Text'].astype(str)
    
    # Sentiment Analysis (VADER) 
    print("\n1. Performing Sentiment Analysis (VADER)...")
    analyzer = SentimentIntensityAnalyzer()
    df['Compound Score'] = df['Review Text'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
    df['Sentiment'] = df['Compound Score'].apply(get_sentiment)
    
    #  Thematic Analysis (TF-IDF + NMF) 
    print("\n2. Performing Thematic Analysis (TF-IDF + NMF) per bank...")
    
    # Create a cleaned text column for NLP
    df['Cleaned Text'] = df['Review Text'].apply(clean_text)
    
    analyzed_data = []
    
    for bank in df['Bank/App Name'].unique():
        print(f"\n-> Analyzing themes for: {bank}")
        bank_df = df[df['Bank/App Name'] == bank].copy()
        
        # Vectorization (TF-IDF)
        # Using 1-gram and 2-grams (single words and pairs)
        vectorizer = TfidfVectorizer(max_df=0.85, min_df=5, ngram_range=(1, 2))
        try:
            dtm = vectorizer.fit_transform(bank_df['Cleaned Text'])
            feature_names = vectorizer.get_feature_names_out()
        except ValueError:
            print(f"   Skipping NMF for {bank}: Not enough unique documents/terms.")
            bank_df['Theme'] = 'General/Not Enough Data'
            analyzed_data.append(bank_df)
            continue
        
        # Topic Modeling (NMF)
        nmf = NMF(n_components=N_THEMES, random_state=42, max_iter=300)
        nmf.fit(dtm)
        topic_weights = nmf.transform(dtm)
        
        # Theme Assignment
        theme_map = get_theme_map(nmf, feature_names)
        
        print("   Identified Themes (Top 3 Keywords):")
        for idx, name in theme_map.items():
            print(f"   Theme {idx+1}: {name}")
            
        # Assign the dominant topic index and map to theme name
        bank_df['Theme_Index'] = np.argmax(topic_weights, axis=1)
        bank_df['Theme'] = bank_df['Theme_Index'].map(theme_map)
        bank_df.drop('Theme_Index', axis=1, inplace=True)
        
        analyzed_data.append(bank_df)
    
    # Combine results and save
    final_df = pd.concat(analyzed_data, ignore_index=True)
    final_df.drop('Cleaned Text', axis=1, inplace=True)
    
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n Task 2 Complete. Analyzed data saved to {OUTPUT_FILE}")
    print(f"Final data shape: {final_df.shape}")

if __name__ == "__main__":
    run_task2_analysis()

import pandas as pd
import psycopg2
from psycopg2 import sql
from typing import Dict
from dotenv import load_dotenv  
import os                     

load_dotenv()

# Configuration 
INPUT_FILE = "data/analyzed_reviews.csv"

# DB_PARAMS now populated by environment variables
DB_PARAMS: Dict[str, str] = {
    "host": os.getenv("HOST"),
    "database": os.getenv("DATABASE"),
    "user": os.getenv("DB_USER"),      
    "password": os.getenv("DB_PASSWORD"), 
    "port": os.getenv("PORT")
}


# SQL Commands to Create Tables 
SCHEMA_SQL = """
-- 1. Create the Banks Table
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) UNIQUE NOT NULL,
    app_source VARCHAR(50) NOT NULL
);

-- 2. Create the Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER NOT NULL REFERENCES banks(bank_id),
    review_text TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_date DATE NOT NULL,
    compound_score DECIMAL(5, 4),
    sentiment VARCHAR(10) NOT NULL,
    theme VARCHAR(255)
);
"""

def create_tables(cursor):
    """Executes the necessary SQL to create the banks and reviews tables."""
    print("Executing schema creation script...")
    try:
        cursor.execute(SCHEMA_SQL)
        print("Schema (banks and reviews tables) successfully created or already exists.")
    except psycopg2.Error as e:
        print(f"Database error during table creation: {e}")
        raise

def insert_bank_if_not_exists(cursor, bank_name: str, app_source: str) -> int:
    """Inserts a bank name into the banks table if it doesn't exist, and returns its ID."""
    try:
        cursor.execute(
            sql.SQL("SELECT bank_id FROM banks WHERE bank_name = %s"),
            [bank_name]
        )
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        cursor.execute(
            sql.SQL("INSERT INTO banks (bank_name, app_source) VALUES (%s, %s) RETURNING bank_id"),
            [bank_name, app_source]
        )
        return cursor.fetchone()[0]
    
    except psycopg2.Error as e:
        print(f"Database error during bank insertion: {e}")
        raise

def insert_reviews(cursor, df: pd.DataFrame):
    """Inserts all reviews into the reviews table."""
    print(f"Starting insertion of {len(df)} reviews...")
    
    bank_id_map = {}
    
    for bank in df['Bank/App Name'].unique():
        bank_id = insert_bank_if_not_exists(cursor, bank, df['Source'].iloc[0]) 
        bank_id_map[bank] = bank_id

    records = []
    for index, row in df.iterrows():
        bank_id = bank_id_map.get(row['Bank/App Name'])
        
        # NOTE: Explicitly casting values to ensure correct type for SQL insertion
        records.append((
            bank_id,
            row['Review Text'],
            int(row['Rating']),
            row['Date'],
            float(row['Compound Score']),
            row['Sentiment'],
            row['Theme']
        ))

    insert_query = sql.SQL("""
        INSERT INTO reviews (bank_id, review_text, rating, review_date, compound_score, sentiment, theme)
        VALUES ({})
    """).format(sql.SQL(', ').join(sql.Placeholder() * 7))

    try:
        cursor.executemany(insert_query, records)
        print(f"Successfully inserted {cursor.rowcount} review records.")
    except psycopg2.Error as e:
        print(f"Database error during review bulk insertion: {e}")
        raise

def ingestion():
    """Main function to handle database connection, table creation, and data ingestion."""
    conn = None
    
    #  Ensure env variables were loaded
    if not all(DB_PARAMS.values()):
        print("Fatal Error: Database credentials are missing. Check your .env file and ensure all variables (HOST, DATABASE, USER, PASSWORD, PORT) are defined.")
        return

    try:
        # Load Data
        df = pd.read_csv(INPUT_FILE)
        df = df.dropna(subset=['Review Text'])
        
        # Connect to DB
        print(f"Attempting to connect to PostgreSQL database: {DB_PARAMS['database']}...")
        conn = psycopg2.connect(**DB_PARAMS)
        conn.autocommit = False 
        cursor = conn.cursor()
        
        # Create Tables
        create_tables(cursor)

        # Ingest Data
        insert_reviews(cursor, df)
        
        # Commit and Close
        conn.commit()
        print("\n Data successfully stored and transaction committed.")
        
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found. Ensure Task 2 was run correctly.")
    except psycopg2.OperationalError as e:
        print(f"Connection Error: Could not connect to the database. Please check your PostgreSQL server status and your .env file settings.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if conn:
            conn.rollback()
            print("Transaction rolled back.")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    ingestion()

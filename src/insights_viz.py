import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration 
DB_PARAMS = {
    "host": os.getenv("HOST"),
    "database": os.getenv("DATABASE"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("PORT")
}

# Define output paths
FIGURES_DIR = "reports/figures/"
os.makedirs(FIGURES_DIR, exist_ok=True)

def fetch_data_from_db():
    """Connects to PostgreSQL and fetches all required review data."""
    print("Connecting to database and fetching analyzed data...")
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        
        sql_query = """
        SELECT b.bank_name, r.review_text, r.rating, r.review_date, r.compound_score, r.sentiment, r.theme
        FROM reviews r JOIN banks b ON r.bank_id = b.bank_id;
        """
        
        df = pd.read_sql(sql_query, conn)
        df['review_date'] = pd.to_datetime(df['review_date'])
        print(f"Successfully fetched {len(df)} records.")
        return df

    except psycopg2.Error as e:
        print(f"Database error during data fetching: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def save_plot(fig, filename):
    """Saves the figure and closes it."""
    filepath = os.path.join(FIGURES_DIR, filename)
    fig.savefig(filepath, bbox_inches='tight')
    plt.close(fig)

def generate_all_plots(df):
    """Generates and saves all 10 required plots."""
    print("\nStarting the generation of 10 Visualizations...")

    # Plot 1: Overall Sentiment Distribution (Pie Chart)
    fig1, ax1 = plt.subplots(figsize=(7, 7))
    sentiment_counts = df['sentiment'].value_counts()
    ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=90,
            colors=sns.color_palette('pastel', n_colors=len(sentiment_counts)))
    ax1.set_title('Plot 1: Overall Sentiment Distribution')
    save_plot(fig1, 'plot1_overall_sentiment_pie.png')

    # Plot 2: Sentiment Distribution by Bank (Grouped Bar Chart)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sentiment_counts_bank = df.groupby('bank_name')['sentiment'].value_counts(normalize=True).mul(100).rename('percentage').reset_index()
    sns.barplot(data=sentiment_counts_bank, x='bank_name', y='percentage', hue='sentiment', 
                hue_order=['Positive', 'Neutral', 'Negative'], palette={'Positive': 'g', 'Neutral': 'y', 'Negative': 'r'}, ax=ax2)
    ax2.set_title('Plot 2: Sentiment Distribution by Bank')
    ax2.set_xlabel('Bank/App Name')
    ax2.set_ylabel('Percentage of Reviews')
    save_plot(fig2, 'plot2_sentiment_by_bank_bar.png')

    # Plot 3: Average Rating by Bank
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    avg_ratings = df.groupby('bank_name')['rating'].mean().sort_values(ascending=False)
    sns.barplot(x=avg_ratings.index, y=avg_ratings.values, palette='viridis', ax=ax3)
    ax3.set_title('Plot 3: Average Rating by Bank')
    ax3.set_ylim(1, 5)
    save_plot(fig3, 'plot3_avg_rating_by_bank.png')

    # Plot 4: Overall Rating Distribution (Histogram)
    fig4, ax4 = plt.subplots(figsize=(8, 5))
    sns.histplot(df['rating'], bins=5, kde=False, ax=ax4, color='skyblue')
    ax4.set_title('Plot 4: Overall Rating Distribution')
    save_plot(fig4, 'plot4_overall_rating_distribution.png')

    # Plot 5: Top 4 Thematic Clusters by Bank
    fig5, ax5 = plt.subplots(figsize=(12, 8))
    theme_analysis = df.groupby(['bank_name', 'theme']).size().reset_index(name='count')
    total_reviews_bank = df.groupby('bank_name').size().reset_index(name='total')
    # Merge and calculate percentage using the corrected variable: total_reviews_bank
    theme_analysis = pd.merge(theme_analysis, total_reviews_bank, on='bank_name')
    theme_analysis['percentage'] = (theme_analysis['count'] / theme_analysis['total']) * 100 
    
    theme_analysis['rank'] = theme_analysis.groupby('bank_name')['percentage'].rank(method='first', ascending=False)
    top_themes_df = theme_analysis[theme_analysis['rank'] <= 4].sort_values(by=['bank_name', 'percentage'], ascending=[True, False])
    sns.barplot(data=top_themes_df, x='bank_name', y='percentage', hue='theme', palette='Set2', ax=ax5)
    ax5.set_title('Plot 5: Top 4 Thematic Clusters by Bank')
    ax5.legend(title='Top Theme', bbox_to_anchor=(1.05, 1), loc='upper left')
    save_plot(fig5, 'plot5_top_themes_by_bank.png')

    # Plot 6: Overall Sentiment Trend Over Time (Line Plot)
    fig6, ax6 = plt.subplots(figsize=(12, 6))
    df_monthly_sentiment = df.groupby([df['review_date'].dt.to_period('M'), 'sentiment']).size().unstack(fill_value=0)
    df_monthly_sentiment.index = df_monthly_sentiment.index.to_timestamp()
    
    color_map = {'Negative': 'r', 'Neutral': 'y', 'Positive': 'g'}
    plot_colors = [color_map.get(col, 'gray') for col in df_monthly_sentiment.columns] 
    
    df_monthly_sentiment.plot(ax=ax6, kind='line', marker='o', color=plot_colors)
    
    ax6.set_title('Plot 6: Overall Sentiment Trend Over Time')
    ax6.set_xlabel('Date')
    ax6.set_ylabel('Number of Reviews')
    ax6.legend(title='Sentiment')
    save_plot(fig6, 'plot6_overall_sentiment_trend.png')

    # Plot 7: Ratings Distribution by Bank (Box Plot)
    fig7, ax7 = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=df, x='bank_name', y='rating', ax=ax7, palette='pastel')
    ax7.set_title('Plot 7: Ratings Distribution by Bank (Box Plot)')
    save_plot(fig7, 'plot7_rating_distribution_boxplot.png')

    # Plot 8: Top Themes in Negative Reviews for BOA
    boa_df = df[df['bank_name'] == 'Bank of Abyssinia (BOA)']
    negative_boa_themes = boa_df[boa_df['sentiment'] == 'Negative']['theme'].value_counts().head(5)
    if not negative_boa_themes.empty:
        fig8, ax8 = plt.subplots(figsize=(8, 8))
        ax8.pie(negative_boa_themes, labels=negative_boa_themes.index, autopct='%1.1f%%', startangle=90,
                colors=sns.color_palette('Reds', n_colors=len(negative_boa_themes)))
        ax8.set_title('Plot 8: Top Themes in Negative Reviews for BOA')
        save_plot(fig8, 'plot8_boa_negative_themes_pie.png')

    # Plot 9: Distribution of Sentiment Scores by Bank (Violin Plot)
    fig9, ax9 = plt.subplots(figsize=(10, 6))
    sns.violinplot(data=df, x='bank_name', y='compound_score', palette='muted', ax=ax9)
    ax9.set_title('Plot 9: Distribution of Sentiment Scores by Bank')
    ax9.axhline(y=0.05, color='green', linestyle='--')
    ax9.axhline(y=-0.05, color='red', linestyle='--')
    save_plot(fig9, 'plot9_sentiment_score_distribution.png')

    # Plot 10: 7-Day Rolling Average Rating Over Time (Line Plot)
    df_daily_avg_rating = df.groupby(df['review_date'])['rating'].mean().rolling(window=7).mean().dropna()
    fig10, ax10 = plt.subplots(figsize=(12, 6))
    df_daily_avg_rating.plot(ax=ax10, color='purple')
    ax10.set_title('Plot 10: 7-Day Rolling Average Rating Over Time')
    ax10.grid(axis='y', linestyle='--')
    save_plot(fig10, 'plot10_rolling_avg_rating_trend.png')

    print("\nAll 10 visualizations have been successfully saved to 'reports/figures/'")

def print_key_metrics(df):
    """Calculates and prints essential metrics for the manual PDF report."""
    
    # --- Metrics for Executive Summary ---
    total_reviews_count = len(df)
    avg_ratings = df.groupby('bank_name')['rating'].mean().sort_values(ascending=False)
    sentiment_dist = df.groupby('bank_name')['sentiment'].value_counts(normalize=True).mul(100).unstack(fill_value=0)
    
    bank_highest_avg_rating = avg_ratings.index[0]
    bank_highest_positive = sentiment_dist['Positive'].idxmax()
    bank_highest_negative = sentiment_dist['Negative'].idxmax()
    
    # For BOA's most critical theme
    boa_df = df[df['bank_name'] == 'Bank of Abyssinia (BOA)']
    boa_negative_themes = boa_df[boa_df['sentiment'] == 'Negative']['theme'].value_counts(normalize=True).mul(100)
    most_critical_boa_theme = boa_negative_themes.index[0] if not boa_negative_themes.empty else "N/A"

    print("\n--- Key Metrics for Final PDF Report ---")
    print(f"Total Reviews Analyzed: {total_reviews_count}")
    print(f"1. Highest Average Rating: {bank_highest_avg_rating} ({avg_ratings.loc[bank_highest_avg_rating]:.2f})")
    print(f"2. Bank with Highest Negative Sentiment: {bank_highest_negative} ({sentiment_dist.loc[bank_highest_negative, 'Negative']:.1f}%)")
    print(f"3. Bank with Highest Positive Sentiment: {bank_highest_positive} ({sentiment_dist.loc[bank_highest_positive, 'Positive']:.1f}%)")
    print(f"4. BOA's Critical Negative Theme: {most_critical_boa_theme}")
    print("\n(Use the charts in 'reports/figures/' and these metrics to write the final PDF narrative.)")


def run_task4_reporting():
    """Main function for Task 4."""
    
    if not all(DB_PARAMS.values()):
        print("\nFatal Error: Database credentials are not correctly loaded from environment variables.")
        return
        
    df = fetch_data_from_db()
    
    if df.empty:
        print("\n⚠️ Report generation stopped. Data fetching failed.")
        return

    generate_all_plots(df)
    
    print_key_metrics(df)


if __name__ == "__main__":
    run_task4_reporting()

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import pandas as pd

# Load FinBERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

# Initialize sentiment analysis pipeline
nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Sample data - replace this with your news data DataFrame
data = [
    {'date': '2023-01-01', 'stock': 'AAPL', 'news_text': 'Apple releases new iPhone with positive reviews.'},
    {'date': '2023-01-01', 'stock': 'AAPL', 'news_text': 'Apple stock expected to rise after quarterly earnings report.'},
    {'date': '2023-01-02', 'stock': 'AAPL', 'news_text': 'Concerns over Apple’s supply chain could impact stock.'},
]

# Convert data to DataFrame
df = pd.DataFrame(data)

# Run FinBERT on each news article and get sentiment scores
finbert_sentiment_scores = []
for _, row in df.iterrows():
    news_text = row['news_text']
    result = nlp(news_text)[0]
    sentiment_label = result['label']  # Positive, Neutral, Negative
    sentiment_score = result['score']  # Confidence score
    
    finbert_sentiment_scores.append({
        'date': row['date'],
        'stock': row['stock'],
        'FinBERT_Sentiment': sentiment_label,
        'FinBERT_Score': sentiment_score
    })

# Create a DataFrame from the FinBERT sentiment results
finbert_sentiment_df = pd.DataFrame(finbert_sentiment_scores)
print(finbert_sentiment_df)

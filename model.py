import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Embedding
from tensorflow.keras.preprocessing.sequence import pad_sequences
import datetime

from reuters import search_articles, get_article_content
from screen import get_stock_historical

stock_symbol = "AAPL"
query = "Apple Inc."
number_of_articles = 10

def combine_and_label(news_articles, stock_data):
    # Convert list of dictionaries to pandas DataFrame
    news_df = pd.DataFrame(news_articles)
    stock_df = pd.DataFrame(stock_data)

    # Merge the two dataframes on the date field
    combined_df = pd.merge(news_df, stock_df, on='date')

    # You might want to handle cases where there's no matching stock data for an article
    # For simplicity, this example just drops such cases
    combined_df.dropna(inplace=True)

    # Here, 'price_change' is the target variable
    # You can create a binary label based on whether the price_change is positive or negative
    combined_df['label'] = combined_df['price_change'].apply(lambda x: 1 if x > 0 else 0)

    return combined_df

# 1. Data Collection and Preparation
# Assuming you have functions to scrape news articles and stock data
articles = search_articles(query, size=number_of_articles,order_by="display_date:asc")
news_articles = []
for article in articles:
    url = article['url']
    article_date = datetime.datetime.strptime(article['date'].split(".")[0], '%Y-%m-%dT%H:%M:%S').date()
    content = get_article_content(url)
    news_articles.append({
        'date': article_date,
        'text': content
    })

stock_data = []

for article in news_articles:
    article_date = article['date']
    stock_data_on_publish = get_stock_historical(stock_symbol, article_date, article_date)
    if stock_data_on_publish != None:
        closing_price_on_publish = stock_data_on_publish[0]['Open']
        closing_price_next_day = stock_data_on_publish[0]['Close']
        price_change_percentage = ((closing_price_next_day - closing_price_on_publish) / closing_price_on_publish) * 100
        stock_data.append({
            'date': article_date,
            'price_change': price_change_percentage
        })

# Combine datasets and label data
data = combine_and_label(news_articles, stock_data)

# 2. Text Preprocessing
def preprocess_text(text):
    # Tokenization, normalization, cleaning, etc.
    # Return preprocessed text
    pass

data['processed_text'] = data['text'].apply(preprocess_text)

# 3. Feature Extraction
# Convert text data to numerical format
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(data['processed_text']).toarray()
y = data['label'].values

# 4. Model Selection
# Example: LSTM model
model = Sequential()
model.add(Embedding(input_dim=1000, output_dim=128))
model.add(LSTM(128, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(1, activation='sigmoid'))

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# 5. Model Training
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train, epochs=10, batch_size=64, validation_split=0.1)

# 6. Evaluation and Testing
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy}")

# 7. Iteration and Improvement
# Based on the evaluation, iterate and improve the model

# Note: This is a very basic skeleton. Real-world implementation would require more detailed handling of each step, especially data collection, preprocessing, and model tuning.

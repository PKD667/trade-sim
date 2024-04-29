import json
from reuters import search_articles, get_article_content
import datetime
from screen import get_stock_historical, get_stock_data

from gpt_analysis import get_analysis

# Example stock and timeframe
stock_symbol = "TSLA"
query = "Tesla"
name  = get_stock_data(stock_symbol)["name"]
number_of_articles = 10

# Fetch news articles
articles = search_articles(query, size=number_of_articles,order_by="display_date:asc")

analysis_pairs = []

# Analyze each article
for article in articles:
    url = article['url']
    article_date = datetime.datetime.strptime(article['date'].split(".")[0], '%Y-%m-%dT%H:%M:%S').date()
    content = get_article_content(url)
    
    analysis = get_analysis(article,content,stock_symbol,name)

    # Fetch stock data for the date of the article and the next day
    stock_data_on_publish = get_stock_historical(stock_symbol, article_date, article_date)

    # Calculate percentage change in stock price
    if stock_data_on_publish:
        closing_price_on_publish = stock_data_on_publish[0]['Open']
        closing_price_next_day = stock_data_on_publish[0]['Close']
        price_change_percentage = ((closing_price_next_day - closing_price_on_publish) / closing_price_on_publish) * 100

        # Add the sentiment score and price change percentage to a list
        analysis_pairs.append((analysis["impact"], price_change_percentage))

        # Output the results
        print(f"Article Date: {article_date}, Sentiment Score: {analysis['impact']}")
        print(f"Stock Price Change (%): {price_change_percentage}\n")
        print(f"subjectivity: {analysis['reliability']}")

# Calculate the success rate of the sentiment analysis
success_count = 0
for pair in analysis_pairs:
    if (pair[0] > 0 and pair[1] > 0) or (pair[0] < 0 and pair[1] < 0):
        success_count += 1
success_rate = success_count / len(analysis_pairs) * 100
print(f"Success Rate: {success_rate}%")

# print a nice graph of the data
import matplotlib.pyplot as plt
import numpy as np

x = np.array([pair[0] for pair in analysis_pairs])
y = np.array([pair[1] for pair in analysis_pairs])

plt.scatter(x, y)

plt.xlabel("Sentiment Score")
plt.ylabel("Stock Price Change (%)")
plt.title(f"Sentiment Analysis vs Stock Price Change for {name}")
plt.show()

# print the best and worst analysis

best_analysis = max(analysis_pairs, key=lambda x: x[0])
worst_analysis = min(analysis_pairs, key=lambda x: x[0])

print(f"Best Analysis: {best_analysis}")
print(f"Worst Analysis: {worst_analysis}")
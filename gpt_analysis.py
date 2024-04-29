import requests
import json
import screen
import reuters

import os

# Your OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI API URL for making requests
api_url = "https://api.openai.com/v1/chat/completions"

# Headers for the API request
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

base_request = {
  "model": "gpt-3.5-turbo-16k",
  "messages": [
    {
      "role": "system",
      "content": open("prompt.txt", "r").read()
    }
  ],
  "temperature": 1,
  "max_tokens": 256,
  "top_p": 1,
  "frequency_penalty": 0,
  "presence_penalty": 0
}


def get_analysis(article,article_content,symbol,name) : 
     #End prompt
    end_prompt = {
        "role": "system",
        "content": f"""
    Symbol: {symbol}
    Name: {name}
    Headline: {article["headline"]}
    Content: {article_content}
    """
    }

    json_request = base_request.copy()
    json_request["messages"].append(end_prompt)

    # Make the API request
    response = requests.post(api_url, headers=headers, data=json.dumps(json_request))

    analysis = []

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response
        response_data = response.json()
        analysis = response_data["choices"][0]["message"]["content"]
    else:
        print("Error:", response.status_code, response.text)

    print(article["headline"])
    print(analysis)

    return json.loads(analysis)

if __name__ == "__main__":
    # Example stock and timeframe

    symbol = "TSLA"

    stock_data = screen.get_stock_data(symbol)
    name = stock_data["name"]

    article = reuters.search_articles(name, size=1, order_by="display_date:asc")[0]
    article_content = reuters.get_article_content(article["url"])

    analysis = get_analysis(article,article_content,symbol,name)




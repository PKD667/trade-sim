import requests
import json
from bs4 import BeautifulSoup
import datetime

# Set necessary headers for the request
headers = {
    "Host" : "www.reuters.com",
    "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language" : "en-US,en;q=0.5",
    "Accept-Encoding" : "gzip, deflate, br",
    "Connection" : "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest" : "document",
    "Sec-Fetch-Mode" : "navigate",
    "Sec-Fetch-Site" : "none",
    "Sec-Fetch-User" : "?1",
}

def fetch_hierarchy():
    url = 'https://www.reuters.com/pf/api/v3/content/fetch/site-hierarchy-by-name-v1'
    params = {
        'query': '{"hierarchy_name":"Website","website":"reuters"}',
        'd': '163',
        '_website': 'reuters'
    }

    response = requests.get(url, headers=headers, params=params)
    data = {}
    if response.status_code == 200:
        data = response.json()
    else:
        print("Failed to retrieve data: Status code", response.status_code)
        print(response.text)
        return 1

    # format the data like data = { "section_id" : {"name":"section_name","children" : [subsections]} }
    formatted_data = {}
    for section in data["result"]["children"]:
        formatted_data[section["id"]] = {
            "name" : section["name"],
            "children" : {}
        }
        for subsection in section.get("children",[]):
            formatted_data[section["id"]]["children"][subsection["id"]] = subsection["name"]
    return formatted_data
    
def parse_article(article):
    return {
            "url" : article["canonical_url"],
             "headline" : article["basic_headline"],
              "description" : article["description"],
                "image" : article.get("thumbnail",{}).get("url",""),
                  "date" : article["updated_time"],
                  "section_path" : article["kicker"].get("path","")
        }

def search_articles(query,size = 10,order_by = "display_date:desc"):
    # Set the query parameters (in this case, we're not specifying a topic filter)
    # Customize this to fit the specific topic you'd like to query
    query_params = {
        "keyword":query,
        "offset":0,
        "orderby":order_by,
        "size":size,
        "website":"reuters"
    }
    # URL-encode the query parameters
    encoded_query_params = json.dumps(query_params, separators=(',', ':'))
    print("Searching for:",query)
    # Set the API endpoint URL (add your specific endpoint details)
    url = f"https://www.reuters.com/pf/api/v3/content/fetch/articles-by-search-v2?query={encoded_query_params}&_website=reuters"

    # Make the API request
    response = requests.get(url, headers=headers)

    articles_data = {}
    # Check if the request was successful
    if response.status_code == 200:
        # Parse response to JSON
        articles_data = response.json()
    else:
        print("Failed to retrieve articles. Status code:", response.status_code)
        print(response.text)

    parsed_articles = []
    for article in articles_data["result"]["articles"]:
        parsed_articles.append(parse_article(article))
    return parsed_articles

def fetch_news(section,size = 10):
    # Set the query parameters (in this case, we're not specifying a topic filter)
    # Customize this to fit the specific topic you'd like to query
    query_params = {
        "called_from_a_component":True,
        "fetch_type":"section",
        "section_id":f"/{section}/",
        "size":size,
        "website":"reuters"
    }

    # URL-encode the query parameters
    encoded_query_params = json.dumps(query_params, separators=(',', ':'))

    # Set the API endpoint URL (add your specific endpoint details)
    url = f"https://www.reuters.com/pf/api/v3/content/fetch/articles-by-section-alias-or-id-v1?query={encoded_query_params}&d=163&_website=reuters"

    # Make the API request
    response = requests.get(url, headers=headers)

    articles_data = {}
    # Check if the request was successful
    if response.status_code == 200:
        # Parse response to JSON
        articles_data = response.json()
    else:
        print("Failed to retrieve articles. Status code:", response.status_code)
        print(response.text)

    return articles_data["result"]["articles"]



def get_news(section,size=10):
    
    articles = fetch_news(section,size)
    # parse the articles and get the url, the basic headline and the description
    useful_articles = []
    for article in articles:
        useful_articles.append(parse_article(article))
    return useful_articles

def get_article_content(url):
    # get the article content from the url
    # Set the API endpoint URL (add your specific endpoint details)
    url = f"https://www.reuters.com{url}"

    # Make the API request
    response = requests.get(url, headers=headers)

    article_data = ""
    # Check if the request was successful
    if response.status_code == 200:
        # Parse response to JSON
        article_data = response.text
    else:
        print("Failed to retrieve articles. Status code:", response.status_code)
        print(url)
    # parse the article data
    soup = BeautifulSoup(article_data,"html.parser")

    article_body = ""
    # get the article body
    # print all div classes
    for div in soup.find_all("div"):
        try: 
            if div.get("class",[""])[0].startswith("article-body__content"):
                article_body = div
                break
        except IndexError:
            pass

    #print(article_body)
    # get the paragraphs
    paragraphs = []
    for p in article_body.find_all("p") :
        for c in p.get("class",[""]):
            if c.startswith("article-body__paragraph"):
                paragraphs.append(p)
                break
    # get the article text
    article_text = ""
    for paragraph in paragraphs:
        article_text += paragraph.text
    return article_text




if __name__ == "__main__":
    # get site hierarchy
    article = search_articles("tesla",1)
    print("Date:")
    print(f"{article[0]['date'][:10]} {article[0]['date'][11:19]} - {datetime.datetime.now() - datetime.datetime.strptime(article[0]['date'][:19],'%Y-%m-%dT%H:%M:%S')} ago")
    print("Headline:")
    print(article[0]["headline"])
    print("Article:")
    #print(article)
    content = get_article_content(article[0]["url"])
    print(content)
import requests
import json
import sys
import datetime


headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'trailers'
    }

def screen() :
    # NASDAQ API URL
    url = 'https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&download=true'

    # Make the request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response as JSON
        data = response.json()
        #with open('data.json', 'w') as outfile:
        #    json.dump(data, outfile,indent=4)
    else:
        print("Failed to retrieve data: Status code", response.status_code)

    # convert data data to nice dict
    useful_data = {}
    for i in data['data']['rows']:
        useful_data[i['symbol']] = {"price" : i['lastsale'], "volume" : i['volume'],  "country" : i['country'], "pctchange" : i['pctchange'], "netchange" : i['netchange']}
        # make the price a float
        useful_data[i['symbol']]["price"] = float(useful_data[i['symbol']]["price"].replace("$","").replace(",",""))
        useful_data[i['symbol']]["volume"] = int(useful_data[i['symbol']]["volume"].replace("$","").replace(",",""))
    return useful_data

def get_stock_data(stock):
    url = "https://api.nasdaq.com/api/quote/{stock}/info?assetclass=stocks"
    url = url.format(stock=stock)
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()["data"]
        if data == None:
            print("Stock non-existent")
            return 1
    else :
        print("Failed to retrieve data: Status code", response.status_code)
        return 1
    useful_data = {}
    useful_data["symbol"] = data["symbol"]
    useful_data["name"] = data["companyName"]
    useful_data["price"] = data["primaryData"]["lastSalePrice"]
    useful_data["volume"] = data["primaryData"]["volume"]
    useful_data["pctchange"] = data["primaryData"]["percentageChange"]
    useful_data["netchange"] = data["primaryData"]["netChange"]
    return useful_data

def get_stock_historical(stock, start=None, end=None, timeframe="1y"):
    url = 'https://charting.nasdaq.com/data/charting/historical?symbol={stock}&date={start}~{end}'
    if start != None and end != None:
        pass
    else:
        if timeframe != None:
            end = datetime.datetime.now().strftime("%Y-%m-%d")
            # start = end - timeframe
            # convert timeframe to days
            if timeframe[-1] == "d":
                days = int(timeframe[:-1])
            elif timeframe[-1] == "w":
                days = int(timeframe[:-1])*7
            elif timeframe[-1] == "m":
                days = int(timeframe[:-1])*30
            elif timeframe[-1] == "y":
                days = int(timeframe[:-1])*365
            else:
                print("Invalid timeframe")
                return 1
        start = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        print(start,end)

    url = url.format(stock=stock,start=start,end=end)
    print(url)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None
    data = response.json()
    #print(json.dumps(data,indent=4))
    historical_data = data.get("marketData",None)
    return historical_data

def get_autocomplete(query,limit=10):
    url = f"https://api.nasdaq.com/api/autocomplete/slookup/{limit}?search={query}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()["data"]
        if data == None:
            print("ERROR: Something went wrong")
            return 1
    else :
        print("Failed to retrieve data: Status code", response.status_code)
        return 1

    return data


if __name__ == "__main__":
    # check for args
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            print(json.dumps(screen(),indent=4))            
        else:
            if len(sys.argv) > 2:
                print(json.dumps(get_stock_historical(sys.argv[1],timeframe=sys.argv[2]),indent=4))
            else:
                print(json.dumps(get_stock_data(sys.argv[1]),indent=4))

        
    


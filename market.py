import screen
import graph
import datetime
import json
import os

class market:
    cache = {}
    def __init__(self,balance=1000):
        self.balance = balance
        self.owned = {}

    def get_stock_price(self,stock,date):
        # remove one month from the date
        date = datetime.datetime.strptime(date,"%Y-%m-%d") - datetime.timedelta(days=30)
        if stock not in self.cache:
            stock_data = screen.get_stock_historical(stock,start=date.strftime("%Y-%m-%d"),end=datetime.datetime.now().strftime("%Y-%m-%d"),timeframe=None)
            if stock_data == 1:
                print("Some error")
                return 1
            self.cache[stock] = stock_data
        
        # return closest date
        closest = None
        for i in self.cache[stock]:
            # compre the difference between the dates and the current closest date
            if closest == None or abs(
                (datetime.datetime.strptime(i["date"],"%m/%d/%Y") - date).days) < abs((datetime.datetime.strptime(closest["date"],"%m/%d/%Y") - date).days):
                closest = i
        return closest

    def buy(self,stock, amount,date):
        if self.balance < amount:
            print("Not enough money")
            return 1
        # get the stock price at the desired date
        historical = self.get_stock_price(stock,date)
        if historical == 1:
            print("Invalid stock")
            return 1
        price = historical["open"]
        print("Buying",stock,"at",price,"for",amount)
        shares = amount/price
        if stock in self.owned:
            self.owned[stock] += shares
        else:
            self.owned[stock] = shares
        self.balance -= amount
        return 0

    def sell(self,stock, amount,date):
        if stock not in self.owned:
            print("You don't own any of this stock")
            return 1
        # get the stock price at the desired date
        historical = self.get_stock_price(stock,date)
        if historical == 1:
            print("Invalid stock")
            return 1
        price = historical["open"]
        print("Selling",stock,"at",price,"for",amount)
        shares = amount/price
        self.owned[stock] -= shares
        self.balance += amount
        return 0

    def get_value(self,date):
        value = 0
        for stock in self.owned:
            historical = self.get_stock_price(stock,date)
            if historical == 1:
                print("Invalid stock")
                return 1
            price = historical["open"]
            value += price*self.owned[stock]
        return value
    
if __name__ == "__main__":
    # simulate a situtation from 1 year ago
    m = market(balance=10000)

    start_date = "2020-01-01"
    date = start_date

    if os.path.exists("market.json"):
        if input("Load previous market? (y/n): ") == "y":
            with open("market.json","r") as f:
                data = json.loads(f.read())
                m.balance = data["balance"]
                m.owned = data["owned"]
                date = data["date"]

    while datetime.datetime.strptime(date,"%Y-%m-%d") < datetime.datetime.now():
        print("===",date,"===")
        print("Balance:",m.balance)
        print("Owned:",m.owned)
        print("Value:",m.get_value(date))
        print("Net profit:",(m.balance+m.get_value(date))-10000)
        print("Options:")
        print("1. Buy")
        print("2. Sell")
        print("3. Graph")
        print("4. Fast forward")
        print("5. Exit")
        choice = input("Choice: ")
        if choice == "1":
            stock = input("Stock: ")
            # get some info
            info = screen.get_stock_data(stock)
            if info == 1:
                print("Invalid stock")
                continue
            price = m.get_stock_price(stock,date)["open"]
            f = input(f"Buy {info['name']} ({stock}) at {price}? (y/n): ")
            if f != "y":
                continue
            amount = float(input("Amount: "))
            m.buy(stock,amount,date)
        elif choice == "2":
            stock = input("Stock: ")
            amount = float(input("Amount: "))
            m.sell(stock,amount,date)
        elif choice == "3":
            stock = input("Stock: ")
            graph.graph_historical(stock,start="2016-01-01",end=date)
        elif choice == "4":
            days = input("How many days to fast forward: ")
            date = (datetime.datetime.strptime(date,"%Y-%m-%d") + datetime.timedelta(days=int(days))).strftime("%Y-%m-%d")
        elif choice == "5":
            break
        else:
            print("Invalid choice")

        # save all the data
        with open("market.json","w") as f:
            f.write(json.dumps({"balance":m.balance,"owned":m.owned,"date":date},indent=4))

    print("Final balance:",m.balance)
    print("Final owned:",m.owned)
    print("Final value:",m.get_value(datetime.datetime.now().strftime("%Y-%m-%d")))
    print("Final net profit:",(m.balance+m.get_value(datetime.datetime.now().strftime("%Y-%m-%d")))-10000)

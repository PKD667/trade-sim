import screen
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys

matplotlib.use('Agg')

def graph_historical(stock,timeframe="1y",start=None,end=None,dims=(10,5),dpi=100):
    if start != None and end != None:
        data = screen.get_stock_historical(stock,start=start,end=end)
    else :  
        data = screen.get_stock_historical(stock,timeframe=timeframe)
    print("Retrieved",len(data),"records")

    # plot the data in a nice graph
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    df = df.sort_index()

    # Calculate the figure size in inches
    fig_dims = (int(dims[0])/dpi, int(dims[1])/dpi)
    # plot the data
    print("Plotting graph with dimensions",fig_dims)
    fig, ax = plt.subplots(figsize=fig_dims,dpi=dpi)

    # compute when stock went up between Open and Closed
    up = df["Close"] > df["Open"]
    # compute when stock went down between Open and Closed
    down = df["Open"] > df["Close"]
    # plot the data
    ax.bar(df.index[up], df["Close"][up]-df["Open"][up], width=0.5, bottom=df["Open"][up], color='green')
    ax.bar(df.index[down], df["Open"][down]-df["Close"][down], width=0.5, bottom=df["Close"][down], color='red')
    # plot the High and Low
    ax.vlines(df.index, df['Low'], df['High'], color='black', linewidth=0.5)
    # plot the mean of the Open and Close
    ax.plot(df.index, (df['Open']+df['Close'])/2, color='blue', linewidth=1)

    # put the date so that it fits
    fig.autofmt_xdate()
    # format the dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # set the labels
    ax.set(xlabel='Date', ylabel='Price ($)',
        title=stock)
    # set the grid
    ax.grid()
    # show the graph
    plt.title(stock)
    if start != None and end != None:
        image_path  = f"graphs/{stock}-{start}-{end}.png"
    else:
        image_path  = f"graphs/{stock}-{timeframe}.png"

    plt.savefig(image_path)
    print("Saved graph to",image_path)
    return image_path

if __name__ == "__main__":
    timeframe = "1y"
    if len(sys.argv) > 2:
        timeframe = sys.argv[2]
    graph_historical(sys.argv[1],timeframe=timeframe)
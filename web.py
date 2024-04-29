# create a webserver

import socket
import sys
import os
import mimetypes
import datetime
import time
import threading
import signal
import logging
import argparse
import json
import requests

import screen
import graph
import reuters

from pyweb.server import WebServer


# global variables
# define the default port number
PORT = 8080
# define the default directory
DIRECTORY = os.getcwd()

# define the default log file
LOG_FILE = "webserver.log"

# define the default number of threads
NUM_THREADS = 3

# define the default timeout
TIMEOUT = 60

def parse_body(body):
    """
    parse the body
    """
    # check if the body is empty
    if body == "":
        # return an empty dictionary
        return {}
    # split the body by '&'
    body = body.split("&")
    # create a dictionary
    data = {}
    # loop through each key-value pair
    for key_value in body:
        # split the key-value pair by '='
        key_value = key_value.split("=")
        # get the key
        key = key_value[0]
        # get the value
        value = key_value[1]
        # add the key-value pair to the dictionary
        data[key] = value
    # return the dictionary
    return data

def postapi(handler,request):
    """
    handle the post api
    """
    handler.logger.info("Using Custom Post API")

    # get the request body
    body = request["body"]
    # get the request url
    url = request["url"]
    # check if the request path is /screen
    if url.startswith("/news"): 
        if url == "/news/stock":
            # get post data
            post_data = parse_body(body)
            # get stock
            stock = post_data["stock"]
            # get stock info
            data = screen.get_stock_data(stock)
            # get from reuters with the stock name
            reuters_data = reuters.search_articles(data["name"].split(" ")[0])

            # send the data
            handler.send_data(json.dumps(reuters_data))
            handler.logger.log(request,200)
    else :
        if url == "/screen":
            # return market screening
            data = screen.screen()
            # send the data
            handler.send_data(data)
            handler.logger.log(request,200)

        elif url == "/graph":
            # get post data
            post_data = parse_body(body)
            print(post_data)
            # get time frame
            time_frame = post_data["timeframe"]
            # get stock
            stock = post_data["stock"]
            dims = (post_data["width"],post_data["height"])
            # create a graph
            image_path = graph.graph_historical(stock,timeframe=time_frame,dims=dims)
            # send the image

            handler.send_file(image_path)
            handler.logger.log(request,200)
        
        elif url == "/info":
            # get post data
            post_data = parse_body(body)
            # get stock
            stock = post_data["stock"]
            # get info
            data = screen.get_stock_info(stock)
            # send the data
            handler.send_data(json.dumps(data))
            handler.logger.log(request,200)
        elif url == "/autocomplete":
            # get post data
            post_data = parse_body(body)
            # get search
            search = post_data["search"]
            #print("autocomplete request for ",search)
            # get autocomplete
            data = screen.get_autocomplete(search,limit=10)
            # send the data
            #print(data)
            handler.send_data(json.dumps(data))
            handler.logger.log(request,200)
        
        else :
            # send 404 not found
            handler.send_404()
            handler.logger.log(request,404)

# signal handler
def signal_handler(signal, frame):
    """
    signal handler
    """
    print("SHUTTING DOWN")
    # stop the webserver
    webserver.stop()
    # log the signal
    logging.info("signal " + str(signal))
    # log the exit
    logging.info("exit")
    # exit the program
    sys.exit(0)


# launch the webserver
if __name__ == "__main__":
    # register the signal handler
    signal.signal(signal.SIGINT, signal_handler)
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="port number", type=int)
    parser.add_argument("-d", "--directory", help="directory", type=str)
    parser.add_argument("-l", "--log", help="log file", type=str)
    parser.add_argument("-t", "--threads", help="number of threads", type=int)
    parser.add_argument("-o", "--timeout", help="timeout", type=int)
    args = parser.parse_args()
    if args.port:
        PORT = args.port
    if args.directory:
        DIRECTORY = args.directory
    if args.log:
        LOG_FILE = args.log
    if args.threads:
        NUM_THREADS = args.threads
    if args.timeout:
        TIMEOUT = args.timeout
    # create a webserver
    webserver = WebServer(PORT, DIRECTORY, LOG_FILE, NUM_THREADS, TIMEOUT,postapi=postapi)
    # start the webserver
    webserver.start()

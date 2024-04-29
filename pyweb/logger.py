import os 
import threading
import datetime


import threading
import os
import datetime

class Logger:

    def __init__(self, log_file):
        """
        Initialize the logger
        """
        self.log_file = log_file
        self.lock = threading.Lock()
    
    def log(self, request,status):
        """
        Log a request
        """
        # get the current time
        now = datetime.datetime.now()
        # get the current time in the correct format
        now = now.strftime("%d/%b/%Y:%H:%M:%S")
        # get the request method
        method = request.get("method","-")
        # get the request path
        path = request.get("url","-")
        # get the request version
        version = request.get("version","-")

        user_agent = request["headers"].get("User-Agent","-")
        # get the status code
        status_code = status
        
        # get the log message
        message = " - - [" + now + "] \"" + method + " " + path + " " + version + "\" " + str(status_code) + "\n"

        # color message based on status code
        if status_code >= 200 and status_code < 300:
            message = "\033[32m" + message + "\033[0m"
        elif status_code >= 300 and status_code < 400:
            message = "\033[33m" + message + "\033[0m"
        elif status_code >= 400 and status_code < 500:
            message = "\033[31m" + message + "\033[0m"
        elif status_code >= 500 and status_code < 600:
            message = "\033[35m" + message + "\033[0m"
        else:
            message = "\033[34m" + message + "\033[0m"

        print(message)


        # acquire the lock
        self.lock.acquire()
        # open the log file
        log_file = open(self.log_file, "a")
        # write the log message
        log_file.write(message)
        # close the log file
        log_file.close()
        # release the lock  
        self.lock.release()

    def info(self, message):
        """
        Log an info message
        """
        # get the current time
        now = datetime.datetime.now()
        # get the current time in the correct format
        now = now.strftime("%d/%b/%Y:%H:%M:%S")
        # get the log message
        message = " - - [" + now + "] " + message + "\n"
        # acquire the lock
        self.lock.acquire()
        # open the log file
        log_file = open(self.log_file, "a")
        # write the log message
        log_file.write(message)
        # close the log file
        log_file.close()
        # release the lock  
        self.lock.release()
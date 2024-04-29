import socket
import threading
import os

from .request_handler import RequestHandler
from .logger import Logger

class WebServerThread(threading.Thread):
    """
    WebServerThread class
    """
    def __init__(self, server_socket, directory, logger, timeout,postapi=None):
        """
        initialize the thread
        """
        threading.Thread.__init__(self)
        self.server_socket = server_socket
        self.directory = directory
        self.logger = logger
        self.timeout = timeout
        self.running = True

        # define an optional postapi
        self.postapi = postapi
    
    def run(self):
        """
        run the thread
        """
        while self.running:
            # accept a connection
            connection_socket, address = self.server_socket.accept()
            # set the timeout
            connection_socket.settimeout(self.timeout)
            # create a request handler
            request_handler = RequestHandler(connection_socket, self.directory, self.logger,postapi=self.postapi)
            # handle the request
            request_handler.handle()
            # close the connection
            connection_socket.close()
    
    def stop(self):
        """
        stop the thread
        """
        self.running = False
        self.logger.info("WebServerThread stopped")


class WebServer:
    """
    WebServer class
    """
    def __init__(self, port, directory, log_file, num_threads, timeout,postapi=None):
        """
        initialize the webserver
        """
        self.port = port
        self.directory = directory
        self.log_file = log_file
        self.num_threads = num_threads
        self.timeout = timeout
        self.server_socket = None
        self.logger = None
        self.threads = []

        # define an optional postapi
        self.postapi = postapi

    def start(self):
        """
        start the webserver
        """
        # create a socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to the port
        self.server_socket.bind(('', self.port))
        # start listening
        self.server_socket.listen(1)
        # create a logger
        self.logger = Logger(self.log_file)
        # create threads
        for i in range(self.num_threads):
            thread = WebServerThread(self.server_socket, self.directory, self.logger, self.timeout,postapi=self.postapi)
            # give a name to the thread
            thread.name = "WebServerThread-" + str(i)
            self.threads.append(thread)
            thread.start()
        print(self.threads)
        # wait for threads to finish
        for thread in self.threads:
            thread.join()
        # close the socket
        self.server_socket.close()
    
    def stop(self):
        """
        stop the webserver
        """
        print("Stopping server")
        # stop threads
        for thread in self.threads:
            print("Stopping thread " + str(thread.ident))
            thread.stop()
        
        # close the socket
        self.server_socket.close()

        print("Server stopped")
        self.logger.info("WebServer stopped")
    
    def restart(self):
        """
        restart the webserver
        """
        # stop the webserver
        self.stop()
        # start the webserver
        self.start()
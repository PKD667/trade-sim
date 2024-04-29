from threading import Thread
import socket
import os
import mimetypes
import datetime
from .logger import Logger

def parse_request(request):
    """
    parse the request
    """
    # parse the request
    request = request.decode().split('\r\n')
    # get the request method
    method = request[0].split(' ')[0]
    # get the request url
    url = request[0].split(' ')[1]
    # get the request version
    version = request[0].split(' ')[2]
    # get the request headers
    headers = request[1:-2]
    headers_dict = {}
    for header in headers:
        header = header.split(": ")
        headers_dict[header[0]] = header[1]
    # get the request body
    body = request[-1]
    # return the request
    return { "method": method, "url": url, "version": version, "headers": headers_dict, "body": body }
    
class RequestHandler:
    """
    RequestHandler class
    """
    def __init__(self, connection_socket, directory, logger,postapi=None):
        """
        initialize the request handler
        """
        self.connection_socket = connection_socket
        self.directory = directory
        self.logger = logger

        self.postapi = postapi
    
    def handle(self):
        """
        handle the request
        """
        # get the request
        request = self.connection_socket.recv(4096)
        # parse the request
        request = parse_request(request)
        # get the request method
        method = request["method"]
        # get the request path
        url = request["url"]
        # get url
        path = self.directory + request["url"]

        # check if the request method is GET
        if method == "GET":
            # check if the request path is a directory
            if os.path.isdir(path):
                # check if the request path ends with '/'
                if path.endswith('/'):
                    # get the default file
                    default_file = path + "index.html"
                    # check if the default file exists
                    if os.path.exists(default_file):
                        # send the default file
                        self.send_file(default_file)
                        #log the request
                        self.logger.log(request,200)
                    else:
                        # send the directory
                        self.send_directory(path)
                        #log the request
                        self.logger.log(request,200)
                else:
                    # redirect to the directory
                    self.redirect(request["url"] + '/')
                    #log the request
                    self.logger.log(request,301)

            # check if the request path is a file
            elif os.path.isfile(path):
                # send the file
                self.send_file(path)
                #log the request
                self.logger.log(request,200)
            # otherwise
            else:
                # send 404 not found
                self.send_404()
                # log the request
                self.logger.log(request,404)
        # Check if it is a post request
        elif method == "POST":
            if self.postapi != None:
                self.postapi(self,request)
            else:
                print("No post api defined")
                self.send_501()
                # log the request
                self.logger.log(request,501)
        # otherwise
        else:
            # send 501 not implemented
            self.send_501()
            # log the request
            self.logger.log(request,501)

            
    
    def send_file(self, path):
        """
        send a file
        """
        # get the file size
        file_size = os.path.getsize(path)
        # get the file type
        file_type = mimetypes.guess_type(path)[0]
        # get the file last modified time
        file_last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        # get the file content
        file_content = open(path, 'rb').read()
        # create the response
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: " + file_type + "\r\n"
        response += "Content-Length: " + str(file_size) + "\r\n"
        response += "Last-Modified: " + file_last_modified + "\r\n"
        response += "\r\n"
        response = response.encode()
        response += file_content
        # send the response
        self.connection_socket.send(response)
    
    def send_directory(self, path):
        """
        send a directory
        """
        # get the directory content
        directory_content = os.listdir(path)
        # create the response
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: text/html\r\n"
        response += "\r\n"
        response += "<html>\n"
        response += "<head>\n"
        response += "<title>Index of " + path + "</title>\n"
        response += "</head>\n"
        response += "<body>\n"
        response += "<h1>Index of " + path + "</h1>\n"
        response += "<hr>\n"
        response += "<pre>\n"
        response += "<a href=\"../\">../</a>\n"
        for content in directory_content:
            response += "<a href=\"" + content + "\">" + content + "</a>\n"
        response += "</pre>\n"
        response += "<hr>\n"
        response += "</body>\n"
        response += "</html>\n"
        response = response.encode()
        # send the response
        self.connection_socket.send(response)
    
    def send_data(self, data):
        """
        send data
        """
        # create the response
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: application/json\r\n"
        response += "\r\n"
        response += data
        response = response.encode()
        # send the response
        self.connection_socket.send(response)
    
    def send_404(self):
        """
        send 404 not found
        """
        # create the response
        response = "HTTP/1.1 404 Not Found\r\n"
        response += "Content-Type: text/html\r\n"
        response += "\r\n"
        response += "<html>\n"
        response += "<head>\n"
        response += "<title>404 Not Found</title>\n"
        response += "</head>\n"
        response += "<body>\n"
        response += "<h1>404 Not Found</h1>\n"
        response += "</body>\n"
        response += "</html>\n"
        response = response.encode()
        # send the response
        self.connection_socket.send(response)
    
    def send_501(self):
        """
        send 501 not implemented
        """
        # create the response
        response = "HTTP/1.1 501 Not Implemented\r\n"
        response += "Content-Type: text/html\r\n"
        response += "\r\n"
        response += "<html>\n"
        response += "<head>\n"
        response += "<title>501 Not Implemented</title>\n"
        response += "</head>\n"
        response += "<body>\n"
        response += "<h1>501 Not Implemented</h1>\n"
        response += "</body>\n"
        response += "</html>\n"
        response = response.encode()
        # send the response
        self.connection_socket.send(response)
    
    def redirect(self, url):
        """
        redirect to a url
        """
        # create the response
        response = "HTTP/1.1 301 Moved Permanently\r\n"
        response += "Location: " + url + "\r\n"
        response += "\r\n"
        response = response.encode()
        # send the response
        self.connection_socket.send(response)
    


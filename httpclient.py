#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Connor Resler, Ryan Satyabrata
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #Get the Port Number
    #Help with approaching this function was obtained from reading
    #Ryan Satyabrata's code at https://github.com/kobitoko/CMPUT404-assignment-web-client/blob/master/httpclient.py on February 3, 2017
    def get_host_port(self,url):
        #Check for http
        urlSplit = url.split("/")
        #If url contains http, this will skip the http://
        if("http" in urlSplit[0]):
            urlSplit = urlSplit[2:]
        #If there is still a ':', there is a port defined so use that
        if(":" in urlSplit[0]):
            urlSplit = urlSplit[0].split(":")
            if(len(urlSplit) == 2):
                return int(urlSplit[1])
        #Else use default http port 80
        else:
            return 80

    #Adapted from lab 2, written by Joseph Campbell at 
    #https://github.com/joshua2ua/cmput404w17lab2/blob/master/client.py
    def connect(self, host, port):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((host, port))
        return clientSocket

    #The following 3 functions were written by Ryan Satyabrata at
    #https://github.com/kobitoko/CMPUT404-assignment-web-client/blob/master/httpclient.py I obtained it on February 2, 2017
    #This function will split up the http response and return the code part
    #The code is found after 'HTTP/1.1 ', so it will be the first element
    #following the space after that
    def get_code(self, data):
        return int(data.split(" ")[1])

    #This function will split up the http response and return the header
    #The header is separated from the body by \r\n\r\n, so anything before that
    #will be the header
    def get_headers(self,data):
        return "".join(data.split("\r\n\r\n")[0])

    #This function will split up the http response and return the body
    #The body is separated from the header by \r\n\r\n, so anything after that
    #will be the body
    def get_body(self, data):
        return "".join(data.split("\r\n\r\n")[1:])

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    #This function will get the url of the host
    def getHost(self, url):
        #Check for http
        urlSplit = url.split("/")
        #If length is more than 1, then url contains http
        if(len(urlSplit) > 1):
            host = urlSplit[2:]
            #If there is a ':', get only the part before it because
            #what following will be the port
            if(":" in host[0]):
                return host[0].split(":")[0]
            else:
                return host[0]
        return urlSplit

    #Return the local url
    def getLocal(self, url):
        #Check for http
        urlSplit = url.split("/")
        local = "/"
        #Learned about join function from code written by Ryan Satyabrata at
        #https://github.com/kobitoko/CMPUT404-assignment-web-client/blob/master/httpclient.py
        if(len(urlSplit) > 1):
            local = local + "/".join(urlSplit[3:])
        return local

    #Function to create a GET Request given a url
    def GET(self, url, args=None):
        hostURL = self.getHost(url)
        local = self.getLocal(url)
        host = "Host: " + hostURL
        #print "HostURL: " + hostURL
        port = self.get_host_port(url)
        clientSocket = self.connect(hostURL, port)
        getRequest = "GET " + local + " HTTP/1.1\r\n" + host + "\r\n\r\n"
        clientSocket.sendall(getRequest)
        response = self.recvall(clientSocket)
        code = self.get_code(response)
        body = self.get_body(response)
        print response
        return HTTPResponse(code, body)

    #Function to create a POST Request given a url
    #Portions of this function that involve args were taken from code writen by Ryan Satyabrata at
    #https://github.com/kobitoko/CMPUT404-assignment-web-client/blob/master/httpclient.py
    def POST(self, url, args=None):
        hostURL = self.getHost(url)
        host = "Host: " + hostURL
        port = self.get_host_port(url)
        local = self.getLocal(url)
        clientSocket = self.connect(hostURL, port)
        argsEncoded = ""
        if(args != None):
            #Transform query into a string
            argsEncoded = urllib.urlencode(args)
        contTyp = "content-type: application/x-www-form-urlencoded\r\n"
        contLen = "content-length: " + str(len(argsEncoded)) + "\r\n"

        postRequest = "POST " + local + " HTTP/1.1\r\n" + host + "\r\n" +contTyp + contLen + "\r\n" + argsEncoded + "\r\n\r\n"
        clientSocket.sendall(postRequest)
        response = self.recvall(clientSocket)
        code = self.get_code(response)
        body = self.get_body(response)
        print response
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   

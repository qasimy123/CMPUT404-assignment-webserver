#  coding: utf-8
import socketserver
from functools import reduce
import os
BASE_DIR = "www"

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class HTTPRequest(object):
    '''
     HTTP Request object that parses the request data
    '''

    def __init__(self, data):
        self.data = data
        self.method = None
        self.path = None
        self.version = None
        self.headers = {}
        self.parse()

    def parse(self):
        '''Parse the request and populate the properties above'''

        lines = list(map(lambda x: x.strip().split(
            ' '), self.data.splitlines()))
        self.method, self.path, self.version = lines[0]
        mappings = filter(lambda x: len(x) == 2, lines[1:])
        other = list(filter(lambda x: len(x) == 1, lines[1:]))
        self.headers = dict(map(lambda x: (x[0], x[1]), mappings))
        if other:
            other = reduce(lambda x, y: x + y, other)
            other = '\n'.join(other)
            self.headers['body'] = other

    def __str__(self):
        return f"Method: {self.method}\nPath: {self.path}\nVersion: {self.version}\nHeaders: {self.headers}"


class MyWebServer(socketserver.BaseRequestHandler):
    '''
        Serves files via HTTP
    '''

    def handle(self):
        self.data = self.request.recv(1024).strip().decode("utf-8")
        request = self.parse_request(self.data)
        self.handle_request(request)

    def parse_request(self, request) -> HTTPRequest:
        '''Parse the request and return a HTTPRequest object'''
        return HTTPRequest(request)

    def handle_request(self, request: HTTPRequest):
        '''Handle the request and return a response'''
        if request.method == "GET":
            self.handle_get(request)
        else:
            self.handle_error()

    def handle_get(self, request: HTTPRequest):
        '''Handle a GET request'''
        path = request.path
        if not self.in_base_dir(path):
            self.send_404()
            return
        if self.is_path_dir(path):
            print('is dir'+path)
            if path[-1] != '/':
                self.handle_redirect(path + '/')
                return
            path += 'index.html'

        self.send_file(path)

    def handle_get_index(self, path):
        '''Handle a GET request for an index file'''
        if path[-1] != '/':
            self.handle_redirect(path + '/')
            return
        if not self.file_exists(path + 'index.html'):
            self.send_404()
            return
        self.send_file(path + 'index.html')

    def in_base_dir(self, path) -> bool:
        '''Check if a path is in the base directory'''
        resolved_path = os.path.realpath(BASE_DIR + path)
        if not resolved_path.startswith(os.path.realpath(BASE_DIR)):
            return False
        return True

    def is_path_dir(self, path) -> bool:
        '''Check if a path is a directory'''
        return os.path.isdir(BASE_DIR + path)

    def file_exists(self, path) -> bool:
        '''Check if a file exists'''
        return os.path.exists(BASE_DIR + path)

    def send_404(self):
        '''Send a 404 response'''
        response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r"
        self.request.sendall(bytearray(response, "utf-8"))

    def send_file(self, path):
        '''Send a file'''
        try:

            with open(BASE_DIR + path, 'r', encoding='utf-8') as f:
                content = f.read()

                content_type = self.get_content_type(path)
                response = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(content)}\r\n\n"
                response += content
                self.request.sendall(bytearray(response, "utf-8"))
        except Exception as e:
            print(e)
            self.send_404()

    def get_content_type(self, path) -> str:
        '''Get the content type of a file'''

        extension = path.split('.')[-1]
        mime_types = {
            'html': 'text/html',
            'css': 'text/css',
            'js': 'application/javascript',
            'png': 'image/png'}
        return mime_types.get(extension, 'text/plain')

    def handle_redirect(self, path):
        '''Redirect to a path'''
        response = f"HTTP/1.1 301 Moved Permanently\r\nLocation: {path}\r\n\r"
        self.request.sendall(bytearray(response, "utf-8"))

    def handle_error(self):
        '''Handle an error'''
        response = "HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r"
        self.request.sendall(bytearray(response, "utf-8"))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

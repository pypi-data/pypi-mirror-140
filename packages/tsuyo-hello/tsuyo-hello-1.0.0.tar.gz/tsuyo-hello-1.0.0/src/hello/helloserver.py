import argparse
import json
import socket
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from random import randint
from babel.numbers import format_number


class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        hostname = socket.gethostname()
        message = os.getenv('MESSAGE', 'Hello, world!')
        version = os.getenv('VERSION', '0.0.1')

        rmap = {
            'Welcome': "Hello from Python!",
            'Hostname': hostname,
            'Message': message,
            "Version": version
        }

        self.wfile.write(json.dumps(rmap).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=Server, addr="localhost", port=8080):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)
    id = format_number(randint(0, 1000000), locale="en_US")

    print(f"Starting httpd server on {addr}:{port} with {id}")
    httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8080,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)
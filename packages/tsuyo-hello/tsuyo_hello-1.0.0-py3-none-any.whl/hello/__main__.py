import argparse
from .helloserver import run

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

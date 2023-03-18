#!/usr/bin/env python3

import argparse
import socket
import sys


class Server:

    class Connection:

        def __init__(self, conn, addr):
            self._conn = conn
            self._addr = addr

    def __init__(self, host: str, port: int, bufsize: int = 1024):
        self._host = host
        self._port = port
        self._bufsize = bufsize

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_RAW)
        self._socket.bind((self._host, self._port))

    def listen(self):
        self._socket.listen()

    def __del__(self):
        self._socket.close()


def listen(host: str, port: int, bufsize: int = 1024):
    # with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.IPPROTO_RAW) as s:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                while True:
                    data = conn.recv(bufsize)
                    is_last = len(data) < bufsize

                    yield data, addr, is_last

                    if is_last:
                        break

                conn.send(data)
                conn.close()


def main():
    parser = argparse.ArgumentParser(description="Listen network socket")
    parser.add_argument("-p", "--port", dest="port", required=True, type=int, help="server network port")
    parser.add_argument("--host", dest="host", type=str, default="0.0.0.0", help="server network hostname")
    parser.add_argument("-f", "--logfile", dest="logfile", type=str, help="file to store logs")
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true", help="do not print response")
    parser.add_argument(
        "--pretty",
        dest="pretty",
        action="store_true",
        help="view logs as a huma-readable string instead of raw bytes"
    )
    parser.add_argument(
        "-d",
        "-v",
        "--debug",
        "--verbose",
        dest="debug",
        action="store_true",
        help="set debug log level"
    )

    args = parser.parse_args()

    try:
        connection = listen(args.host, args.port)

        is_first = True
        for data, addr, is_last in connection:
            if args.pretty:
                try:
                    data = data.decode()
                except UnicodeError:
                    pass

            line = f"[{addr[0]}] {data}" if is_first else f"{data}"
            if is_last:
                line += "\n"

            if not args.quiet:
                sys.stdout.write(line)
            if args.logfile:
                with open(args.logfile, "w") as file:
                    file.write(line)

            is_first = is_last

    except KeyboardInterrupt:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())

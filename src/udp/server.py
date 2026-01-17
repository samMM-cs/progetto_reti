import argparse
import socket
from ..log import build_json_entry, dump_to_file

host = '0.0.0.0'
DGRAM_MAX_LEN = 2**16 - 1  # 16bit length


def server(port, file):
    print("Starting udp server")
    # build log in memory and dump it to file at the end
    log = []
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # allow socket to reuse the address in case it crashes
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # fail after 5 seconds
            sock.settimeout(5)
            server_address = (host, port)
            sock.bind(server_address)
            while True:
                data, address = sock.recvfrom(DGRAM_MAX_LEN)
                log.append(build_json_entry(("10.4.0.4", 5555), address, data))
    except socket.timeout:
        with open(file, "w+") as handle:
            tot = sum(rec["payload_length"] for rec in log)
            print(f"writing to disk {len(log)} packets ({tot} bytes)")
            dump_to_file(handle, log)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UDP server')
    parser.add_argument('-p', '--port', dest='port',
                        type=int, default=5555, help='Port to listen to (%(type))')
    parser.add_argument('-f', '--file', dest='file',
                        required=True, help='File to log to')
    given_args = parser.parse_args()

    port = given_args.port
    file = given_args.file
    server(port, file)

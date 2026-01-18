import argparse
import socket
import os
from ..log import build_json_entry, dump_to_file

HOST = '0.0.0.0'

# I due server devono effettuare log in tempo reale di tutti i pacchetti
# di livello applicativo inviati da tutti gli host cliente della rete.
# Le informazioni sono le seguenti:
# a. Timestamp
# b. IP sender
# c. Port sender
# d. IP receiver
# e. Port receiver
# f. Payload
# g. Payload length


def server(port, file):
    # build log in memory and dump it to file at the end
    log = []
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Create TCP socket
            # sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEA DDR,1)

            # fail after 5 seconds
            # sock.settimeout(5)

            server_address = (HOST, port)
            sock.bind(server_address)
            print("Listen...")
            sock.listen()

            conn, sender_addr = sock.accept()
            with conn:
                receiver_addr = conn.getsockname()
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print(f"Ricevuti {len(data)} byte da {sender_addr}")
                    entry = build_json_entry(
                        receiver_address=receiver_addr,
                        sender_address=sender_addr,
                        payload=data
                    )
                    # Scrivi subito su file (append) per log real-time
                    with open(file, "a") as handle:
                        dump_to_file(handle, [entry])
    except socket.timeout:
        print("Server stopped")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TCP server')
    parser.add_argument('-p', '--port', dest='port',
                        type=int, default=5555, help='Port to listen to (%(type))')
    parser.add_argument('-f', '--file', dest='file',
                        required=True, help='File to log to')
    given_args = parser.parse_args()

    port = given_args.port
    file = given_args.file
    server(port, file)

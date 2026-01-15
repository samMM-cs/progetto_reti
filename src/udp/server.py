import socket
import os

from ..log import log_packet

host = '0.0.0.0'
DGRAM_MAX_LEN = 2**16 - 1  # 16bit length

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


def echo_server(port):
    # Create a UDP socket
    if not os.path.exists("./log/"):
        os.mkdir("./log")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        with open("./log/udp.json", "a+") as udp_log:
            # Bind the socket to the port
            server_address = (host, port)
            print("Starting up echo server on %s port %s" % server_address)

            sock.bind(server_address)
            i = 0
            while True:
                data, address = sock.recvfrom(DGRAM_MAX_LEN)
                print("%d -- received %s bytes from %s" %
                      (i, len(data), address))
                log_packet(udp_log, ("10.4.0.4", 5555), address, data)
                i += 1


if __name__ == '__main__':
    """
    parser = argparse.ArgumentParser(description='Socket Server Example')
    parser.add_argument('--port', action="store", dest="port", type=int, required=True)
    given_args = parser.parse_args()
    port = given_args.port
    """
    echo_server(5555)

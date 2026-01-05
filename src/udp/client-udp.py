import socket
# import time
import os


host = '10.4.0.2'
# data_payload = 2048
pkt_len = 2048

SERVER_PORT = 8888


def udp_client(host, port):
    """ A simple echo client """
    # Create a UDP socket
    # DGRAM = Datagram = UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = (host, port)
    print("Connecting to %s port %s" % server_address)
    message = 'messaggio di prova'
    # Send data

    i = 0
    while True:
        payload = os.urandom(pkt_len)
        print("Sending %s bytes" % len(payload))

        # print("message length={}".format(len(payload)))
        sent = sock.sendto(payload, server_address)
        # time.sleep(1)
        i += 1

    # Receive response
    # data, server = sock.recvfrom(data_payload)
    # print("-- received %s \n" % data)

    """
    try:

        # Send data
        message = "Test message. This will be echoed"
        print("Sending %s" % message)
        print("message length={}".format(len(message)))
        sent = sock.sendto(message.encode('utf-8'), server_address)

        # Receive response
        data, server = sock.recvfrom(data_payload)
        print("received %s" % data)
    finally:
        print("Closing connection to the server")
        sock.close()
    """


if __name__ == '__main__':
    """
    parser = argparse.ArgumentParser(description='Socket Server Example')
    parser.add_argument('--port', action="store", dest="port", type=int, required=True)
    given_args = parser.parse_args()
    port = given_args.port
    """

    udp_client(host, SERVER_PORT)

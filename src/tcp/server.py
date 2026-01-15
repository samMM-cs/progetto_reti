import socket
import os
from ..log import log_packet
HOST = '0.0.0.0'
PORT = 5555

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
    if not os.path.exists("./log/"):
        os.mkdir("./log")

    # create TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        with open("./log/tcp.json", "a+") as handle:
            # Bind socket to address and port
            s.bind((HOST, PORT))
            s.listen()
            print("Server S1 in listening mode on port", PORT)
            conn, addr = s.accept()

            receiver_addr = conn.getsockname()

            with conn:
                print("Connected by", addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    conn.sendall(data)       # echo back the received data
                    log_packet(handle, addr, receiver_addr, data)


if __name__ == '__main__':
    echo_server(5555)

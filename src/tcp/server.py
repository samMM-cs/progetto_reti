import argparse
import socket
import os
from ..log import build_json_entry, dump_to_file

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


def server(port,file):
    # build log in memory and dump it to file at the end
    log=[]
    try:
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            #Create TCP socket
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

            #fail after 5 seconds
            sock.settimeout(5)

            s1_ip=socket.gethostbyname(socket.gethostname())
            server_adress=(HOST, port)
            sock.bind(server_adress)
            sock.listen()

            conn,send_addr=sock.accept()

            receiver_addr=conn.getsockName()
            with conn:
                while True:
                    data=conn.recv(1024)
                    if not data: 
                        break
                entry=build_json_entry(receiver_address=receiver_addr,sender_address=send_addr,payload=data)
                log.append(entry)
    except socket.timeout:
        with open(file,"w+") as handle:
            dump_to_file(handle,log)


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


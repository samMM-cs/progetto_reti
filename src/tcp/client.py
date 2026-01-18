import socket
import time
import os
import argparse

# Gli host H1, H2, H3 devono implementare un client TCP che invia pacchetti al 
#server  S1.  Il  payload  deve  essere  generato  randomicamente  con  dimensione 
#variabile  assegnato  programmaticamente  al  momento  dell’avvio  dello  script. 
#L’intervallo di invio dei pacchetti deve essere variabile ed anch’esso assegnato 
#dall’utente al momento dell’avvio dello script. Se T=0 significa che i pacchetti 
#vengono inviati al massimo della capacità del canale.

PROXY='10.4.0.2'
SERVER_PORT = 8888  # send to port 8888 of proxy
server_address = (PROXY, SERVER_PORT)

def tcp_client(interval, length,duration,file):
    start=time.time()
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)

    print("Connecting to %s port %s" % server_address)

    i=0
    while time.time()-start<=duration:
        payload = os.urandom(length) # generate random payload
        sock.sendall(payload)

        if interval>0:
            time.sleep(interval)
        i+=1
        
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='UDP client')
    parser.add_argument('-T', '--interval', dest='interval',
                        type=float, required=True, help='Sending interval, 0 to flood (%(type))')
    parser.add_argument('-L', '--length', dest='length',
                        type=int, required=True, help='Packet length (%(type))')
    parser.add_argument('-D', '--duration', dest='duration',
                        type=int, default=30, help='Duration (%(type))')
    parser.add_argument('-f', '--file', dest='file',
                        required=True, help='File to write diagnostics (%(type))')
    given_args = parser.parse_args()

    length = given_args.length
    interval = given_args.interval
    duration = given_args.duration
    file = given_args.file
    tcp_client(interval, length, duration, file)
import argparse
import socket
import time
import os

# Gli host H4, H5, H6 devono implementare un client UDP che invia pacchetti al
# server S2. Il payload deve essere generato randomicamente con dimensione
# variabile assegnato programmaticamente al momento dell’avvio dello script.
# L’intervallo di invio dei pacchetti deve essere variabile ed anch’esso assegnato
# dall’utente al momento dell’avvio dello script. Se T=0 significa che i pacchetti
# vengono inviati al massimo della capacità del canale.

PROXY = '10.4.0.2'
SERVER_PORT = 8888  # send to port 8888 of proxy
server_address = (PROXY, SERVER_PORT)


def udp_client(interval, length, duration, file):
    start = time.time()
    n_packets = 0
    data_sent = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Connecting to %s port %s" % server_address)

    while time.time() - start <= duration:
        payload = os.urandom(length)
        sent = sock.sendto(payload, server_address)
        data_sent += sent
        n_packets += 1
        # if i % 100 == 0:
        #     print("%d - Sent %s/%s bytes" % (i, length, sent))
        if interval > 0:
            time.sleep(interval)

    # smth = f"sent {n_packets} packets ({data_sent} bytes) in {time.time() - start} s"
    smth = f'{{"sent": {n_packets}, "data": {data_sent}, "time": {time.time() - start}}}'
    # print(smth)
    with open(file, "+w") as f:
        f.write(smth+'\n')


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
    udp_client(interval, length, duration, file)

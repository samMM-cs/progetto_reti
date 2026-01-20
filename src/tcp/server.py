import argparse
from json import dump, loads
import socket
import os
from threading import Thread
from uuid import uuid4
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


# def server(port, file, large_buffer):
#   # build log in memory and dump it to file at the end
#   try:
#     with open(file, "w+") as f:
#       with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         # Create TCP socket
#         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#         if large_buffer:
#           # set bigger buffer to avoid flood losses
#           sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2**20)
#         # fail after 5 seconds
#         sock.settimeout(5)

#         server_address = (HOST, port)
#         sock.bind(server_address)
#         print("Listen...")
#         sock.listen()

#         conn, sender_addr = sock.accept()
#         with conn:
#           receiver_addr = conn.getsockname()
#           while True:
#             data = conn.recv(1024)
#             if not data:
#               break
#             # print(f"Ricevuti {len(data)} byte da {sender_addr}")
#             entry = build_json_entry(
#                 receiver_address=receiver_addr,
#                 sender_address=sender_addr,
#                 payload=data
#             )

#             # Scrivi subito su file (append) per log real-time
#             f.write(entry + '\n')
#   finally:
#     with open(file, "r+") as handle:
#       print("Consolidating lines in a single object")
#       log = [loads(line) for line in handle]

#     tmp_file = file + '.tmp'
#     with open(tmp_file, 'w') as out:
#       dump(log, out)

#     os.replace(tmp_file, file)

def server_thread(conn: socket.socket, sender, temp_files: list[str]):
  file = f"temp_{uuid4().hex}.log"
  temp_files.append(file)
  conn.settimeout(5)
  with conn:
    with open(file, "w") as f:
      receiver = conn.getsockname()
      while True:
        try:
          data = conn.recv(1024)
          if not data:
            break
          f.write(build_json_entry(receiver, sender, data) + '\n')
        except (socket.timeout, ConnectionResetError, BrokenPipeError):
          break


def server(port: int, file, large_buffer: bool, max_connections: int):
  threads = []
  temp_files = []
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    if large_buffer:
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2**20)
    sock.bind((HOST, port))
    sock.listen()

    # even though only three clients, fail if one fails to connect
    sock.settimeout(30)
    try:
      for _ in range(max_connections):
        conn, addr = sock.accept()
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        thread = Thread(target=server_thread, args=(conn, addr, temp_files))
        threads.append(thread)
        thread.start()
    except socket.timeout:
      print("OOPS")
      for tmp in temp_files:
        if os.path.exists(tmp):
          os.remove(tmp)
        if os.path.exists(file):
          os.remove(file)
        return

    for thread in threads:
      thread.join()

    final_log = []
    for tmp in temp_files:
      with open(tmp) as f:
        final_log.extend([loads(line) for line in f])
      os.remove(tmp)
    with open(file, "w") as f:
      dump(final_log, f)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='UDP server')
  parser.add_argument('-p', '--port', dest='port',
                      type=int, default=5555, help='Port to listen to (%(type))')
  parser.add_argument('-f', '--file', dest='file',
                      required=True, help='File to log to')
  parser.add_argument('-b', '--large-buffer', dest='large_buffer',
                      type=bool, default=False, help='Whether to use a large buffer (%(type))')
  parser.add_argument('-N', '--max-connections', dest='max_connections',
                      type=int, default=3, help='Maximum number of connections to listen to (%(type))')
  given_args = parser.parse_args()

  port = given_args.port
  file = given_args.file
  large_buffer = given_args.large_buffer
  max_connections = given_args.max_connections
  server(port, file, large_buffer, max_connections)

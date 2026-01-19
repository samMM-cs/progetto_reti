import argparse
from json import dump, loads
from os import replace
import socket
from ..log import build_json_entry, dump_to_file

host = '0.0.0.0'
DGRAM_MAX_LEN = 2**16 - 1  # 16bit length


def server(port: int, file: str, large_buffer: bool):
  print("Starting udp server")
  try:
    with open(file, "w+") as f:
      with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # allow socket to reuse the address in case it crashes
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if large_buffer:
          # set bigger buffer to avoid flood losses
          sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2**20)

        # stop after 5 seconds of no packets
        sock.settimeout(5)

        server_address = (host, port)
        sock.bind(server_address)

        # build jsonl file while receiving packets
        while True:
          data, address = sock.recvfrom(DGRAM_MAX_LEN)
          f.write(build_json_entry(("10.4.0.4", 5555), address, data) + '\n')
  except socket.timeout:
    # at the end, build normal json
    with open(file, "r+") as handle:
      print("Consolidating lines in a single object")
      log = [loads(line) for line in handle]

    tmp_file = file + '.tmp'
    with open(tmp_file, 'w') as out:
      dump(log, out)

    replace(tmp_file, file)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='UDP server')
  parser.add_argument('-p', '--port', dest='port',
                      type=int, default=5555, help='Port to listen to (%(type))')
  parser.add_argument('-f', '--file', dest='file',
                      required=True, help='File to log to')
  parser.add_argument('-b', '--large-buffer', dest='large_buffer',
                      type=bool, default=False, help='Whether to use a large buffer (%(type))')
  given_args = parser.parse_args()

  port = given_args.port
  file = given_args.file
  large_buffer = given_args.large_buffer
  server(port, file, large_buffer)

from genericpath import exists, getsize
from os import makedirs, mkdir
from time import sleep
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import info

# throughput and congestion tests:
# for each host, length, interval combination send packets for 30 seconds
# check how many are dropped and the effective throughput

lengths = [64, 512, 1460, 1500, 2048, 4096]
intervals = [0, .0001, .001, .01, .1, 1]
duration = 30
directory = "./log6x6"


def exe_and_log(exe, cmd):
  res = exe.cmd(cmd)
  info(exe.name + ': ' + cmd + '\n' + str(res) + '\n\n')


def test(net: Mininet, tcp: bool = True):
  proto = "tcp" if tcp else "udp"
  server = net.get("S1" if tcp else "S2")
  hosts = [net.get(h) for h in (["H1", "H2", "H3"] if tcp else ["H4", "H5", "H6"])]
  assert isinstance(server, Node)
  for large in [False, True]:
    loc_directory = directory + ("_1mb" if large else "_no") + f"_buf_{proto}"
    # create log directories if they don't exist
    makedirs(loc_directory, exist_ok=True)
    for host in hosts:
      assert isinstance(host, Node)
      for interval in intervals:
        for length in lengths:
          if length == 1472 and tcp:
            length = 1460  # 1500 ethernet frame - 20 IP header - 20 TCP header
          log_file = f"log_{host.name}_{interval}_{length}_{proto}.json"
          exe_and_log(server, f"python3 -m src.{proto}.server -f {loc_directory}/server_{log_file} -b {large} &")
          exe_and_log(host, f"python3 -m src.{proto}.client -T {interval} -L {length} -f {loc_directory}/client_{log_file} -D {duration}")
          sleep(10)
    sleep(30)


def test_all_together(net: Mininet):
  proto = "tcp"
  server = net.get("S1")
  [h1, h2, h3] = hosts = [net.get(h) for h in (["H1", "H2", "H3"])]
  assert isinstance(server, Node)
  assert isinstance(h1, Node)
  assert isinstance(h2, Node)
  assert isinstance(h3, Node)
  run = True
  while run:
    run = False
    for large in [False, True]:
      loc_directory = directory + ("_1mb" if large else "_no") + f"_buf_{proto}_together"
      # create log directories if they don't exist
      makedirs(loc_directory, exist_ok=True)
      for interval in intervals:
        for length in lengths:
          if length == 1472:
            length = 1460  # 1500 ethernet frame - 20 IP header - 20 TCP header
          log_file = f"log_together_{interval}_{length}_{proto}.json"
          if exists(f"{loc_directory}/server_{log_file}") and getsize(f"{loc_directory}/server_{log_file}") > 2:
            print((interval, length, large), "already done")
            continue
          run = True
          # 1. KILL any lingering processes from previous failed runs
          server.cmd('pkill -f "src.tcp.server"')
          h1.cmd('pkill -f "src.tcp.client"')
          h2.cmd('pkill -f "src.tcp.client"')
          h3.cmd('pkill -f "src.tcp.client"')
          sleep(2)

          # 2. START Server
          # Note: Use a small delay after starting server to ensure it's listening
          server.sendCmd(f"python3 -m src.{proto}.server -f {loc_directory}/server_{log_file} -b {large}")
          sleep(1)

          # 3. START Clients (All in background)
          exe_and_log(h1, f"python3 -m src.{proto}.client -T {interval} -L {length} -f {loc_directory}/{h1.name}_{log_file} -D {duration} &")
          exe_and_log(h2, f"python3 -m src.{proto}.client -T {interval} -L {length} -f {loc_directory}/{h2.name}_{log_file} -D {duration} &")
          exe_and_log(h3, f"python3 -m src.{proto}.client -T {interval} -L {length} -f {loc_directory}/{h3.name}_{log_file} -D {duration} &")

          # 4. WAIT for the duration + extra time for consolidation
          print(f"Running test for {duration}s...")
          sleep(duration + 15)

          # 5. COLLECT Server Output and ensure it exited
          server.waitOutput()
    sleep(30)


def missing_tests(net: Mininet):
  proto = "tcp"
  server = net.get("S1")
  [H1, H2, H3] = [net.get(h) for h in ["H1", "H2", "H3"]]
  tests = [(True, H3, 0.0001, 4096),
           ]
  for (large, host, interval, length) in tests:
    assert isinstance(host, Node)
    loc_directory = directory + ("_1mb" if large else "_no") + f"_buf_{proto}"
    log_file = f"log_{host.name}_{interval}_{length}_{proto}.json"
    exe_and_log(server, f"python3 -m src.{proto}.server -f {loc_directory}/server_{log_file} -b {large} &")
    exe_and_log(host, f"python3 -m src.{proto}.client -T {interval} -L {length} -f {loc_directory}/client_{log_file} -D {duration}")
    sleep(10)

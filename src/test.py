from mininet.net import Mininet
from mininet.node import Node
from mininet.log import info
# throughput and congestion tests:
# for each host, length, interval combination send packets for 30 seconds
# check how many are dropped and the effective throughput

LENGTHS = [64, 512, 1472, 1500, 4096]
INTERVALS = [0, .001, .01, .1, .5, 1]
DURATION = 30
DIRECTORY = "./log/"


def exe_and_log(exe, cmd):
    res = exe.cmd(cmd)
    info(exe.name + ': ' + cmd + '\n' + str(res)+'\n\n')


def test(net: Mininet, tcp: bool = True):
    proto = "tcp" if tcp else "udp"
    server = net.get("S1" if tcp else "S2")
    hosts = [net.get(h)
             for h in (["H1", "H2", "H3"] if tcp else ["H4", "H5", "H6"])]
    assert isinstance(server, Node)
    for host in hosts:
        assert isinstance(host, Node)
        for interval in INTERVALS:
            for length in LENGTHS:
                log_file = f"log_{host.name}_{interval}_{length}_{proto}.json"
                exe_and_log(server,
                            f"python3 -m src.{proto}.server -f {DIRECTORY}server_{log_file} &")
                exe_and_log(host,
                            f"python3 -m src.{proto}.client -T {interval} -L {length} -f {DIRECTORY}client_{log_file} -D {DURATION}")

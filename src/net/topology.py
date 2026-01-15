from router_data import router_data
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, Host
from ..log import exe_and_log


class Topology(Topo):
    def __init__(self):
        super().__init__()
        # routers will be ryu switches
        R1 = self.addSwitch("R1")
        R2 = self.addSwitch("R2")
        R3 = self.addSwitch("R3")
        R4 = self.addSwitch("R4")
        R5 = self.addSwitch("R5")
        R6 = self.addSwitch("R6")

        # router-router connections
        self.addLink(R1, R3, bw=500, delay="10ms")
        self.addLink(R3, R5, bw=500, delay="10ms")
        self.addLink(R5, R6, bw=1000, delay="10ms")
        self.addLink(R3, R4, bw=1000, delay="10ms")
        self.addLink(R4, R2, bw=500, delay="10ms")

        # subnet behind R1
        H1 = self.addHost("H1", ip="10.0.0.2/24", defaultRoute="via 10.0.0.1")
        H2 = self.addHost("H2", ip="10.0.0.3/24", defaultRoute="via 10.0.0.1")
        self.addLink(R1, H1, bw=100, delay="1ms")
        self.addLink(R1, H2, bw=100, delay="1ms")

        # subnet behind R3
        H3 = self.addHost("H3", ip="10.1.0.2/24", defaultRoute="via 10.1.0.1")
        self.addLink(R3, H3, bw=100, delay="1ms")

        # subnet behind R5
        H4 = self.addHost("H4", ip="10.2.0.2/24", defaultRoute="via 10.2.0.1")
        H5 = self.addHost("H5", ip="10.2.0.3/24", defaultRoute="via 10.2.0.1")
        self.addLink(R5, H4, bw=100, delay="0.05ms")
        self.addLink(R5, H5, bw=100, delay="0.05ms")

        # subnet behind R6
        H6 = self.addHost("H6", ip="10.3.0.2/24", defaultRoute="via 10.3.0.1")
        self.addLink(R6, H6, bw=100, delay="1ms")

        # subnet behind R2
        PROXY = self.addHost("PROXY", ip="10.4.0.2/24",
                             defaultRoute="via 10.4.0.1")
        S1 = self.addHost("S1", ip="10.4.0.3/24", defaultRoute="via 10.4.0.1")
        S2 = self.addHost("S2", ip="10.4.0.4/24", defaultRoute="via 10.4.0.1")
        self.addLink(R2, PROXY, bw=100, delay="1ms")
        self.addLink(R2, S1, bw=100, delay="1ms")
        self.addLink(R2, S2, bw=100, delay="1ms")


def set_routers(net: Mininet):
    c: RemoteController = net.controllers[0]
    for (name, data) in router_data.items():
        # set point to point addresses
        for ip in data["intf_ip"].values():
            cmd = 'curl -X POST -d \'{"address":"%s"}\' http://localhost:8080/router/%s' % \
                (ip, data["dpid"])
            exe_and_log(c, cmd)

        # set router addresses for subnets
        if data['subnet'] is not None:
            cmd = 'curl -X POST -d \'{"address":"%s"}\' http://localhost:8080/router/%s' % \
                (data["gateway_ip"], data["dpid"])
            exe_and_log(c, cmd)

        # set routes
        for (subnet, hop) in data['next_hop'].items():
            cmd = 'curl -X POST -d \'{"destination": "%s", "gateway": "%s"}\'' \
                ' http://localhost:8080/router/%s' % \
                (subnet, router_data[hop]["intf_ip"]
                    [name][:-3], data["dpid"])
            # res = c.cmd(cmd)
            exe_and_log(c, cmd)


def set_proxy(net: Mininet):
    s1: Host | list[Host] = net.get('S1')
    s2: Host | list[Host] = net.get('S2')
    proxy: Host | list[Host] = net.get('PROXY')

    # start proxy
    cmd = 'nginx -c $(pwd)/src/proxy_nginx.conf -g "daemon off;" &'
    exe_and_log(proxy, cmd)
    # exe_and_log(proxy, "wireshark &")
    # input("Select interface on wireshark, press enter to continue")
    # Block traffic on S1 except coming from proxy
    # accept icmp and tcp on port 5555 from proxy, block everything else
    cmd = 'iptables -A INPUT -p tcp -s 10.4.0.2 --dport 5555 -j ACCEPT -v'
    exe_and_log(s1, cmd)
    cmd = 'iptables -A INPUT -p icmp -s 10.4.0.2 -j ACCEPT -v'
    exe_and_log(s1, cmd)
    cmd = 'iptables -A INPUT -p all -j DROP -v'
    exe_and_log(s1, cmd)

    # same for S2, but with udp
    cmd = 'iptables -A INPUT -p udp -s 10.4.0.2 --dport 5555 -j ACCEPT -v'
    exe_and_log(s2, cmd)
    cmd = 'iptables -A INPUT -p icmp -s 10.4.0.2 -j ACCEPT -v'
    exe_and_log(s2, cmd)
    cmd = 'iptables -A INPUT -p all -j DROP -v'
    exe_and_log(s2, cmd)


def run_applicatives(net: Mininet):
    # Start TCP server on S1 and clients on H1, H2, H3
    s1: Host | list[Host] = net.get('S1')
    h1: Host | list[Host] = net.get('H1')
    h2: Host | list[Host] = net.get('H2')
    h3: Host | list[Host] = net.get('H3')

    cmd = 'python3 $(pwd)/src/tcp/server.py &'
    exe_and_log(s1, cmd)
    cmd = 'python3 $(pwd)/src/tcp/client.py -T {interval} -L {length} &'
    exe_and_log(h1, cmd.format(interval=1, length=512))
    exe_and_log(h2, cmd.format(interval=.5, length=256))
    exe_and_log(h3, cmd.format(interval=0, length=64))

    # start UDP server on s2 and client on h4
    s2: Host | list[Host] = net.get('S2')
    h4: Host | list[Host] = net.get('H4')
    h5: Host | list[Host] = net.get('H5')
    h6: Host | list[Host] = net.get('H6')
    cmd = 'python3 $(pwd)/src/udp/server.py &'
    exe_and_log(s2, cmd)
    cmd = 'python3 $(pwd)/src/udp/client.py -T {interval} -L {length} &'
    exe_and_log(h4, cmd.format(interval=1, length=512))
    exe_and_log(h5, cmd.format(interval=.5, length=256))
    exe_and_log(h6, cmd.format(interval=0, length=64))

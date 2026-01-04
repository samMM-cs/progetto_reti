from mininet.net import Mininet, CLI
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.log import setLogLevel, info


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


def create_topology():
    setLogLevel("info")
    # Add Controller
    c0 = RemoteController('c0', ip='127.0.0.1',
                          port=6653, protocols="OpenFlow13")
    net = Mininet(topo=Topology(), controller=c0,
                  switch=OVSKernelSwitch, link=TCLink, autoSetMacs=True)
    net.start()
    set_routers_and_firewall(net)
    CLI(net)
    net.stop()


def set_routers_and_firewall(net: Mininet):
    from router_data import router_data

    def log(name, cmd, res):
        return info(name + ': ' + cmd + '\n' + str(res)+'\n\n')

    c: RemoteController = net.controllers[0]
    for (name, data) in router_data.items():
        # set point to point addresses
        for ip in data["intf_ip"].values():
            cmd = 'curl -X POST -d \'{"address":"%s"}\' http://localhost:8080/router/%s' % \
                (ip, data["dpid"])
            res = c.cmd(cmd)
            log(name, cmd, res)

        # set router addresses for subnets
        if data['subnet'] is not None:
            cmd = 'curl -X POST -d \'{"address":"%s"}\' http://localhost:8080/router/%s' % \
                (data["gateway_ip"], data["dpid"])
            res = c.cmd(cmd)
            log(name, cmd, res)

        # set routes
        for (subnet, hop) in data['next_hop'].items():
            cmd = 'curl -X POST -d \'{"destination": "%s", "gateway": "%s"}\'' \
                ' http://localhost:8080/router/%s' % \
                (subnet, router_data[hop]["intf_ip"][name][:-3], data["dpid"])
            res = c.cmd(cmd)
            log(name, cmd, res)
        if name == 'R2':
            c.cmd(
                "curl -X PUT http://localhost:8080/firewall/module/enable/%s" % data["dpid"])
            # DROP S1 <-> S2
            for src, dst in [("10.4.0.3/32", "10.4.0.4/24"), ("10.4.0.4/24", "10.4.0.3/24")]:
                cmd = ('curl -X POST -d \'{"src":"%s", "dst":"%s", '
                       '"nw_proto":"ICMP", "action":"DENY", "priority":"10"}\' '
                       'http://localhost:8080/firewall/rules/%s' % (src, dst, data["dpid"]))
                c.cmd(cmd)
            # ALLOW Generale (Essenziale per ARP e traffico da altre subnet)
            c.cmd(
                'curl -X POST -d \'{"action":"ALLOW", "priority":"1"}\' http://localhost:8080/firewall/rules/%s' % data["dpid"])


if __name__ == "__main__":
    create_topology()

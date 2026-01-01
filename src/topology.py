from mininet.net import Mininet, CLI
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.node import Switch
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch


class Topology(Topo):
    def __init__(self):
        super().__init__()
        # routers will be ryu switches
        R1: Switch = self.addSwitch("R1", ip="10.0.0.1/24")
        R2: Switch = self.addSwitch("R2", ip="10.4.0.1/24")
        R3: Switch = self.addSwitch("R3", ip="10.1.0.1/24")
        R4: Switch = self.addSwitch("R4")
        R5: Switch = self.addSwitch("R5", ip="10.2.0.1/24")
        R6: Switch = self.addSwitch("R6")

        # router-router connections
        self.addLink(R1, R3, cls=TCLink,
                     bw=500, delay="10ms",
                     params1={"ip": "200.0.0.1/30"},
                     params2={"ip": "200.0.0.2/30"})
        self.addLink(R3, R5, cls=TCLink,
                     bw=500, delay="10ms",
                     params1={"ip": "200.0.1.1/30"},
                     params2={"ip": "200.0.1.2/30"})
        self.addLink(R5, R6, cls=TCLink,
                     bw=1000, delay="10ms",
                     params1={"ip": "200.0.2.1/30"},
                     params2={"ip": "200.0.2.2/30"})
        self.addLink(R3, R4, cls=TCLink,
                     bw=1000, delay="10ms",
                     params1={"ip": "200.0.3.1/30"},
                     params2={"ip": "200.0.3.2/30"})
        self.addLink(R4, R2, cls=TCLink,
                     bw=500, delay="10ms",
                     params1={"ip": "200.0.4.1/30"},
                     params2={"ip": "200.0.4.2/30"})

        # subnet behind R1
        H1 = self.addHost("H1", ip="10.0.0.1/24")
        H2 = self.addHost("H2", ip="10.0.0.2/24")
        self.addLink(R1, H1, cls=TCLink,
                     bw=100, delay="1ms")
        self.addLink(R1, H2, cls=TCLink,
                     bw=100, delay="1ms")

        # subnet behind R3
        H3 = self.addHost("H3", ip="10.1.0.2/24")
        self.addLink(R3, H3, cls=TCLink,
                     bw=100, delay="1ms")

        # subnet behind R5
        H4 = self.addHost("H4", ip="10.2.0.2/24")
        H5 = self.addHost("H5", ip="10.2.0.3/24")
        self.addLink(R5, H4, cls=TCLink,
                     bw=100, delay="0.05ms")
        self.addLink(R5, H5, cls=TCLink,
                     bw=100, delay="0.05ms")

        # subnet behind R6
        H6 = self.addHost("H6", ip="10.3.0.2/24")
        self.addLink(R6, H6, cls=TCLink,
                     bw=100, delay="1ms",
                     params1={"ip": "10.3.0.1/24"})

        # subnet behind R2
        PROXY = self.addHost("PROXY", ip="10.4.0.2/24")
        S1 = self.addHost("S1", ip="10.4.0.3/24")
        S2 = self.addHost("S2", ip="10.4.0.4/24")
        self.addLink(R2, PROXY, cls=TCLink,
                     bw=100, delay="1ms")
        self.addLink(R2, S1, cls=TCLink,
                     bw=100, delay="1ms")
        self.addLink(R2, S2, cls=TCLink,
                     bw=100, delay="1ms")


def create_topology():
    net = Mininet(topo=Topology())

    # Add Controller
    c0 = RemoteController('c0', ip='127.0.0.1',
                          port=6653, protocols="OpenFlow13")
    net.start()
    CLI(net)
    net.stop()


if __name__ == "__main__":
    create_topology()

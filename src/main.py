from mininet.net import Mininet, CLI
from mininet.node import RemoteController, OVSKernelSwitch, Node
from mininet.link import TCLink
from mininet.log import setLogLevel
from net.topology import Topology, set_routers, set_proxy, start_servers


def create_topology():
    setLogLevel("info")
    # Add Controller
    c0 = RemoteController('c0', ip='127.0.0.1',
                          port=6653, protocols="OpenFlow13")
    net = Mininet(topo=Topology(), controller=c0,
                  switch=OVSKernelSwitch, link=TCLink, autoSetMacs=True)
    net.start()
    set_routers(net)
    set_proxy(net)
    # start_servers(net)
    test(net)
    CLI(net)
    net.stop()


def test(net: Mininet):
    s2 = net.get("S2")
    assert isinstance(s2, Node)
    h1 = net.get("H1")
    h2 = net.get("H2")
    h3 = net.get("H3")
    h4 = net.get("H4")
    h5 = net.get("H5")
    h6 = net.get("H6")
    for h in [h1, h2, h3, h4, h5, h6]:
        assert isinstance(h, Node)
        s2.cmd(f"python -m src.udp.server -f ./flood{h.name}.udp.json &")
        h.cmd("timeout 30 python -m src.udp.client -T 0 -L 512")
        s2.cmd("pkill -f 'python -m src.udp.server'")


if __name__ == '__main__':
    create_topology()

from mininet.net import Mininet, CLI
from mininet.node import RemoteController, OVSKernelSwitch, Node
from mininet.link import TCLink
from mininet.log import setLogLevel
from net.topology import Topology, set_routers, set_proxy, start_servers
from test import test


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
  net.pingAll("1s")
  test(net, False)
  CLI(net)
  net.stop()


if __name__ == '__main__':
  create_topology()

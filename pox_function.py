from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer
global array_stats,port,dpid
PACKET_MAX=pow(10,6)
array_stats={}
port=None
dpid=None
def _send_request():
 core.openflow.addListenerByName("PortStatsReceived", _handle_monitor)
 for connection in core.openflow._connections.values():
   connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
def _block_port():
 for connection in core.openflow._connections.values():
  for ports in connection.ports:
   if dpid==connection.dpid and ports==port and port!=65534:
       pm = of.ofp_port_mod(port_no=port.port_no,
                            hw_addr = port.hw_addr,
                            config = of.OFPPC_PORT_DOWN,
                            mask=of.OFPPC_PORT_DOWN)
       connection.send(pm)
 times.cancel()
def _handle_switch():
 for dpids in array_stats:
  if dpids==dpid:
    for links in core.openflow_discovery.adjacency:
	  if links.dpid1==dpid and links.port1==port:
        core.getLogger().info("Blocked Switch DPID: %s" % (dpid,))
        core.getLogger().info("Port %s" % (port,))
	    core.getLogger().info("Connected to Switch DPID: %s" %(links.dpid2,))
		core.getLogger().info("Port %s" % (links.port2,))
      if links.dpid2==dpid and links.port2==port:
        core.getLogger().info("Blocked Switch DPID: %s" % (dpid,))
        core.getLogger().info("Port %s" % (port,))core.getLogger().info("Connected to Switch DPID: %s" %(links.dpid1,))
		core.getLogger().info("Port %s" % (links.port1,))
        _block_port()
      else:
	    core.getLogger().info("Blocked Switch DPID: None")
def set_dpid():
	packets=0
    for dpids in array_stats:
        for ports in array_stats[dpids]:
            if ports.rx_packets>=PACKET_MAX and ports.rx_packets>=packets:
                dpid=dpids
                port=ports
                packets=ports.rx_packets
def _handle_monitor(event):
    if event.dpid not in array_stats:
          array_stats[event.dpid]=event.stats
    if len(array_stats)==5:
        set_dpid()
        _handle_switch()

times=Timer(30,_send_request,recurring=True)








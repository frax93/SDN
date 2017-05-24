from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer
PACKET_MAX=pow(10,6)

class change_topology():
    def __init__(self):
        self.array_stats={}
        self.dpid=None
        self.logger=core.getLogger()
        self.util=core.openflow
	      self.port=None
        self.setTimer()
    def _send_request(self):
        self.util.addListenerByName("PortStatsReceived", self._handle_monitor)
        for connection in self.util._connections.values():
            connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
    def _handle_switch(self):
      for dpid in self.array_stats:
        if dpid == self.dpid:
	     for links in core.openflow_discovery.adjacency:
	       if links.dpid1==self.dpid and links.port1==self.port:
                self.logger.info("Blocked Switch DPID: %s" % (self.dpid,))
                self.logger.info("Port %s" % (self.port,))
	            self.logger.info("Connected to Switch DPID: %s" %(links.dpid2,))
		        self.logger.info("Port %s" % (links.port2,))
	       if links.dpid2==self.dpid and links.port2==self.port:
                self.logger.info("Blocked Switch DPID: %s" % (self.dpid,))
                self.logger.info("Port %s" % (self.port,))
	            self.logger.info("Connected to Switch DPID: %s" %(links.dpid1,))
		        self.logger.info("Port %s" % (links.port1,))
         self.block_port()
        else:
	      self.logger.info("Blocked Switch DPID: None")
    def set_dpid(self):
	      packets=0
          for dpid in self.array_stats:
              for ports in self.array_stats[dpid]:
                  if ports.rx_packets >= PACKET_MAX and ports.rx_packets>=packets:
		       packets=ports.rx_packets
		       self.port=ports.port_no
                       self.dpid=dpid
    def _handle_monitor(self,event): 
       if event.dpid not in self.array_stats:
	   self.array_stats[event.dpid]=event.stats
       if len(self.array_stats)==5:
          self.set_dpid()
          self._handle_switch()
    def setTimer(self):
        self.timer=Timer(30,self._send_request,recurring=True)
        self.logger.info("Change topology module started")
    def block_port(self):
        for connection in self.util._connections.values():
            for port in connection.ports:
	        if connection.dpid==self.dpid:
		       if self.port==port and port!=65534:
                    pm = of.ofp_port_mod(
                      port_no=port,
                      hw_addr=connection.ports[port].hw_addr,
                      config=of.OFPPC_PORT_DOWN,
                      mask=of.OFPPC_PORT_DOWN)
                    connection.send(pm)
	self.timer.cancel()
		
def launch():
    core.registerNew(change_topology)

from ryu.base import app_manager
from ryu.lib import hub
from ryu.controller.handler import set_ev_cls
from ryu.controller import handler
from ryu.controller import ofp_event
from ryu.ofproto import ofproto_v1_0
import logging
from ryu.lib.dpid import str_to_dpid
PACKET_MAX=pow(10,6)

class change_topology(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(change_topology, self).__init__(*args, **kwargs)
        self.port=None
        self.datapaths={}
        self.dpid=None
        self.stats={}
    @set_ev_cls(ofp_event.EventOFPStateChange, [handler.MAIN_DISPATCHER])
    def event_handler(self, ev):
        if not ev.datapath.id in self.datapaths:
            self.datapaths[ev.datapath.id] = ev.datapath
	if len(self.datapaths)==5:
           hub.spawn(self._monitor)
    def set_ports(self): 
	    hub.sleep(40) 
        for datapath in self.datapaths:
	         if datapath==self.dpid:
              for port in self.datapaths[datapath].ports.values():
	   	          if port.port_no==self.port:	  
                    ofp = self.datapaths[datapath].ofproto
                    parser = self.datapaths[datapath].ofproto_parser
                    config = ofp.OFPPC_PORT_DOWN
                    mask = ofp.OFPPC_PORT_DOWN
                    msg=parser.OFPPortMod(self.datapaths[datapath],
                    						port.port_no,
                    						port.hw_addr, 
                    						config, 
                    						mask,port.advertised)
                    self.datapaths[datapath].send_msg(msg)
              hub.kill(hub.getcurrent()) 
    def portstatsreq(self,datapath): 
	      for ports in datapath.ports:
           ofproto=datapath.ofproto
           parser = datapath.ofproto_parser
           req = parser.OFPPortStatsRequest(datapath,0,ofproto.OFPP_NONE)
           datapath.send_msg(req)
    def _monitor(self):
            for dp in self.datapaths.values():
                self.portstatsreq(dp)
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, handler.MAIN_DISPATCHER)
    def save_portstate(self,ev):
	    if ev.msg.datapath.id not in self.stats:
		     self.stats[ev.msg.datapath.id]=ev.msg.body	   	 
        if len(self.stats) == len(self.datapaths):
	       self.calc_dpid()
    def calc_dpid(self):
       packets=0
       for dpid in self.stats:
	      for port in self.stats[dpid]:
	       if port.rx_packets>=PACKET_MAX and port.rx_packets>=packets:
	        packets=port.rx_packets
	        self.dpid=dpid
	        self.port=port.port_no
       log=logging.getLogger()
       if self.dpid!=None:
         log.info('Ignored Datapath %016x',self.dpid)
         log.info('Port blocked %01x',self.port)
         self.set_ports()
       else:
         log.info('Ignored Datapath None')
#!/usr/bin/env python3

class IpHeader(object):
    def __init__(self, sip, dip):
        self.sip = sip
        self.dip = dip

    def __repr__(self):
        return '%15s %15s' % (self.sip, self.dip)

class Packet(object):
    def __init__(self, iph, loc):
        self.iph = iph
        self.loc = loc

    def ip(self):
        return self.iph[-1]

    def pos(self):
        return self.loc

    def push(self, iph):
        return Packet(self.iph + [iph], self.pos())

    def pop(self):
        return Packet(self.iph[:-1], self.pos())

    def forward(self, loc):
        return Packet(self.iph, loc)

    def __repr__(self):
        return '@%7s: %s' % (self.loc, '|'.join(map(str, self.iph)))

def serror(msg, printmsg=False):
    if printmsg:
        print('Error: %s', msg)

class Simulator(object):
    def __init__(self, external_ports):
        self.external_ports = external_ports

    def simulate(self, f, pkts, debug=False):
        while len(pkts) > 0:
            pkts = f(pkts)
            finished = filter(lambda pkt: pkt.pos() in self.external_ports, pkts)
            pkts = pkts - set(finished)

if __name__ == '__main__':
    pkt = Packet([IpHeader('20.0.0.55', '20.0.0.56')], 'sw1:1')
    print(pkt)
    pkt = pkt.push(IpHeader('255.255.255.255', '10.0.0.6'))
    pkt = pkt.push(IpHeader('10.0.0.6', '255.255.255.255'))
    print(pkt)

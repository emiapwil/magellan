#!/usr/bin/env python3

from functools import reduce

class SDNProgram(object):
    def __call__(self, pkts):
        return pkts

class Union(SDNProgram):
    def __init__(self, p1, *args):
        self.ps = [p1] + list(args)

    def __call__(self, pkts):
        return reduce(lambda x,y: x | y, map(lambda p: p(pkts), self.ps))

class Link(SDNProgram):
    def __init__(self, egress, ingress):
        self.egress = egress
        self.ingress = ingress

    def transform(self, pkt):
        if pkt.pos() == self.egress:
            print('%s :: -> %s' % (pkt, self.ingress))
            return {pkt.forward(self.ingress)}
        else:
            return {}

    def __call__(self, pkts):
        return set(reduce(lambda x,y: x | y, map(lambda pkt: self.transform(pkt), pkts)))

class Hub(SDNProgram):
    def __init__(self, ports):
        self.ports = set(ports)

    def transform(self, pkt):
        if pkt.pos() not in self.ports:
            return set()
        other_ports = self.ports - {pkt.pos()}
        print('%s :: -> %s' % (pkt, other_ports))
        return { pkt.forward(p + '\'') for p in other_ports }

    def __call__(self, pkts):
        return set(reduce(lambda x, y: x | y, map(lambda pkt: self.transform(pkt), pkts)))

if __name__ == '__main__':
    '''
    h1 - (1)S1(2) - (1)S2(2) - (1)S3(2) - h2
                                  (3)
                                   |
                                  h3
    '''
    from simulator import *

    simulator = Simulator(['s1:1\'', 's3:3\'', 's3:2\''])
    links = [
        Link('s1:2\'', 's2:1'),
        Link('s2:2\'', 's3:1')
    ]
    hubs = [
        Hub(['s1:1', 's1:2']),
        Hub(['s2:1', 's2:2']),
        Hub(['s3:1', 's3:2', 's3:3'])
    ]
    f = Union(*(links + hubs))

    pkts = {Packet([IpHeader('10.0.0.55', '10.0.0.56')], 's1:1')}
    simulator.simulate(f, pkts)

#!/usr/bin/env python
#  Author:
#  Rudiger Birkner (Networked Systems Group at ETH Zurich)

import re


class RIBEntry(object):
    def __init__(self, peer_asn, peer_address, prefix, as_path, next_hop, communities):
        self.peer_asn = peer_asn
        self.peer_address = peer_address
        self.prefix = prefix
        self.as_path = self.parse_as_path(as_path)
        self.next_hop = next_hop
        self.communities = communities

    @staticmethod
    def parse_as_path(path_string):
        # takes a string representing an AS path and translates it to a list. a path string consists of ASNs or AS Sets
        # separated by white space. An AS set is a string of ASNs separated by white space and enclosed by curly
        # brackets ('{' and '}').

        # if there is any AS set in the path
        if '{' in path_string:
            tmp_path = re.findall(r'(?:{[^{}]*}|[^\s{}])+', path_string)

            as_path = list()
            for element in tmp_path:
                if '{' in element and '}' in element:
                    tmp_set = re.split(',|, | ', element.strip('{').strip('}'))
                    as_set = [int(asn) for asn in tmp_set]
                    as_path.append(as_set)
                else:
                    asn = int(element)
                    as_path.append(asn)
        # if there is no AS set in the path
        else:
            tmp_path = path_string.split(' ')
            as_path = [int(asn) for asn in tmp_path]

        return as_path

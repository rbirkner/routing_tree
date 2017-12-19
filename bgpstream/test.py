#!/usr/bin/env python
#  Author:
#  Rudiger Birkner (Networked Systems Group at ETH Zurich)

import datetime

from _pybgpstream import BGPStream, BGPRecord


stream = BGPStream()
rec = BGPRecord()

# Consider RIBs dumps only
stream.add_filter('project', 'ris')
stream.add_filter('record-type', 'ribs')
# Only receive data for the given interval
stime = int((datetime.datetime(2016, 6, 1, 00, 00) - datetime.datetime(1970, 1, 1)).total_seconds())
etime = int((datetime.datetime(2016, 6, 3, 00, 00) - datetime.datetime(1970, 1, 1)).total_seconds())
stream.add_interval_filter(stime, etime)

print 'start the stream'

stream.start()
# Iterate through the different records

while stream.get_next_record(rec):
    # available data (for more check
    # https://bgpstream.caida.org/docs/api/pybgpstream/_pybgpstream.html#bgprecord)
    project = rec.project  # The name of the project that created the record.
    collector = rec.collector  # The name of the collector that created the record.
    type = rec.type  # The type of the record, can be one of "update", "rib", or "unknown"
    dump_time = rec.dump_time  # The time associated with the entire dump that contained the record.
    time = rec.time  # The time that the record represents.

    print '# project: %s-collector: %s-type: %s-dump_time: %s' % (project, collector, type, dump_time)

    elem = rec.get_next_elem()
    while elem:
        # available data (for more check
        # https://bgpstream.caida.org/docs/api/pybgpstream/_pybgpstream.html#bgpelem)
        elem_type = elem.type  # The type of the element.
        peer_address = elem.peer_address  # The IP address of the peer that this element was received from.
        peer_asn = elem.peer_asn  # The ASN of the peer that this element was received from.
        fields = elem.fields

        if type != 'update':
            print 'type: %s-peer_address: %s-peer_asn: %s\nfields: %s\n' % (type, peer_asn, peer_address, fields)
        elem = rec.get_next_elem()

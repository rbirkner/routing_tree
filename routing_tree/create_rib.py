#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)

import logging
import argparse
import re
from collections import defaultdict


def get_asn_to_prefix_mapping(rib_file):
    asn_to_prefixes = defaultdict(list)

    with open(rib_file, 'r') as infile:
        for line in infile:
            if line and ':' not in line:
                data, path_string = line.strip().split(' ', 1)
                prefix = data
                as_path = parse_as_path(path_string)

                if isinstance(as_path[-1], list):
                    last_as = as_path[-2]
                else:
                    last_as = as_path[-1]

                asn_to_prefixes[last_as].append(prefix)

    return asn_to_prefixes


def parse_as_path(path_string):
    # takes a string representing an AS path and translates it to a list. a path string consists of ASNs or AS Sets
    # separated by white space. An AS set is a string of ASNs separated by white space and enclosed by curly brackets.

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
    else:
        tmp_path = path_string.split(' ')
        as_path = [int(asn) for asn in tmp_path]
    return as_path


def get_paths_from_file(asns, path_file):
    paths = defaultdict(list)

    print 'getting the routes of ASes %s' % ', '.join([str(asn) for asn in asns])

    with open(path_file, 'r') as input_file:
        for line in input_file:
            if line:
                tmp_owner, tmp_tmp, path_string = line.strip().split('|', 2)
                owner = int(tmp_owner)

                as_path = [owner]
                if path_string:
                    as_path += [int(asn) for asn in path_string.split(',')]

                if owner in asns:
                    paths[owner].append(as_path)

    return paths


def get_ribs(asn_to_paths, asn_to_prefixes):
    for asn, paths in asn_to_paths.iteritems():
        with open('%d-caida-rib.out' % asn, 'a') as outfile:
            for path in paths:
                destination = path[-1]
                prefixes = asn_to_prefixes[destination]

                for prefix in prefixes:
                    tmp_path = [str(asn) for asn in path]
                    output = '%s\n' % ' '.join([prefix] + tmp_path)
                    outfile.write(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('asns', help='comma separated list of ASNs of which the RIB should be created', type=str)
    parser.add_argument('paths_file', help='path to the file containing all the CAIDA paths', type=str)
    parser.add_argument('rib_file', help='path to a complete rib obtained through bgpstream', type=str)
    parsed_args = parser.parse_args()

    # initialize logging
    log_level = logging.INFO

    # add handler
    logger = logging.getLogger('DataPreprocessor')
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # prepare for data processing
    asns_string = parsed_args.asns
    asns = [int(asn) for asn in asns_string.split(',')]
    paths_file = parsed_args.paths_file
    rib_file = parsed_args.rib_file

    logger.info('get asn to prefix mapping')
    asn_to_prefixes = get_asn_to_prefix_mapping(rib_file)
    logger.info('get asn to paths mapping')
    asn_to_paths = get_paths_from_file(asns, paths_file)
    logger.info('create ribs from the mappings')
    get_ribs(asn_to_paths, asn_to_prefixes)
    logger.info('done')

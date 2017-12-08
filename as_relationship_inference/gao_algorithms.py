#!/usr/bin/env python
#  Author:
#  Rudiger Birkner(ETH Zurich)

import sys
import networkx as nx

from collections import defaultdict


def basic_heuristic(as_paths):
    """
    Implements Gao's basic AS relationship inference heuristic [GAO IEEE Global Internet, Nov. 2000 Figure 4]
    :param as_paths: list of AS paths where each AS path is again a list of ASNs in order from source to destination
    :return: annotated AS graph
    """

    as_graph = nx.Graph()

    # phase 1: compute degree for each AS - actually build the entire AS graph and then use networkx to get the degree
    for as_path in as_paths:
        for i in range(0, len(as_path) - 1):
            as1 = as_path[i]
            as2 = as_path[i + 1]

            # don't consider self edges (AS path prepending)
            if as1 != as2:
                as_graph.add_edge(as1, as2)

    # phase 2: parse AS path to initialize consecutive AS pair's transit relationship
    transit = defaultdict(int)

    for as_path in as_paths:
        # find the uphill top provider
        top_provider_index, top_provider_asn = max(enumerate(as_path), key=lambda item: as_graph.degree(item[1]))

        for i in range(0, len(as_path) - 1):
            if i < top_provider_index:
                transit[(as_path[i], as_path[i + 1])] = 1
            else:
                transit[(as_path[i + 1], as_path[i])] = 1

    # phase 3: assign relationships to AS pairs
    # instead of going through all as_paths in the input as suggested in Gao's algorithm, we only iterate over every
    # edge in the AS graph once.
    for edge in as_graph.edges_iter():
        as1 = edge[0]
        as2 = edge[1]

        if transit[(as1, as2)] == 1 and transit[(as2, as1)] == 1:
            # sibling to sibling relationship
            as_graph[as1][as2]['as1'] = as1
            as_graph[as1][as2]['as2'] = as2
            as_graph[as1][as2]['type'] = 's2s'

        elif transit[(as2, as1)] == 1:
            # provider to customer relationship
            as_graph[as1][as2]['as1'] = as2
            as_graph[as1][as2]['as2'] = as1
            as_graph[as1][as2]['type'] = 'c2p'

        elif transit[(as1, as2)] == 1:
            # customer to provider relationship
            as_graph[as1][as2]['as1'] = as1
            as_graph[as1][as2]['as2'] = as2
            as_graph[as1][as2]['type'] = 'c2p'

    return as_graph


def refined_heuristic(as_paths, l=1):
    """
    Implements Gao's refined AS relationship inference heuristic [GAO IEEE Global Internet, Nov. 2000 Figure 5]
    :param as_paths: list of AS paths where each AS path is again a list of ASNs in order from source to destination
    :param l: threshold to account for noise in the AS paths
    :return: annotated AS graph
    """

    as_graph = nx.Graph()

    # phase 1: compute degree for each AS - actually build the entire AS graph and then use networkx to get the degree
    for as_path in as_paths:
        for i in range(0, len(as_path) - 1):
            as1 = as_path[i]
            as2 = as_path[i + 1]

            # don't consider self edges (AS path prepending)
            if as1 != as2:
                as_graph.add_edge(as1, as2)

    # phase 2: parse AS path to initialize consecutive AS pair's transit relationship
    transit = defaultdict(int)

    for as_path in as_paths:
        # find the uphill top provider
        top_provider_index, top_provider_asn = max(enumerate(as_path), key=lambda item: as_graph.degree(item[1]))

        for i in range(0, len(as_path) - 1):
            if i < top_provider_index:
                transit[(as_path[i], as_path[i + 1])] += 1
            else:
                transit[(as_path[i + 1], as_path[i])] += 1

    # phase 3: assign relationships to AS pairs
    for edge in as_graph.edges_iter():
        as1 = edge[0]
        as2 = edge[1]

        if (transit[(as1, as2)] > l and transit[(as2, as1)] > l) \
                or (0 < transit[(as1, as2)] <= l and 0 < transit[(as2, as1)] <= l):
            # sibling to sibling relationship
            as_graph[as1][as2]['as1'] = as1
            as_graph[as1][as2]['as2'] = as2
            as_graph[as1][as2]['type'] = 's2s'

        elif transit[(as2, as1)] > l or transit[(as1, as2)] == 0:
            # provider to customer relationship
            as_graph[as1][as2]['as1'] = as2
            as_graph[as1][as2]['as2'] = as1
            as_graph[as1][as2]['type'] = 'c2p'

        elif transit[(as1, as2)] > l or transit[(as2, as1)] == 0:
            # customer to provider relationship
            as_graph[as1][as2]['as1'] = as1
            as_graph[as1][as2]['as2'] = as2
            as_graph[as1][as2]['type'] = 'c2p'

    return as_graph


def peering_heuristic(as_graph, as_paths, r=100000):
    """
    Implements Gao's peering inference heuristic [GAO IEEE Global Internet, Nov. 2000 Phase 2 & 3 in Figure 6]
    :param as_graph: annotated AS graph
    :param as_paths: list of AS paths where each AS path is again a list of ASNs in order from source to destination
    :param r: threshold to account for noise in the AS paths
    :return: annotated AS graph
    """

    # phase 2: identify AS pairs that cannot have a peering relationship
    not_peering = defaultdict(int)

    for as_path in as_paths:
        # find the uphill top provider
        top_provider_index, top_provider_asn = max(enumerate(as_path), key=lambda item: as_graph.degree(item[1]))

        for i in range(0, len(as_path) - 1):
            if i < top_provider_index - 1:
                not_peering[(as_path[i], as_path[i + 1])] = 1
            elif i > top_provider_index:
                not_peering[(as_path[i], as_path[i + 1])] = 1

        if as_graph[(as_path[top_provider_index - 1], as_path[top_provider_index])]['type'] != 's2s' \
                and as_graph[(as_path[top_provider_index], as_path[top_provider_index + 1])]['type'] != 's2s':
            if as_graph.degree(as_path[top_provider_index - 1]) > as_graph.degree(as_path[top_provider_index + 1]):
                not_peering[(as_path[top_provider_index], as_path[top_provider_index + 1])] = 1
            else:
                not_peering[(as_path[top_provider_index - 1], as_path[top_provider_index])] = 1

    # phase 3: assign peering relationships to AS pairs
    for edge in as_graph.edges_iter():
        as1 = edge[0]
        as2 = edge[1]

        if not_peering[as1, as2] != 1 and not_peering[as2, as1] != 1 \
                and as_graph.degree(as1)/as_graph.degree(as2) < r \
                and float(as_graph.degree(as2))/float(as_graph.degree(as1)) > 1.0/r:
            as_graph[as1][as2]['as1'] = as1
            as_graph[as1][as2]['as2'] = as2
            as_graph[as1][as2]['type'] = 'p2p'

    return as_graph


def final_inference(as_paths, mode='basic', l=1, r=100000):
    """
    Implements Gao's full AS relationship inference heuristic including s2s, c2p and p2p
    [GAO IEEE Global Internet, Nov. 2000 Figure 6]
    :param as_paths: list of AS paths where each AS path is again a list of ASNs in order from source to destination
    :param mode: 'basic' or 'refined' to coarsely classify AS pairs into provider-customer or sibling relationships
    :param l: threshold to account for noise in the AS paths
    :param r: threshold to account for noise in the AS paths
    :return: annotated AS graph
    """
    if mode == 'basic':
        as_graph = basic_heuristic(as_paths)
    elif mode == 'refined':
        as_graph = refined_heuristic(as_paths, l)
    else:
        print 'Error: no valid mode specified - mode=%s' % mode
        sys.exit(1)

    as_graph = peering_heuristic(as_graph, as_paths, r)

    return as_graph

#!/usr/bin/env python
#  Author:
#  Rudiger Birkner(ETH Zurich)


import sys
import networkx as nx

from collections import defaultdict


def inference_heuristic(vp_as_paths, delta_0=3, delta_1=2):
    """
    Implements SARK's AS relationship inference heuristic [SARK IEEE INFOCOM, 2002] Figure 3 and III-D.
    :param vp_as_paths: dict of list of AS paths. The keys are the ASNs of the vantage points from which the AS paths
     come. Each AS path is again a list of ASNs in order from source to destination.
    :param delta_0: threshold used for probabilistic dominance (provider-to-customer inference). Should be greater than
    delta_1
    :param delta_1: threshold used for probabilistic equivalence (peer-to-peer inference). Should be less than delta_0
    :return: annotated AS graph
    """

    # Phase 1: Compute Rank Vectors
    vp_as_ranks = dict()
    ases = set()

    for vp, as_paths in vp_as_paths.iteritems():
        tmp_as_ranks = compute_as_ranking(as_paths)
        ases.add(set(tmp_as_ranks.keys()))

        vp_as_ranks[vp] = tmp_as_ranks

    as_ranks = defaultdict(list)
    for vp, tmp_as_ranks in vp_as_ranks.iteritems():
        for asn in ases:
            as_ranks[asn].append(tmp_as_ranks[asn])

    # Phase 2: Annotate AS graph
    # build full AS graph from all AS paths from all vantage points
    as_graph = nx.Graph()
    for vp, as_paths in vp_as_paths.iteritems():
        for as_path in as_paths:
            for i in range(0, len(as_path) - 1):
                as1 = as_path[i]
                as2 = as_path[i + 1]

                # don't consider self edges (AS path prepending)
                if as1 != as2:
                    as_graph.add_edge(as1, as2)

    edges = as_graph.edges()

    # precompute larger and equal
    larger = defaultdict(lambda: defaultdict(int))
    equal = defaultdict(lambda: defaultdict(int))

    for as1, as2 in edges:
        larger[as1][as2] = compute_larger(as1, as2)
        larger[as2][as1] = compute_larger(as2, as1)

        equal[as1][as2] = compute_equal(as1, as2)
        equal[as2][as1] = compute_equal(as2, as1)

    # use inference heuristics to annotate the AS graph

    num_vps = len(vp_as_paths)  # number of vantage points from which we got the AS paths

    # peer-to-peer: equivalence
    remaining_edges = list()
    for as1, as2 in edges:
        if equal[as1][as2] > num_vps / 2.0:
            as_graph[as1][as2]['as1'] = as1
            as_graph[as1][as2]['as2'] = as2
            as_graph[as1][as2]['type'] = 'p2p'
        else:
            remaining_edges.append((as1, as2))

    # provider-to-customer: dominance
    for as1, as2 in remaining_edges:
        if larger[as1][as2] >= num_vps / 2.0 and larger[as2][as1] == 0:
            as_graph[as1][as2]['as1'] = as2
            as_graph[as1][as2]['as2'] = as1
            as_graph[as1][as2]['type'] = 'c2p'
        else:
            remaining_edges.append((as1, as2))

    # peer-to-peer: probabilistic equivalence
    for as1, as2 in remaining_edges:
        if 1.0 / delta_1 <= float(larger[as1][as2]) / larger[as2][as1] <= delta_1:
            as_graph[as1][as2]['as1'] = as1
            as_graph[as1][as2]['as2'] = as2
            as_graph[as1][as2]['type'] = 'p2p'
        else:
            remaining_edges.append((as1, as2))

    # provider-to-customer: probabilistic dominance
    for as1, as2 in remaining_edges:
        if larger[as1][as2] / larger[as2][as1] > delta_0:
            as_graph[as1][as2]['as1'] = as2
            as_graph[as1][as2]['as2'] = as1
            as_graph[as1][as2]['type'] = 'c2p'
        else:
            remaining_edges.append((as1, as2))

    return as_graph


def compute_as_ranking(as_paths):
    """
    Computes the ranking of each AS seen in the provided AS paths. The algorithm follows Fig. 3 in the paper.
    :param as_paths: List of AS paths
    :return: Dict where the key is the ASN and the value the rank of that AS
    """
    routing_graph = nx.DiGraph()
    # build routing graph using the given AS paths (G_X in Fig. 3)
    for as_path in as_paths:
        for i in range(0, len(as_path) - 1):
            as1 = as_path[i]
            as2 = as_path[i + 1]

            # don't consider self edges (AS path prepending)
            if as1 != as2:
                routing_graph.add_edge(as1, as2)

    # iteratively assign ranks to all ASes in the routing graph starting with the leaves and iteratively
    # repeating the process until the root is reached.
    leaves = [x for x in routing_graph.nodes_iter()
              if routing_graph.out_degree(x) == 0 and routing_graph.in_degree(x) == 1]

    as_ranks = defaultdict(lambda : -1)

    rank = 1
    while leaves:
        for leaf in leaves:
            as_ranks[leaf] = rank
        rank += 1
        routing_graph.remove_edges_from(leaves)
        leaves = [x for x in routing_graph.nodes_iter()
                  if routing_graph.out_degree(x) == 0 and routing_graph.in_degree(x) == 1]

    return as_ranks


def compute_larger(rank_vector1, rank_vector2):
    """
    Implements the l(i, j) as described on page 622
    :param rank_vector1: list with ranks (integers)
    :param rank_vector2: list with ranks (integers)
    :return: count of how many ranks are larger in rank_vector1 compared to rank_vector2
    """

    if len(rank_vector1) != len(rank_vector2):
        print "Error: The two rank vectors have different length"
        sys.exit(1)

    count = 0
    for item1, item2 in zip(rank_vector1, rank_vector2):
        if item1 > item2:
            count += 1
    return count


def compute_equal(rank_vector1, rank_vector2):
    """
    Implements the e(i, j) as described on page 622
    :param rank_vector1: list with ranks (integers)
    :param rank_vector2: list with ranks (integers)
    :return: count of how many ranks are equal in rank_vector1 and rank_vector2
    """

    if len(rank_vector1) != len(rank_vector2):
        print "Error: The two rank vectors have different length"
        sys.exit(1)

    count = 0
    for item1, item2 in zip(rank_vector1, rank_vector2):
        if item1 == item2:
            count += 1
    return count

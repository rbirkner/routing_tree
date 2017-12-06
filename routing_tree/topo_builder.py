#!/usr/bin/env python
#  Author:
#  Rudiger Birkner (ETH Zurich)

import networkx as nx
import itertools
import argparse
import time

from collections import namedtuple, defaultdict


class ASTopo(nx.Graph):
    def __init__(self, topology_file, topology_format):
        """
        AS-level topology object.
        :param topology_file: path of the toplogy file
        :param topology_format: format of the topology file (CAIDA = 0, UCLA = 1)
        :param tier1_threshold: all nodes with more than tier1_threshold connections and no providers are considered tier1 nodes
        :return:
        """

        super(ASTopo, self).__init__()

        self.no_provider_nodes = []

        # build graph
        print "Build from Topology File"
        self.build_from_file(topology_file, topology_format)

        print "Identify all Nodes without Provider"
        self.no_provider_nodes = self.get_all_nodes_without_provider()

        print "Remove Backedges"
        self.remove_backedges()

        # print basic information
        print "Built AS-Level Topology"
        print "-> No. ASes: " + str(self.number_of_nodes())
        print "-> No. of Connections: " + str(self.number_of_edges())

    def build_from_file(self, topology_file, topology_format):
        """
        build basic networkx topology from file
        :param topology_file: path of the topology file
        :param topology_format: format of the topology file (CAIDA = 0, UCLA = 1)
        """
        with open(topology_file) as infile:
            for line in infile:
                if line.startswith("#"):
                    continue
                else:
                    if topology_format == 0:
                        x = line.split("\n")[0].split("|")
                        as1 = int(x[0])
                        as2 = int(x[1])
                        relationship = int(x[2])
                    else:
                        x = line.split("\n")[0].split("\t")
                        if x[2] == "p2c":
                            as1 = int(x[0])
                            as2 = int(x[1])
                            relationship = -1
                        elif x[2] == "c2p":
                            as1 = int(x[1])
                            as2 = int(x[0])
                            relationship = -1
                        elif x[2] == "p2p":
                            as1 = int(x[1])
                            as2 = int(x[0])
                            relationship = 0
                        else:
                            continue

                    if not self.has_edge(as1, as2):
                        self.add_edge(as1, as2, relationship=relationship, as1=as1, as2=as2)

    def has_customers(self, asn):
        """
        checks if an AS has customers.
        :param asn: asn of the AS to be checked
        :return: True if the AS has customers, else False
        """
        for neighbor in nx.all_neighbors(self, asn):
            edge_data = self.get_edge_data(asn, neighbor)

            # node is a provider of neighbor
            if edge_data["relationship"] == -1 and edge_data["as1"] == asn:
                return True
        return False

    def has_providers(self, asn):
        """
        checks if an AS has providers.
        :param asn: asn of the AS to be checked
        :return: True if the AS has customers, else False
        """
        for neighbor in nx.all_neighbors(self, asn):
            edge_data = self.get_edge_data(asn, neighbor)

            # node is a customer of neighbor
            if edge_data["relationship"] == -1 and edge_data["as2"] == asn:
                return True
        return False

    def number_of_connections(self, asn):
        """
        Method that counts the number of links of an AS with respect to their type.
        :param asn: asn of the AS of which we are interested in the number of links
        :return: a tuple consisting of the number of customers, providers and peers
        """
        customer_count = 0
        provider_count = 0
        peer_count = 0

        for neighbor in nx.all_neighbors(self, asn):
            edge_data = self.get_edge_data(asn, neighbor)
            if edge_data["relationship"] == -1 and edge_data["as1"] == asn:
                customer_count += 1
            elif edge_data["relationship"] == -1 and edge_data["as2"] == asn:
                provider_count += 1
            elif edge_data["relationship"] == 0:
                peer_count += 1
        return customer_count, provider_count, peer_count

    def get_all_nodes_without_provider(self):
        """
        This method goes through the whole graph and finds all nodes without provider.
        :return: list of all nodes without provider (asns)
        """

        no_provider_nodes = []
        # create list of all nodes without provider and more than tier1_threshold customers
        for node in self.nodes():
            tier1 = True

            # check that node is not a customer of any node
            if not self.has_providers(node):
                no_provider_nodes.append(node)

        return no_provider_nodes

    def remove_backedges(self):
        """
        Based on the identified tier1 nodes, this method removes all backedges by doing a DFS traversal of the
        topology starting at a tier1 node.
        """

        # Add virtual super node
        super_node = 1000000
        self.add_node(super_node)

        # connect super node to all nodes that don't have a provider through c2p
        for np_node in self.no_provider_nodes:
            self.add_edge(super_node, np_node, relationship=-1, as1=super_node, as2=np_node)

        qnode = namedtuple('Node', 'asn path')

        q = list()
        q.append(qnode(super_node, list()))

        visited = list()

        num_deleted_edges = 0
        j = 0
        while q:
            node = q.pop()

            # debug output
            if node.asn in self.no_provider_nodes:
                j += 1
                print str(j) + "/" + str(len(self.no_provider_nodes))

            # update list of visited nodes and copy it
            if node.path:
                path = list(node.path)
            else:
                path = list()

            path.append(node.asn)
            visited.append(node.asn)

            # first we mark backedges and after checking all neighbors, we remove them
            edges_to_remove = []

            for neighbor in nx.all_neighbors(self, node.asn):
                edge_data = self.get_edge_data(node.asn, neighbor)
                # node is a customer of neighbor - only follow provider to customer links
                if edge_data["relationship"] == -1 and edge_data["as1"] == node.asn:
                    # if we see a backedge, mark it and continue search
                    if neighbor in path:
                        edges_to_remove.append((node.asn, neighbor))
                    # if we haven't looked at this node yet, we add it to the list of nodes
                    elif neighbor not in visited:
                        q.append(qnode(neighbor, list(path)))

            # remove the marked edges
            for edge in edges_to_remove:
                num_deleted_edges += 1
                self.remove_edge(edge[0], edge[1])

        # Remove virtual node and all edges
        for np_node in self.no_provider_nodes:
            self.remove_edge(super_node, np_node)
        self.remove_node(super_node)

        print "Removed " + str(num_deleted_edges) + " backedges"

    def c2p_connection(self, u, v):
        """
        Checks if a pure c2p connection exists between nodes u and v
        :param u: asn
        :param v: asn
        :return: True if c2p connection exists, else False
        """
        qnode = namedtuple('Node', 'asn path_type')

        q = list()
        q.append(qnode(u, -1))

        visited = defaultdict(int)

        while q:
            node = q.pop()
            visited[node.asn] = 1

            if self.has_node(node.asn):
                for neighbor in nx.all_neighbors(self, node.asn):
                    if visited[neighbor] != 1:
                        edge_data = self.get_edge_data(node.asn, neighbor)

                        # c2p - p2c link
                        if edge_data["relationship"] == -1:
                            if node.path_type == -1:
                                path_type = 0 if node.asn == edge_data["as2"] else 1
                            else:
                                path_type = node.path_type
                            # c2p
                            if (node.asn == edge_data["as2"] and path_type == 0)\
                                    or (node.asn == edge_data["as1"] and path_type == 1):
                                if neighbor == v:
                                    return True, -1 if path_type == 0 else 1
                                q.append(qnode(neighbor, path_type))
        return False, None


''' main '''
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to CAIDA topology file')

    args = parser.parse_args()

    print "-> Build Topology"
    tmp_start = time.clock()
    as_topo = ASTopo(args.path, 0)
    print "--> Execution Time: " + str(time.clock() - tmp_start) + "s\n"

    nx.write_gpickle(as_topo, 'caida_as_graph.gpickle')
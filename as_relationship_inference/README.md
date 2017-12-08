## [On Inferring Autonomous System Relationships in the Internet](http://portal.acm.org/citation.cfm?id=504616)
Lixin Gao, IEEE/ACM Transactions on Networking, December 2001.

Very first AS relationship inference paper. The inference is based on the assumption that ASes with a higher degree 
(more connections) are higher in the hierarchy. In the inference, always the node with the highest degree (top provider) 
is chosen. All edges before that node are customer-to-provider, all edges after are provider-to-customer. In addition, 
edges that provide transit in both directions are labelled as sibling-to-sibling edges. There exists a basic and a 
refined algorithm. The refined algorithm differs in the sense that it is more stable to noise. As a last part there is
a last algorithm to infer peer-to-peer edges. Only the two edges of the top provider are considered and only if the node
degree of one of the neighbors and the top provider is similar, the edge is considered to be a peer-to-peer edge.

The algorithms are evaluated using data from AT&T. They check if their inference of AT&T's edges is aligned with the
actual peerings of AT&T.

All the algorithms of the paper are implemented in `gao_algorithms.py`.

# TODO: ADD HOW TO USE IT

## [Characterizing the Internet Hierarchy from Multiple Vantage Points](http://ieeexplore.ieee.org/xpls/abs_all.jsp?isnumber=21922&arnumber=1019307)
Lakshminarayanan Subramanian, Sharad Agarwal, Jennifer Rexford, and Randy H. Katz, IEEE INFOCOM, 2002.

In contrast to Gao, they take BGP routing tables from multiple vantage points to get a (more) complete view of the 
Internet. Each vantage point provides a partial view. They define the Type-of-Relationship problem (ToR):

> Given an undirected graph *G* with vertex set *V* and edge set *E* and a set of paths *P*, label the edges in *E* as
either -1, 0 or +1 yo maximize the number of *valid* paths in *P*.

*G* represents the entire Internet topology where each node is an AS and each edges represents a relationship between
the incident pair of ASes. *P* consists of all paths seen from the various vantage points. It is an NP-complete problem
(other works proofed this).

Their algorithm only infers customer-to-provider and peer-to-peer relationships.

For each vantage point, they build a tree using all the paths of that vantage point. The vantage point AS is the root of
the directed graph. Then, the tree is iteratively processed by assigning all the leaf nodes the current rank, removing
them from the graph, increasing the rank and repeating the process until the root is reached. Each AS can get a rank 
from each vantage point. By combining the data of all vantage points, each AS gets a rank vector. 

This rank vector is then used to infer the relationships. There are always two rules per relationship inference:
for peer-to-peer there are the equivalence and probabilistic equivalence rules; for provider-to-customer there are 
dominance and probabilistic dominance rules.

The equivalence rules look at how similar the rank vectors of two adjacent ASes are. If they are equal or very similar,
then a peer-to-peer relationship is inferred. The dominance rules look at whether one AS dominates another one. If one 
has always (or often) a higher rank than the other, a provider-to-customer relationship is inferred.

First the two normal, then the two probilistic rules are applied. A few AS relationships remain unlabeled.

As evaluation methods they propose four options:

1. The number of invalid paths;
2. Compare output to other inference algorithms;
3. Compare output to routing policies archived in the [Routing Arbiter Database (RADB)](https://www.radb.net)
4. Compare output with proprietary data of individual ASes

They choose to use the first option.

All the algorithms of the paper are implemented in `sark_algorithms.py`.


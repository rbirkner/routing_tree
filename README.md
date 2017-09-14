# Routing Tree

Scripts to compute the paths in the Internet using the 
[CAIDA AS Relationships Dataset](http://www.caida.org/data/as-relationships/)
following the routing tree algorithm as described in the appendix B.1 of 
["How Secure are Secure Interdomain Routing Protocols"](http://www.cs.yale.edu/homes/schapira/BGPAttack.pdf)
which takes the Gao-Rexford route preferences and exportation policies into account.


## Creating the AS Level Graph
First, you will need to build a graph based on the AS relationship dataset. Download a relationship dataset from the
 following website: [CAIDA Data Server](http://data.caida.org/datasets/as-relationships/). Then, use the `topo_builder.py`
script with the path to the file containing the AS relationship dataset to build the graph:

```bash
$ python topo_builder.py path_to_file
```

The graph will be stored in a file called `caida_as_graph.gpickle`.

## Computing all the Paths

Now, you can run the routing tree algorithm to compute the paths. Depending on what you are interested in, you might
want to tweak the script a bit.

First, I will go through the python script computing all paths and its arguments. Then, I will quickly explain how to
run it in parallel to speed up the computation.

### The Script

```bash
$ python bgp_paths.py rank size graph outpath destination rib_asns
```

* __rank__ id of that instance (for running multiple instances in parallel)
* __size__ total number of instances
* __graph__ path to the graph file from the previous step
* __outpath__ path to where the output should be stored
* __destination__ -1 if you want to compute the path to all ASes, else path to a file that contains a list of all ASNs 
that should be used as destinations (json)
* __rib_asns__ -1 if you want to keep the RIB of every AS, else path to a file that conatins a list of all ASNs of which
the RIB should be stored (json)

### Running It

I have prepared a bash script to run multiple instances of the script in parallel:

```bash
$ bash paths.sh
```

In this file, you have a few parameters which you need to fix:

* __GRAPHFILE__ - path to the graph file from the previous step
* __OUTPATH__ - path to where the output should be stored
* __DESTINATIONS__ - -1 if you want to compute the path to all ASes, else path to a file that contains a list of all ASNs 
that should be used as destinations (json)
* __RIBS__ - -1 if you want to keep the RIB of every AS, else path to a file that conatins a list of all ASNs of which
the RIB should be stored (json)
* __END__ - number of instances of the script to run

### Merging All the Output

Each instance will create one file `paths-ID.log` where ID is the id of that instance. In the end, you will have to 
merge all of these files. This can be done using `cat`

```bash
$ cat paths-* > paths.log
```

## Create Actual RIBS

Now, you have the AS paths from the RIB ASes to all destination ASes. To create files containing for each prefix in the
Internet an entry with the matching AS path, you can use yet another script: `create_rib.py`.

```bash
$ python bgp_paths.py asns paths_file rib_file
```

* __asns__ - comma separated list of ASNs of which the RIB should be created
* __paths_file__ - path to the file containing all the paths
* __rib_file__ - help='path to a complete rib obtained through bgpstream


#!/bin/bash

GRAPHFILE=xyz.zyx
OUTPATH=./
DESTINATIONS=asfj.asdf
RIBS=asfj.asdf

END=12

pidArr=()
for i in $(seq 0 $END); do
    python ~/GitHub/bgp_policy_learning/new_learning/caida_graph/bgp_paths.py "$i" "$END" "$GRAPHFILE" "$OUTPATH" "$DESTINATIONS" "$RIBS" > ~/output.log 2>&1 &
    pidArr+=($!)
done

for j in "${pidArr[@]}"; do
    wait j
done

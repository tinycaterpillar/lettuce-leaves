#!/bin/bash

ulimit -v 8000000  # Around 8GB

seq 0 178 | parallel -j 20 \
    --timeout 60m \
    --nice 19 \
    "ionice -c3 python M_reachable_from_non_cut_vertex.py -i {}"

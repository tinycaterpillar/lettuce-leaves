#!/bin/bash

ulimit -v 8000000  # Around 8GB

seq 0 1741 | parallel -j 24 \
    --timeout 60m \
    --nice 19 \
    "ionice -c3 python M_constrained_spanning_tree.py -i {}"

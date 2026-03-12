#!/bin/bash

ulimit -v 8000000  # Around 8GB

seq 0 487 | parallel -j 10 \
    --timeout 30m \
    --nice 19 \
    "ionice -c3 python path_starting_vertex.py -i {}"

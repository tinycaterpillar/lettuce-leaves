#!/bin/bash

ulimit -v 8000000  # Around 8GB

seq 0 355 | parallel -j 20 \
    --timeout 60m \
    --nice 19 \
    "ionice -c3 python path_starting_vertex.py -i {}"

#!/bin/bash

ulimit -v 8000000  # Around 8GB

seq 0 1294 | parallel -j 10 \
    --timeout 30m \
    --nice 19 \
    "ionice -c3 python Count_oriented_path.py -i {}"

#!/bin/bash
ulimit -v 8000000 # 8GB
seq 0 42 | xargs -n 1 -P 10 timeout 600s python Labeled_oriented_path.py -i

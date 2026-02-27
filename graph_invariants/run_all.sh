#!/bin/bash
seq 0 1661 | xargs -n 1 -P 15 python check_antidirected_path.py -i

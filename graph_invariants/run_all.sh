#!/bin/bash
seq 0 1661 | xargs -n 1 -P 10 python main.py -i
# seq 0 1 | xargs -n 1 -P 10 python main.py -i

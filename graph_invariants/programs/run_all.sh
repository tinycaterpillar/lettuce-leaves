#!/bin/bash
seq 0 1661 | xargs -n 1 -P 15 python Hamiltonian_cycle.py -i

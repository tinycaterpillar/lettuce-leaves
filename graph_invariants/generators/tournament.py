from sage.all import *

from utils import encode

def get_tournament(n):
    return digraphs.tournaments_nauty(Integer(n))


if __name__ == "__main__":  
    get_tournament(3)
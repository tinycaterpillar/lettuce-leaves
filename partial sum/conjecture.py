from fractions import Fraction as frac

def f(poly, n):
    ret = 0
    for degree, coefficient in enumerate(poly):
        ret += coefficient*pow(n, degree)
    return ret

def verify(poly):
    poly_degree = len(poly)-1
    sigma_degree = poly_degree - 1
    sum = 0
    k = 1
    for n in range(1, poly_degree+2): # verify by interpolation formula
        sum += pow(k, sigma_degree)
        if f(poly, n) != sum: return False
        k += 1

    return True

def integral(poly):
    poly_degree = len(poly)-1
    sigma_degree = poly_degree - 1

    for degree, coefficient in enumerate(poly[1:], 1):
        poly[degree] = poly[degree]*poly_degree/(degree+1)

    poly = [0] + poly

    c = frac(1, 1)
    for coefficient in poly[2:]:
        c -= coefficient
    poly[1] = c

    return poly

nex = [0, frac(1, 2), frac(1, 2)] # denote 1/2*n + 1/2*n^2
for e in range(1, 10000):
    print(f"Verifing f(n) relative to sigma k^{e}")
    print(verify(nex), nex)
    nex = integral(nex)
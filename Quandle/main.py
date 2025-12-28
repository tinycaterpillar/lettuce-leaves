from sage.all import *
from solver import QuandleColoringSAT, SatStatus
from utils import read_quandles, show_PD1_PD2

# PD notation for two diagrams (pd1, pd2)
pd1 = [[7, 1, 8, 26], [1, 19, 2, 18], [17, 3, 18, 2], [3, 17, 4, 16],
       [13, 5, 14, 4], [5, 13, 6, 12], [19, 7, 20, 6], [25, 9, 26, 8],
       [9, 23, 10, 22], [21, 11, 22, 10], [11, 21, 12, 20], [14, 23, 15, 24],
       [24, 15, 25, 16]]

pd2 = [[3, 1, 4, 26], [1, 14, 2, 15], [13, 2, 14, 3], [21, 4, 22, 5],
       [5, 20, 6, 21], [25, 7, 26, 6], [7, 25, 8, 24], [19, 8, 20, 9],
       [9, 22, 10, 23], [15, 11, 16, 10], [11, 17, 12, 16], [17, 13, 18, 12],
       [23, 18, 24, 19]]

# Iterate over all quandles from file
for qunadle in read_quandles("simple_quandles.dat"):

    # Solve Q-colorability for each diagram
    sat1, knot1, color1 = QuandleColoringSAT(pd1, qunadle).solve()
    sat2, knot2, color2 = QuandleColoringSAT(pd2, qunadle).solve()

    # Case 1: pd1 is Q-colorable, pd2 is not
    if sat1 == SatStatus.SAT and sat2 == SatStatus.UNSAT:
        # Save colored pd1 and uncolored pd2
        knot1.plot(color=color1, gap=0.2, thickness=2).save("pd1.png")
        knot2.plot(gap=0.2, thickness=2).save("pd2_nocolor.png")

        # Display them side by side
        print(f"Use quandle of size: {len(qunadle)}")
        show_PD1_PD2("pd1.png", "pd2_nocolor.png")
        break

    # Case 2: pd2 is Q-colorable, pd1 is not
    elif sat1 == SatStatus.UNSAT and sat2 == SatStatus.SAT:
        knot1.plot(gap=0.2, thickness=2).save("pd1_nocolor.png")
        knot2.plot(color=color2, gap=0.2, thickness=2).save("pd2.png")
        
        print(f"Use quandle of size: {len(qunadle)}")
        show_PD1_PD2("pd1_nocolor.png", "pd2.png")
        break

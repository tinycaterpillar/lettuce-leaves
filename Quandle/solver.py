from itertools import combinations
from enum import Enum, auto

from pysat.formula import CNF, IDPool
from pysat.solvers import Cadical195
from pysat.card import CardEnc
from sage.all import Knot

class SatStatus(Enum):
    SAT = auto()
    UNSAT = auto()
    TIMEOUT = auto()
    ERROR = auto()

class QuandleColoringSAT:
    """
    Strand-based SAT quandle coloring solver.

    Given:
        - A planar diagram PD of a knot, written as crossings [a, b, c, d]
        - A finite quandle table Q (n × n)

    We:
        1) Build a Knot from PD
        2) Use K.arcs(presentation='pd') to get strands (each is a list of PD labels)
        3) Create SAT variables for (strand, color)
        4) Encode quandle rules at each crossing in terms of strand colors
    """

    def __init__(self, pd, quandle, solver=Cadical195):
        """
        pd      : list of crossings [a, b, c, d]
        quandle : n × n operation table representing x ▷ y
        solver  : PySAT solver class
        """
        self.pd = pd
        self.n_arcs =  max(max(crossing) for crossing in self.pd) # number of arcs
        self.Q = quandle
        self.n = len(quandle)
        self.pool = IDPool()
        self.solver = solver

        # Build Knot object and extract "strands" from PD
        # Each strand is a list of PD labels (the quandle-coloring arcs)
        self.knot = Knot(self.pd)
        self.strands = self.knot.arcs(presentation='pd')   # e.g. [[1,7,2,6], [3,17,4,16], ...]

        # Map each PD label e to the strand index it belongs to
        self.label_to_strand = {}
        for s_id, seg in enumerate(self.strands):
            for e in seg:
                self.label_to_strand[e] = s_id

        self.num_strands = len(self.strands)

        # Build CNF containing all static constraints
        self.cnf_base = self._build_base()

    # SAT variable: strand s has color c
    def var(self, strand_id, color):
        return self.pool.id(("strand_color", strand_id, color))

    def _add_crossing_rule(self, cnf, a, b, c, d):
        """
        PD crossing {a, b, c, d}:

            a → c : under strand
            
            if b+1 ≡ d (mod n_arcs) then b → d : over strand
            if d+1 ≡ b (mod n_arcs) then d → b : over strand
        
            alpha = over-in
            beta  = under-out if b+1 ≡ d (mod n_arcs)
            gamma = under-in if b+1 ≡ d (mod n_arcs)
            (swap beta, gamma if d+1 ≡ b (mod n_arcs))

        Enforce:
            color(gamma) = color(alpha) ▷ color(beta)
        """

        alpha = self.label_to_strand[b]   # over-in
        beta = self.label_to_strand[c]   # under-out
        gamma = self.label_to_strand[a]   # under-in

        # d → b : over strand
        if (d+1-b)%self.n_arcs == 0: beta, gamma = gamma, beta

        for x in range(1, self.n + 1):        # color(alpha)
            for y in range(1, self.n + 1):    # color(beta)
                z = self.Q[x - 1][y - 1]      # x * y

                cnf.append([
                    -self.var(alpha, x),
                    -self.var(beta, y),
                    self.var(gamma, z)
                ])

    # Build base CNF: strand one-hot + all crossing constraints
    def _build_base(self):
        cnf = CNF()

        # 1) One-hot constraints for every strand
        for s_id in range(self.num_strands):
            am1 = CardEnc.equals(lits=[self.var(s_id, c) for c in range(1, self.n + 1)], bound=1, encoding=1, top_id=self.pool.top)
            self.pool.top = am1.nv  # update top_id
            cnf.extend(am1.clauses)
        
        # 2) Exclude trivial coloring (all strands same color)  
        for c in range(1, self.n + 1):
            clause = [-self.var(s_id, c) for s_id in range(self.num_strands)]
            cnf.append(clause)

        # 3) Quandle equations for every crossing (PD entry)
        for (a, b, c, d) in self.pd:
            self._add_crossing_rule(cnf, a, b, c, d)

        return cnf

    # Solve once, return (Knot, strand_color_for_plot)
    def solve(self):
        cnf = CNF()
        cnf.extend(self.cnf_base.clauses)

        with self.solver(bootstrap_with=cnf.clauses) as s:
            if not s.solve():
                print("No quandle coloring exists.")
                return SatStatus.UNSAT, self.knot, None
            model = set(s.get_model())

        # Extract chosen color for each strand
        strand_color = {}
        for s_id in range(self.num_strands):
            for c in range(1, self.n + 1):
                if self.var(s_id, c) in model:
                    strand_color[s_id] = c
                    break

        # Convert to the format Knot.plot(color=...) expects:
        # color: { tuple_of_PD_labels (strand) -> color_index }
        color_for_plot = {}
        for s_id, seg in enumerate(self.strands):
            color_for_plot[tuple(seg)] = strand_color[s_id]

        # self.knot is already built
        return SatStatus.SAT, self.knot, color_for_plot

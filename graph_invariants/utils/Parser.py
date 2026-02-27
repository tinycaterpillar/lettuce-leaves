import re

def parse_kissat_output(output: str, quick: bool = False):
    """
    Parse kissat stdout.
    Returns: sat (bool), model (set[int])
    """
    sat = False
    model = set()

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("s "):
            if "UNSAT" in line:
                return False, set()
            if "SAT" in line:
                sat = True
                if quick:
                    return True, set()
            else:
                raise RuntimeError(f"Unknown kissat status line: {line}")

        elif sat and not quick and line.startswith("v "):
            for token in line.split()[1:]:
                lit = int(token)
                if lit == 0: break
                if lit > 0:
                    model.add(lit)

    return sat, model


def parse_adjacency_matrix(m):
    rows = []
    for line in m.strip().split('\n'):
        row = [int(x) for x in re.findall(r'\d+', line)]
        if row:
            rows.append(row)
    return rows

if __name__ == "__main__":
    s = """[0 0 1 0 0 1 1 0 0]
    [1 0 0 0 0 0 0 1 1]
    [0 1 0 0 0 0 0 1 1]
    [1 1 0 0 0 0 0 1 0]
    [1 1 0 0 0 0 0 0 1]
    [0 0 1 1 1 0 0 0 0]
    [0 0 1 1 1 0 0 0 0]
    [0 0 0 0 1 1 1 0 0]
    [0 0 0 1 0 1 1 0 0]
    """
    print(parse_adjacency_matrix(s))


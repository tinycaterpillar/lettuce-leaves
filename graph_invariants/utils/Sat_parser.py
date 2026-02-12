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
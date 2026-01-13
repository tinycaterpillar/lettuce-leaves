import os
import time

from utils import TIGHT_DIR, REDUCIBLE_DIR, clear_dir
from A import solve

ALPHA_TARGET = 6.0

def move_tight_to_reducible():
    """
    Append files from TIGHT_DIR into REDUCIBLE_DIR.
    Source files are deleted. No deduplication.
    """
    os.makedirs(REDUCIBLE_DIR, exist_ok=True)
    moved = 0

    for fn in os.listdir(TIGHT_DIR):
        src = os.path.join(TIGHT_DIR, fn)
        dst = os.path.join(REDUCIBLE_DIR, fn)

        if not os.path.isfile(src):
            continue

        with open(dst, "a") as out, open(src) as inp:
            for line in inp:
                out.write(line)

        os.remove(src)
        moved += 1

    return moved


def main():
    iteration = 0

    while True:
        iteration += 1
        print(f"\n===== ITERATION {iteration} =====")

        clear_dir(TIGHT_DIR)

        alpha = solve(verbose=False)
        print(f"alpha = {alpha:.8f}")

        if alpha >= ALPHA_TARGET:
            print("alpha >= target. STOP.")
            break

        moved = move_tight_to_reducible()
        print(f"moved {moved} files to reducible")

        if moved == 0:
            print("no new files. STOP.")
            break

        time.sleep(0.3)


if __name__ == "__main__":
    main()

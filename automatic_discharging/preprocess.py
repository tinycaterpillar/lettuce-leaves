import os
from collections import Counter
from tqdm import tqdm

from utils import REDUCIBLE_DIR

PENDING_DIR = "pending"

def signature(config):
    cnt = Counter(config)
    return tuple(sorted(cnt.items()))


def canonical_config(config):
    return tuple(sorted(config))


def filter_file(input_path, output_path):
    seen = {}
    total = 0

    with open(input_path) as f:
        lines = list(f)

    for line in tqdm(lines, desc=os.path.basename(input_path)):
        if not line.strip():
            continue
        total += 1

        config = list(map(int, line.split()))
        sig = signature(config)

        if sig not in seen:
            seen[sig] = canonical_config(config)

    with open(output_path, "w") as out:
        for cfg in seen.values():
            out.write(" ".join(map(str, cfg)) + "\n")

    return total, len(seen)


if __name__ == "__main__":
    grand_total_before = 0
    grand_total_after = 0

    for fn in os.listdir(PENDING_DIR):
        if not fn.endswith("-vertex.txt"):
            continue

        input_path = os.path.join(PENDING_DIR, fn)
        output_path = os.path.join(
            PENDING_DIR,
            fn.replace("-vertex.txt", "-vertex_filtered.txt")
        )

        before, after = filter_file(input_path, output_path)
        grand_total_before += before
        grand_total_after += after

        print(f"{fn}: {before} -> {after}")

    print("-" * 40)
    print(f"TOTAL: {grand_total_before} -> {grand_total_after}")

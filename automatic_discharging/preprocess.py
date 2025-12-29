import os

SRC_DIR = "."
DST_DIR = "reducible"
os.makedirs(DST_DIR, exist_ok=True)

def has_3_alternating_cycle(deg):
    """
    길이 4 cycle에서
    3-vertex가 하나 건너 등장 (3-* -3-*)
    """
    n = len(deg)
    if n < 3:
        return False

    # k 포함 cycle: (i, i+1, i+2)
    for i in range(n):
        if deg[i] == 3 and deg[(i + 2) % n] == 3:
            return True

    # k 미포함 cycle: (i, i+1, i+2, i+3)
    if n >= 4:
        for i in range(n):
            if deg[i] == 3 and deg[(i + 2) % n] == 3:
                return True

    return False


for fname in os.listdir(SRC_DIR):
    if not fname.endswith("-vertex.txt"):
        continue

    reducible_lines = []

    with open(fname) as f:
        for line in f:
            nums = list(map(int, line.split()))
            deg = nums[::2]   # 이웃 차수만 추출

            if has_3_alternating_cycle(deg):
                reducible_lines.append(line)

    if reducible_lines:
        with open(os.path.join(DST_DIR, fname), "w") as out:
            out.writelines(reducible_lines)



if __name__ == "main.py":
    pass

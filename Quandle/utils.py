import re
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def read_quandles(filename):
    """
    Generator: yields each quandle table from a .dat file.
    Each quandle is returned as a list of lists of ints.
    Mirrors the logic of Perl readquandle().
    """
    with open(filename, "r") as f:
        lines = f.readlines()

    i = 0
    n = len(lines)

    while i < n:
        # skip empty or non-numeric lines
        while i < n and not re.search(r"\d", lines[i]):
            i += 1
        if i >= n:
            break

        # first line of quandle
        row = list(map(int, re.findall(r"\d+", lines[i])))
        size = len(row)
        if size == 0:
            break

        quandle = [row]
        i += 1

        # read next size-1 lines
        for _ in range(size - 1):
            if i >= n:
                raise ValueError("Unexpected EOF while reading quandle")

            row = list(map(int, re.findall(r"\d+", lines[i])))
            if len(row) != size:
                raise ValueError("Quandle corrupted (wrong row size)")

            quandle.append(row)
            i += 1

        # skip separator line
        if i < n:
            i += 1

        yield quandle


def show_PD1_PD2(pd1_path, pd2_path):
    img1 = mpimg.imread(pd1_path)
    img2 = mpimg.imread(pd2_path)

    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    # Left – PD1
    axs[0].imshow(img1)
    axs[0].axis('off')
    axs[0].set_title("PD1")

    # Right – PD2
    axs[1].imshow(img2)
    axs[1].axis('off')
    axs[1].set_title("PD2")

    plt.tight_layout()
    plt.savefig("result.png")
    plt.show()

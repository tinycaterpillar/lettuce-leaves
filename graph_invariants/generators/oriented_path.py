# 0b1011 -> 0b1101
def rev(path, length):
    ret = 0
    for _ in range(length):
        ret <<= 1
        ret |= (path&1)
        path >>= 1
    return ret

# 0b1011 -> 0b0100
def invert(path, length):
    return (path^(2**length-1))

def orbit(path, length):
    r = rev(path, length)
    i = invert(path, length)
    ir = invert(r, length)
    return (path, i, r, ir)

def canonical(path, length):
    return min(orbit(path, length))

def oriented_path(length):
    reps = []
    seen = set()
    for x in range(1 << length):
        c = canonical(x, length)
        if c not in seen:
            seen.add(c)
            reps.append(c)
    return reps

def oriented_path_string(length):
    ret = []
    for p in oriented_path(length):
        tmp = (1<<(length-1))
        s = []
        for _ in range(length):
            s.append('←' if (tmp&p) else '→')
            tmp >>= 1
        ret.append("".join(s))
    return ret


if __name__ == "__main__":
    for i in range(1, 11):
        print(len(oriented_path(i)))
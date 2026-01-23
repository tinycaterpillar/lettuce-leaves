from itertools import product

BASE_DIR = "./pending/"
vertices = [5, 6, 7, 8]
faces = [3, 4]

def canonical_form(config):
    k = len(config) // 2
    ret = config

    rev = [x for f, v in zip(config[-2::-2], config[-1::-2]) for x in (f, v)]
    for i in range(k):
        # rotation
        tmp1 = config[2*i:] + config[:2*i]
        # reflextion & rotation
        tmp2 = rev[2*i:] + rev[:2*i]
        ret = min(ret, tmp1, tmp2)

    return tuple(ret)

def generate_configs(k):
    # generate [f1, v1, f2, v2, ..., fk, vk]
    ret = set()

    for pairs in product(product(faces, vertices), repeat=k):
        config = [x for f, v in pairs for x in (f, v)]
        ret.add(canonical_form(config))

    return ret

def config_around_face(k):
    with open(BASE_DIR+f"{k}-face.txt", "w") as f:
        for config in generate_configs(k):
            f.write(" ".join(map(str, config)) + "\n")


def config_around_vertex(k):
    with open(BASE_DIR+f"{k}-vertex.txt", "w") as f:
        for config in generate_configs(k):
            f.write(" ".join(map(str, config)) + "\n")

if __name__ == "__main__":
    # config_around_vertex(5)
    # config_around_vertex(6)
    # config_around_vertex(7)
    # config_around_face(3)
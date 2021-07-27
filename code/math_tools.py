import numpy as np
from numpy.linalg import matrix_rank
import math
from scipy.linalg import block_diag


def get_S(r):
    rx = r[0]
    ry = r[1]
    rz = r[2]
    return np.array([[0, -rz, ry], [rz, 0, -rx], [-ry, rx, 0]])


def get_Hi(hi):
    if hi == "P":
        return np.array([[1, 0, 0, 0, 0, 0]])
    elif hi == "S":
        return np.concatenate((np.identity(4), np.zeros((4, 2))), axis=1)
    else:
        return np.concatenate((np.identity(3), np.zeros((3, 3))), axis=1)


def gen_H(h):
    H_result = get_Hi(h[0])
    for hi in h[1:]:
        Hi_temp = get_Hi(hi)
        Hi_temp = np.concatenate(
            (np.zeros((Hi_temp.shape[0], H_result.shape[1])), Hi_temp), axis=1
        )
        H_result = np.concatenate((H_result, np.zeros((H_result.shape[0], 6))), axis=1)
        H_result = np.concatenate((H_result, Hi_temp), axis=0)
    return H_result


def get_rank(m):
    return matrix_rank(m)


def gen_F(nc, ng=8, mu=0.3):
    S = []
    for k in range(ng):
        sk = np.array(
            [
                1,
                mu * math.cos(2 * k * math.pi / ng),
                mu * math.sin(2 * k * math.pi / ng),
            ]
        )
        S.append(sk)
    S = np.array(S).transpose()

    F = []
    for k in range(ng):
        kk = k + 1 if k != ng - 1 else 0
        Fk = np.cross(S[:, k], S[:, kk])
        F.append(Fk)
    F = np.array(F)
    F = block_diag(*([F] * nc))
    return F

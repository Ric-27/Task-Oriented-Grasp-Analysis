from __future__ import annotations
import os, sys
import numpy as np
from numpy.linalg import matrix_rank
from scipy.linalg import null_space
from typing import List

sys.path.append(os.path.dirname(__file__))
from data_types import Contact


def get_S(r):
    rx = r[0]
    ry = r[1]
    rz = r[2]
    return np.array([[0, -rz, ry], [rz, 0, -rx], [-ry, rx, 0]])


def get_rank(m):
    return matrix_rank(m)


def block_diag(values):
    result = values[0]
    for value in values[1:]:
        existing_rows_zeros = np.zeros((result.shape[0], value.shape[1]))
        new_row_zeros = np.zeros((value.shape[0], result.shape[1]))
        new_row = np.concatenate((new_row_zeros, value), axis=1)
        result = np.concatenate((result, existing_rows_zeros), axis=1)
        result = np.concatenate((result, new_row), axis=0)
    return result


def check_equal_matrices(a, b):
    if a.shape[0] != b.shape[0] and a.shape[1] != b.shape[1]:
        return False
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            if a[i, j] != b[i, j]:
                return False
    return True


def check_equal_vectors(a, b):
    # print("{} == {}".format(a, b))
    if a.shape[0] != b.shape[0]:
        return False
    for i in range(a.shape[0]):
        if a[i] != b[i]:
            return False
    return True


def list_to_vertical_matrix(list_):
    """
    for i in range(len(list_)):
        if i == 0:
            base = list_[0].shape[1]
        assert base == list_[i].shape[1], "dim 1 must be the same for all elements"
    """
    result = np.array(list_[0])
    for value in list_[1:]:
        result = np.concatenate((result, value), axis=0)
    return result


def get_H_and_l(contact_points: List[Contact]) -> Tuple(np.ndarray, int):
    hi = []
    l = 0
    for contact in contact_points:
        hi.append(contact.h)
        l += contact.l
    return block_diag(hi), l


def is_nullspace_trivial(matrix: np.ndarray) -> bool:
    ns_m = null_space(matrix).round(2)
    if ns_m.size > 0 and ns_m.any() != 0:
        ns_m *= np.sign(ns_m[0, 0])
        ns_m1d = ns_m.flatten()
        for elem in ns_m1d:
            if elem != 0:
                return False
    return True


def is_grasp_valid(grasp: "Grasp") -> bool:
    from class_grasp import Grasp

    assert (
        str(type(grasp)).split(".")[-1] == str(Grasp).split(".")[-1]
    ), "\033[91m {}\033[00m".format("grasp argument must be of type Grasp")

    G = grasp.get_Gt().transpose()
    if get_rank(G) != 6:
        return False
    if not grasp.graspable:
        return False
    for contact in grasp.contact_points:
        if contact.type != "HF":
            return False
    return True


def main():
    val = (
        __file__.replace(os.path.dirname(__file__), "")[1:]
        + " is meant to be imported not executed"
    )
    print(f"\033[91m {val}\033[00m")


if __name__ == "__main__":
    main()

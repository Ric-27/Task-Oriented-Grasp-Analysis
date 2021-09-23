import os, sys
import numpy as np
from numpy.linalg import matrix_rank
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


def get_H_and_l(contact_points: List[Contact]):
    hi = []
    l = 0
    for contact in contact_points:
        hi.append(contact.h)
        l += contact.l
    return block_diag(hi), l

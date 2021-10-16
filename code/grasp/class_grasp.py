from __future__ import annotations
import os, sys
import numpy as np

sys.path.append(os.path.dirname(__file__))
from data_types import Contact
from grasp_functions import (
    block_diag,
    get_S,
    list_to_vertical_matrix,
    get_H_and_l,
    is_nullspace_trivial,
)
from typing import List

np.set_printoptions(suppress=True)


class Grasp:
    def __init__(self, p: List, contact_points: List[Contact]) -> "Grasp":
        self.p = np.array(p)
        assert contact_points, "There must be contact points to calculate the grasp"
        self.contact_points = contact_points
        self.nc = len(contact_points)
        self.H = np.zeros(1)
        self.l = 0
        self.Gt = np.zeros(1)
        self.indeterminate = True
        self.graspable = False
        self.__updt_H()
        self.__updt_classification()
        self.__updt_Gt()
        self.F = None
        not_hf = False
        for contact in contact_points:
            if contact.type != "HF":
                print(
                    "One or more contact point was not HF, cant use the quality metrics"
                )
                not_hf = True
                break
        if not not_hf:
            self.__updt_F()

    def __updt_F(self):
        fi = []
        for contact in self.contact_points:
            fi.append(contact.F)
        self.F = block_diag(fi)

    def __updt_H(self):
        self.H, self.l = get_H_and_l(self.contact_points)

    def get_Gt(self):
        self.__updt_Gt()
        return self.Gt

    def get_classification(self, print_bool=False):
        self.__updt_classification()
        if print_bool:
            print("-" * 25)
            print("GRASP CLASSIFICATION: ")
            if not self.indeterminate:
                print("Nullspace(Gt): trivial --> Not Indeterminate")
            else:
                print("Nullspace(Gt): not trivial --> Indeterminate")
            if not self.graspable:
                print("Nullspace(G): trivial --> Not Graspable")
            else:
                print("Nullspace(G): not trivial --> Graspable")
        return self.indeterminate, self.graspable

    def __pi(self, ci):
        return np.block(
            [
                [np.identity(3), np.zeros((3, 3))],
                [get_S(ci - self.p), np.identity(3)],
            ]
        )

    def __pGi_t(self, Ri, Pi):
        R = block_diag([Ri, Ri])
        result = np.dot(R.transpose(), Pi.transpose())
        return result

    def __updt_Gt(self):
        pGt = []
        for contact in self.contact_points:
            pGt.append(self.__pGi_t(contact.r, self.__pi(contact.c)))
        pGt = list_to_vertical_matrix(pGt)
        self.Gt = np.dot(self.H, pGt)

    def __updt_classification(self):
        Gt = self.get_Gt()
        G = Gt.transpose()
        self.graspable = not is_nullspace_trivial(G)
        self.indeterminate = not is_nullspace_trivial(Gt)


def main():
    val = (
        __file__.replace(os.path.dirname(__file__), "")[1:]
        + " is meant to be imported not executed"
    )
    print(f"\033[91m {val}\033[00m")


if __name__ == "__main__":
    main()

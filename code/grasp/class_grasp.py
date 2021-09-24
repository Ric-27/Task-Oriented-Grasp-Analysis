import os
import numpy as np
from grasp_functions import (
    block_diag,
    get_S,
    list_to_vertical_matrix,
    get_H_and_l,
    is_nullspace_trivial,
)

np.set_printoptions(suppress=True)


class Grasp:
    def __init__(self, p, contact_points):
        self.p = p
        self.contact_points = contact_points
        self.nc = contact_points.shape[0]
        self.H = np.zeros(1)
        self.Gt = np.zeros(1)
        self.F = None
        self.l = 0
        self.indeterminate = -1
        self.graspable = -1
        self.updt_H()
        self.updt_classification()
        not_hf = False
        for contact in contact_points:
            if contact.type != "HF":
                print(
                    "One or more contact point was not HF, cant use the quality metrics"
                )
                not_hf = True
                break
        if not not_hf:
            self.updt_F()

    def updt_F(self):
        fi = []
        for contact in self.contact_points:
            fi.append(contact.F)
        self.F = block_diag(fi)

    def updt_H(self):
        self.H, self.l = get_H_and_l(self.contact_points)

    def get_Gt(self):
        self.updt_Gt()
        return self.Gt

    def get_classification(self, print_bool=False):
        self.updt_classification()
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

    def updt_Gt(self):
        pGt = []
        for contact in self.contact_points:
            pGt.append(self.__pGi_t(contact.r, self.__pi(contact.c)))
        pGt = list_to_vertical_matrix(pGt)
        self.Gt = np.dot(self.H, pGt)

    def updt_classification(self):
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

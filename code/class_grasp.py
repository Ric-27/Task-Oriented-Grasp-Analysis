import sys
import numpy as np
from scipy.linalg import block_diag, null_space
from math_tools import gen_H, get_S

np.set_printoptions(suppress=True)


class Grasp:
    def __init__(self, p, C, R, h=None):
        assert C.shape[0] == R.shape[0], "C and R must have the number of elements"
        assert (
            R.shape[1] == 3 and R.shape[2] == 3
        ), "Contact Rotation Elements must be 3x3"
        assert C.shape[1] == 3, "Contact Location Elements must be in 3d"
        self.p = p
        self.C = C
        self.R = R
        if not isinstance(h, np.ndarray):
            h = np.array(["H" for _ in range(C.shape[0])])
        else:
            assert (
                h.size == C.shape[0]
            ), "The amount of Contact Model Elements must be the same as Contact Points"
            for hi in h:
                if hi != "S" and hi != "H" and hi != "P":
                    sys.exit(
                        "ERROR: Values inside h must be H for hardfinger, S for softfinger or P for point contact. NOT: {}".format(
                            hi
                        )
                    )
        self.h = h

    def __pi(self, ci):
        return np.block(
            [
                [np.identity(3), np.zeros((3, 3))],
                [get_S(ci - self.p), np.identity(3)],
            ]
        )

    def __pGi_t(self, Ri, Pi):
        R = block_diag(*([Ri] * 2))
        result = np.dot(R.transpose(), Pi.transpose())
        return result

    def get_grasp_matrix_t(self):
        pG = self.__pGi_t(self.R[0], self.__pi(self.C[0])).transpose()
        for i in range(1, self.C.shape[0]):
            pGi = self.__pGi_t(self.R[i], self.__pi(self.C[i])).transpose()
            pG = np.concatenate((pG, pGi), axis=1)

        G_t = np.dot(gen_H(self.h), pG.transpose())
        return G_t

    def get_grasp_classification(self, print_bool=False):
        graspable = True
        indeterminate = True
        Gt = self.get_grasp_matrix_t()
        G = Gt.transpose()

        ns_Gt = null_space(Gt).round(2)
        if ns_Gt.size > 0 and ns_Gt.any() != 0:
            ns_Gt *= np.sign(ns_Gt[0, 0])
            ns_Gt1d = ns_Gt.flatten()
            Zero = True
            for elem in ns_Gt1d:
                if elem != 0:
                    Zero = False
                    break
            if Zero:
                indeterminate = False
            else:
                indeterminate = True
        else:
            indeterminate = False

        ns_G = null_space(G).round(2)
        if ns_G.size > 0 and ns_G.any() != 0:
            ns_G *= np.sign(ns_G[0, 0])
            ns_G1d = ns_G.flatten()
            Zero = True
            for elem in ns_G1d:
                if elem != 0:
                    Zero = False
                    break
            if Zero:
                graspable = False
            else:
                graspable = True
        else:
            graspable = False
        if print_bool:
            print("-" * 25)
            print("GRASP CLASSIFICATION: ")
            if not indeterminate:
                print("Nullspace(Gt): trivial --> Not Indeterminate")
            else:
                print(
                    "Nullspace(Gt): not trivial --> Indeterminate"
                )  # \nN(Gt):\n",ns_Gt)
            if not graspable:
                print("Nullspace(G): trivial --> Not Graspable")
            else:
                print("Nullspace(G): not trivial --> Graspable")  # \nN(G):\n")#,ns_G)
        return indeterminate, graspable

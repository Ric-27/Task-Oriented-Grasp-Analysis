import os
import numpy as np
import math
import sys
from typing import List


class Joint:
    def __init__(
        self, jointID, frameOrigin, unitVectorZ, contact_location=None, revolute=True
    ):
        assert (
            frameOrigin.shape[0] == 3
        ), "Frame Origin Element must be a vector of size [3,1]"
        assert (
            unitVectorZ.shape[0] == 3
        ), "Unit Vector Z Element must be a vector of size [3,1]"
        assert np.sum(unitVectorZ) == 1, "Vector Z must be a unit vector"

        self.joint_id = jointID
        self.joint_origin = frameOrigin
        self.joint_z = unitVectorZ
        self.joint_contact_location = contact_location
        self.joint_revolute = revolute


class Finger:
    def __init__(self, fingerID, joints):
        self.finger_id = fingerID
        self.finger_joints = joints


class Contact:
    def __init__(
        self,
        location: List,
        rotation_matrix: np.ndarray,
        tangential_f_coef: float = 0.3,
        torsional_f_coef: float = 0.2,
        char_len: float = 1,
        number_cone_faces: int = 8,
        adhesive_force: float = 0,
        contact_name: str = "",
    ):
        assert (
            tangential_f_coef >= 0
        ), "Tangential Friction coefficient must be positive"
        assert torsional_f_coef >= 0, "Torsional friction coefficient must be positive"
        assert (
            number_cone_faces >= 3
        ), "Number of cone faces must be greater or equal to 3"
        assert adhesive_force >= 0, "the adhesive force must be positive"
        if not isinstance(location, np.ndarray):
            location = np.array(location)

        self.c = location
        self.r = rotation_matrix
        self.mu = tangential_f_coef
        self.iota = torsional_f_coef
        self.b = char_len
        self.ng = int(number_cone_faces)
        self.fa = adhesive_force
        self.name = contact_name
        self.type = "None"
        self.F = np.zeros((1))

        self.upt_type()

    def upt_type(self):
        if self.mu == 0 and self.iota == 0:
            self.type = "PwoF"
            self.l = 1
            self.h = np.array([[1, 0, 0, 0, 0, 0]])
        elif self.mu > 0 and self.iota == 0:
            self.type = "HF"
            self.l = 3
            self.h = np.concatenate((np.identity(3), np.zeros((3, 3))), axis=1)
            self.upt_cone()
        elif self.mu > 0 and self.iota > 0:
            self.type = "SF"
            self.l = 4
            self.h = np.concatenate((np.identity(4), np.zeros((4, 2))), axis=1)
            self.upt_cone()
        else:
            sys.exit("ERROR: Contact Type Invalid")
        if self.fa != 0:
            self.type += " with Adhesion\n"

    def upt_cone(self):
        S = []
        for k in range(self.ng):
            sk = np.array(
                [
                    1,
                    self.mu * math.cos(2 * k * math.pi / self.ng),
                    self.mu * math.sin(2 * k * math.pi / self.ng),
                ]
            )
            S.append(sk)
        S = np.array(S).transpose()

        F = []
        for k in range(self.ng):
            kk = k + 1 if k != self.ng - 1 else 0
            Fk = np.cross(S[:, k], S[:, kk])
            F.append(Fk)
        self.F = np.array(F)

        if self.type.startswith("SF"):
            self.F = np.concatenate((self.F, np.zeros((self.ng, 1))), axis=1)
            self.F = np.concatenate(
                (
                    self.F,
                    np.array(
                        [[1, 0, 0, self.b * self.iota], [1, 0, 0, -self.b * self.iota]]
                    ),
                )
            )

    def __repr__(self):
        return "<Contact Point at %s of type %s>" % (self.c, self.type)

    def __str__(self) -> str:
        return "Contact Point at {} of type {}".format(self.c, self.type)


def main():
    val = (
        __file__.replace(os.path.dirname(__file__), "")[1:]
        + " is meant to be imported not executed"
    )
    print(f"\033[91m {val}\033[00m")


if __name__ == "__main__":
    main()

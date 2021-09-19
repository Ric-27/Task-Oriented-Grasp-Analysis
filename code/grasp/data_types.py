import numpy as np
import math
import sys


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
        location,
        rotation_matrix,
        tangential_f_coef=0.3,
        torsional_f_coef=0,
        number_cone_faces=8,
    ):
        assert (
            tangential_f_coef >= 0
        ), "Tangential Friction coefficient must be positive"
        assert torsional_f_coef >= 0, "Torsional friction coefficient must be positive"
        assert (
            number_cone_faces >= 3
        ), "Number of cone faces must be greater or equal to 3"
        self.c = location
        self.r = rotation_matrix
        self.mu = tangential_f_coef
        self.iota = torsional_f_coef
        self.ng = int(number_cone_faces)

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
        else:
            sys.exit("ERROR: Contact Type Invalid")

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

    def __repr__(self):
        return "<Contact Point at %s of type %s>" % (self.c, self.type)

    def __str__(self) -> str:
        return "Contact Point at {} of type {}".format(self.c, self.type)

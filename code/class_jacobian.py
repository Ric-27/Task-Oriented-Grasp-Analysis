import sys
import numpy as np
from scipy.linalg import block_diag, null_space
from data_types import Finger
from math_tools import gen_H, get_S

np.set_printoptions(suppress=True)


class Jacobian:
    def __init__(self, fingers, C, R, h=None):
        assert C.shape[0] == R.shape[0], "C and R must have the number of elements"
        assert (
            R.shape[1] == 3 and R.shape[2] == 3
        ), "Contact Rotation Elements must be 3x3"
        assert C.shape[1] == 3, "Contact Location Elements must be in 3d"
        assert isinstance(
            fingers.all(), Finger
        ), "finger elements must be of type Finger"
        self.fingers = fingers
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
        nq = 0
        for finger in self.fingers:
            for _ in finger.finger_joints:
                nq += 1
        self.nq = nq

    def __zi(self, Ci, Cid):
        exit_loop = False
        finger_id = -1
        joint_id = -1
        for finger in self.fingers:
            for joint in finger.finger_joints:
                if joint.joint_contact_id == Cid:
                    finger_id = finger.finger_id
                    joint_id = joint.joint_id
                    exit_loop = True
                    break
            if exit_loop:
                break

        Zi = np.zeros((6, self.nq), dtype=np.float64)
        exit_loop = False

        for finger in self.fingers:
            if finger.finger_id == finger_id:
                for joint in finger.finger_joints:
                    if joint.joint_revolute:
                        dij = np.dot(
                            get_S(Ci - joint.joint_origin).transpose(),
                            joint.joint_z,
                        )
                        lij = joint.joint_z
                    else:
                        dij = joint.joint_z
                        lij = np.zeros((3, 1))
                    Zi[0, joint.joint_id - 1] = dij[0]
                    Zi[1, joint.joint_id - 1] = dij[1]
                    Zi[2, joint.joint_id - 1] = dij[2]
                    Zi[3, joint.joint_id - 1] = lij[0]
                    Zi[4, joint.joint_id - 1] = lij[1]
                    Zi[5, joint.joint_id - 1] = lij[2]
                    if joint_id == joint.joint_id:
                        exit_loop = True
                        break
            if exit_loop:
                break
        return Zi

    def __p_ji(self, Ri, Zi):
        R = block_diag(*([Ri] * 2))
        result = np.dot(R.transpose(), Zi)
        return result

    def get_jacobian_matrix(self):
        pJ = self.__p_ji(self.R[0], self.__zi(self.C[0], 0))
        for i in range(1, self.C.shape[0]):
            pJ = np.concatenate(
                (pJ, self.__p_ji(self.R[i], self.__zi(self.C[i], i))), axis=0
            )
        J = np.dot(gen_H(self.h), pJ)
        return J

    def get_jacobian_classification(self, print_bool=False):
        defective = True
        redundant = True
        J = self.get_jacobian_matrix()
        Jt = J.transpose()
        ns_Jt = null_space(Jt).round(2)
        if ns_Jt.size > 0 and ns_Jt.any() != 0:
            ns_Jt *= np.sign(ns_Jt[0, 0])
            ns_Jt1d = ns_Jt.flatten()
            Zero = True
            for elem in ns_Jt1d:
                if elem != 0:
                    Zero = False
                    break
            if Zero:
                defective = False
            else:
                defective = True
        else:
            defective = False

        ns_J = null_space(J).round(2)

        if ns_J.size > 0 and ns_J.any() != 0:
            ns_J *= np.sign(ns_J[0, 0])
            ns_J1d = ns_J.flatten()
            Zero = True
            for elem in ns_J1d:
                if elem != 0:
                    Zero = False
                    break
            if Zero:
                redundant = False
            else:
                redundant = True
        else:
            redundant = False

        if print_bool:
            print("-" * 25)
            print("JACOBIAN CLASSIFICATION: ")
            if not defective:
                print("Nullspace(Jt): trivial --> Not Defective")
            else:
                print("Nullspace(Jt): not trivial --> Defective")  # \nN(Jt):\n,ns_Jt)
            if not redundant:
                print("Nullspace(J): trivial --> Not Redundant")
            else:
                print(
                    "Nullspace(Jt): not trivial --> Redundant"
                )  # \nN(J):\n")  # ,ns_J)
        return defective, redundant

    def get_hand_architecture(self):
        print("-" * 25)
        print("Hand Architecture")
        print(
            "The hand has {} joints divided in {} fingers".format(
                self.nq, self.fingers.shape[0]
            )
        )
        for finger in self.fingers:
            print("Finger{}: HAND ".format(finger.finger_id), end="")
            for joint in finger.finger_joints:
                if joint.joint_contact_id < 0:
                    print("- q{} ".format(joint.joint_id), end="")
                else:
                    print(
                        "- q{}[C{}({})] ".format(
                            joint.joint_id,
                            joint.joint_contact_id + 1,
                            "HF"
                            if self.h[joint.joint_contact_id] == "H"
                            else "SF"
                            if self.h[joint.joint_contact_id] == "S"
                            else "PwoF",
                        ),
                        end="",
                    )
            print("")

        for finger in self.fingers:
            for j, joint in enumerate(finger.finger_joints, 0):
                if (
                    finger.finger_joints.shape[0] == 1
                    or j == finger.finger_joints.shape[0] - 1
                ):
                    lenght = np.linalg.norm(
                        joint.joint_origin - self.C[joint.joint_contact_id]
                    )
                else:
                    lenght = np.linalg.norm(
                        joint.joint_origin - finger.finger_joints[j + 1].joint_origin
                    )
                lenght = round(lenght, 2)
                print(
                    "q{} \t lenght:{} \t type:{}".format(
                        joint.joint_id,
                        lenght,
                        "revolute" if joint.joint_revolute else "prismatic",
                    )
                )
        print("-" * 25)

import numpy as np
from data_types import Contact, Finger
from scipy.linalg import null_space
from grasp_functions import (
    get_H_and_l,
    get_S,
    check_equal_vectors,
    block_diag,
    list_to_vertical_matrix,
)

np.set_printoptions(suppress=True)


class Jacobian:
    def __init__(self, fingers, contact_points):
        assert isinstance(
            contact_points.all(), Contact
        ), "Contact elements must be of type Contact"
        assert isinstance(
            fingers.all(), Finger
        ), "finger elements must be of type Finger"
        self.fingers = fingers
        self.contact_points = contact_points
        nq = 0
        for finger in self.fingers:
            for _ in finger.finger_joints:
                nq += 1
        self.nq = nq
        self.nc = contact_points.shape[0]
        self.H = np.zeros(1)
        self.J = np.zeros(1)
        self.L = 0
        self.defective = -1
        self.redundant = -1
        self.updt_H()
        self.updt_classification()

    def updt_H(self):
        self.H, self.l = get_H_and_l(self.contact_points)

    def get_J(self):
        self.upt_J()
        return self.J

    def get_classification(self, print_bool=False):
        self.updt_classification()
        if print_bool:
            print("-" * 25)
            print("JACOBIAN CLASSIFICATION: ")
            if not self.defective:
                print("Nullspace(Jt): trivial --> Not Defective")
            else:
                print("Nullspace(Jt): not trivial --> Defective")
            if not self.redundant:
                print("Nullspace(J): trivial --> Not Redundant")
            else:
                print("Nullspace(Jt): not trivial --> Redundant")
        return self.defective, self.redundant

    def __zi(self, Ci):
        exit_loop = False
        finger_id = -1
        joint_id = -1
        for finger in self.fingers:
            for joint in finger.finger_joints:
                if joint.joint_contact_location is not None:
                    if check_equal_vectors(joint.joint_contact_location, Ci):
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
        R = block_diag([Ri, Ri])
        result = np.dot(R.transpose(), Zi)
        return result

    def upt_J(self):
        pJ = []
        for contact in self.contact_points:
            pJ.append(self.__p_ji(contact.r, self.__zi(contact.c)))
        pJ = list_to_vertical_matrix(pJ)
        self.J = np.dot(self.H, pJ)

    def updt_classification(self):
        defective = True
        redundant = True
        J = self.get_J()
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
        self.defective = defective
        self.redundant = redundant

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
                if joint.joint_contact_location is None:
                    print("- q{} ".format(joint.joint_id), end="")
                else:
                    for i, contact in enumerate(self.contact_points, 0):
                        if check_equal_vectors(joint.joint_contact_location, contact.c):
                            contact_id = i
                            break
                    print(
                        "- q{}[C{}({})] ".format(
                            joint.joint_id,
                            contact_id,
                            self.contact_points[contact_id].type,
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
                        joint.joint_origin - joint.joint_contact_location
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

import numpy as np


class Joint:
    def __init__(
        self, jointID, frameOrigin, unitVectorZ, affectedContactIndex, revolute=True
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
        self.joint_contact_id = affectedContactIndex
        self.joint_revolute = revolute


class Finger:
    def __init__(self, fingerID, joints):
        self.finger_id = fingerID
        self.finger_joints = joints

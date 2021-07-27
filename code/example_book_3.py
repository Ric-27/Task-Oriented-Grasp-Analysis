import numpy as np
from class_jacobian import Jacobian
from data_types import Finger, Joint
from class_grasp import Grasp
import math

zv = np.array([0, 0, 1]).reshape(3, 1)

p = np.array([0, 0, 0])

h = np.array(["H", "H", "H"])

l = 2

c1 = np.array([math.cos(math.pi), math.sin(math.pi), 0]) * l

c2 = np.array([math.cos(math.pi / 2), math.sin(math.pi / 2), 0]) * l

c3 = np.array([math.cos(0), math.sin(0), 0]) * l

R1 = np.array(
    [
        [-math.cos(math.pi), math.sin(math.pi), 0],
        [-math.sin(math.pi), -math.cos(math.pi), 0],
        [0, 0, 1],
    ]
)

R2 = np.array(
    [
        [-math.cos(math.pi / 2), math.sin(math.pi / 2), 0],
        [-math.sin(math.pi / 2), -math.cos(math.pi / 2), 0],
        [0, 0, 1],
    ]
)

R3 = np.array(
    [[-math.cos(0), math.sin(0), 0], [-math.sin(0), -math.cos(0), 0], [0, 0, 1]]
)

q1c = np.array([-l, -l, 0])
q2c = np.array([-l, l, 0])
q3c = np.array([l, l, 0])

C = np.array([c1, c2, c3])
R = np.array([R1, R2, R3])

grasp = Grasp(p, C, R, h)

# Gt = grasp.get_grasp_matrix_t()
# print("Gt shape:", Gt.shape)
# print("Gt:\n", Gt)

q1 = Joint(1, q1c, zv, 0)
q2 = Joint(2, q2c, zv, 1)
q3 = Joint(3, q3c, zv, 2)

f1 = Finger(1, np.array([q1, q2, q3]))

f = np.array([f1])

jacobian = Jacobian(f, C, R, h)
J = jacobian.get_jacobian_matrix()

print("J shape:", J.shape)
print("J:\n", J)

# grasp.GraspClassification(True)
jacobian.get_jacobian_classification(True)
jacobian.get_hand_architecture()

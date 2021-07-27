import numpy as np
from scipy.linalg import block_diag, null_space
from class_jacobian import Jacobian
from class_grasp import Grasp
from data_types import Finger, Joint
from math_tools import getRank
from quality_metrics import testForceClosure

zv = np.array([0, 0, 1]).reshape(3, 1)

p = np.array([2, 10, 0])

h = np.array(["H", "H"])

c1 = np.array([6, 10, 0])

c2 = np.array([-3, 10, 0])

c3 = np.array([-7, 5, 0])

R1 = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])

R2 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

R3 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

q1c = np.array([9, 0, 0])
q2c = np.array([8, 6, 0])
q3c = np.array([-8, 0, 0])
q4c = np.array([-8, 3, 0])
q5c = np.array([-6, 7, 0])


def S(r):
    rx = r[0]
    ry = r[1]
    rz = r[2]
    return np.array([[0, -rz, ry], [rz, 0, -rx], [-ry, rx, 0]])


def fHi(h):
    if h == "P":
        return np.array([[1, 0, 0, 0, 0, 0]])
    elif h == "S":
        return np.concatenate((np.identity(4), np.zeros((4, 2))), axis=1)
    else:
        return np.concatenate((np.identity(3), np.zeros((3, 3))), axis=1)


def fH(h):
    H = fHi(h[0])
    for hi in h[1:]:
        Hi = fHi(hi)
        Hi = np.concatenate((np.zeros((Hi.shape[0], H.shape[1])), Hi), axis=1)
        H = np.concatenate((H, np.zeros((H.shape[0], 6))), axis=1)
        H = np.concatenate((H, Hi), axis=0)
    return H


P1 = np.block([[np.identity(3), np.zeros((3, 3))], [S(c1 - p), np.identity(3)]])

P2 = np.block([[np.identity(3), np.zeros((3, 3))], [S(c2 - p), np.identity(3)]])

P3 = np.block([[np.identity(3), np.zeros((3, 3))], [S(c3 - p), np.identity(3)]])

pG1t = np.dot(block_diag(*([R1] * 2)).transpose(), P1.transpose())
pG2t = np.dot(block_diag(*([R2] * 2)).transpose(), P2.transpose())
pG3t = np.dot(block_diag(*([R3] * 2)).transpose(), P3.transpose())
pGt = np.concatenate((pG1t, pG2t), axis=0)
H = fH(h)
# print(H.shape)
Gt = np.dot(H, pGt)
# print(Gt)

C = np.array([c1, c2])
R = np.array([R1, R2])

grasp = Grasp(p, C, R, h)

Gtclass = grasp.get_grasp_matrix_t()

if (Gt == Gtclass).all():
    print("correct implementation of Grasp Class")
else:
    print("ERROR: Gt Matrices are different")

d11 = np.dot(S(c1 - q1c).transpose(), zv)
d12 = np.dot(S(c1 - q2c).transpose(), zv)
d13 = np.array([0, 0, 0]).reshape(3, 1)
d14 = np.array([0, 0, 0]).reshape(3, 1)
d15 = np.array([0, 0, 0]).reshape(3, 1)

l11 = zv
l12 = zv
l13 = np.array([0, 0, 0]).reshape(3, 1)
l14 = np.array([0, 0, 0]).reshape(3, 1)
l15 = np.array([0, 0, 0]).reshape(3, 1)

d21 = np.array([0, 0, 0]).reshape(3, 1)
d22 = np.array([0, 0, 0]).reshape(3, 1)
d23 = np.dot(S(c2 - q3c).transpose(), zv)
d24 = np.dot(S(c2 - q4c).transpose(), zv)
d25 = np.dot(S(c2 - q5c).transpose(), zv)

l21 = np.array([0, 0, 0]).reshape(3, 1)
l22 = np.array([0, 0, 0]).reshape(3, 1)
l23 = zv
l24 = zv
l25 = zv

d31 = np.array([0, 0, 0]).reshape(3, 1)
d32 = np.array([0, 0, 0]).reshape(3, 1)
d33 = np.dot(S(c3 - q3c).transpose(), zv)
d34 = np.dot(S(c3 - q4c).transpose(), zv)
d35 = np.array([0, 0, 0]).reshape(3, 1)

l31 = np.array([0, 0, 0]).reshape(3, 1)
l32 = np.array([0, 0, 0]).reshape(3, 1)
l33 = zv
l34 = zv
l35 = np.array([0, 0, 0]).reshape(3, 1)

d1 = np.concatenate((d11, d12, d13, d14, d15), axis=1)
l1 = np.concatenate((l11, l12, l13, l14, l15), axis=1)
Z1 = np.concatenate((d1, l1), axis=0)

d2 = np.concatenate((d21, d22, d23, d24, d25), axis=1)
l2 = np.concatenate((l21, l22, l23, l24, l25), axis=1)
Z2 = np.concatenate((d2, l2), axis=0)

d3 = np.concatenate((d31, d32, d33, d34, d35), axis=1)
l3 = np.concatenate((l31, l32, l33, l34, l35), axis=1)
Z3 = np.concatenate((d3, l3), axis=0)

pJ1 = np.dot(block_diag(*([R1] * 2)).transpose(), Z1)
pJ2 = np.dot(block_diag(*([R2] * 2)).transpose(), Z2)
pJ3 = np.dot(block_diag(*([R3] * 2)).transpose(), Z3)

pJ = np.concatenate((pJ1, pJ2), axis=0)
J = H @ pJ

q1 = Joint(1, q1c, zv, -1)
q2 = Joint(2, q2c, zv, 0)
q3 = Joint(3, q3c, zv, -1)
q4 = Joint(4, q4c, zv, -1)
q5 = Joint(5, q5c, zv, 1)

f1 = Finger(1, np.array([q1, q2]))
f2 = Finger(2, np.array([q3, q4, q5]))

f = np.array([f1, f2])

jacobian = Jacobian(f, C, R, h)
Jclass = jacobian.getJ()

if (J == Jclass).all():
    print("correct implementation of Jacobian Class")
else:
    print("ERROR: J Matrices are different")


print("Gt: \n", grasp.getGt())
grasp.GraspClassification(True)
print("Rank G:", getRank(Gtclass.transpose()))

print("*" * 25)

print("J: \n", Jclass)
jacobian.JacobianClassification(True)
print("Rank J:", getRank(Jclass))
jacobian.printHandSpecifications()


ns_G = null_space(Gt.transpose())
ns_Jt = null_space(J.transpose())

"""if np.intersect1d(ns_G, ns_Jt).all() == 0:
    print("Force Closure Exists")
else:
    print("Force Closure Doesn't Exists")
"""
testForceClosure(grasp, jacobian)

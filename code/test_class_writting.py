import numpy as np
from scipy.linalg import block_diag, null_space
from class_jacobian import Jacobian
from class_grasp import Grasp
from data_types import Finger, Joint, Contact
from math_tools import get_rank, check_equal_matrices
from quality_metrics import force_closure

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
contact1 = Contact(c1, R1)
contact2 = Contact(c2, R2)
C = np.array([contact1, contact2])

grasp = Grasp(p, C)

Gtclass = grasp.Gt

if check_equal_matrices(Gt, Gtclass):
    print("correct writting of Grasp Class")
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
Jnoob = H @ pJ

q1 = Joint(1, q1c, zv)
q2 = Joint(2, q2c, zv, c1)
q3 = Joint(3, q3c, zv)
q4 = Joint(4, q4c, zv)
q5 = Joint(5, q5c, zv, c2)

f1 = Finger(1, np.array([q1, q2]))
f2 = Finger(2, np.array([q3, q4, q5]))

f = np.array([f1, f2])

jacobian = Jacobian(f, C)
Jclass = jacobian.J

if check_equal_matrices(Jnoob, Jclass):
    print("correct implementation of Jacobian Class")
else:
    print("ERROR: J Matrices are different")

print("Gt: \n", Gtclass)
grasp.get_classification(True)
print("Rank G:", get_rank(Gtclass.transpose()))

print("*" * 25)
jacobian.get_classification(True)
print("Rank J:", get_rank(Jclass))
jacobian.get_hand_architecture()


ns_G = null_space(Gt.transpose())
ns_Jt = null_space(Jnoob.transpose())

force_closure(grasp, jacobian)

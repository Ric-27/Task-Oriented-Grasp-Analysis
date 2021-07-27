import numpy as np
from Jacobian import Jacobian
from data_types import Finger, Joint

xv = np.array([1, 0, 0]).reshape(3, 1)
yv = np.array([0, 1, 0]).reshape(3, 1)
zv = np.array([0, 0, 1]).reshape(3, 1)

h = np.array(["H"])

l0 = 1
l1 = 1
l2 = 1
l3 = 1

c1 = np.array([0, 0, l0 + l1 + l2 + l3])

R1 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

C = np.array([c1])
R = np.array([R1])

q1c = np.array([0, 0, 0])
q2c = np.array([0, 0, 0])
q3c = np.array([0, 0, l0])
q4c = np.array([0, 0, l0])
q5c = np.array([0, 0, l0 + l1])
q6c = np.array([0, 0, l0 + l1 + l2])

q1 = Joint(1, q1c, xv, -1, False)  # q1
q2 = Joint(2, q2c, yv, -1, False)  # q2
q3 = Joint(3, q3c, zv, -1)  # q3
q4 = Joint(4, q4c, xv, -1)  # q4
q5 = Joint(5, q5c, xv, -1)  # q7
q6 = Joint(6, q6c, xv, 0)  # q10

f1 = Finger(1, np.array([q1, q2, q3, q4, q5, q6]))
f = np.array([f1])

Jacob = Jacobian(f, C, R, h)
Jclass = Jacob.getJ()

print(Jclass.shape)
print("Jclass\n", Jclass)

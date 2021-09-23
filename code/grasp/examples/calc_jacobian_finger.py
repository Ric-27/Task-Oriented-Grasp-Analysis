import sys, os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_types import Contact, Joint, Finger
from class_jacobian import Jacobian

xv = np.array([1, 0, 0]).reshape(3, 1)
yv = np.array([0, 1, 0]).reshape(3, 1)
zv = np.array([0, 0, 1]).reshape(3, 1)

l0 = 1
l1 = 1
l2 = 1
l3 = 1

c1 = np.array([0, 0, l0 + l1 + l2 + l3])

R1 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

contact1 = Contact(c1, R1)
C = np.array([contact1])

q1c = np.array([0, 0, 0])
q2c = np.array([0, 0, 0])
q3c = np.array([0, 0, l0])
q4c = np.array([0, 0, l0])
q5c = np.array([0, 0, l0 + l1])
q6c = np.array([0, 0, l0 + l1 + l2])

q1 = Joint(1, q1c, xv, None, False)  # q1
q2 = Joint(2, q2c, yv, None, False)  # q2
q3 = Joint(3, q3c, zv)  # q3
q4 = Joint(4, q4c, xv)  # q4
q5 = Joint(5, q5c, xv)  # q7
q6 = Joint(6, q6c, xv, c1)  # q10

f1 = Finger(1, np.array([q1, q2, q3, q4, q5, q6]))
f = np.array([f1])

jacobian = Jacobian(f, C)
J = jacobian.J

print(J.shape)
print("J\n", J)

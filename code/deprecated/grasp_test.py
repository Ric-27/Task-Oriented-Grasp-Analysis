import numpy as np
from GraspMap import GraspMap

np.set_printoptions(suppress=True)

p = np.array([0, 0, 0])


c1 = np.array([-0.8, -0.6, 0])
r1 = np.array([[0.8, -0.6, 0], [0.6, 0.8, 0], [0, 0, 1]])

c2 = np.array([0.8, -0.6, 0])
r2 = np.array([[-0.8, -0.6, 0], [0.6, -0.8, 0], [0, 0, 1]])

h = np.array(["S", "H"])

C = np.array([c1, c2])
R = np.array([r1, r2])

grasp = Grasp(p, C, R, h)

print("Gt: \n", grasp.getGt())
grasp.GraspClassification(True)
print("Rank G:", grasp.getRank())

exit(0)

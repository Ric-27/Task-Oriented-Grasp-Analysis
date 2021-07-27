from class_stl import STL
from class_grasp import Grasp
import numpy as np
import time

path = "../stl/fluid_container_high.stl"
path = "../stl/cube_low.stl"
path = "../stl/TransferNeedle-new.stl"

path = "../stl/new/rinse_glass.stl"
nc = 4

# start = time.time()
mesh = STL(path)
# end = time.time()
# print("declaration time: ",end - start)

# mesh.view()


# start = time.time()
Ct, Rt, Ce, Re, Cv, Rv = mesh.gen_C_randomly(nc)
C = np.concatenate((Ct, Ce, Cv), axis=0)
# R = np.concatenate((Rt, Re, Rv), axis=0)
print(Ct.shape)
mesh.view_with_C(Ct, Rt)

exit()
# end = time.time()
# print("generation time: ",end - start)
C1, R1 = mesh.gen_C_from_coordinates(np.array([5, 0, 0]), "E")
C2, R2 = mesh.gen_C_from_coordinates(np.array([0, 5, 0]), "E")
C3, R3 = mesh.gen_C_from_coordinates(np.array([0, 0, 5]), "E")
C4, R4 = mesh.gen_C_from_coordinates(np.array([-5, 0, 0]), "E")
C5, R5 = mesh.gen_C_from_coordinates(np.array([0, -5, 0]), "E")
C6, R6 = mesh.gen_C_from_coordinates(np.array([0, 0, -5]), "E")
C7, R7 = mesh.gen_C_from_coordinates(np.array([5, 5, 5]), "V")
C = np.concatenate((C1, C2, C3, C4, C5, C6, C7))

R = np.concatenate((R1, R2, R3, R4, R5, R6, R7))
mesh.view_with_C(C, R)
print("mesh center:", mesh.cog)

# coord = np.array([5,-6,0])
# C, R = mesh.gen_C_from_coordinates(coord,'E')
# mesh.view()
# print(Ct)
# h = np.array(['H','H','H','H','H','H'])
# grasp = GraspMap(mesh.cog, Ct, Rt)
# print(grasp.getGt())
# d, l = grasp.calcFFormClosure()
# print(d, l)
# print(grasp.GraspClassification())
# print(grasp.getGt())
# print(Rv.shape)
# print(R.shape)
# mesh.view()
exit(0)

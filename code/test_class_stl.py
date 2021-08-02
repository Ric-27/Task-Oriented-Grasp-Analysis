from matplotlib.pyplot import axis
from class_stl import STL
from class_grasp import Grasp
from data_types import Contact
import numpy as np
import time

path = "../stl/cube_low.stl"
NC = 8

start = time.time()
mesh = STL(path)
end = time.time()
print("declaration time: ", end - start)

mesh.view()

start = time.time()
Ct, Ce, Cv = mesh.gen_C_randomly(NC)
end = time.time()
print("generation time: ", end - start)

C = np.concatenate((Ct, Ce, Cv), axis=0)
mesh.view(C)

C1 = mesh.gen_C_from_coordinates(np.array([5, 0, 0]), "E")
C2 = mesh.gen_C_from_coordinates(np.array([0, 5, 0]), "E")
C3 = mesh.gen_C_from_coordinates(np.array([0, 0, 5]), "E")
C4 = mesh.gen_C_from_coordinates(np.array([-5, 0, 0]), "E")
C5 = mesh.gen_C_from_coordinates(np.array([0, -5, 0]), "E")
C6 = mesh.gen_C_from_coordinates(np.array([0, 0, -5]), "E")
C7 = mesh.gen_C_from_coordinates(np.array([5, 5, 5]), "V", 0.3, 0.5, 10)
print(C7)
C = np.concatenate((C1, C2, C3, C4, C5, C6, C7), axis=0)
mesh.view(C)
print("mesh center:", mesh.cog)

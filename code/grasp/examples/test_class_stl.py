import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from class_stl import STL

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import path_join_str, path_starting_from_code

path = path_join_str(path_starting_from_code(1), "stl/cube_low.stl")

mesh = STL(path, [0, 0, 0])

mesh.view()

C = mesh.gen_C_randomly(1)

mesh.view(C)

C1 = mesh.contact_from_point([5, 1, 1])
C2 = mesh.contact_from_point([0, 5, 0])
C3 = mesh.contact_from_point([0, 0, 5])
C4 = mesh.contact_from_point([-5, 0, 0])
C5 = mesh.contact_from_point([0, -5, 0])
C6 = mesh.contact_from_point([0, 0, -5])
C7 = mesh.contact_from_point([5, 5, 5], 0.3, 0, 4)
print(C7)
mesh.view([C1, C2, C3, C4, C5, C6, C7])
print("center of mass:", mesh.com)

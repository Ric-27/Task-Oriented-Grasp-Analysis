import ast
from math_tools import list_to_vertical_matrix
from quality_metrics import alpha_from_direction, fcn_from_g
import numpy as np
from class_stl import STL
from class_grasp import Grasp

with open("./code/textfiles/grasps.txt") as f:
    objects_grasps_definition = f.read()
objects_grasps_definition = ast.literal_eval(objects_grasps_definition)

DECIMAL_PLACES = 3

D_EXT = np.array([0, 0, -1, 0, 0, 0])
FC_MAX = 0.2
ALPHA = 0.141
obj = "petri"
grsp = "c6"

key_g = obj + "_" + grsp
coord = objects_grasps_definition[key_g].copy()
path = "./stl/" + coord.pop(0) + ".stl"
var = np.array(coord)  # .reshape((int(len(coord) / 4), 4))
mesh = STL(path)
contact_points = []
for pt in var:
    contact_points.append(
        mesh.gen_C_from_coordinates(
            np.array([pt[0], pt[1], pt[2]], dtype=np.float64),
            pt[3].upper(),
        )
    )

contact_points = list_to_vertical_matrix(contact_points)
print(type(contact_points[0]))
grasp = Grasp(mesh.cog, contact_points)
al, forces = alpha_from_direction(grasp, D_EXT, FC_MAX, 8, 0.3)
print(
    "alpha: {}, Forces: {}".format(
        round(al, DECIMAL_PLACES), forces[0::3].round(DECIMAL_PLACES)
    )
)
print(30 * "-")
forces = fcn_from_g(grasp, ALPHA * D_EXT, FC_MAX, 8, 0.3)
print("Forces: {}".format(forces[0::3].round(DECIMAL_PLACES)))

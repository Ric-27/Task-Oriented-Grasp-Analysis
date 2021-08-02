import ast
from quality_metrics import alpha_from_direction, fcn_from_g
import numpy as np
from class_stl import STL
from class_grasp import Grasp

with open("./textfiles/grasps.txt") as f:
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
path = "../stl/" + coord.pop(0) + ".stl"
var = np.array(coord)  # .reshape((int(len(coord) / 4), 4))
mesh = STL(path)
cc = []
rr = []
for point in var:
    c, r = mesh.gen_C_from_coordinates(
        np.array([point[0], point[1], point[2]], dtype=np.float64),
        point[3].upper(),
    )
    cc.append(
        c.reshape(
            3,
        )
    )
    rr.append(r.reshape(3, 3))
cc = np.array(cc)
rr = np.array(rr)

grasp = Grasp(mesh.cog, cc, rr)

al, forces = alpha_from_direction(grasp, D_EXT, FC_MAX, 8, 0.3)
print(
    "alpha: {}, Forces: {}".format(
        round(al, DECIMAL_PLACES), forces[0::3].round(DECIMAL_PLACES)
    )
)
print(30 * "-")
forces = fcn_from_g(grasp, ALPHA*D_EXT,FC_MAX, 8, 0.3)
print("Forces: {}".format(forces[0::3].round(DECIMAL_PLACES)))

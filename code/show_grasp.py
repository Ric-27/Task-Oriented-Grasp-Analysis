# importing the module
import ast
from math_tools import list_to_vertical_matrix
import numpy as np
from class_stl import STL
from class_grasp import Grasp

np.set_printoptions(suppress=True)

obj = "petri"
grsp = "c6"

# reading the data from the file
with open("./code/textfiles/grasps.txt") as f:
    data_grasps = f.read()
data_grasps = ast.literal_eval(data_grasps)

for key, value in data_grasps.items():
    if obj != "" and grsp != "":
        key = obj + "_" + grsp
    coord = data_grasps[key].copy()
    path = "./stl/" + coord.pop(0) + ".stl"
    var = np.array(coord)  # .reshape((int(len(coord) / 4), 4))
    print(key)
    print("nc:", var.shape[0])
    mesh = STL(path)
    contact_points = []
    for point in var:
        contact_points.append(
            mesh.gen_C_from_coordinates(
                np.array([point[0], point[1], point[2]], dtype=np.float64),
                point[3].upper(),
            )
        )

    contact_points = list_to_vertical_matrix(contact_points)

    grasp = Grasp(mesh.cog, contact_points)
    print("Gt \n", grasp.Gt)
    grasp.get_classification(True)

    mesh.view(contact_points)

    if obj != "" and grsp != "":
        break

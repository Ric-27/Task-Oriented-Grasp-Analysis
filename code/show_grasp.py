# importing the module
import ast
from re import T
import numpy as np
from class_stl import STL
from class_grasp import Grasp

np.set_printoptions(suppress=True)

key_view = ""

# reading the data from the file
with open("textfiles/grasps.txt") as f:
    data = f.read()
data = ast.literal_eval(data)

for key, value in reversed(data.items()):
    if key_view != "":
        key = key_view
        value = data[key]
    coord = value.copy()
    path = "../stl/new/" + coord.pop(0) + ".stl"
    var = np.array(coord)  # .reshape((int(len(coord) / 4), 4))
    print(key)
    print("nc:", var.shape[0])
    mesh = STL(path)
    cc = []
    rr = []
    for point in var:
        c, r = mesh.gen_C_from_coordinates(
            np.array([point[0], point[1], point[2]], dtype=np.float64), point[3].upper()
        )
        cc.append(
            c.reshape(
                3,
            )
        )

        # print(point, "\t\t", c)
        rr.append(r.reshape(3, 3))
    cc = np.array(cc)
    rr = np.array(rr)
    """
    grasp = Grasp(mesh.cog, cc, rr)
    print("Gt \n", grasp.getGt())
    grasp.GraspClassification(True)
    """
    mesh.view_with_C(cc, rr)

    # if key == list(data)[-1] or key == key_view:
    #    break

# importing the module
import ast
from math_tools import list_to_vertical_matrix
import numpy as np
from class_stl import STL
from class_grasp import Grasp

np.set_printoptions(suppress=True)

OBJ = "rinse"
GRSP = "c6"

# reading the data from the file
with open("./code/textfiles/final_grasps.txt") as f:
    data_grasps = f.read()
data_grasps = ast.literal_eval(data_grasps)

skip = False

for key, value in data_grasps.items():
    if OBJ != "":
        if GRSP != "":
            key = OBJ + " " + GRSP
        else:
            head, partition, tail = key.partition("_")
            head2 = tail.partition("_")[0]
            if head2 != tail:
                head += "_" + head2
            if OBJ != head:
                skip = True

    if not skip:
        path = "./stl/" + data_grasps[key].pop(0) + ".stl"
        contacts = np.array(data_grasps[key])
        mesh = STL(path)
        contact_points = []
        for pt in contacts:
            contact_points.append(
                mesh.gen_C_from_coordinates(
                    np.array([pt[0], pt[1], pt[2]], dtype=np.float64),
                    pt[3].upper(),
                )
            )
        contact_points = list_to_vertical_matrix(contact_points)
        print("{} \t nc: {}".format(key, contacts.shape[0]))
        mesh.view(contact_points)

        """
        print(
            "X: {} - {} \t Y: {} - {} \t Z: {} - {}".format(
                min(mesh.vertices[:, 0]),
                max(mesh.vertices[:, 0]),
                min(mesh.vertices[:, 1]),
                max(mesh.vertices[:, 1]),
                min(mesh.vertices[:, 2]),
                max(mesh.vertices[:, 2]),
            )
        )

        # grasp = Grasp(mesh.cog, contact_points)
        # print("Gt \n", grasp.Gt)
        # grasp.get_classification(True)
        """

    skip = False

    if OBJ == key:
        break

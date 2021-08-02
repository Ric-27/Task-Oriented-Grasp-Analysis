# importing the module
import ast
from quality_metrics import alpha_from_direction
import numpy as np
from class_stl import STL
from class_grasp import Grasp
from math_tools import get_rank

# np.set_printoptions(suppress=True)

# reading the data from the files

with open("./textfiles/alpha.txt") as f:
    objects = f.read()
objects = ast.literal_eval(objects)

with open("./textfiles/grasps.txt") as f:
    objects_grasps_definition = f.read()
objects_grasps_definition = ast.literal_eval(objects_grasps_definition)

DECIMAL_PLACES = 3

DIR_W_EXT = np.array(
    (
        [
            [1, 0, 0, 0, 0, 0],
            [-1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, -1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, -1, 0, 0, 0],
            [1, 1, 1, 0, 0, 0],
            [-1, 1, 1, 0, 0, 0],
            [-1, -1, 1, 0, 0, 0],
            [1, -1, 1, 0, 0, 0],
            [1, 1, -1, 0, 0, 0],
            [-1, 1, -1, 0, 0, 0],
            [-1, -1, -1, 0, 0, 0],
            [1, -1, -1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, -1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, -1, 0],
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, -1],
            [0, 0, 0, 1, 1, 1],
            [0, 0, 0, -1, 1, 1],
            [0, 0, 0, -1, -1, 1],
            [0, 0, 0, 1, -1, 1],
            [0, 0, 0, 1, 1, -1],
            [0, 0, 0, -1, 1, -1],
            [0, 0, 0, -1, -1, -1],
            [0, 0, 0, 1, -1, -1],
            [1, 1, 1, 1, 1, 1],
        ]
    )
)

F_MAXS = np.array(
    [
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
        0.9,
        1,
        1.1,
        1.2,
        1.3,
        1.4,
        1.5,
        1.6,
        1.7,
        1.8,
        1.9,
        2,
        2.2,
        2.4,
        2.6,
        2.8,
        3,
        3.2,
        3.4,
        3.6,
        3.8,
        4,
        4.2,
        4.4,
        4.6,
        4.8,
        5,
        5.5,
        6,
        6.5,
        7,
        7.5,
        8,
    ]
)

for fmax in F_MAXS:
    print(fmax)
    print(50 * "+")
    for key, value in objects.items():
        info = value.copy()
        obj = info[0]
        grasps = info[1]
        for g in grasps:
            key_g = obj + "_" + g
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

            alphas = []
            all_forces = []

            for dExt in DIR_W_EXT:
                al, forces = alpha_from_direction(grasp, dExt, fmax, 8, 0.3)
                alphas.append(round(al, DECIMAL_PLACES))
                all_forces.append(forces.round(DECIMAL_PLACES))

            for alpha in alphas:
                if alpha >= 0:
                    print(alpha, end=",")
                else:
                    print("-", end=",")
            print("")
            """
            G = grasp.get_grasp_matrix_t().transpose()
            rank = getRank(G)
            ind, gra = grasp.get_grasp_classification()
            print(
                "{},{},{}".format(
                    rank,
                    "TRUE" if ind == 1 else "FALSE",
                    "TRUE" if gra == 1 else "FALSE",
                )
            )
            nc = var.shape[0]
            fcn = []
            for i, force in enumerate(forces, 0):
                if i % 3 == 0:
                    fcn.append(force)
            fcn = np.array(fcn)
            print(
                "\tgrasp: {}, nc:{}, alpha: {}, fcn: \n{}".format(
                    g, var.shape[0], round(al, 2), fcn
                )
            )
            break
            mesh.viewCR(cc, rr)
            """
    print("")
print("DONE!!!")

# importing the module
import ast
import numpy as np
from class_stl import STL
from class_grasp import Grasp
from quality_metrics import task_oriented
from math_tools import get_rank

np.set_printoptions(suppress=True)

# reading the data from the file
with open("textfiles/alpha.txt") as f:
    data_f = f.read()
data_f = ast.literal_eval(data_f)

with open("textfiles/grasps.txt") as f:
    data_g = f.read()
data_g = ast.literal_eval(data_g)
DECIMAL_PLACES = 3
dExts = np.array(
    (
        [
            [1, 0, 0, 0, 0, 0],
            [-1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, -1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, -1, 0, 0, 0],
            [1, 1, 1, 0, 0, 0],
            [-1, -1, -1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, -1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, -1, 0],
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, -1],
            [0, 0, 0, 1, 1, 1],
            [0, 0, 0, -1, -1, -1],
            [1, 1, 1, 1, 1, 1],
            [-1, -1, -1, -1, -1, -1],
        ]
    )
)
fmaxs = np.array([0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
for fmax in fmaxs:
    print(fmax)
    print(50 * "+")
    for key, value in data_f.items():
        info = value.copy()
        obj = info[0]
        grasps = info[1]
        for g in grasps:
            key_g = obj + "_" + g
            coord = data_g[key_g].copy()
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
            """
            alphas = []
            for dExt in dExts:

                al, forces = task_oriented(grasp, dExt, fmax, 8, 0.3)
                alphas.append(al)

            print(
                "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
                    round(alphas[0], DECIMAL_PLACES) if alphas[0] >= 0 else "-",
                    round(alphas[1], DECIMAL_PLACES) if alphas[1] >= 0 else "-",
                    round(alphas[2], DECIMAL_PLACES) if alphas[2] >= 0 else "-",
                    round(alphas[3], DECIMAL_PLACES) if alphas[3] >= 0 else "-",
                    round(alphas[4], DECIMAL_PLACES) if alphas[4] >= 0 else "-",
                    round(alphas[5], DECIMAL_PLACES) if alphas[5] >= 0 else "-",
                    round(alphas[6], DECIMAL_PLACES) if alphas[6] >= 0 else "-",
                    round(alphas[7], DECIMAL_PLACES) if alphas[7] >= 0 else "-",
                    round(alphas[8], DECIMAL_PLACES) if alphas[8] >= 0 else "-",
                    round(alphas[9], DECIMAL_PLACES) if alphas[9] >= 0 else "-",
                    round(alphas[10], DECIMAL_PLACES) if alphas[10] >= 0 else "-",
                    round(alphas[11], DECIMAL_PLACES) if alphas[11] >= 0 else "-",
                    round(alphas[12], DECIMAL_PLACES) if alphas[12] >= 0 else "-",
                    round(alphas[13], DECIMAL_PLACES) if alphas[13] >= 0 else "-",
                    round(alphas[14], DECIMAL_PLACES) if alphas[14] >= 0 else "-",
                    round(alphas[15], DECIMAL_PLACES) if alphas[15] >= 0 else "-",
                    round(alphas[16], DECIMAL_PLACES) if alphas[16] >= 0 else "-",
                    round(alphas[17], DECIMAL_PLACES) if alphas[17] >= 0 else "-",
                )
            )
            """
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
    print(30 * "-")
    """
    print(50 * "+")
print("DONE!!!")

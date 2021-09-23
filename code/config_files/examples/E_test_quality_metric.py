import argparse
import numpy as np
import ast, sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from class_stl import STL
from functions import list_to_vertical_matrix
from quality_metrics import alpha_from_direction, forces_from_perturbation
from class_grasp import Grasp

parser = argparse.ArgumentParser(
    description="view the grasps saved on the predetermined file"
)
parser.add_argument(
    "-o",
    "--object",
    type=str,
    default="petri",
    help="select an object [def: petri]",
)
parser.add_argument(
    "-g",
    "--grasp",
    type=str,
    default="c12",
    help="select a grasp of an object [def: c12]",
)
parser.add_argument(
    "-gf",
    "--grasp_file",
    type=str,
    default="grasps",
    help="name of grasp file [def: grasps]",
)
parser.add_argument(
    "-df",
    "--dir_file",
    type=str,
    default="dir",
    help="name of directions file [def: dir]",
)
parser.add_argument(
    "-d",
    "--dir",
    type=str,
    default="X",
    help="direction of study [def: X]",
)
parser.add_argument(
    "-fc",
    "--fc_max",
    type=int,
    default=1,
    help="fc max value to study [def: 1]",
)
parser.add_argument(
    "-a",
    "--alpha",
    type=int,
    default=1,
    help="alpha to study [def: 1]",
)
args = parser.parse_args()
OBJ = args.object
GRP = args.grasp
assert not ((GRP == "") or (OBJ == "")), "Can't leave grasp or object empty"

with open("./code/config_files/" + args.grasp_file + ".txt") as f:
    data_grasps = f.read()
data_grasps = ast.literal_eval(data_grasps)

with open("./code/config_files/" + args.dir_file + ".txt") as f:
    data_dir = f.read()
data_dir = ast.literal_eval(data_dir)

DECIMAL_PLACES = 3

D_EXT = data_dir[args.dir]
FC_MAX = args.fc_max
ALPHA = args.alpha

var = data_grasps[OBJ + "-" + GRP]
mesh = STL("./stl/" + OBJ + ".stl")

print(parser.format_usage())
print("Arguments Values", vars(args), "\n")

contact_points = []
for pt in var:
    contact_points.append(
        mesh.gen_C_from_coordinates(
            np.array([pt[0], pt[1], pt[2]], dtype=np.float64),
            pt[3].upper(),
        )
    )

contact_points = list_to_vertical_matrix(contact_points)
grasp = Grasp(mesh.cog, contact_points)
al, forces = alpha_from_direction(grasp, D_EXT, FC_MAX)
print(
    "alpha: {}, Forces: {}".format(
        round(al, DECIMAL_PLACES), forces[0::3].round(DECIMAL_PLACES)
    )
)
print(30 * "-")
forces = forces_from_perturbation(grasp, ALPHA * D_EXT, FC_MAX, 8, 0.3)[1]
print("Forces: {}".format(forces[::3].round(DECIMAL_PLACES)))

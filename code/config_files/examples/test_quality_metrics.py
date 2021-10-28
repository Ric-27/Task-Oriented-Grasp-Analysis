import argparse
import sys, os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from grasp.quality_metrics import (
    alpha_from_direction,
    forces_from_perturbation,
    friction_form_closure,
)
from grasp.class_grasp import Grasp

from functions import (
    __coordinate_dict_to_list,
    __get_grasp_dict,
    __grp_item_to_Contacts,
    get_dwext_dict,
    get_object_dict,
)

parser = argparse.ArgumentParser(
    description="view the grasps saved on the predetermined file"
)
parser.add_argument(
    "-o",
    "--object",
    type=str,
    default="Petri",
    help="select an object [def: Petri]",
)
parser.add_argument(
    "-g",
    "--grasp",
    type=str,
    default="C12",
    help="select a grasp of an object [def: C12]",
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

objects = get_object_dict()
grasps = __get_grasp_dict()
dirs = get_dwext_dict()

DECIMAL_PLACES = 3

D_EXT = dirs[args.dir]
FC_MAX = args.fc_max
ALPHA = args.alpha
print(parser.format_usage())
print("Arguments Values", vars(args), "\n")

grasp_obj = Grasp(
    __coordinate_dict_to_list(objects[OBJ]["center of mass"]),
    __grp_item_to_Contacts(grasps[OBJ]["grasps"][GRP], char_len=objects[OBJ]["characteristic length"]),
)
# ffc = friction_form_closure(grasp_obj)[0]
# print("Friction Form Closure\nd= {}".format(round(ffc, DECIMAL_PLACES)))
# print(80 * "-")
al, forces = alpha_from_direction(grasp_obj, D_EXT, FC_MAX)
print(
    "UNKNOWN PERTURBATION: \nfor dWext={} with Fmax= {}N \n  max magnitude resisted={}, required Normal Contact Forces={}".format(
        D_EXT, FC_MAX, round(al, DECIMAL_PLACES), forces.round(DECIMAL_PLACES)
    )
)
# print(80 * "-")
# forces = forces_from_perturbation(grasp_obj, [ALPHA * np.array(D_EXT)])
# print(
#     "KNOWN PERTURBATION: \nfor Perturbation={}, required Normal Contact Forces={}".format(
#         str(ALPHA * np.array(D_EXT)), forces[::3].round(DECIMAL_PLACES)
#     )
# )

import argparse
import numpy as np
import os, sys
import keyboard

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from grasp.class_stl import STL
from grasp.class_grasp import Grasp
from functions import (
    check_TARGET_OBJ_GRP,
    get_grasps_STLs_dict,
    is_TARGET_OBJ_GRP,
    point_dict_to_Contact,
    object_file_name,
    print_if_worked,
)

parser = argparse.ArgumentParser(
    description="view the grasps saved on the predetermined file"
)
parser.add_argument(
    "-o",
    "--object",
    type=str,
    default="",
    help="select an object [def: all]",
)
parser.add_argument(
    "-g",
    "--grasp",
    type=str,
    default="",
    help="select a grasp of an object [def: all]",
)
parser.add_argument(
    "-gi",
    "--grasp_info",
    type=bool,
    default=False,
    help="print Grasp Info [def: False]",
)

args = parser.parse_args()
OBJ = args.object
GRP = args.grasp

check_TARGET_OBJ_GRP(OBJ, GRP)

objects = get_grasps_STLs_dict()

worked = False
for obj, items in objects.items():
    mesh = items["mesh"]
    for grp, v_points in items["grasps"].items():
        if is_TARGET_OBJ_GRP(OBJ, GRP, obj, grp):
            worked = True
            contact_points = [point_dict_to_Contact(pt) for pt in v_points.values()]

            if args.grasp_info:
                grasp = Grasp(mesh.com, contact_points)
                print("Gt \n", grasp.Gt.round(3))
                grasp.get_classification(True)

            mesh.view(obj + " " + grp, contact_points)

print_if_worked(
    worked,
    "Finished" + 50 * " ",
    "No objects and/or grasps declared on "
    + object_file_name()
    + ".yaml or object and/or grasp passed as argument doesn't exists",
)

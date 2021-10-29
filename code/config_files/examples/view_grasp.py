import argparse
import numpy as np
import os, sys
import keyboard

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import (
    assert_OBJ_exist_if_GRP_exist,
    get_OBJECT_dict,
    is_obj_grp_OBJ_GRP,
    partition_str,
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

assert_OBJ_exist_if_GRP_exist(OBJ, GRP)

objects = get_OBJECT_dict()

worked = False
for obj1, mesh in objects["meshes"].items():
    for grp1, grasp in objects["grasps"].items():
        obj, grp = partition_str(grp1)
        if obj != obj1:
            continue
        if is_obj_grp_OBJ_GRP(OBJ, GRP, obj, grp):
            worked = True
            if args.grasp_info or True:
                print("Gt \n", grasp.Gt.round(3))
                grasp.get_classification(True)

            mesh.view(grp1, grasp.contact_points)

print_if_worked(
    worked,
    "Finished" + 50 * " ",
    "No objects and/or grasps declared on "
    + object_file_name()
    + ".yaml or object and/or grasp passed as argument doesn't exists",
)

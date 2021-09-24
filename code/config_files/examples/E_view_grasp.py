import argparse
import numpy as np
import os, sys
import keyboard

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from grasp.class_stl import STL
from grasp.class_grasp import Grasp
from grasp.grasp_functions import list_to_vertical_matrix
from functions import (
    check_TARGET_OBJ_GRP,
    get_grasp_dict,
    is_TARGET_OBJ_GRP,
    get_STLs_dict,
    point_dict_to_Contact,
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

args = parser.parse_args()
OBJ = args.object
GRP = args.grasp

check_TARGET_OBJ_GRP(OBJ, GRP)

grasps = get_grasp_dict()
stl_path = get_STLs_dict()

print("\nPress [q] to continue or [z + q] to exit\n")

worked = False

for obj, v_grasps in grasps.items():
    for grp, v_points in v_grasps.items():
        if is_TARGET_OBJ_GRP:
            worked = True
            mesh = stl_path[obj]
            contact_points = [point_dict_to_Contact(pt) for pt in v_points.values()]
            if args.mesh_range:
                if prev_obj != obj:
                    print("cog location: ", mesh.cog)
                    print(
                        "{} \n range of model: \t X: {:.3f} - {:.3f} \t Y: {:.3f} - {:.3f} \t Z: {:.3f} - {:.3f}".format(
                            obj,
                            min(mesh.vertices[:, 0]),
                            max(mesh.vertices[:, 0]),
                            min(mesh.vertices[:, 1]),
                            max(mesh.vertices[:, 1]),
                            min(mesh.vertices[:, 2]),
                            max(mesh.vertices[:, 2]),
                        )
                    )
            print("{} \t nc: {}".format(obj + "-" + grp, len(contact_points)))

            if args.grasp_info:
                grasp = Grasp(mesh.cog, contact_points)
                print("Gt \n", grasp.Gt.round(3))
                grasp.get_classification(True)

            mesh.view(contact_points)

        skip = False
        if keyboard.is_pressed("z"):
            exit("\nExecution Cancelled\n")
        if prev_obj is None or prev_obj != obj:
            prev_obj = obj
if worked:
    print("\nFinished\n")
else:
    print("No grasps found\n")

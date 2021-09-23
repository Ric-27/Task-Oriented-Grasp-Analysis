import argparse
import numpy as np
import os, sys
import keyboard

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from grasp.class_stl import STL
from grasp.class_grasp import Grasp
from grasp.functions import (
    list_to_vertical_matrix,
    check_TARGET_OBJ_GRP,
    get_grasp_dict,
    is_TARGET_OBJ_GRP,
    get_STLs_dict,
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
stls = get_STLs_dict()

print("\nPress [q] to continue or [z + q] to exit\n")

worked = False

for obj, ograsps in grasps.items():
    for grp in ograsps:
        if is_TARGET_OBJ_GRP:
            worked = True
            mesh = STL(stl_path_dict_item_to_STL(stl_path[obj]))
            contact_points = []
            for pt in contacts:
                contact_points.append(
                    mesh.gen_C_from_coordinates(
                        np.array([pt[0], pt[1], pt[2]], dtype=np.float64),
                        pt[3].upper(),
                    )
                )
            contact_points = list_to_vertical_matrix(contact_points)
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
            print("{} \t nc: {}".format(key_grasp, contacts.shape[0]))

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

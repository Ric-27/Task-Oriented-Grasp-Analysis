import os, sys
import argparse
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from functions import (
    object_file_name,
    print_if_worked,
    path_join_str,
    path_starting_from_code,
    check_TARGET_OBJ_GRP,
    get_grasps_STLs_dict,
    is_TARGET_OBJ_GRP,
    grp_item_to_Contacts,
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

objects = get_grasps_STLs_dict()

worked = False
counter = 0
for obj in tqdm(
    objects,
    total=len(objects),
    unit="obj",
    colour="red",
    leave=True,
    desc="Going through the objects",
):
    mesh = objects[obj]["mesh"]
    for grp in tqdm(
        objects[obj]["grasps"],
        total=len(objects[obj]["grasps"]),
        unit="grp",
        colour="yellow",
        leave=False,
        desc=f"saving each grasp",
    ):
        if is_TARGET_OBJ_GRP(OBJ, GRP, obj, grp):
            worked = True
            contact_points = grp_item_to_Contacts(objects[obj]["grasps"][grp])
            mesh.view(obj + "-" + grp, contact_points, view_not_return=False).savefig(
                path_join_str(
                    path_starting_from_code(1),
                    "excel/images/grp/" + str(counter) + "_" + obj + "-" + grp + ".png",
                ),
                bbox_inches="tight",
            )
            counter += 1

print_if_worked(
    worked,
    "Finished the Image Creation" + 50 * " ",
    "No objects and/or grasps declared on "
    + object_file_name()
    + ".yaml or object and/or grasp passed as argument doesn't exists",
)

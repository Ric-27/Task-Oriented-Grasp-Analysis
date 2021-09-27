import os, sys
import argparse
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from functions import (
    get_STLs_dict,
    object_file_name,
    print_if_worked,
    path_join_str,
    path_starting_from_code,
    is_TARGET_OBJ,
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
args = parser.parse_args()
OBJ = args.object
STLs = get_STLs_dict()

worked = False
counter = 0
for obj in tqdm(
    STLs,
    total=len(STLs),
    unit="obj",
    colour="red",
    leave=True,
    desc="Going through the objects",
):
    if is_TARGET_OBJ(OBJ, obj):
        worked = True
        STLs[obj].view(obj, view_not_return=False).savefig(
            path_join_str(
                path_starting_from_code(1),
                "excel/images/obj/" + str(counter) + "_" + obj + ".png",
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

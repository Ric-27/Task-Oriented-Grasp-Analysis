import os, sys
import argparse
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from grasp.class_grasp import Grasp
from grasp.quality_metrics import friction_form_closure
from grasp.grasp_functions import get_rank
from functions import (
    assert_TARGET_OBJ_GRP,
    get_grasp_dict,
    is_TARGET_OBJ_GRP,
    point_dict_to_list,
    grp_item_to_Contacts,
    check_save_for_excel,
    save_to_excel,
    print_if_worked,
)

parser = argparse.ArgumentParser(
    description="view or save the force analysis of each grasp of each object"
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

assert_TARGET_OBJ_GRP(OBJ, GRP)

grasps = get_grasp_dict()

print(parser.format_usage())

index = []
data = []
counter = 0

prev_obj = ""
worked = False
save = check_save_for_excel(OBJ, GRP)

for obj in tqdm(
    grasps,
    total=len(grasps),
    unit="obj",
    colour="red",
    leave=True,
    desc="Updating Grasp Info of Excel file",
):
    for grp in tqdm(
        grasps[obj]["grasps"],
        total=len(grasps[obj]["grasps"]),
        unit="grp",
        colour="yellow",
        leave=False,
        desc=f"going through grasps of {obj}",
    ):
        if is_TARGET_OBJ_GRP(OBJ, GRP, obj, grp):
            worked = True
            grasp_obj = Grasp(
                point_dict_to_list(grasps[obj]["center of mass"]),
                grp_item_to_Contacts(grasps[obj]["grasps"][grp]),
            )
            d = friction_form_closure(grasp_obj)[0]
            row = [
                obj + "-" + grp,
                grasp_obj.nc,
                get_rank(grasp_obj.Gt.transpose()),
                "True" if grasp_obj.indeterminate else "False",
                "True" if grasp_obj.graspable else "False",
                "True" if d > 0 else "False",
            ]
            if not save:
                print(row)
            else:
                data.append(row)
                index.append(counter)
                counter += 1


if save:
    save_to_excel(
        "Task Oriented Analysis",
        "raw grasp info",
        data,
        ["grasp", "nc", "rank", "ind", "grs", "fcc"],
        index,
    )
print_if_worked(worked, "Finished", "No grasps were found")

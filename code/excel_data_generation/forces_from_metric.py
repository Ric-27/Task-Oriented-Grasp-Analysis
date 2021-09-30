import os, sys
import argparse
from tqdm import tqdm
import time
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from grasp.class_grasp import Grasp
from grasp.quality_metrics import forces_from_perturbation
from functions import (
    assert_TARGET_OBJ_GRP,
    get_object_dict,
    is_TARGET_OBJ_GRP,
    point_dict_to_list,
    grp_item_to_Contacts,
    check_save_for_excel,
    save_to_excel,
    print_if_worked,
    get_fmax_list,
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
parser.add_argument(
    "-f",
    "--force",
    type=str,
    default="",
    help="select a force to analyze [def: all]",
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
FRC = args.force
ALPHA = args.alpha

assert_TARGET_OBJ_GRP(OBJ, GRP)

objects = get_object_dict()
fmaxs = get_fmax_list()

print("Arguments Values", vars(args))

save = check_save_for_excel(OBJ, GRP)

len_grp = 0
len_frc = 0
for obj in objects.values():
    len_grp += len(obj["grasps"])
    len_frc += len(obj["forces"])

columns = []
for obj, item in objects.items():
    for force in item["forces"]:
        columns.append(obj + "-" + force)

index = []
worked = False
data = np.zeros((len_grp, len_frc))
# start = time.time()
data1 = np.full((len_grp, len_frc), "", dtype=object)
# data1[:, :] = ""
# end = time.time()
# print("declaration time: ", end - start)
row = -1

for obj, items in tqdm(
    objects.items(),
    total=len(objects),
    unit="obj",
    colour="red",
    leave=True,
    desc="Calculating Required Forces",
):
    for grp in tqdm(
        items["grasps"],
        total=len(items["grasps"]),
        unit="grp",
        colour="yellow",
        leave=False,
        desc=f"going through the grasps of {obj}",
    ):
        if is_TARGET_OBJ_GRP(OBJ, GRP, obj, grp):
            row += 1
            index.append(obj + "-" + grp)

            worked = True
            grasp_obj = Grasp(
                point_dict_to_list(items["center of mass"]),
                grp_item_to_Contacts(items["grasps"][grp]),
            )
            for key_force, value_force in items["forces"].items():
                value_force = list(value_force.values())
                fc = forces_from_perturbation(grasp_obj, value_force)
                col = obj + "-" + key_force
                fc_str = []
                for i in range(0, len(fc), 3):
                    fc_str.append(str(list(fc[i : i + 3].round(3))))
                fc_str = " ".join(fc_str)
                data1[row, columns.index(col)] = fc_str
                data[row, columns.index(col)] = (
                    round(max(fc), 3) if max(fc) != 0 else -1
                )
                if save:
                    continue
                print(
                    "OBJ:{}, GRP:{}, FRC:<{}>{}, fc vector:{}".format(
                        obj, grp, key_force, value_force, fc_str
                    )
                )

if save:
    data[data == 0] = None
    data1[data == 0] = None
    save_to_excel(
        "Task Oriented Analysis",
        "raw forces fmin",
        data,
        columns,
        index,
    )
    save_to_excel(
        "Task Oriented Analysis",
        "raw forces vec",
        data1,
        columns,
        index,
    )
print_if_worked(worked, "Finished", "No grasps were found")

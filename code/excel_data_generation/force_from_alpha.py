import os, sys
import argparse
from tqdm import tqdm
import time
import numpy as np
import re

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from grasp.class_grasp import Grasp
from functions import (
    assert_TARGET_OBJ_GRP,
    read_excel,
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


print("Arguments Values", vars(args))

save = check_save_for_excel(OBJ, GRP)

df_alpha = read_excel("Task Oriented Analysis", "raw alpha mod")

objects = get_object_dict()
fmaxs_list = get_fmax_list()

len_grp = 0
len_frc = 0
for obj in objects.values():
    len_grp += len(obj["grasps"])
    len_frc += len(obj["forces"])

index = []
dirs = ["X", "Y", "Z", "mX", "mY", "mZ"]
data = np.zeros((len_grp, len_frc))
row = -1

columns = []
for obj, item in objects.items():
    for force in item["forces"]:
        columns.append(obj + "-" + force)

FORCE_MIN_PATTERN = re.compile(r"(?<=<)\d+(\.\d+)?(?=>)")
for obj, items in tqdm(
    objects.items(),
    total=len(objects),
    unit="obj",
    colour="red",
    leave=True,
    desc="Calculating Force from Alpha",
):
    for grp in items["grasps"]:
        if is_TARGET_OBJ_GRP(OBJ, GRP, obj, grp):
            row += 1
            index.append(obj + "-" + grp)

            worked = True
            grasp_obj = Grasp(
                point_dict_to_list(items["center of mass"]),
                grp_item_to_Contacts(items["grasps"][grp]),
            )
        for key_force, value_force in items["forces"].items():
            value_force = value_force.values()
            min_f = -1
            for i, val in enumerate(value_force, 0):
                if val == 0:
                    continue
                col_dir = "-" if val < 0 else ""
                col_dir += dirs[i]
                col_fmax = map(lambda x: "{} <{}>".format(col_dir, str(x)), fmaxs_list)
                for col_f in col_fmax:
                    if df_alpha.loc[obj + "-" + grp, col_f] < abs(val):
                        continue
                    min_f_match = FORCE_MIN_PATTERN.search(col_f)
                    min_f_temp = float(col_f[min_f_match.start() : min_f_match.end()])
                    min_f = min_f_temp if min_f_temp > min_f else min_f
                    break
            col = obj + "-" + key_force
            data[row, columns.index(col)] = min_f
            if save:
                continue
            print(
                "OBJ:{}, GRP:{}, FORCE NAME:{}, FORCE VECTOR:{}, MIN F:{}".format(
                    obj, grp, key_force, value_force, min_f
                )
            )


if save:
    data[data == 0] = None
    save_to_excel(
        "Task Oriented Analysis",
        "force from alpha",
        data,
        columns,
        index,
    )
print_if_worked(worked, "Finished", "No grasps were found")

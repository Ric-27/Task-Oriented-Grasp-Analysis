import os, sys
import argparse
from tqdm import tqdm
import numpy as np
from multiprocessing import Pool

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from grasp.class_grasp import Grasp
from grasp.quality_metrics import alpha_from_direction
from functions import (
    assert_TARGET_OBJ_GRP,
    get_dwext_dict,
    get_fmax_list,
    get_grasp_dict,
    red_txt,
    green_txt,
    check_save_for_excel,
    is_TARGET_OBJ_GRP,
    point_dict_to_list,
    grp_item_to_Contacts,
    save_to_excel,
    print_if_worked,
)

"""
parser = argparse.ArgumentParser(
    description="view or save the alpha analysis of each grasp of each object"
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
    "-d",
    "--dir",
    type=str,
    default="",
    help="direction to study [def: all]",
)
parser.add_argument(
    "-fm",
    "--fmax",
    type=int,
    default=0,
    help="direction to study [def: all]",
)
"""


def gen_OBJ_GRP_par(arg):
    key, values = arg
    result = []
    for key_grasp, val_grasp in values["grasps"].items():
        result.append(
            (
                key + "-" + key_grasp,
                Grasp(
                    point_dict_to_list(values["center of mass"]),
                    grp_item_to_Contacts(val_grasp),
                ),
            )
        )
    return result


"""
args = parser.parse_args()
OBJ = args.object
GRP = args.grasp
DIR = args.dir
FMAX = args.fmax

# assert_TARGET_OBJ_GRP(OBJ, GRP)

assert FMAX >= 0, red_txt("fmax must be positive")



# print(parser.format_usage())

# save = check_save_for_excel(OBJ, GRP)

index = []
data = []

prev_obj = ""
worked = False
# save = check_save_for_excel(OBJ, GRP)
"""

fmaxs = get_fmax_list()
dwext = get_dwext_dict()


def gen_FMAX_DIR_par(arg):
    key, value = arg
    row = []
    for f_max in fmaxs:
        for d_w_ext in dwext.values():
            row.append(round(alpha_from_direction(value, d_w_ext, f_max)[0], 3))
    print(green_txt(key))
    return row


if __name__ == "__main__":
    print(red_txt("started"))
    grasps = get_grasp_dict()
    with Pool(processes=os.cpu_count()) as p:
        result = p.map(gen_OBJ_GRP_par, grasps.items())
    l = []
    for x in result:
        l.extend(x)

    grasps = {key: val for key, val in l}
    print(green_txt("grasps created"))

    with Pool(processes=int(os.cpu_count() / 2)) as p:
        data = p.map(gen_FMAX_DIR_par, grasps.items())
    columns = []
    for f_max in fmaxs:
        for key_dir in dwext.keys():
            columns.append(key_dir + " <" + str(f_max) + ">")

    save_to_excel("Task Oriented Analysis", "raw alpha", data, columns, grasps.keys())

    columns1 = []
    for key_dir in dwext.keys():
        for f_max in fmaxs:
            columns1.append(key_dir + " <" + str(f_max) + ">")
    grasp_info = {}
    data = np.array(data)
    for i, col in enumerate(columns, 0):
        grasp_info[col] = data[:, i]
    grasp_info1 = {}
    for col in columns1:
        grasp_info1[col] = grasp_info[col]

    save_to_excel(
        "Task Oriented Analysis",
        "raw alpha mod",
        grasp_info,
        columns1,
        grasps.keys(),
    )
    print_if_worked(True, "Finished", "No grasps were found")

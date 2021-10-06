import os, sys
import argparse
from tqdm import tqdm
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from grasp.class_grasp import Grasp
from grasp.quality_metrics import alpha_from_direction
from functions import (
    assert_TARGET_OBJ_GRP,
    get_dwext_dict,
    get_fmax_list,
    get_object_dict,
    red_txt,
    check_save_for_excel,
    is_TARGET_OBJ_GRP,
    __coordinate_dict_to_list,
    __grp_item_to_Contacts,
    save_to_excel,
    print_if_worked,
)

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

args = parser.parse_args()
OBJ = args.object
GRP = args.grasp
DIR = args.dir
FMAX = args.fmax

assert_TARGET_OBJ_GRP(OBJ, GRP)

assert FMAX >= 0, red_txt("fmax must be positive")

objs = get_object_dict()
fmaxs = get_fmax_list()
dwext = get_dwext_dict()

print(parser.format_usage())

save = check_save_for_excel(OBJ, GRP)

index = []
data = []

prev_obj = ""
worked = False
save = check_save_for_excel(OBJ, GRP)

for obj, items in tqdm(
    objs.items(),
    total=len(objs),
    unit="obj",
    colour="red",
    leave=True,
    desc="Updating Alpha Info of Excel file",
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
            index.append(obj + "-" + grp)
            worked = True
            grasp_obj = Grasp(
                __coordinate_dict_to_list(items["center of mass"]),
                __grp_item_to_Contacts(items["grasps"][grp]),
            )
        data_obj = []
        for f_max in tqdm(
            fmaxs,
            total=len(fmaxs),
            unit="fmax",
            colour="green",
            leave=False,
            desc=f"going through fmax of {grp}",
        ):
            for key_dir, d_w_ext in tqdm(
                dwext.items(),
                total=len(dwext.items()),
                unit="dir",
                colour="magenta",
                leave=False,
                desc=f"going through directions of {f_max}",
            ):
                worked = True
                d_w_ext[3] *= items["characteristic length"]
                d_w_ext[4] *= items["characteristic length"]
                d_w_ext[5] *= items["characteristic length"]
                alpha = round(alpha_from_direction(grasp_obj, d_w_ext, f_max)[0], 3)
                data_obj.append(alpha)
                if not save:
                    print(
                        "OBJ:{}, GRP:{}, FMAX:{}, DIR:{}, ALPHA:{}".format(
                            obj, grp, f_max, key_dir, alpha
                        )
                    )

        data_obj = np.array(data_obj).flatten()
        data.append(data_obj)

if save and worked:
    columns = []
    for f_max in fmaxs:
        for key_dir in dwext.keys():
            columns.append(key_dir + " <" + str(f_max) + ">")

    save_to_excel("Task Oriented Analysis", "raw alpha", data, columns, index)

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
        index,
    )
print_if_worked(worked, "Finished", "No grasps were found")

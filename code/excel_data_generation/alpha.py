import os, sys
from tqdm import tqdm
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from grasp.quality_metrics import alpha_from_direction
from functions import (
    get_dwext_dict,
    get_OBJECT_dict,
    get_object_dict,
    save_to_excel,
    print_if_worked,
    partition_str,
)

objects = get_OBJECT_dict()
objs = get_object_dict()
dwext = get_dwext_dict()

index = []
data = []

worked = False

for key_grasp, grasp in tqdm(
    objects["grasps"].items(),
    total=len(objects["grasps"].items()),
    unit="grp",
    colour="red",
    leave=True,
    desc="Updating Alpha Info of Excel file",
):
    index.append(key_grasp)
    name_obj, name_grasp = partition_str(key_grasp)
    char_length = objs[name_obj]["characteristic length"]
    grasp_obj = grasp
    row_data = []
    for key_dir, d_w_ext in tqdm(
        dwext.items(),
        total=len(dwext.items()),
        unit="dir",
        colour="magenta",
        leave=False,
        desc=f"going through directions of {key_grasp}",
    ):
        worked = True
        d_ext_mod = np.copy(d_w_ext)
        d_ext_mod[3:] *= char_length
        d_ext_mod = d_ext_mod.round(3)
        alpha = round(alpha_from_direction(grasp_obj, d_ext_mod)[0], 3)
        row_data.append(alpha)
    data.append(np.array(row_data).flatten())
if worked:
    columns = []
    for key_dir in dwext.keys():
        columns.append(key_dir)
    save_to_excel(name_of_sheet="alpha", data=data, columns=columns, index=index)
print_if_worked(worked, "Finished", "No grasps were found")

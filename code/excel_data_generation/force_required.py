import os, sys
from tqdm import tqdm
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from functions import (
    read_excel,
    get_OBJECT_dict,
    red_txt,
    save_to_excel,
    print_if_worked,
    get_dwext_dict,
    partition_str,
)

objects = get_OBJECT_dict()
dwext = get_dwext_dict()

df_alpha = read_excel(file_name="Task Oriented Analysis", sheet_name="alpha")

dirs = ["X", "Y", "Z", "mX", "mY", "mZ"]

for d in dirs:
    if d not in df_alpha.columns:
        exit(red_txt(f"The Alpha Table doesnt have the requiered direction: {d}"))

columns = []
for force in objects["forces"].keys():
    columns.append(force)

index = []
for grasp in objects["grasps"].keys():
    index.append(grasp)

data = np.zeros((len(index), len(columns)))

worked = False

for key_grasp in tqdm(
    objects["grasps"].keys(),
    total=len(objects["grasps"].keys()),
    unit="grp",
    colour="red",
    leave=True,
    desc="Updating Min Force Required Info of Excel file",
):
    name_obj, name_grasp = partition_str(key_grasp)
    for key_force, value_force in objects["forces"].items():
        worked = True
        name_obj2, name_force = partition_str(key_force)
        if name_obj != name_obj2:
            continue
        min_f = -1
        for i, val in enumerate(value_force, 0):
            if val == 0:
                continue
            col_dir = "-" if val < 0 else ""
            col_dir += dirs[i]
            val_alpha = df_alpha.loc[key_grasp, col_dir]
            if val_alpha <= 0:
                continue
            min_f_temp = round(abs(val) / val_alpha, 3)
            min_f = min_f_temp if min_f_temp > min_f else min_f
        data[index.index(key_grasp), columns.index(key_force)] = min_f


if worked:
    data1 = []
    for row in data:
        mx = max(row)
        row_min = np.copy(row)
        row_min[row_min <= 0] = np.inf
        mn = min(row_min)
        val1 = [0, "none"]
        val2 = [0, "none"]
        row_t = list(row)
        if mx > 0:
            frc_mx = columns[row_t.index(mx)]
            val1 = [mx, partition_str(frc_mx)[1]]
        if mn < np.inf:
            frc_mn = columns[row_t.index(mn)]
            val2 = [mn, partition_str(frc_mn)[1]]
        data1.append(val1 + val2)

    data2 = []
    index_obj = []
    mx = -1
    for i, idx in enumerate(index):
        if mx < data1[i][0]:
            mx = data1[i][0]
        if (
            i == len(index) - 1
            or partition_str(idx)[0] != partition_str(index[i + 1])[0]
        ):
            data2.append(mx)
            index_obj.append(partition_str(idx)[0])
            mx = -1

    data3 = []
    for row in data.T:
        row_min = np.copy(row)
        row_min[row_min <= 0] = np.inf
        mn = min(row_min)
        val = [0, "none"]
        row_t = list(row)
        if mn < np.inf:
            grp_mn = index[row_t.index(mn)]
            val = [mn, partition_str(grp_mn)[1]]
        data3.append(val)

    data4 = []
    mx = -1
    mn = float("inf")
    count = 0
    for i, idx in enumerate(columns):
        if mx < data3[i][0]:
            mx = data3[i][0]
            grp_mx = data3[i][1]
        if mn > data3[i][0] > 0:
            mn = data3[i][0]
            grp_mn = data3[i][1]
        if (
            i == len(columns) - 1
            or partition_str(idx)[0] != partition_str(columns[i + 1])[0]
        ):
            data4.append([mn, grp_mn, mx, grp_mx, data2[count]])
            count += 1
            mx = -1
            mn = float("inf")

    columns2 = [
        "min",
        "grasp",
        "all tasks - limited",
        "grasp_",
        "all tasks - all grasps",
    ]
    data[data == 0] = None
    save_to_excel(
        name_of_file="Task Oriented Analysis",
        name_of_sheet="force required",
        data=data.T,
        columns=index,
        index=columns,
    )
    save_to_excel(
        name_of_file="Task Oriented Analysis",
        name_of_sheet="force required - obj",
        data=data4,
        columns=columns2,
        index=index_obj,
    )
print_if_worked(worked, "Finished", "No grasps were found")

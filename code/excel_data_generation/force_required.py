import os, sys
from tqdm import tqdm
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from functions import (
    get_raw_force_dict,
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

df_alpha = read_excel(file_name="Task Oriented Analysis", sheet_name="alpha1")
df_vec = read_excel(
    file_name="Task Oriented Analysis", sheet_name="alpha - force vectors1"
)

dirs = ["X", "Y", "Z", "mX", "mY", "mZ"]

for d in dirs:
    if d not in df_alpha.columns:
        exit(red_txt(f"The Alpha Table doesnt have the requiered direction: {d}"))

columns = []
for force in objects["perturbations"].keys():
    columns.append(force)

index = []
for grasp in objects["grasps"].keys():
    index.append(grasp)

data = np.zeros((len(index), len(columns)))
data6 = np.empty((len(index), len(columns)), dtype=object)

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
    for key_force, value_force in objects["perturbations"].items():
        worked = True
        name_obj2, name_force = partition_str(key_force)
        if name_obj != name_obj2:
            continue
        min_f = -1
        val_vec = "NONE"
        for i, val in enumerate(value_force, 0):
            if val == 0:
                continue
            col_dir = "-" if val < 0 else ""
            col_dir += dirs[i]
            val_alpha = df_alpha.loc[key_grasp, col_dir]
            if val_alpha <= 0:
                continue
            min_f_temp = round(abs(val) / val_alpha, 3)

            if min_f_temp > min_f:
                min_f = min_f_temp

                val_vec = df_vec.loc[key_grasp, col_dir]
                val_vec = val_vec.replace("] [", ",")
                val_vec = val_vec[1:-1]
                val_vec = val_vec.split(",")
                val_vec = list(map(float, val_vec))
                val_vec = np.array(val_vec)
                val_vec_temp = min_f * val_vec
                fc_str = []
                for i in range(0, len(val_vec_temp), 3):
                    fc_str.append(str(list(val_vec_temp[i : i + 3].round(3))))
                val_vec = " ".join(fc_str)

        data[index.index(key_grasp), columns.index(key_force)] = min_f
        data6[index.index(key_grasp), columns.index(key_force)] = val_vec

if worked:
    columns1 = [
        "min",
        "frc",
        "max",
        "frc_",
    ]
    data1 = []
    for row in data:
        mx = max(row)
        row_min = np.copy(row)
        row_min[row_min <= 0] = np.inf
        mn = min(row_min)
        val1 = [0, "none"]
        val2 = [0, "none"]
        row_t = list(row)
        if mn < np.inf:
            frc_mn = columns[row_t.index(mn)]
            val1 = [mn, partition_str(frc_mn)[1]]
        if mx > 0:
            frc_mx = columns[row_t.index(mx)]
            val2 = [mx, partition_str(frc_mx)[1]]
        data1.append(val1 + val2)

    data2 = []
    index_obj = []
    mx = -1
    for i, idx in enumerate(index):
        if mx < data1[i][2]:
            mx = data1[i][2]
        if (
            i == len(index) - 1
            or partition_str(idx)[0] != partition_str(index[i + 1])[0]
        ):
            data2.append(mx)
            index_obj.append(partition_str(idx)[0])
            mx = -1
    columns3 = [
        "min",
        "grp",
        "max",
        "grp_",
    ]
    data3 = []
    for row in data.T:
        row_min = np.copy(row)
        row_min[row_min <= 0] = np.inf
        mn = min(row_min)
        mx = max(row)
        val1 = [0, "none"]
        val2 = [0, "none"]
        row_t = list(row)
        if mn < np.inf:
            grp_mn = index[row_t.index(mn)]
            val1 = [mn, partition_str(grp_mn)[1]]
        if mx > 0:
            grp_mx = index[row_t.index(mx)]
            val2 = [mx, partition_str(grp_mx)[1]]
        data3.append(val1 + val2)

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

    columns4 = [
        "min",
        "grasp",
        "all tasks - limited",
        "grasp_",
        "all tasks - all grasps",
    ]
    data5 = []
    raw_frc_dict = get_raw_force_dict()
    for key_force, value_force in objects["perturbations"].items():
        if key_force in raw_frc_dict:
            key = key_force
        else:
            key = key_force.rpartition("_")[0]
        desc = raw_frc_dict[key]
        for arr in desc:
            arr[0] = round(arr[0], 3)
        data5.append([str(desc), str(list(np.array(value_force).round(3)))])
    columns5 = ["description", "vector"]
    data[data == 0] = None
    save_to_excel(
        name_of_file="Task Oriented Analysis",
        name_of_sheet="force required1",
        data=data.T,
        columns=index,
        index=columns,
    )
    save_to_excel(
        name_of_file="Task Oriented Analysis",
        name_of_sheet="force required - grasp1",
        data=data1,
        columns=columns1,
        index=index,
    )
    save_to_excel(
        name_of_file="Task Oriented Analysis",
        name_of_sheet="force required - perturbation1",
        data=data3,
        columns=columns3,
        index=columns,
    )
    save_to_excel(
        name_of_file="Task Oriented Analysis",
        name_of_sheet="force required - obj1",
        data=data4,
        columns=columns4,
        index=index_obj,
    )
    save_to_excel(
        name_of_file="Task Oriented Analysis",
        name_of_sheet="force description",
        data=data5,
        columns=columns5,
        index=columns,
    )
    save_to_excel(
        name_of_file="Task Oriented Analysis",
        name_of_sheet="force required - vectors1",
        data=data6.T,
        columns=index,
        index=columns,
    )
print_if_worked(worked, "Finished", "No grasps were found")

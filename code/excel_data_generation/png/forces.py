import os, sys, shutil
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import (
    object_file_name,
    print_if_worked,
    path_join_str,
    path_starting_from_code,
    get_OBJECT_dict,
    get_object_dict,
    partition_str,
    get_raw_force_dict,
    __coordinate_dict_to_list,
)

folder = path_join_str(path_starting_from_code(1), "excel/images/frc/")
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print("Failed to delete %s. Reason: %s" % (file_path, e))

objs = get_object_dict()
old_data = get_raw_force_dict()
dir_sup = ["X", "Y", "Z"]
data = {}
for key, items in old_data.items():
    obj = key.partition("-")[0]
    if obj not in objs:
        continue
    frc = key.partition("-")[2]
    cm = __coordinate_dict_to_list(objs[obj]["center of mass"])
    if frc == "hold":
        for di in dir_sup:
            mag = abs(items[0][0])
            data[key + "_" + di] = [{"mag": mag, "dir": di, "pos": cm}]
            data[key + "_-" + di] = [{"mag": -mag, "dir": di, "pos": cm}]
    else:
        temp_data = []
        for item in items:
            if item[2] == "com":
                pos = cm
            else:
                pos = list(np.array(item[2:]) / 100)
            temp_data.append({"mag": item[0], "dir": item[1], "pos": pos})
        data[key] = temp_data

objects = get_OBJECT_dict()

worked = False
counter = 0
for obj1, mesh in tqdm(
    objects["meshes"].items(),
    total=len(objects["meshes"].items()),
    unit="obj",
    colour="red",
    leave=True,
    desc="Going through the objects",
):
    for frc1, force in tqdm(
        data.items(),
        total=len(data.items()),
        unit="dir",
        colour="magenta",
        leave=False,
        desc=f"saving frc img of {obj1}",
    ):
        obj, frc = partition_str(frc1)
        if obj != obj1:
            continue
        worked = True

        # mesh.view(frc1, forces=force)
        mesh.view(frc1, forces=force, view_not_return=False).savefig(
            path_join_str(
                path_starting_from_code(1),
                "excel/images/frc/" + str(counter) + "_" + frc1 + ".png",
            ),
            bbox_inches="tight",
        )
        counter += 1

print_if_worked(
    worked,
    "Finished the Image Creation" + 50 * " ",
    "No objects and/or forces declared on "
    + object_file_name()
    + ".yaml or object and/or force passed as argument doesn't exists",
)

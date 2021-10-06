import os, sys
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import (
    __get_grasp_dict,
    save_yaml,
    get_raw_force_dict,
    object_file_name,
)

old_data = get_raw_force_dict()
dir_sup = ["X", "Y", "Z"]
data = {}
for key, items in old_data.items():
    obj = key.partition("-")[0]
    frc = key.partition("-")[2]
    if frc == "hold":
        for di in dir_sup:
            mag = abs(items[0][0])
            data[key + "_" + di] = [[mag, di, "com"]]
            data[key + "_-" + di] = [[-1 * mag, di, "com"]]
    else:
        data[key] = items

objects = __get_grasp_dict()

vec_helper = {
    "X": np.array([1, 0, 0], dtype=float),
    "Y": np.array([0, 1, 0], dtype=float),
    "Z": np.array([0, 0, 1], dtype=float),
}

for key, item in tqdm(
    data.items(),
    total=len(data),
    unit="force",
    colour="red",
    leave=True,
    desc="Updating Force Definitions of " + object_file_name() + ".yaml",
):
    obj = key.partition("-")[0]
    frc = key.partition("-")[2]
    if not "forces" in objects[obj]:
        objects[obj]["forces"] = {}

    forces = np.zeros((6,))
    for point in item:
        mag = point[0]
        di = point[1]
        fov = mag * vec_helper[di]
        if len(point) > 4:
            com = list(objects[obj]["center of mass"].values())
            fom = np.cross(
                (np.array(point[2:]).flatten() - np.array(com).flatten()),
                fov,
            )
        else:
            fom = [0, 0, 0]
        forces += np.array([fov, fom]).flatten()
    objects[obj]["forces"][frc] = str(list(forces))

save_yaml("objects", objects)

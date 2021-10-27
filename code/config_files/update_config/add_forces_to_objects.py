import os, sys
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import (
    get_object_dict,
    save_yaml,
    get_raw_force_dict,
    object_file_name,
)

objects = get_object_dict()

old_data = get_raw_force_dict()
vec_helper = {
    "X": np.array([1, 0, 0], dtype=float),
    "Y": np.array([0, 1, 0], dtype=float),
    "Z": np.array([0, 0, 1], dtype=float),
}
dir_sup = vec_helper.keys()
data = {}
for key, items in old_data.items():
    obj = key.partition("-")[0]
    if obj not in objects:
        continue
    frc = key.partition("-")[2]
    if frc == "hold":
        for di in dir_sup:
            mag = abs(items[0][0])
            data[key + "_" + di] = [[mag, di, "com"]]
            data[key + "_-" + di] = [[-1 * mag, di, "com"]]
    else:
        data[key] = items

for key, item in tqdm(
    data.items(),
    total=len(data),
    unit="force",
    colour="red",
    leave=True,
    desc="Updating Force Definitions of " + object_file_name() + ".yaml",
):
    obj, part, frc = key.partition("-")
    if "perturbations" not in objects[obj]:
        objects[obj]["perturbations"] = {}

    forces = np.zeros((6,))
    for point in item:
        mag = point[0]
        di = point[1]
        fov = mag * vec_helper[di]
        if len(point) > 4:
            com = list(objects[obj]["center of mass"].values())
            loc = np.array(point[2:]) / 100 - com
            fom = np.cross(
                loc,
                fov,
            )
        else:
            fom = [0, 0, 0]
        forces += np.array([fov, fom]).flatten().round(5)
    objects[obj]["perturbations"][frc] = str(list(forces))
for obj, items in objects.items():
    perturbation = {}
    for key in data.keys():
        obj1, part, frc = key.partition("-")
        if obj1 != obj:
            continue
        perturbation[frc] = objects[obj]["perturbations"][frc]
    objects[obj]["perturbations"] = perturbation
save_yaml(object_file_name(False), objects)

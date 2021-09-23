import os, sys
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import (
    get_grasp_dict,
    save_yaml,
    get_raw_force_dict,
    object_file_name,
)

data = get_raw_force_dict()

objects = get_grasp_dict()

for key, item in tqdm(
    data.items(),
    total=len(data),
    unit="force",
    colour="red",
    leave=True,
    desc="Updating Force Definitions of" + object_file_name() + ".yaml",
):
    obj = key.partition("-")[0]
    frc = key.partition("-")[2]
    if not "forces" in objects[obj]:
        objects[obj]["forces"] = {}

    forces = np.zeros((6,))
    for point in item:
        if point[1] == "X":
            vec = np.array([point[0], 0, 0])
        elif point[1] == "Y":
            vec = np.array([0, point[0], 0])
        else:
            vec = np.array([0, 0, point[0]])
        if len(point) > 4:
            x = objects[obj]["center of mass"]["x"]
            y = objects[obj]["center of mass"]["y"]
            z = objects[obj]["center of mass"]["z"]
            x1 = float(point[2])
            y1 = float(point[3])
            z1 = float(point[4])
            com = np.cross(
                (np.array([x1, y1, z1]).flatten() - np.array([x, y, z]).flatten())
                / 100,
                vec,
            )
        else:
            com = [0, 0, 0]
        forces += np.array([vec, com]).flatten()
    objects[obj]["forces"][frc] = {
        "x": float(forces[0]),
        "y": float(forces[1]),
        "z": float(forces[2]),
        "mx": float(forces[3]),
        "my": float(forces[4]),
        "mz": float(forces[5]),
    }

save_yaml("objects", objects)

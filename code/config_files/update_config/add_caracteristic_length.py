import os, sys
import numpy as np
from tqdm import tqdm
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import get_object_dict, save_yaml, object_file_name, get_STLs_dict

objects = get_object_dict()
STLs = get_STLs_dict()

for key, item in tqdm(
    objects.items(),
    total=len(objects),
    unit="object",
    colour="red",
    leave=True,
    desc="Adding Caracteristic Length definitions to " + object_file_name() + ".yaml",
):
    x = objects[key]["center of mass"]["x"]
    y = objects[key]["center of mass"]["y"]
    z = objects[key]["center of mass"]["z"]
    com = np.array([x, y, z])
    mesh = STLs[key]
    dist = -float("inf")
    for pt in mesh.vertices:
        t_dist = math.dist(com, pt)
        dist = t_dist if t_dist > dist else dist
    objects[key]["characteristic length"] = round(dist, 5)

save_yaml(object_file_name(False), objects)

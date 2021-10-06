from stl import mesh
import sys, os
import os
import random
import string

path = "../stl/"

files = os.listdir(path)

sys.path.append(os.path.dirname(__file__))
from functions import get_STLs_dict, get_object_dict, save_yaml, object_file_name

objects = get_object_dict()

SCALE = 1 / 100

for obj, items in objects.items():
    com = items["center of mass"]
    items["center of mass"] = {
        "x": com["x"] * SCALE,
        "y": com["y"] * SCALE,
        "z": com["z"] * SCALE,
    }
    for grp, pts in items["grasps"].items():
        grp_points = pts.values()
        new_pts = {}
        for pt in grp_points:
            position_name = "".join(
                random.choice(string.ascii_letters) for x in range(5)
            )
            new_pts[position_name] = {
                "x": pt["x"] * SCALE,
                "y": pt["y"] * SCALE,
                "z": pt["z"] * SCALE,
            }
        objects[obj]["grasps"][grp] = new_pts

save_yaml("objects", objects)

# for f in files:
#     my_mesh = mesh.Mesh.from_file(path + f)
#     my_mesh.points *= SCALE
#     my_mesh.save(path + f)

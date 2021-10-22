import os, sys
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from functions import get_STL_dict, get_object_dict, save_yaml, object_file_name

STLs = get_STL_dict()
objects = get_object_dict()

letters = ["D", "I", "P"]

for obj, mesh in tqdm(
    STLs.items(),
    total=len(STLs),
    unit="obj",
    colour="red",
    leave=True,
    desc="Updating Grasp Definitions of " + object_file_name() + ".yaml",
):
    for grp, pts in objects[obj]["grasps"].items():
        new_pts = {}
        for idx, pt in pts.items():
            new_pt = mesh.contact_from_point([pt["x"], pt["y"], pt["z"]])
            rot = new_pt.r.round(3).flatten()
            rotation = list(map(str, rot))
            str_rm = ",".join(rotation)
            new_pts[idx] = {
                "x": round(float(pt["x"]), 5),
                "y": round(float(pt["y"]), 5),
                "z": round(float(pt["z"]), 5),
                # "z": round(float(new_pt.c[2]), 5),
                "rm": str_rm,
            }
        if len(new_pts) >= 5:
            del_list = []
            for i in range(1, 6):
                found_distal = False
                for l in letters:
                    idx = str(i) + l
                    if idx in new_pts:
                        if not found_distal:
                            found_distal = True
                        else:
                            del_list.append(idx)

            for idx in new_pts:
                if idx[0] == "0":
                    del_list.append(idx)
            if len(new_pts) - len(del_list) >= 5:
                for l in letters:
                    idx = "4" + l
                    if idx in new_pts:
                        del_list.append(idx)
            del_list = set(del_list)
            for dp in del_list:
                del new_pts[dp]
        objects[obj]["grasps"][grp] = new_pts

SORT_ORDER = [
    "stl file name",
    "center of mass",
    "characteristic length",
    "grasps",
    "perturbations",
]

SORT_ORDER_POINTS = [
    "01P",
    "1P",
    "1D",
    "02P",
    "2P",
    "2I",
    "2D",
    "03P",
    "3P",
    "3I",
    "3D",
    "04P",
    "4P",
    "4I",
    "4D",
    "05P",
    "5P",
    "5I",
    "5D",
]

for obj, items in objects.items():
    for grp, grasps in items["grasps"].items():
        objects[obj]["grasps"][grp] = {
            key: grasps[key] for key in SORT_ORDER_POINTS if key in grasps
        }
    grasps_dict = {}
    for grp, grasps in items["grasps"].items():
        grasps_dict[grp.upper()] = grasps
    objects[obj]["grasps"] = dict(sorted(grasps_dict.items()))
    objects[obj] = {key: items[key] for key in SORT_ORDER}
new_objs = {}
for obj, items in objects.items():
    head, part, tail = obj.partition("_")
    if tail:
        new_key = head[0].upper() + head[1:] + part + tail[0].upper() + tail[1:]
    else:
        new_key = head[0].upper() + head[1:]
    new_objs[new_key] = items

save_yaml("objects_grip1", new_objs)

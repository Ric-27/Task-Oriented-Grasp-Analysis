import os, sys
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from functions import get_STL_dict, get_object_dict, save_yaml, object_file_name

STLs = get_STL_dict()
objects = get_object_dict()

keep = {"proximal": False, "len": 3, "Fingers": 4}
letters = ["D", "I", "P"]

for obj, mesh in tqdm(
    STLs.items(),
    total=len(STLs),
    unit="obj",
    colour="red",
    leave=True,
    desc="Modifying Grasp Definitions of " + object_file_name() + ".yaml",
):
    for grp, pts in tqdm(
        objects[obj]["grasps"].items(),
        total=len(objects[obj]["grasps"].items()),
        unit="grp",
        colour="magenta",
        leave=False,
        desc=f"going through the grasps of {obj}",
    ):

        new_dict = pts.copy()
        new_dict2 = new_dict.copy()
        if len(pts) > 4:
            # keep distal and if required proximal
            del_list = []
            for i in range(6):
                found_distal = False
                for l in letters:
                    idx = str(i) + l
                    if idx in pts:
                        if not found_distal:
                            found_distal = True
                        else:
                            if not (l == "P" and keep["proximal"]):
                                del_list.append(idx)
            for dele in del_list:
                del new_dict[dele]
            # include palm
            for idx in pts:
                if len(idx) > keep["len"]:
                    new_dict.pop(idx)
            # 4 fingers
            fingers_used = {int(x[:-1]) for x in new_dict}
            new_dict2 = new_dict.copy()
            if len(fingers_used) > keep["Fingers"]:
                for idx in new_dict:
                    idf = int(idx[:-1])
                    if idf == 4:
                        new_dict2.pop(idx)

        objects[obj]["grasps"][grp] = new_dict2


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

save_yaml(object_file_name(False), new_objs)

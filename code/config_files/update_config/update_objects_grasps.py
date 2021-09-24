import os, sys
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import get_STLs_dict, get_object_dict, save_yaml, object_file_name

STLs = get_STLs_dict()
objects = get_object_dict()

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
            new_pts[idx] = {
                "x": float(round(new_pt.c[0], 3)),
                "y": float(round(new_pt.c[1], 3)),
                "z": float(round(new_pt.c[2])),
                "rm": str(new_pt.r.round(3).flatten()),
                "mu": float(round(new_pt.mu, 3)),
            }
        objects[obj]["grasps"][grp] = new_pts


save_yaml("objects", objects)

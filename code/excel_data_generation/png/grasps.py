import os, sys, shutil
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import (
    object_file_name,
    print_if_worked,
    path_join_str,
    path_starting_from_code,
    get_OBJECT_dict,
    partition_str,
)

folder = path_join_str(path_starting_from_code(1), "excel/images/grp/")
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print("Failed to delete %s. Reason: %s" % (file_path, e))
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
    for grp1, grasp in tqdm(
        objects["grasps"].items(),
        total=len(objects["grasps"].items()),
        unit="dir",
        colour="magenta",
        leave=False,
        desc=f"saving grp img of {obj1}",
    ):
        obj, grp = partition_str(grp1)
        if obj != obj1:
            continue
        worked = True
        mesh.view(grp1, grasp.contact_points, view_not_return=False).savefig(
            path_join_str(
                path_starting_from_code(1),
                "excel/images/grp/" + str(counter) + "_" + grp1 + ".png",
            ),
            dpi=100.0,
            bbox_inches="tight",
            pad_inches=0,
            transparent=False,
        )
        counter += 1

print_if_worked(
    worked,
    "Finished the Image Creation" + 50 * " ",
    "No objects and/or grasps declared on "
    + object_file_name()
    + ".yaml or object and/or grasp passed as argument doesn't exists",
)

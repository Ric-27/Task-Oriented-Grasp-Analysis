import os, sys, shutil
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import (
    get_STL_dict,
    object_file_name,
    print_if_worked,
    path_join_str,
    path_starting_from_code,
)

folder = path_join_str(path_starting_from_code(1), "excel/images/obj/")
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print("Failed to delete %s. Reason: %s" % (file_path, e))

STLs = get_STL_dict()

worked = False
counter = 0
for obj in tqdm(
    STLs,
    total=len(STLs),
    unit="obj",
    colour="red",
    leave=True,
    desc="Going through the objects",
):
    worked = True
    STLs[obj].view(obj, view_not_return=False).savefig(
        path_join_str(
            path_starting_from_code(1),
            "excel/images/obj/" + str(counter) + "_" + obj + ".png",
        ),
        bbox_inches="tight",
    )
    counter += 1

print_if_worked(
    worked,
    "Finished the Image Creation" + 50 * " ",
    "No objects and/or grasps declared on "
    + object_file_name()
    + ".yaml or object and/or grasp passed as argument doesn't exists",
)

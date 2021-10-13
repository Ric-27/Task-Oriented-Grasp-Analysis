import os, sys
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from grasp.quality_metrics import friction_form_closure
from grasp.grasp_functions import get_rank
from functions import (
    get_OBJECT_dict,
    save_to_excel,
    print_if_worked,
)

objects = get_OBJECT_dict()

data = []
worked = False

for key_grasp, grasp in tqdm(
    objects["grasps"].items(),
    total=len(objects["grasps"].items()),
    unit="grp",
    colour="red",
    leave=True,
    desc="Updating Grasp Info of Excel file",
):
    worked = True
    d = friction_form_closure(grasp)[0]
    row = [
        key_grasp,
        grasp.nc,
        get_rank(grasp.Gt.transpose()),
        "True" if grasp.indeterminate else "False",
        "True" if grasp.graspable else "False",
        "True" if d > 0 else "False",
    ]
    data.append(row)

if worked:
    index = list(range(0, len(objects["grasps"])))
    save_to_excel(
        name_of_file="Task Oriented Analysis",
        name_of_sheet="raw grasp info",
        data=data,
        columns=["grasp", "nc", "rank", "ind", "grs", "fcc"],
        index=index,
    )
print_if_worked(worked, "Finished", "No grasps were found")

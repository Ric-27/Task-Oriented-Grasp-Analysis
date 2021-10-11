import os, sys
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import get_STL_dict, object_file_name, print_if_worked

parser = argparse.ArgumentParser(
    description="view the grasps saved on the predetermined file"
)
parser.add_argument(
    "-o",
    "--object",
    type=str,
    default="",
    help="select an object [def: all]",
)
args = parser.parse_args()
OBJ = args.object
stl_path = get_STL_dict()

worked = False
if not OBJ == "":
    if OBJ in stl_path:
        worked = True
        stl_path[OBJ].view(OBJ)
else:
    for obj, mesh in stl_path.items():
        worked = True
        mesh.view(obj)

print_if_worked(
    worked,
    "Finished" + 50 * " ",
    "No objects declared on "
    + object_file_name()
    + ".yaml or object passed as argument doesn't exists",
)

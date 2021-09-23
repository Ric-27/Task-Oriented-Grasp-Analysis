import keyboard, os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import get_STLs_dict

stl_path = get_STLs_dict()

# print("\nPress [q] to continue or [z + q] to exit\n")
worked = False
for obj, mesh in stl_path.items():
    worked = True
    print(
        "{} \n range of model: \t X: {:.3f} - {:.3f} \t Y: {:.3f} - {:.3f} \t Z: {:.3f} - {:.3f}".format(
            obj,
            min(mesh.vertices[:, 0]),
            max(mesh.vertices[:, 0]),
            min(mesh.vertices[:, 1]),
            max(mesh.vertices[:, 1]),
            min(mesh.vertices[:, 2]),
            max(mesh.vertices[:, 2]),
        )
    )
    print(" COM: ", mesh.com)

    mesh.view()
    if keyboard.is_pressed("z"):
        exit("\nExecution Cancelled\n")
if worked:
    print("\nFinished\n")
else:
    print("No stl files found\n")

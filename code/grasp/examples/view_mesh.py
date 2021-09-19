import argparse
import keyboard
from glob import iglob
import os
import sys

sys.path.append(os.path.dirname(sys.path[0]))
from class_stl import STL

parser = argparse.ArgumentParser(
    description="view the meshs saved on the stl directory"
)
parser.add_argument(
    "-mr",
    "--mesh_range",
    type=bool,
    default=False,
    help="show mesh coordinate ranges [def: False]",
)
args = parser.parse_args()
stls = list(
    map(
        os.path.basename,
        iglob(
            os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    )
                ),
                "stl/",
            )
            + "*.stl"
        ),
    )
)

print(parser.format_usage())
print("Arguments Values", vars(args))
print("\nPress [q] to continue or [z + q] to exit\n")
worked = False
for object in stls:
    worked = True
    mesh = STL(
        os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
            ),
            "stl/",
        )
        + object
    )
    if args.mesh_range:
        print(
            "{} \n range of model: \t X: {:.3f} - {:.3f} \t Y: {:.3f} - {:.3f} \t Z: {:.3f} - {:.3f}".format(
                object.partition(".")[0],
                min(mesh.vertices[:, 0]),
                max(mesh.vertices[:, 0]),
                min(mesh.vertices[:, 1]),
                max(mesh.vertices[:, 1]),
                min(mesh.vertices[:, 2]),
                max(mesh.vertices[:, 2]),
            )
        )
        print(" cog location: ", mesh.cog)
    else:
        print(object.partition(".")[0])

    mesh.view()
    if keyboard.is_pressed("z"):
        exit("\nExecution Cancelled\n")
if worked:
    print("\nFinished\n")
else:
    print("No stl files found\n")

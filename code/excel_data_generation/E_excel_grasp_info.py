from grasp import class_grasp as Grasp
import os
import argparse
import yaml

parser = argparse.ArgumentParser(
    description="view or save the force analysis of each grasp of each object"
)
parser.add_argument(
    "-o",
    "--object",
    type=str,
    default="",
    help="select an object [def: all]",
)
parser.add_argument(
    "-g",
    "--grasp",
    type=str,
    default="",
    help="select a grasp of an object [def: all]",
)

args = parser.parse_args()
OBJ = args.object
GRP = args.grasp

assert not (
    (GRP != "") and (OBJ == "")
), "Can't specify a grasp without specifying and object"

# reading the data from the file
with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_files/grasps.yaml")
) as f:
    data_grasps = yaml.load(f)

print(data_grasps)

print(parser.format_usage())
print("Arguments Values", vars(args))
print("\nPress [q] to exit, [s] to show current status\n")

if OBJ != "" or GRP != "":
    print("data wont be saved to Excel\n")
    save = False
else:
    print("data will be saved to Excel")
    save = True

index = []
data = []
counter = 0

prev_obj = ""
worked = False
skip = False

for key_grasp, value_grasp in data_grasps.items():
    obj = key_grasp.partition("-")[0]
    grp = key_grasp.partition("-")[2]
    if OBJ != "":
        if OBJ != obj:
            skip = True
        elif GRP != "":
            if GRP != grp:
                skip = True
    if not skip:
        counter += 1
        worked = True
        index.append(counter)
        if save:
            if prev_obj != obj:
                prev_obj = obj
                print("\nworking on... {}:".format(obj), end="", flush=True)
            print("[{}]".format(grp), end="", flush=True)
        path = "./stl/" + obj + ".stl"
        contacts = np.array(value_grasp)
        mesh = STL(path)
        contact_points = []
        for pt in contacts:
            contact_points.append(
                mesh.gen_C_from_coordinates(
                    np.array([pt[0], pt[1], pt[2]], dtype=np.float64),
                    pt[3].upper(),
                )
            )
        contact_points = list_to_vertical_matrix(contact_points)

        grasp = Grasp(mesh.cog, contact_points)
        d = friction_form_closure(grasp)[0]
        data.append(
            [
                key_grasp,
                grasp.nc,
                get_rank(grasp.Gt.transpose()),
                "True" if grasp.indeterminate else "False",
                "True" if grasp.graspable else "False",
                "True" if d > 0 else "False",
            ]
        )
        if not save:
            print(
                "grasp:{}, nc:{}, rank:{}, indeterminate:{}, graspable:{}, ffc:{}".format(
                    key_grasp,
                    grasp.nc,
                    get_rank(grasp.Gt.transpose()),
                    "True" if grasp.indeterminate else "False",
                    "True" if grasp.graspable else "False",
                    "True" if d > 0 else "False",
                )
            )
    skip = False

if save:
    print("\nsaving...", end="")
    columns = ["grasp_name", "nc", "rank", "indeterminate", "graspable", "FFC"]
    data = np.array(data)
    grasp_info = {}
    for i, col in enumerate(columns, 0):
        grasp_info[col] = data[:, i]

    book = load_workbook("Task Oriented Analysis.xlsx")
    writer = pd.ExcelWriter("Task Oriented Analysis.xlsx", engine="openpyxl")
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    df = pd.DataFrame(grasp_info, index, columns)

    df.to_excel(writer, sheet_name="raw grasp info", index=True, na_rep="-")
    writer.save()

    print("saved")
if worked:
    print("\nFinished\n")
else:
    print("\nNo grasps were found\n")

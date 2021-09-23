from grasp import *

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
parser.add_argument(
    "-f",
    "--force",
    type=str,
    default="",
    help="select a force to analyze [def: all]",
)
parser.add_argument(
    "-gf",
    "--grasp_file",
    type=str,
    default="grasps",
    help="name of grasp file [def: grasps]",
)
parser.add_argument(
    "-ff",
    "--force_file",
    type=str,
    default="forces",
    help="name of forces file [def: forces]",
)
parser.add_argument(
    "-a",
    "--alpha",
    type=int,
    default=1,
    help="alpha to study [def: 1]",
)
parser.add_argument(
    "-fc",
    "--fc_max",
    type=int,
    default=100,
    help="max possible fc [def: 100]",
)
parser.add_argument(
    "-fmf",
    "--fmax_file",
    type=str,
    default="fmax",
    help="name of fmax file [def: fmax]",
)

args = parser.parse_args()
OBJ = args.object
GRP = args.grasp
FRC = args.force
ALPHA = args.alpha
END = args.fc_max

assert not (
    (GRP != "") and (OBJ == "")
), "Can't specify a grasp without specifying and object"

# reading the data from the file
with open("./code/config_files/" + args.grasp_file + ".txt") as f:
    data_grasps = f.read()
data_grasps = ast.literal_eval(data_grasps)

# reading the data from the file
with open("./code/config_files/" + args.force_file + ".txt") as f:
    data_force = f.read()
data_force = ast.literal_eval(data_force)

# reading the data from the file
with open("./code/config_files/" + args.fmax_file + ".txt") as f:
    F_MAXS = f.read()
F_MAXS = ast.literal_eval(F_MAXS)

print(parser.format_usage())
print("Arguments Values", vars(args))
print("\nPress [q] to exit, [s] to show current status\n")

if OBJ != "" or GRP != "" or FRC != "":
    print("data wont be saved to Excel\n")
    save = False
else:
    print("data will be saved to Excel")
    save = True

start = time.time()
index = []
prev_obj = ""
worked = False
skip = False
data = np.zeros((len(data_grasps), len(data_force)))
data1 = np.chararray((len(data_grasps), len(data_force)), itemsize=80)
data1[:, :] = ""
row = 0
end = time.time()
# print("declaration time: ", end - start)

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
        index.append(key_grasp)
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

        skip2 = False
        col = 0
        for key_force, value_force in data_force.items():
            obj_force = key_force.partition("-")[0]
            frc = key_force.partition("-")[2]
            if FRC != "" and FRC != frc:
                skip2 = True

            if not skip2 and obj == obj_force:
                worked = True
                d_w_ext = value_force
                fc_max, fc = fc_from_g_v2(grasp, d_w_ext, F_MAXS)
                data[row, col] = fc_max
                if fc_max == -2.5:
                    exit("\nExecution Cancelled\n")
                if fc_max == -3.5:
                    print(
                        "\ncurrent status:\n OBJ:{}, GRP:{}, FRC:{} \n".format(
                            obj, grp, frc
                        )
                    )
                    time.sleep(1)
                    print("\nworking on... {}:".format(obj), end="", flush=True)
                # fc = fc[::3]  # only normal forces
                fc_str = ""
                for i, val in enumerate(fc, 0):
                    if i % 3 == 0:
                        fc_str += ";"
                    else:
                        fc_str += ","
                    if fc_max < 0:
                        fc_str += "-"
                    else:
                        fc_str += str(val.round(3))
                fc_str = fc_str[1:]
                data1[row, col] = fc_str
                if not save:
                    print(
                        "OBJ:{}, GRP:{}, FRC:<{}>{}, fc vector:{}".format(
                            obj, grp, frc, value_force, fc_str
                        )
                    )

            skip2 = False
            col += 1

    skip = False
    row += 1

if save:
    print("\nsaving...", end="")
    columns = []

    for key_force in data_force.keys():
        columns.append(key_force)

    data[data == 0] = None
    data1[data == 0] = None
    force_info = {}
    force_info1 = {}
    for i, col in enumerate(columns, 0):
        force_info[col] = data[:, i]
        force_info1[col] = data1[:, i]
    df = pd.DataFrame(force_info, index, columns)
    df1 = pd.DataFrame(force_info1, index, columns)
    book = load_workbook("Task Oriented Analysis.xlsx")
    writer = pd.ExcelWriter("Task Oriented Analysis.xlsx", engine="openpyxl")
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    df.to_excel(writer, sheet_name="raw forces fmin", index=True, na_rep="")
    df1.to_excel(writer, sheet_name="raw forces vec", index=True, na_rep="")
    writer.save()

    print("saved")
if worked:
    print("\nFinished\n")
else:
    print("\nNo grasps were found\n")

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
    "-fmf",
    "--fmax_file",
    type=str,
    default="fmax",
    help="name of fmax file [def: fmax]",
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

df_alpha = pd.read_excel(
    "./Task Oriented Analysis.xlsx",
    sheet_name="raw alpha mod",
    index_col=0,
    engine="openpyxl",
)

start = time.time()
index = []
prev_obj = ""
dirs = ["X", "Y", "Z", "MX", "MY", "MZ"]
worked = False
skip = False
data = np.zeros((len(data_grasps), len(data_force)))
data1 = np.chararray((len(data_grasps), len(data_force)), itemsize=80)
data1[:, :] = ""
row = 0
end = time.time()
# print("declaration time: ", end - start)

FORCE_MIN_PATTERN = re.compile(r"(?<=<)\d+(\.\d+)?(?=>)")

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
                min_f = -1
                for i, val in enumerate(value_force, 0):
                    if val != 0:
                        col_dir = ""
                        if val < 0:
                            col_dir += "-"
                        col_dir += dirs[i]
                        col_fmax = map(
                            lambda x: "{} <{}>".format(col_dir, str(x)), F_MAXS
                        )
                        for col_f in col_fmax:
                            if keyboard.is_pressed("q"):
                                exit("\nExecution Cancelled\n")
                            if keyboard.is_pressed("s"):
                                print(
                                    "\ncurrent status:\n OBJ:{}, GRP:{}, FORCE VALUE:{}, COL:{} \n".format(
                                        obj, grp, abs(val), col_f
                                    )
                                )
                                time.sleep(1)
                                print(
                                    "\nworking on... {}:".format(obj),
                                    end="",
                                    flush=True,
                                )
                            if df_alpha.loc[obj + "-" + grp, col_f] >= abs(val):
                                min_f_match = FORCE_MIN_PATTERN.search(col_f)
                                min_f_temp = float(
                                    col_f[min_f_match.start() : min_f_match.end()]
                                )
                                min_f = min_f_temp if min_f_temp > min_f else min_f
                                break
                data[row, col] = min_f
                if not save:
                    print(
                        "OBJ:{}, GRP:{}, FORCE NAME:{}, FORCE VECTOR:{}, MIN F:{}".format(
                            obj, grp, key_force, value_force, min_f
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
    force_info = {}
    for i, col in enumerate(columns, 0):
        force_info[col] = data[:, i]
    df = pd.DataFrame(force_info, index, columns)
    book = load_workbook("Task Oriented Analysis.xlsx")
    writer = pd.ExcelWriter("Task Oriented Analysis.xlsx", engine="openpyxl")
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    df.to_excel(writer, sheet_name="raw forces alpha", index=True, na_rep="")
    writer.save()

    print("saved")
if worked:
    print("\nFinished\n")
else:
    print("\nNo grasps were found\n")

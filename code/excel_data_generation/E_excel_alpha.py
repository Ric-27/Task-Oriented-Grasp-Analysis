from grasp import *

parser = argparse.ArgumentParser(
    description="view or save the alpha analysis of each grasp of each object"
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
    "-gf",
    "--grasp_file",
    type=str,
    default="grasps",
    help="name of grasp file [def: grasps]",
)
parser.add_argument(
    "-fmf",
    "--fmax_file",
    type=str,
    default="fmax",
    help="name of fmax file [def: fmax]",
)
parser.add_argument(
    "-df",
    "--dir_file",
    type=str,
    default="dir",
    help="name of directions file [def: dir]",
)
parser.add_argument(
    "-d",
    "--dir",
    type=str,
    default="",
    help="direction to study [def: all]",
)
parser.add_argument(
    "-fm",
    "--fmax",
    type=int,
    default=0,
    help="direction to study [def: all]",
)

args = parser.parse_args()
OBJ = args.object
GRP = args.grasp
DIR = args.dir
FMAX = args.fmax

assert not (
    (GRP != "") and (OBJ == "")
), "Can't specify a grasp without specifying and object"

assert FMAX >= 0, "fmax must be positive"

# reading the data from the file
with open("./code/config_files/" + args.grasp_file + ".txt") as f:
    data_grasps = f.read()
data_grasps = ast.literal_eval(data_grasps)

# reading the data from the file
with open("./code/config_files/" + args.fmax_file + ".txt") as f:
    F_MAXS = f.read()
F_MAXS = ast.literal_eval(F_MAXS)

# reading the data from the file
with open("./code/config_files/" + args.dir_file + ".txt") as f:
    DIR_W_EXT = f.read()
DIR_W_EXT = ast.literal_eval(DIR_W_EXT)


print(parser.format_usage())
print("Arguments Values", vars(args))
print("\nPress [q] to exit, [s] to show current status\n")

if OBJ != "" or GRP != "" or DIR != "" or FMAX != 0:
    print("data wont be saved to Excel\n")
    save = False
else:
    print("data will be saved to Excel")
    save = True

index = []
data = []

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
        data_obj = []
        for f_max in F_MAXS:
            if FMAX != 0:
                f_max = FMAX
            skip2 = False
            for key_dir, d_w_ext in DIR_W_EXT.items():
                if DIR != "" and DIR != key_dir:
                    skip2 = True

                if not skip2:
                    worked = True
                    alpha = round(alpha_from_direction(grasp, d_w_ext, f_max)[0], 3)
                    data_obj.append(alpha)
                    if keyboard.is_pressed("q"):
                        exit("\nExecution Cancelled\n")
                    if keyboard.is_pressed("s"):
                        print(
                            "\ncurrent status:\n OBJ:{}, GRP:{}, FMAX:{}, DIR:{}, ALPHA:{} \n".format(
                                obj, grp, f_max, key_dir, alpha
                            )
                        )
                        time.sleep(1)
                        print("\nworking on... {}:".format(obj), end="", flush=True)
                    if not save:
                        print(
                            "OBJ:{}, GRP:{}, FMAX:{}, DIR:{}, ALPHA:{}".format(
                                obj, grp, f_max, key_dir, alpha
                            )
                        )
            if FMAX != 0:
                break

        data_obj = np.array(data_obj).flatten()
        data.append(data_obj)
    skip = False

if save and worked:
    print("saving...", end="")
    columns = []
    for f_max in F_MAXS:
        for key_dir in DIR_W_EXT.keys():
            columns.append(key_dir + " <" + str(f_max) + ">")
        # columns.append("")
    columns1 = []
    for key_dir in DIR_W_EXT.keys():
        for f_max in F_MAXS:
            columns1.append(key_dir + " <" + str(f_max) + ">")
        # columns1.append("")

    data = np.array(data)
    grasp_info = {}
    for i, col in enumerate(columns, 0):
        grasp_info[col] = data[:, i]

    grasp_info1 = {}
    for col in columns1:
        grasp_info1[col] = grasp_info[col]

    df = pd.DataFrame(grasp_info, index, columns)
    df1 = pd.DataFrame(grasp_info1, index, columns1)

    book = load_workbook("Task Oriented Analysis.xlsx")
    writer = pd.ExcelWriter("Task Oriented Analysis.xlsx", engine="openpyxl")
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    df.to_excel(writer, sheet_name="raw alpha", index=True, na_rep="-")
    df1.to_excel(writer, sheet_name="raw alpha mod", index=True, na_rep="-")
    writer.save()

    print("\nsaved")
if worked:
    print("\nFinished\n")
else:
    print("No grasps, directions and/or fmax were found\n")

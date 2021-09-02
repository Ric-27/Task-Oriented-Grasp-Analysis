from grasp import *

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
    "-gi",
    "--grasp_info",
    type=bool,
    default=False,
    help="show grasp information [def: False]",
)
parser.add_argument(
    "-mr",
    "--mesh_range",
    type=bool,
    default=False,
    help="show mesh coordinate ranges [def: False]",
)

args = parser.parse_args()
OBJ = args.object
GRP = args.grasp
assert not (
    (GRP != "") and (OBJ == "")
), "Can't specify a grasp without specifying and object"

# reading the data from the file
with open("./code/textfiles/" + args.grasp_file + ".txt") as f:
    data_grasps = f.read()
data_grasps = ast.literal_eval(data_grasps)

skip = False
print(parser.format_usage())
print("Arguments Values", vars(args))
print("\nPress [q] to continue or [z + q] to exit\n")
prev_obj = ""
worked = False
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
        worked = True
        path = "./stl/" + obj + ".stl"
        contacts = np.array(data_grasps[key_grasp])
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
        if args.mesh_range:
            if prev_obj != obj:
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
        print("{} \t nc: {}".format(key_grasp, contacts.shape[0]))

        if args.grasp_info:
            grasp = Grasp(mesh.cog, contact_points)
            print("Gt \n", grasp.Gt.round(3))
            grasp.get_classification(True)

        mesh.view(contact_points)

    skip = False
    if keyboard.is_pressed("z"):
        exit("\nExecution Cancelled\n")
    if prev_obj != obj:
        prev_obj = obj
if worked:
    print("\nFinished\n")
else:
    print("No grasps found\n")

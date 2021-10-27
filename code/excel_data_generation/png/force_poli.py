import os, sys, shutil
from tqdm import tqdm
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import (
    object_file_name,
    print_if_worked,
    path_join_str,
    path_starting_from_code,
    get_OBJECT_dict,
    partition_str,
    read_excel,
    sheet_sufix,
)

TRIANGLE_TEMPLATE_C = [  # complex
    "X,X:Y,X:Y:Z",
    "X,X:Y,X:Y:-Z",
    "X,X:-Y,X:-Y:Z",
    "X,X:-Y,X:-Y:-Z",
    "X,X:Z,X:Y:Z",
    "X,X:Z,X:-Y:Z",
    "X,X:-Z,X:Y:-Z",
    "X,X:-Z,X:-Y:-Z",
    "-X,-X:Y,-X:Y:Z",
    "-X,-X:Y,-X:Y:-Z",
    "-X,-X:-Y,-X:-Y:Z",
    "-X,-X:-Y,-X:-Y:-Z",
    "-X,-X:Z,-X:Y:Z",
    "-X,-X:Z,-X:-Y:Z",
    "-X,-X:-Z,-X:Y:-Z",
    "-X,-X:-Z,-X:-Y:-Z",
    "Y,X:Y,X:Y:Z",
    "Y,X:Y,X:Y:-Z",
    "Y,-X:Y,-X:Y:Z",
    "Y,-X:Y,-X:Y:-Z",
    "Y,Y:Z,X:Y:Z",
    "Y,Y:Z,-X:Y:Z",
    "Y,Y:-Z,X:Y:-Z",
    "Y,Y:-Z,-X:Y:-Z",
    "-Y,X:-Y,X:-Y:Z",
    "-Y,X:-Y,X:-Y:-Z",
    "-Y,-X:-Y,-X:-Y:Z",
    "-Y,-X:-Y,-X:-Y:-Z",
    "-Y,-Y:Z,X:-Y:Z",
    "-Y,-Y:Z,-X:-Y:Z",
    "-Y,-Y:-Z,X:-Y:-Z",
    "-Y,-Y:-Z,-X:-Y:-Z",
    "Z,Y:Z,X:Y:Z",
    "Z,Y:Z,-X:Y:Z",
    "Z,-Y:Z,X:-Y:Z",
    "Z,-Y:Z,-X:-Y:Z",
    "Z,X:Z,X:Y:Z",
    "Z,X:Z,X:-Y:Z",
    "Z,-X:Z,-X:Y:Z",
    "Z,-X:Z,-X:-Y:Z",
    "-Z,Y:-Z,X:Y:-Z",
    "-Z,Y:-Z,-X:Y:-Z",
    "-Z,-Y:-Z,X:-Y:-Z",
    "-Z,-Y:-Z,-X:-Y:-Z",
    "-Z,X:-Z,X:Y:-Z",
    "-Z,X:-Z,X:-Y:-Z",
    "-Z,-X:-Z,-X:Y:-Z",
    "-Z,-X:-Z,-X:-Y:-Z",
]
# TRIANGLE_TEMPLATE_S = [  # simple
#     "X,Y,Z",
#     "X,Y,-Z",
#     "X,-Y,Z",
#     "X,-Y,-Z",
#     "-X,Y,Z",
#     "-X,Y,-Z",
#     "-X,-Y,Z",
#     "-X,-Y,-Z",
# ]
POINT_TEMPLATE = {
    "X": np.array([1.0, 0.0, 0.0]),
    "-X": np.array([-1.0, 0.0, 0.0]),
    "Y": np.array([0.0, 1.0, 0.0]),
    "-Y": np.array([0.0, -1.0, 0.0]),
    "Z": np.array([0.0, 0.0, 1.0]),
    "-Z": np.array([0.0, 0.0, -1.0]),
}
# TRIANGLE_DICT_S = {}
# for t_key in TRIANGLE_TEMPLATE_S:
#     t_s = t_key.split(",")
#     tr = []
#     for p in t_s:
#         pt = np.zeros((3,), dtype=float)
#         p_s = p.split(":")
#         for pi in p_s:
#             pt += POINT_TEMPLATE[pi]
#         tr.append(pt)
#     key = t_key.replace(":-", "-")
#     key = key.replace(":", "+")
#     TRIANGLE_DICT_S[key] = tr
TRIANGLE_DICT_C = {}
for t_key in TRIANGLE_TEMPLATE_C:
    t_s = t_key.split(",")
    tr = []
    for p in t_s:
        pt = np.zeros((3,), dtype=float)
        p_s = p.split(":")
        for pi in p_s:
            pt += POINT_TEMPLATE[pi]
        tr.append(pt)
    key = t_key.replace(":-", "-")
    key = key.replace(":", "+")
    TRIANGLE_DICT_C[key] = tr
folder = [
    # path_join_str(path_starting_from_code(1), "excel/images/poli_simple/"),
    path_join_str(path_starting_from_code(1), "excel/images/polytope/"),
]
for fold in folder:
    for filename in os.listdir(fold):
        file_path = os.path.join(fold, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))

objects = get_OBJECT_dict()

df_alpha = read_excel(
    file_name="Task Oriented Analysis", sheet_name="alpha " + sheet_sufix()
)

worked = False
counter = 0
for obj1, mesh in tqdm(
    objects["meshes"].items(),
    total=len(objects["meshes"].items()),
    unit="obj",
    colour="red",
    leave=True,
    desc="Going through the objects",
):
    for grp1, grasp in tqdm(
        objects["grasps"].items(),
        total=len(objects["grasps"].items()),
        unit="dir",
        colour="magenta",
        leave=False,
        desc=f"saving grp img of {obj1}",
    ):
        obj, grp = partition_str(grp1)
        if obj != obj1:
            continue

        # triangles_s = []
        # for key, value in TRIANGLE_DICT_S.items():
        #     points = key.split(",")
        #     poi = []
        #     for i, pt in enumerate(points):
        #         poi.append(df_alpha.loc[grp1, pt] * value[i])
        #     triangles_s.append(poi)
        # triangles_s = np.array(triangles_s).flatten()
        # mx = (
        #     abs(min(triangles_s))
        #     if abs(min(triangles_s)) > max(triangles_s)
        #     else max(triangles_s)
        # )
        # if mx:
        #     triangles_s /= mx
        # triangles_s = triangles_s.reshape(len(TRIANGLE_TEMPLATE_S), 3, 3)

        triangles_c = []
        for key, value in TRIANGLE_DICT_C.items():
            points = key.split(",")
            poi = []
            for i, pt in enumerate(points):
                poi.append(df_alpha.loc[grp1, pt] * value[i])
            triangles_c.append(poi)
        worked = True
        # mesh.view(plot_name=grp1, contacts=grasp.contact_points, poli=triangles_s)
        # mesh.view(
        #     plot_name=grp1,
        #     contacts=grasp.contact_points,
        #     poli=triangles_s,
        #     view_not_return=False,
        # ).savefig(
        #     path_join_str(
        #         path_starting_from_code(1),
        #         "excel/images/poli_simple/" + str(counter) + "_" + grp1 + "_poli-s.png",
        #     ),
        #     dpi=100.0,
        #     bbox_inches="tight",
        #     pad_inches=0,
        #     transparent=False,
        # )
        mesh.view(
            plot_name=grp1,
            contacts=grasp.contact_points,
            poli=triangles_c,
            view_not_return=False,
        ).savefig(
            path_join_str(
                path_starting_from_code(1),
                "excel/images/polytope/" + str(counter) + "_" + grp1 + "_poli.png",
            ),
            dpi=100.0,
            bbox_inches="tight",
            pad_inches=0,
            transparent=False,
        )
        counter += 1

print_if_worked(
    worked,
    "Finished the Image Creation" + 50 * " ",
    "No objects and/or grasps declared on "
    + object_file_name()
    + ".yaml or object and/or grasp passed as argument doesn't exists",
)

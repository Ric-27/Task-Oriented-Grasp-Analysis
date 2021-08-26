# importing the module
import ast
import numpy as np
import pandas as pd
from openpyxl import load_workbook

from class_stl import STL
from class_grasp import Grasp
from quality_metrics import friction_form_closure
from math_tools import list_to_vertical_matrix, get_rank

OBJ = ""
GRSP = ""

# reading the data from the file
with open("./code/textfiles/grasps.txt") as f:
    data_grasps = f.read()
data_grasps = ast.literal_eval(data_grasps)

index = []
data = []
counter = 0

skip = False
for key_grasp, value_grasp in data_grasps.items():
    obj = key_grasp.partition("-")[0]
    grsp = key_grasp.partition("-")[2]
    if OBJ != "":
        if OBJ != obj:
            skip = True
        elif GRSP != "":
            if GRSP != grsp:
                skip = True
    if not skip:
        counter += 1
        index.append(counter)
        print("analysing... \t", key_grasp)
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
    skip = False

if OBJ == "" and GRSP == "":
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

    print("saved grasp info onto excel as raw data")
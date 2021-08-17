# importing the modules
import ast
from openpyxl import load_workbook
import numpy as np
import pandas as pd

from class_stl import STL
from class_grasp import Grasp
from quality_metrics import alpha_from_direction
from math_tools import list_to_vertical_matrix

DIR_W_EXT = {
    "X": [1, 0, 0, 0, 0, 0],
    "-X": [-1, 0, 0, 0, 0, 0],
    "Y": [0, 1, 0, 0, 0, 0],
    "-Y": [0, -1, 0, 0, 0, 0],
    "Z": [0, 0, 1, 0, 0, 0],
    "-Z": [0, 0, -1, 0, 0, 0],
    "X+Y+Z": [1, 1, 1, 0, 0, 0],
    "-X+Y+Z": [-1, 1, 1, 0, 0, 0],
    "-X-Y+Z": [-1, -1, 1, 0, 0, 0],
    "X-Y+Z": [1, -1, 1, 0, 0, 0],
    "X+Y-Z": [1, 1, -1, 0, 0, 0],
    "-X+Y-Z": [-1, 1, -1, 0, 0, 0],
    "-X-Y-Z": [-1, -1, -1, 0, 0, 0],
    "X-Y-Z": [1, -1, -1, 0, 0, 0],
    "mX": [0, 0, 0, 1, 0, 0],
    "-mX": [0, 0, 0, -1, 0, 0],
    "mY": [0, 0, 0, 0, 1, 0],
    "-mY": [0, 0, 0, 0, -1, 0],
    "mZ": [0, 0, 0, 0, 0, 1],
    "-mZ": [0, 0, 0, 0, 0, -1],
    "mX+mY+mZ": [0, 0, 0, 1, 1, 1],
    "-mX+mY+mZ": [0, 0, 0, -1, 1, 1],
    "-mX-mY+mZ": [0, 0, 0, -1, -1, 1],
    "mX-mY+mZ": [0, 0, 0, 1, -1, 1],
    "mX+mY-mZ": [0, 0, 0, 1, 1, -1],
    "-mX+mY-mZ": [0, 0, 0, -1, 1, -1],
    "-mX-mY-mZ": [0, 0, 0, -1, -1, -1],
    "mX-mY-mZ": [0, 0, 0, 1, -1, -1],
    "X+Y+Z+mX+mY+mZ": [1, 1, 1, 1, 1, 1],
}
"""
"""

F_MAXS = [
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    1,
    1.1,
    1.2,
    1.3,
    1.4,
    1.5,
    1.6,
    1.7,
    1.8,
    1.9,
    2,
    2.2,
    2.4,
    2.6,
    2.8,
    3,
    3.2,
    3.4,
    3.6,
    3.8,
    4,
    4.2,
    4.4,
    4.6,
    4.8,
    5,
    5.5,
    6,
    6.5,
    7,
    7.5,
    8,
]
"""
"""

OBJ = ""
GRSP = ""

# reading the data from the file
with open("./code/textfiles/grasps.txt") as f:
    data_grasps = f.read()
data_grasps = ast.literal_eval(data_grasps)

index = []
data = []

skip = False
for key_grasp, value_grasp in data_grasps.items():
    obj = key_grasp.partition(" ")[0]
    grsp = key_grasp.partition(" ")[2]
    if OBJ != "":
        if OBJ != obj:
            skip = True
        elif GRSP != "":
            if GRSP != grsp:
                skip = True
    if not skip:
        index.append(key_grasp)
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
        data_obj = []
        for f_max in F_MAXS:
            for d_w_ext in DIR_W_EXT.values():
                data_obj.append(
                    alpha_from_direction(grasp, d_w_ext, f_max)[0]
                )  # if alpha > 0 else 0)
            # data_obj.append("")

        data_obj = np.array(data_obj).flatten()
        data.append(data_obj)
    skip = False

    if OBJ == key_grasp:
        break

if OBJ == "" and GRSP == "":
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

    print("saved alpha onto excel as raw data")

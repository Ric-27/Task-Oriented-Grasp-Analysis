# importing the module
import ast
from openpyxl import load_workbook
import numpy as np
import pandas as pd

from class_stl import STL
from class_grasp import Grasp
from quality_metrics import fc_from_g
from math_tools import list_to_vertical_matrix

OBJ = ""
GRSP = ""
FRC = ""

# reading the data from the file
with open("./code/textfiles/final_grasps.txt") as f:
    data_grasps = f.read()
data_grasps = ast.literal_eval(data_grasps)

# reading the data from the file
with open("./code/textfiles/forces.txt") as f:
    data_force = f.read()
data_force = ast.literal_eval(data_force)

skip = False

ALPHA = 1
END = 100
index = []

data = np.zeros((len(data_grasps), len(data_force)))
data1 = np.chararray((len(data_grasps), len(data_force)), itemsize=80)
data1[:, :] = ""

row = 0
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

        skip2 = False
        col = 0
        for key_force, value_force in data_force.items():
            obj_force = key_force.partition(" ")[0]
            frc = key_force.partition(" ")[2]
            if FRC != "" and FRC != frc:
                skip2 = True

            if not skip2 and obj == obj_force:
                d_w_ext = value_force
                fc_max, fc = fc_from_g(grasp, d_w_ext, end=END)
                fcn = fc[::3]
                data[row, col] = fc_max
                fcn_str = ""
                for val in fcn:
                    if fc_max > END:
                        fcn_str += "-|"
                    else:
                        fcn_str += str(val.round(3)) + "|"
                data1[row, col] = fcn_str[: len(fcn_str) - 1]
                if OBJ != "" or GRSP != "" or FRC != "":
                    print(key_grasp, frc, fc_max, fcn)

            skip2 = False
            col += 1

    skip = False
    row += 1

if OBJ == "" and GRSP == "" and FRC == "":
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

    print("saved forces onto excel as raw data")

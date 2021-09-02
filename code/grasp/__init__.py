import sys
import os

currentDirectory = os.getcwd()
currentDirectory = str(currentDirectory).replace("\\", "/")
assert (
    currentDirectory.rpartition("/")[2] == "TASK-ORIENTED-GRASP-ANALYSIS"
), "Working folder must be '<path>/TASK-ORIENTED-GRASP-ANALYSIS'"
print(currentDirectory)

sys.path.append("./code/grasp")


from req import *
from class_jacobian import *
from class_grasp import *
from class_stl import *
from data_types import *
from math_tools import *
from quality_metrics import *

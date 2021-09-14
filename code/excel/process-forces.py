import numpy as np
import ast


def moment_force(com, pos, vec):
    return np.cross(pos - com, vec)


with open("./code/textfiles/" + "forces" + ".txt") as f:
    data_force = f.read()
data_force = ast.literal_eval(data_force)

com = np.array([0, 0, 0])
pos = np.array([1, 1, 0])
vec = np.array([0, 0, 1])

print(moment_force(com, pos, vec))
# [ 1 -1  0]

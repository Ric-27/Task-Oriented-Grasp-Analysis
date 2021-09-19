import ast
import os
import yaml
import numpy as np

with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "textfiles/raw_forces.txt")
) as f:
    data = f.read()
data = ast.literal_eval(data)

with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "textfiles/grasps.yaml")
) as f:
    data_objects = yaml.load(f, Loader=yaml.FullLoader)

for key, item in data.items():
    obj = key.partition("-")[0]
    frc = key.partition("-")[2]
    if not "forces" in data_objects[obj]:
        data_objects[obj]["forces"] = {}

    forces = np.zeros((6,))
    for point in item:
        if point[1] == "X":
            vec = np.array([point[0], 0, 0])
        elif point[1] == "Y":
            vec = np.array([0, point[0], 0])
        else:
            vec = np.array([0, 0, point[0]])
        if len(point) > 4:
            x = data_objects[obj]["center of mass"]["x"]
            y = data_objects[obj]["center of mass"]["y"]
            z = data_objects[obj]["center of mass"]["z"]
            x1 = float(point[2])
            y1 = float(point[3])
            z1 = float(point[4])
            mom = np.cross(
                (np.array([x1, y1, z1]).flatten() - np.array([x, y, z]).flatten())
                / 100,
                vec,
            )
        else:
            mom = [0, 0, 0]
        forces += np.array([vec, mom]).flatten()
    data_objects[obj]["forces"][frc] = {
        "x": float(forces[0]),
        "y": float(forces[1]),
        "z": float(forces[2]),
        "mx": float(forces[3]),
        "my": float(forces[4]),
        "mz": float(forces[5]),
    }

with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "textfiles/objects.yaml"),
    "w",
) as f:
    # f.write(yaml.dump({"objects": new_dic}, sort_keys=False))
    f.write(yaml.dump(data_objects, sort_keys=False))

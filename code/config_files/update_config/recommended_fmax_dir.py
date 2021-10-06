import os, sys
import numpy as np
from tqdm import tqdm
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions import (
    get_object_dict,
    save_yaml,
    object_file_name,
    get_STLs_dict,
    get_forces_dict,
)

forces = get_forces_dict()

fmax = []
dir = []
ref = ["X", "Y", "Z", "mX", "mY", "mZ"]
for obj, frcs in forces.items():
    for force_name, frc in frcs["forces"].items():
        for i, fc in enumerate(frc.values(), 0):
            fc_str = ""
            if fc > 0:
                fc_str += ref[i]
            elif fc < 0:
                fc_str += "-" + ref[i]
            dir.append(fc_str)
        max_v = max(frc.values())
        min_v = abs(min(frc.values()))
        max_v = min_v if min_v > max_v else max_v
        fmax.append(round(max_v, 1))

print(sorted(set(fmax)))
print(sorted(set(dir), key=len))

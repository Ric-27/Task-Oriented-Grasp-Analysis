import os, sys
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from functions import path_join_str, path_starting_from_code, green_txt

files = [
    "objects_png",
    "grasps_png",
    "grasp_info",
    "alpha_metric",
    "force_from_alpha",
    "forces_from_metric",
]


def main():
    for file in files:
        print(green_txt("executing " + file.upper()))
        cmd = [
            "python",
            path_join_str(
                path_starting_from_code(), "excel_data_generation/" + file + ".py"
            ),
        ]
        subprocess.Popen(cmd).wait()


if __name__ == "__main__":
    main()

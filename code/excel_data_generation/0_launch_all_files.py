import os, sys
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from functions import path_join_str, path_starting_from_code, green_txt

files = [
    "png/objects",
    "png/grasps",
    "png/forces",
    "grasp_info",
    "alpha",
    "force_required",
    "png/force_poli",
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
        try:
            subprocess.Popen(cmd).wait()
        except Exception:
            exit(Exception)


if __name__ == "__main__":
    main()

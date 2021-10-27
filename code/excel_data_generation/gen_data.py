import os, sys
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from functions import path_join_str, path_starting_from_code, green_txt, sheet_sufix

files = [
    "alpha",
    "force_required",
]
if not (int(sheet_sufix()) % 2):
    files.append("grasp_info")
if not int(sheet_sufix()):
    files.extend(
        [
            "png/objects",
            "png/grasps",
            "png/forces",
            "png/force_poli",
        ]
    )


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

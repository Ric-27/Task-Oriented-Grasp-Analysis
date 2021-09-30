import os
from numpy.lib.arraysetops import isin
import yaml
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from typing import Dict, List, Union, Optional
import ast
import itertools

from grasp.data_types import Contact
from grasp.class_stl import STL


def red_txt(txt: str) -> str:
    return f"\033[91m{txt}\033[00m"


def path_starting_from_code(go_back_n_times: int = 0) -> str:
    path = os.path.dirname(__file__)
    for _ in itertools.repeat(None, go_back_n_times):
        path = os.path.dirname(path)
    return path


def path_join_str(path: str, name: str) -> str:
    return os.path.join(path, name)


def open_file_on_config_dir(file_name: str, extention: str = "yaml") -> Dict:
    ext = "."
    ext += extention
    with open(
        path_join_str(
            path_starting_from_code(),
            "config_files/" + file_name + ext,
        )
    ) as f:
        if extention == "yaml":
            return yaml.load(f, Loader=yaml.FullLoader)
        else:
            return ast.literal_eval(f.read())


def return_config_dict() -> Dict:
    return open_file_on_config_dir("config")


def file_name(key: str) -> str:
    config = return_config_dict()
    return config[key]


def object_file_name() -> str:
    return file_name("object yaml file name")


def raw_forces_file_name() -> str:
    return file_name("raw forces txt file name")


def get_object_dict() -> Dict:
    return open_file_on_config_dir(object_file_name())


def get_grasp_dict() -> Dict:
    objects = get_object_dict()
    for obj in objects:
        if "forces" in objects[obj]:
            objects[obj].pop("forces")
    return objects


def get_forces_dict() -> Dict:
    objects = get_object_dict()
    for obj in objects:
        if "grasps" in objects[obj]:
            objects[obj].pop("grasps")
    return objects


def get_stl_path_dict() -> dict:
    objects = get_object_dict()
    path = path_join_str(path_starting_from_code(1), "stl/")
    for obj in objects:
        objects[obj].pop("grasps")
        objects[obj].pop("forces")
        objects[obj]["stl path"] = path_join_str(
            path, str(objects[obj]["stl file name"]) + ".stl"
        )
        objects[obj].pop("stl file name")
    return objects


def stl_path_dict_item_to_STL(item_of_dict: Dict) -> STL:
    return STL(item_of_dict["stl path"], list(item_of_dict["center of mass"].values()))


def grp_item_to_Contacts(grp_item: Dict) -> List[Contact]:
    return [point_dict_to_Contact(pt) for pt in grp_item.values()]


def point_dict_to_list(point_as_dict: Dict) -> List:
    return [point_as_dict["x"], point_as_dict["y"], point_as_dict["z"]]


def point_dict_to_Contact(point_as_dict: Dict) -> Contact:
    location = point_dict_to_list(point_as_dict)
    rot_matrix = point_as_dict["rm"].split(",")
    rotation_matrix = np.array(list(map(float, rot_matrix))).reshape(3, 3)
    tangential_f_coef = point_as_dict["mu"]
    return Contact(
        location=location,
        rotation_matrix=rotation_matrix,
        tangential_f_coef=tangential_f_coef,
    )


def get_STLs_dict() -> Dict[str, STL]:
    objects = get_stl_path_dict()
    new_dict = {}
    for k, v in objects.items():
        new_dict[k] = stl_path_dict_item_to_STL(v)
    return new_dict


def get_grasps_STLs_dict() -> Dict[str, Dict]:
    grasps = get_grasp_dict()
    stl_path = get_STLs_dict()
    objects = {}
    for k in grasps:
        objects[k] = grasps[k]
        objects[k]["mesh"] = stl_path[k]
    return objects


def assert_TARGET_OBJ_GRP(TARGET_OBJ: str, TARGET_GRP: str):
    assert not ((TARGET_GRP != "") and (TARGET_OBJ == "")), red_txt(
        "Can't specify a grasp without specifying an object"
    )


def check_save_for_excel(TARGET_OBJ: str, TARGET_GRP: str) -> bool:
    if TARGET_OBJ != "" or TARGET_GRP != "":
        print(red_txt("data wont be saved to Excel"))
        return False
    else:
        print(green_txt("data will be saved to Excel"))
        return True


def save_to_excel(
    name_of_file: str,
    name_of_sheet: str,
    data: Union[List, Dict],
    columns: List,
    indexes: List,
) -> None:
    path = path_join_str(path_starting_from_code(1), "excel/" + name_of_file + ".xlsx")
    print(green_txt("saving..."), end="\r")
    dict_data = {}
    if isinstance(data, list):
        data = np.array(data)
        for i, col in enumerate(columns, 0):
            dict_data[col] = data[:, i]
    else:
        dict_data = data

    book = load_workbook(path)
    writer = pd.ExcelWriter(path, engine="openpyxl")
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    df = pd.DataFrame(dict_data, index=indexes, columns=columns)

    df.to_excel(writer, sheet_name=name_of_sheet, index=True, na_rep="")
    writer.save()

    print(
        green_txt("saved data onto sheet:({}) of file:({})").format(
            name_of_sheet, name_of_file
        )
        + 50 * " "
    )


def read_excel(file_name: str, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(
        path_join_str(path_starting_from_code(1), "excel/" + file_name + ".xlsx"),
        sheet_name=sheet_name,
        index_col=0,
        engine="openpyxl",
    )


def is_TARGET_OBJ_GRP(TARGET_OBJ: str, TARGET_GRP: str, obj: str, grp: str) -> bool:
    if TARGET_OBJ == "":
        return True
    if TARGET_OBJ == obj and TARGET_GRP == "":
        return True
    if TARGET_OBJ == obj and TARGET_GRP == grp:
        return True
    return False


def is_TARGET_OBJ(TARGET_OBJ: str, obj: str) -> bool:
    if TARGET_OBJ == "":
        return True
    if TARGET_OBJ == obj:
        return True
    return False


def save_yaml(name_of_file: str, dictionary: Dict):
    with open(
        path_join_str(
            path_starting_from_code(), "config_files/" + name_of_file + ".yaml"
        ),
        "w",
    ) as f:
        f.write(yaml.dump(dictionary, sort_keys=False))
    print(green_txt(name_of_file + ".yaml saved"))


def get_raw_force_dict() -> Dict:
    return open_file_on_config_dir(raw_forces_file_name(), "txt")


def get_fmax_list() -> List:
    config = return_config_dict()
    assert isinstance(config["f max"], str), red_txt("f max in config must be str")
    fmax = config["f max"].split(",")
    fmax_t = []
    for value_fmax in fmax:
        desc = value_fmax.split(":")
        start = float(desc[0])
        stop = float(desc[1])
        step = 1
        stp = 1
        if not len(desc) < 3:
            step = float(desc[2])
            stp = step
        if step < 1:
            start = start / stp
            stop = stop / stp
            step = 1
        for i in range(int(start), int(stop), int(step)):
            if stp < 1:
                fmax_t.append(round(i * stp, 3))
            else:
                fmax_t.append(i)

    return fmax_t


def get_dwext_dict() -> Dict:
    dext_ref = {
        "X": np.array([1, 0, 0, 0, 0, 0]),
        "Y": np.array([0, 1, 0, 0, 0, 0]),
        "Z": np.array([0, 0, 1, 0, 0, 0]),
        "mX": np.array([0, 0, 0, 1, 0, 0]),
        "mY": np.array([0, 0, 0, 0, 1, 0]),
        "mZ": np.array([0, 0, 0, 0, 0, 1]),
    }
    config = return_config_dict()
    dext = config["dWext"].split(",")
    dWext = {}
    for k in dext:
        val = k.split(":")
        res = np.zeros((6,))
        key = ""
        for dir in val:
            if dir[0] == "-":
                key += dir
                res -= dext_ref[dir[1:]]
            else:
                key += ("+" + dir) if not key == "" else dir
                res += dext_ref[dir]
        dWext[key] = list(res)
    return dWext


def green_txt(txt: str) -> str:
    return f"\033[92m{txt}\033[00m"


def print_if_worked(worked: bool, yes: str, no: str):
    if worked:
        print(green_txt(yes))
    else:
        print(red_txt(no))


def main():
    val = (
        __file__.replace(os.path.dirname(__file__), "")[1:]
        + " is meant to be imported not executed"
    )
    print(red_txt(val))


if __name__ == "__main__":
    main()

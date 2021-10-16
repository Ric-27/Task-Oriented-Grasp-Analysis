import os
from numpy.core.numerictypes import obj2sctype
import yaml
import numpy as np
from numpy.linalg import norm
import pandas as pd
from openpyxl import load_workbook
from typing import Dict, List, Union, Tuple
import ast
import itertools

from grasp.data_types import Contact
from grasp.class_stl import STL
from grasp.class_grasp import Grasp


def red_txt(txt: str) -> str:
    return f"\033[91m{txt}\033[00m"


def path_starting_from_code(go_back_n_times: int = 0) -> str:
    path = os.path.dirname(__file__)
    for _ in itertools.repeat(None, go_back_n_times):
        path = os.path.dirname(path)
    return path


def path_join_str(path: str, name: str) -> str:
    return os.path.join(path, name)


def __open_file_on_config_dir(file_name: str, extention: str = "yaml") -> Dict:
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


def __return_config_dict() -> Dict:
    return __open_file_on_config_dir("config")


def __get_value_of_key_in_config_file(key: str) -> str:
    config = __return_config_dict()
    return config[key]


def object_file_name() -> str:
    return __get_value_of_key_in_config_file("object yaml file name")


def __raw_forces_file_name() -> str:
    return __get_value_of_key_in_config_file("raw forces txt file name")


def get_object_dict() -> Dict:
    return __open_file_on_config_dir(object_file_name())


def __get_grasp_dict() -> Dict:
    objects = get_object_dict()
    result = {}
    for obj in objects:
        result[obj] = {"grasps": objects[obj]["grasps"]}
    return result


def __get_forces_dict() -> Dict:
    objects = get_object_dict()
    result = {}
    for obj in objects:
        result[obj] = {"perturbations": objects[obj]["perturbations"]}
    return result


def __get_stl_path_dict() -> dict:
    objects = get_object_dict()
    path = path_join_str(path_starting_from_code(1), "stl/")
    for obj in objects:
        objects[obj].pop("grasps")
        objects[obj].pop("perturbations")
        objects[obj]["stl path"] = path_join_str(
            path, str(objects[obj]["stl file name"]) + ".stl"
        )
        objects[obj].pop("stl file name")
    return objects


def __stl_path_dict_item_to_STL(item_of_dict: Dict) -> STL:
    return STL(item_of_dict["stl path"], list(item_of_dict["center of mass"].values()))


def __coordinate_dict_to_list(point_as_dict: Dict) -> List:
    return [point_as_dict["x"], point_as_dict["y"], point_as_dict["z"]]


def __contact_point_dict_to_Contact(point_as_dict: Dict, contact_name: str) -> Contact:
    location = __coordinate_dict_to_list(point_as_dict)
    rot_matrix = point_as_dict["rm"].split(",")
    rotation_matrix = np.array(list(map(float, rot_matrix))).reshape(3, 3)
    return Contact(
        location=location,
        rotation_matrix=rotation_matrix,
        contact_name=contact_name,
    )


def __grp_item_to_Contacts(grp_item: Dict) -> List[Contact]:
    return [
        __contact_point_dict_to_Contact(point_as_dict=pt, contact_name=key)
        for key, pt in grp_item.items()
    ]


def get_STL_dict() -> Dict[str, STL]:
    objects = __get_stl_path_dict()
    result = {}
    for k, v in objects.items():
        result[k] = __stl_path_dict_item_to_STL(v)
    return result


def get_GRP_dict() -> Dict[str, Grasp]:
    grasps = __get_grasp_dict()
    objs = get_object_dict()
    result = {}
    for obj, values in grasps.items():
        for key_grasp, val_grasp in values["grasps"].items():
            # print(obj + "-" + key_grasp)
            com = __coordinate_dict_to_list(objs[obj]["center of mass"])
            cp = __grp_item_to_Contacts(val_grasp)
            result[obj + "-" + key_grasp] = Grasp(
                p=com,
                contact_points=cp,
            )
    return result


def get_FRC_dict() -> Dict[str, List]:
    forces = __get_forces_dict()
    result = {}
    for obj, values in forces.items():
        for key_force, val_force in values["perturbations"].items():
            value = val_force[1:-2].split(",")
            frc = [float(i) for i in value]
            result[obj + "-" + key_force] = frc
    return result


def get_OBJECT_dict() -> Dict[str, Dict]:
    return {
        "perturbations": get_FRC_dict(),
        "grasps": get_GRP_dict(),
        "meshes": get_STL_dict(),
    }


def partition_str(text: str, partition: str = "-") -> Tuple[str, str]:
    part = text.partition(partition)
    return part[0], part[2]


def assert_OBJ_exist_if_GRP_exist(TARGET_OBJ: str, TARGET_GRP: str):
    assert not ((TARGET_GRP != "") and (TARGET_OBJ == "")), red_txt(
        "Can't specify a grasp without specifying an object"
    )


def check_if_save(
    TARGET_OBJ: str = "", TARGET_GRP: str = "", TARGET_FRC: str = ""
) -> bool:
    if TARGET_OBJ != "" or TARGET_GRP != "" or TARGET_GRP != "":
        print(red_txt("data wont be saved to Excel"))
        return False
    else:
        print(green_txt("data will be saved to Excel"))
        return True


def save_to_excel(
    name_of_sheet: str,
    data: List,
    columns: List,
    index: List,
    name_of_file: str = "Task Oriented Analysis",
) -> None:
    path = path_join_str(path_starting_from_code(1), "excel/" + name_of_file + ".xlsx")

    print(green_txt("saving..."), end="\r")

    dict_data = {}
    data = np.array(data)
    for i, col in enumerate(columns, 0):
        dict_data[col] = data[:, i]

    df = pd.DataFrame(dict_data, index=index, columns=columns)

    # print(df)

    book = load_workbook(path)
    writer = pd.ExcelWriter(path, engine="openpyxl")
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    df.to_excel(writer, sheet_name=name_of_sheet, index=True, na_rep="")
    writer.save()

    print(
        green_txt("saved data onto sheet:({}) of file:({})").format(
            name_of_sheet, name_of_file
        )
        + 50 * " "
    )


def read_excel(
    sheet_name: str, file_name: str = "Task Oriented Analysis"
) -> pd.DataFrame:
    return pd.read_excel(
        path_join_str(path_starting_from_code(1), "excel/" + file_name + ".xlsx"),
        sheet_name=sheet_name,
        index_col=0,
        engine="openpyxl",
    )


def is_obj_grp_OBJ_GRP(TARGET_OBJ: str, TARGET_GRP: str, obj: str, grp: str) -> bool:
    if TARGET_OBJ == "":
        return True
    if TARGET_OBJ == obj and TARGET_GRP == "":
        return True
    if TARGET_OBJ == obj and TARGET_GRP == grp:
        return True
    return False


def is_obj_OBJ(TARGET_OBJ: str, obj: str) -> bool:
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
    return __open_file_on_config_dir(__raw_forces_file_name(), "txt")


def get_fmax_list() -> List:
    config = __return_config_dict()
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


def get_dwext_dict() -> Dict[str, np.ndarray]:
    dext_ref = {
        "X": np.array([1, 0, 0, 0, 0, 0]),
        "Y": np.array([0, 1, 0, 0, 0, 0]),
        "Z": np.array([0, 0, 1, 0, 0, 0]),
        "mX": np.array([0, 0, 0, 1, 0, 0]),
        "mY": np.array([0, 0, 0, 0, 1, 0]),
        "mZ": np.array([0, 0, 0, 0, 0, 1]),
    }
    config = __return_config_dict()
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
        norm_lin = norm(res[:3], 2)
        norm_mom = norm(res[3:], 2)
        if norm_lin:
            res[:3] /= norm_lin
        if norm_mom:
            res[3:] /= norm_mom
        dWext[key] = res
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

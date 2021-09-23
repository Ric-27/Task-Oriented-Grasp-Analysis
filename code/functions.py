import os
import yaml
import numpy as np
from typing import Dict, List
import ast
import itertools

from grasp.data_types import Contact
from grasp.class_stl import STL


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


def point_dict_to_Contact(point_as_dict: Dict) -> Contact:
    return Contact(
        [point_as_dict["x"], point_as_dict["y"], point_as_dict["z"]],
        np.array(float(point_as_dict["rm"])).reshape(3, 3),
        point_as_dict["mu"],
    )


def get_STLs_dict() -> Dict[str, STL]:
    objects = get_stl_path_dict()
    new_dict = {}
    for k, v in objects.items():
        new_dict[k] = stl_path_dict_item_to_STL(v)
    return new_dict


def check_TARGET_OBJ_GRP(TARGET_OBJ: str, TARGET_GRP: str):
    assert not (
        (TARGET_GRP != "") and (TARGET_OBJ == "")
    ), "Can't specify a grasp without specifying an object"


def is_TARGET_OBJ_GRP(TARGET_OBJ: str, TARGET_GRP: str, obj: str, grp: str) -> bool:
    if TARGET_OBJ != "":
        if TARGET_OBJ != obj:
            return True
        elif TARGET_GRP != "" and TARGET_GRP != grp:
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


def get_raw_force_dict() -> Dict:
    return open_file_on_config_dir(raw_forces_file_name(), "txt")


def get_fmax_list() -> List:
    config = return_config_dict()
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
    config = return_config_dict()
    dext = config["dWext"].split(",")
    dWext = []
    return dWext

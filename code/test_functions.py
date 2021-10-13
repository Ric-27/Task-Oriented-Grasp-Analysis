from functions import (
    get_fmaW_list,
    object_file_name,
    __raw_forces_file_name,
    get_dwext_dict,
    get_OBJECT_dict,
)
from itertools import product

list1 = ["X", "-X"]
list2 = ["Y", "-Y"]
list3 = ["Z", "-Z"]

TRIANGLE_TEMPLATE = [
    "X,X:Y,X:Y:Z",
    "X,X:Y,X:Y:-Z",
    "X,X:-Y,X:-Y:Z",
    "X,X:-Y,X:-Y:-Z",
    "X,X:Z,X:Y:Z",
    "X,X:Z,X:-Y:Z",
    "X,X:-Z,X:Y:-Z",
    "X,X:-Z,X:-Y:-Z",
    "-X,-X:Y,-X:Y:Z",
    "-X,-X:Y,-X:Y:-Z",
    "-X,-X:-Y,-X:-Y:Z",
    "-X,-X:-Y,-X:-Y:-Z",
    "-X,-X:Z,-X:Y:Z",
    "-X,-X:Z,-X:-Y:Z",
    "-X,-X:-Z,-X:Y:-Z",
    "-X,-X:-Z,-X:-Y:-Z",
    "Y,X:Y,X:Y:Z",
    "Y,X:Y,X:Y:-Z",
    "Y,-X:Y,-X:Y:Z",
    "Y,-X:Y,-X:Y:-Z",
    "Y,Y:Z,X:Y:Z",
    "Y,Y:Z,-X:Y:Z",
    "Y,Y:-Z,X:Y:-Z",
    "Y,Y:-Z,-X:Y:-Z",
    "-Y,X:-Y,X:-Y:Z",
    "-Y,X:-Y,X:-Y:-Z",
    "-Y,-X:-Y,-X:-Y:Z",
    "-Y,-X:-Y,-X:-Y:-Z",
    "-Y,-Y:Z,X:-Y:Z",
    "-Y,-Y:Z,-X:-Y:Z",
    "-Y,-Y:-Z,X:-Y:-Z",
    "-Y,-Y:-Z,-X:-Y:-Z",
    "Z,Y:Z,X:Y:Z",
    "Z,Y:Z,-X:Y:Z",
    "Z,-Y:Z,X:-Y:Z",
    "Z,-Y:Z,-X:-Y:Z",
    "Z,X:Z,X:Y:Z",
    "Z,X:Z,X:-Y:Z",
    "Z,-X:Z,-X:Y:Z",
    "Z,-X:Z,-X:-Y:Z",
    "-Z,Y:-Z,X:Y:-Z",
    "-Z,Y:-Z,-X:Y:-Z",
    "-Z,-Y:-Z,X:-Y:-Z",
    "-Z,-Y:-Z,-X:-Y:-Z",
    "-Z,X:-Z,X:Y:-Z",
    "-Z,X:-Z,X:-Y:-Z",
    "-Z,-X:-Z,-X:Y:-Z",
    "-Z,-X:-Z,-X:-Y:-Z",
]

lst = ["".join(p) for p in product(list4, list5, list6)]
print(lst)
# print(get_fmax_list())
# print(object_file_name())
# print(__raw_forces_file_name())
# print(get_OBJECT_dict()["forces"].items())

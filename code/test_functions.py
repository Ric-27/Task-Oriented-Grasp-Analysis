from functions import (
    get_fmax_list,
    object_file_name,
    __raw_forces_file_name,
    get_dwext_dict,
    get_OBJECT_dict,
)
from itertools import product

list1 = ["X", "-X", ""]
list2 = [":Y", ":-Y", ""]
list3 = [":Z", ":-Z", ""]
lst = ["".join(p) for p in product(list1, list2, list3)]
print(lst)
# print(get_fmax_list())
# print(object_file_name())
# print(__raw_forces_file_name())
# print(get_OBJECT_dict()["forces"].items())

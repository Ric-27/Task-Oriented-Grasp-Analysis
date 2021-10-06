from functions import (
    get_fmax_list,
    object_file_name,
    __raw_forces_file_name,
    get_dwext_dict,
    get_OBJECT_dict,
)

# print(get_fmax_list())
# print(object_file_name())
# print(__raw_forces_file_name())
print(get_OBJECT_dict()["forces"].items())

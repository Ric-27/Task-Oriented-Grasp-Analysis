import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from class_stl import STL

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
path = (
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    + "/stl/cube_low.stl"
)

mesh = STL(path, [0, 0, 0])
fig_name = "test"
mesh.view(fig_name)

C = mesh.gen_C_randomly(8)

mesh.view(fig_name, C)

C1 = mesh.contact_from_point([5, 0, 0])
C2 = mesh.contact_from_point([0, 5, 0])
C3 = mesh.contact_from_point([0, 0, 5])
C4 = mesh.contact_from_point([-5, 0, 0])
C5 = mesh.contact_from_point([0, -5, 0])
C6 = mesh.contact_from_point([0, 0, -5])
C7 = mesh.contact_from_point([5, 5, 5], 0.3, 0, 4)
mesh.view(
    contacts=[C1, C2, C3, C4, C5, C6, C7],
)

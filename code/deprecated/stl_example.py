from StlClass import STL
import numpy as np

path = "../stl/cube_low.stl"
nc = 3

mesh = STL(path, True)  # generate and object of type stl

mesh.view()  # plot the surface of the object
Ct, Rt, Ce, Re, Cv, Rv = mesh.genRandCR(
    nc
)  # from the mesh, create nc points of contact for each location of contact
C = np.concatenate((Ct, Ce, Cv), axis=0)
R = np.concatenate((Rt, Re, Rv), axis=0)
mesh.viewCR(C, R)  # show these random points in a wireframe view
C1, R1 = mesh.getCRofCoord(
    np.array([5, 0, 0]), "E"
)  # find the closest point for the coordinates 5 0 0 (we know that this is the center of a face of the cube) from this point generate the contact and rotation frame, we specified edge because we know that a triangle's edge pass through the center of the face
C2, R2 = mesh.getCRofCoord(np.array([0, 5, 0]), "E")
C3, R3 = mesh.getCRofCoord(np.array([0, 0, 5]), "E")
C4, R4 = mesh.getCRofCoord(np.array([-5, 0, 0]), "E")
C5, R5 = mesh.getCRofCoord(np.array([0, -5, 0]), "E")
C6, R6 = mesh.getCRofCoord(np.array([0, 0, -5]), "E")
C7, R7 = mesh.getCRofCoord(np.array([5, 5, 5]), "V")
C = np.concatenate((C1, C2, C3, C4, C5, C6))  # the information has to be concatenated
R = np.concatenate((R1, R2, R3, R4, R5, R6))
mesh.viewCR(C, R)
print("mesh center:", mesh.cog)
print("mesh volume:", mesh.volume)
print("mesh inertia:", mesh.inertia)
exit(0)

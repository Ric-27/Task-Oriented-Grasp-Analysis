import sys, os
from stl import mesh
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
import random
from typing import List

sys.path.append(os.path.dirname(__file__))
from data_types import Contact

PORC_LINES = 0.2
X_W = np.array([1, 0, 0])
Y_W = np.array([0, 1, 0])
Z_W = np.array([0, 0, 1])


class STL:
    """The STL class uses the numpy-stl library as the reader for the *.stl files, the class allows for the visualization of meshes, the generation of contact points and their rotation frame for the use in Grasp Calculation"""

    def __init__(self, path: str, center_of_mass: List):
        """The constructor recieves 1 parameter, the path to the file as a string.
        Attributes:
        com is the geometric center of the mesh
        triangles is the array of triangles that make the mesh."""

        self.__mesh = mesh.Mesh.from_file(path)

        # self.volume, self.cog, self.inertia = self.__mesh.get_mass_properties()

        self.triangles = self.__mesh.vectors
        self.com = center_of_mass
        # points = self.triangles.flatten().reshape(self.triangles.shape[0] * 3, 3)
        # self.com = np.array(
        #     [
        #         sum(points[:, 0]) / points.shape[0],
        #         sum(points[:, 1]) / points.shape[0],
        #         sum(points[:, 2]) / points.shape[0],
        #     ]
        # )
        edges_temp = []
        for triangle in self.triangles:
            edges_temp.append([triangle[0], triangle[1]])
            edges_temp.append([triangle[1], triangle[2]])
            edges_temp.append([triangle[2], triangle[0]])
        self.edges = np.array(edges_temp)
        self.vertices = self.triangles.flatten().reshape(self.triangles.shape[0] * 3, 3)

    def view(self, contacts: List[Contact] = None):
        """Shows the mesh as a surface in a matplot plot"""

        figure = plt.figure()
        if sys.version_info >= (3, 7):
            ax = mplot3d.Axes3D(
                figure,
                auto_add_to_figure=False,
                azim=30,
            )  # Python 3.8
            figure.add_axes(ax)  # Python 3.8
        else:
            ax = mplot3d.Axes3D(figure)  # Python 3.6

        collection = mplot3d.art3d.Poly3DCollection(
            self.triangles, linewidths=0.2, alpha=0.4
        )
        collection.set_facecolor([0.7, 0.7, 0.7])
        collection.set_edgecolor([0, 0, 0])
        ax.add_collection3d(collection)
        scale = self.triangles.flatten()
        biggest = max(max(scale), abs(min(scale)))
        ax.auto_scale_xyz(scale, scale, scale)
        ax.scatter(0, 0, 0, color="black")
        ax.plot(
            (0, biggest * PORC_LINES * X_W[0]),
            (0, biggest * PORC_LINES * X_W[1]),
            (0, biggest * PORC_LINES * X_W[2]),
            color="red",
        )
        ax.plot(
            (0, biggest * PORC_LINES * Y_W[0]),
            (0, biggest * PORC_LINES * Y_W[1]),
            (0, biggest * PORC_LINES * Y_W[2]),
            color="green",
        )
        ax.plot(
            (0, biggest * PORC_LINES * Z_W[0]),
            (0, biggest * PORC_LINES * Z_W[1]),
            (0, biggest * PORC_LINES * Z_W[2]),
            color="blue",
        )
        ax.scatter(self.com[0], self.com[1], self.com[2], color="magenta")
        if not contacts is None:
            for contact in contacts:
                n = np.dot(contact.r, X_W)

                cx = contact.c[0]
                cy = contact.c[1]
                cz = contact.c[2]

                ax.scatter(cx, cy, cz, color="red")
                ax.plot(
                    (cx, (cx + n[0] * biggest * PORC_LINES)),
                    (cy, (cy + n[1] * biggest * PORC_LINES)),
                    (cz, (cz + n[2] * biggest * PORC_LINES)),
                    color="red",
                )
        plt.show()

    def gen_C_randomly(
        self,
        number_of_contacts: int,
        tangential_f_coef: float = 0.3,
        torsional_f_coef: float = 0,
        number_cone_faces: int = 8,
    ) -> List[Contact]:

        assert number_of_contacts > 0, "NC must be positive and at least 1"
        nct = 0
        nce = 0
        ncv = 0
        while True:
            # print(nct, nce, ncv)
            if nct + nce + ncv == number_of_contacts:
                break
            elif nct + nce + ncv < number_of_contacts:
                chance = random.choice(["t", "e", "v"])
                nct += 1 if chance == "t" else 0
                nce += 1 if chance == "e" else 0
                ncv += 1 if chance == "v" else 0
        # Triangles

        C = []
        triangles = self.triangles[random.sample(range(self.triangles.shape[0]), k=nct)]
        for triangle in triangles:
            cX = (sum(triangle[:, 0])) / 3
            cY = (sum(triangle[:, 1])) / 3
            cZ = (sum(triangle[:, 2])) / 3
            ci = np.array([cX, cY, cZ])

            vector1 = triangle[0] - ci
            vector2 = triangle[2] - ci
            normal = np.cross(vector1, vector2)

            ni = normal / np.linalg.norm(normal)
            ti = vector1 / np.linalg.norm(vector1)

            if np.linalg.norm(ci + ni - self.com) > np.linalg.norm(ci - self.com):
                ni *= -1

            oi = np.cross(ni, ti)

            ri = np.array(
                [
                    [np.dot(ni, X_W), np.dot(ti, X_W), np.dot(oi, X_W)],
                    [np.dot(ni, Y_W), np.dot(ti, Y_W), np.dot(oi, Y_W)],
                    [np.dot(ni, Z_W), np.dot(ti, Z_W), np.dot(oi, Z_W)],
                ]
            )
            C.append(
                Contact(ci, ri, tangential_f_coef, torsional_f_coef, number_cone_faces)
            )
            # print("triangle")

        # Edges
        same = True
        while same:
            same = False
            edges = self.edges[random.sample(range(self.edges.shape[0]), k=nce)]
            centers = []
            for edge in edges:
                centers.append(
                    [
                        edge[0][0] - edge[1][0],
                        edge[0][1] - edge[1][1],
                        edge[0][2] - edge[1][2],
                    ]
                )
            for i, point_i in enumerate(centers, 0):
                if same == True:
                    break
                for j, point_j in enumerate(centers, 0):
                    if i != j:
                        if point_i == point_j:
                            same = True
                            break

        for edge in edges:
            trianglesOfEdge = []
            for triangle in self.triangles:
                if (
                    (edge[0] == triangle[0]).all()
                    or (edge[0] == triangle[1]).all()
                    or (edge[0] == triangle[2]).all()
                ) and (
                    (edge[1] == triangle[0]).all()
                    or (edge[1] == triangle[1]).all()
                    or (edge[1] == triangle[2]).all()
                ):
                    trianglesOfEdge.append(triangle)
            normalsOfTrianglesofEdge = []
            for triangle in trianglesOfEdge:
                cX = (sum(triangle[:, 0])) / 3
                cY = (sum(triangle[:, 1])) / 3
                cZ = (sum(triangle[:, 2])) / 3
                ci = np.array([cX, cY, cZ])

                vector1 = triangle[0] - ci
                vector2 = triangle[2] - ci
                normal = np.cross(vector1, vector2)

                ni = normal / np.linalg.norm(normal)
                normalsOfTrianglesofEdge.append(ni)
            normalsOfTrianglesofEdge = np.array(normalsOfTrianglesofEdge)
            nX = (sum(normalsOfTrianglesofEdge[:, 0])) / 2
            nY = (sum(normalsOfTrianglesofEdge[:, 1])) / 2
            nZ = (sum(normalsOfTrianglesofEdge[:, 2])) / 2
            nE = np.array([nX, nY, nZ])
            nE = nE / np.linalg.norm(nE)

            cX = (sum(edge[:, 0])) / 2
            cY = (sum(edge[:, 1])) / 2
            cZ = (sum(edge[:, 2])) / 2
            ci = np.array([cX, cY, cZ])

            tE = edge[0] - ci
            tE = tE / np.linalg.norm(tE)

            oE = np.cross(nE, tE)
            oE = oE / np.linalg.norm(oE)

            ri = np.array(
                [
                    [np.dot(nE, X_W), np.dot(tE, X_W), np.dot(oE, X_W)],
                    [np.dot(nE, Y_W), np.dot(tE, Y_W), np.dot(oE, Y_W)],
                    [np.dot(nE, Z_W), np.dot(tE, Z_W), np.dot(oE, Z_W)],
                ]
            )
            C.append(
                Contact(ci, ri, tangential_f_coef, torsional_f_coef, number_cone_faces)
            )
            # print("edge")

        # Points

        same = True
        while same:
            same = False
            vertices = self.vertices[
                random.sample(range(self.vertices.shape[0]), k=ncv)
            ]
            for i, point_i in enumerate(vertices, 0):
                if same == True:
                    break
                for j, point_j in enumerate(vertices, 0):
                    if i != j:
                        if (point_i == point_j).all():
                            same = True
                            break

        for vertex in vertices:
            trianglesOfVertex = []
            for triangle in self.triangles:
                for point in triangle:
                    if (point == vertex).all():
                        trianglesOfVertex.append(triangle)
                        break
            triangleNormals = []
            for triangle in trianglesOfVertex:
                cX = (sum(triangle[:, 0])) / 3
                cY = (sum(triangle[:, 1])) / 3
                cZ = (sum(triangle[:, 2])) / 3
                ci = np.array([cX, cY, cZ])

                vector1 = triangle[0] - ci
                vector2 = triangle[2] - ci
                normal = np.cross(vector1, vector2)
                normal = normal / np.linalg.norm(normal)
                inArray = False
                for normalT in triangleNormals:
                    if (normal == normalT).all():
                        inArray = True
                        break
                if not inArray:
                    triangleNormals.append(normal)
            triangleNormals = np.array(triangleNormals)
            nX = (sum(triangleNormals[:, 0])) / 2
            nY = (sum(triangleNormals[:, 1])) / 2
            nZ = (sum(triangleNormals[:, 2])) / 2
            nV = np.array([nX, nY, nZ])
            nV = nV / np.linalg.norm(nV)

            ctX = (sum(trianglesOfVertex[0][:, 0])) / 3
            ctY = (sum(trianglesOfVertex[0][:, 1])) / 3
            ctZ = (sum(trianglesOfVertex[0][:, 2])) / 3
            cti = np.array([ctX, ctY, ctZ])

            vectorT = trianglesOfVertex[0][0] - cti
            vectorT = vectorT / np.linalg.norm(vectorT)

            tV = np.cross(nV, vectorT)
            tV = tV / np.linalg.norm(tV)

            oV = np.cross(nV, tV)
            oV = oV / np.linalg.norm(oV)

            ri = np.array(
                [
                    [np.dot(nV, X_W), np.dot(tV, X_W), np.dot(oV, X_W)],
                    [np.dot(nV, Y_W), np.dot(tV, Y_W), np.dot(oV, Y_W)],
                    [np.dot(nV, Z_W), np.dot(tV, Z_W), np.dot(oV, Z_W)],
                ]
            )
            C.append(
                Contact(
                    vertex, ri, tangential_f_coef, torsional_f_coef, number_cone_faces
                )
            )
            # print("vertex")

        return C

    def contact_from_point(
        self,
        point: List,
        tangential_f_coef: float = 0.3,
        torsional_f_coef: float = 0,
        number_cone_faces: int = 8,
    ) -> Contact:

        dist = float("inf")
        type_contact = "E"

        coordEdge = self.edges[0]
        for edge in self.edges:
            cX = (sum(edge[:, 0])) / 2
            cY = (sum(edge[:, 1])) / 2
            cZ = (sum(edge[:, 2])) / 2
            cOfE = np.array([cX, cY, cZ])
            temp_dist = np.linalg.norm(cOfE - point)
            if temp_dist < dist:
                dist = temp_dist
                coordEdge = edge

        trianglesOfEdge = []
        for triangle in self.triangles:
            if (
                (coordEdge[0] == triangle[0]).all()
                or (coordEdge[0] == triangle[1]).all()
                or (coordEdge[0] == triangle[2]).all()
            ) and (
                (coordEdge[1] == triangle[0]).all()
                or (coordEdge[1] == triangle[1]).all()
                or (coordEdge[1] == triangle[2]).all()
            ):
                trianglesOfEdge.append(triangle)
        normalsOfTrianglesofEdge = []
        for triangle in trianglesOfEdge:
            cX = (sum(triangle[:, 0])) / 3
            cY = (sum(triangle[:, 1])) / 3
            cZ = (sum(triangle[:, 2])) / 3
            ci = np.array([cX, cY, cZ])

            vector1 = triangle[0] - ci
            vector2 = triangle[2] - ci
            normal = np.cross(vector1, vector2)

            ni = normal / np.linalg.norm(normal)
            normalsOfTrianglesofEdge.append(ni)
        normalsOfTrianglesofEdge = np.array(normalsOfTrianglesofEdge)
        nX = (sum(normalsOfTrianglesofEdge[:, 0])) / 2
        nY = (sum(normalsOfTrianglesofEdge[:, 1])) / 2
        nZ = (sum(normalsOfTrianglesofEdge[:, 2])) / 2
        nE = np.array([nX, nY, nZ])
        nE = nE / np.linalg.norm(nE)

        cX = (sum(coordEdge[:, 0])) / 2
        cY = (sum(coordEdge[:, 1])) / 2
        cZ = (sum(coordEdge[:, 2])) / 2
        cOfE = np.array([cX, cY, cZ])

        tE = coordEdge[0] - cOfE
        tE = tE / np.linalg.norm(tE)

        oE = np.cross(nE, tE)
        oE = oE / np.linalg.norm(oE)

        rOfE = np.array(
            [
                [np.dot(nE, X_W), np.dot(tE, X_W), np.dot(oE, X_W)],
                [np.dot(nE, Y_W), np.dot(tE, Y_W), np.dot(oE, Y_W)],
                [np.dot(nE, Z_W), np.dot(tE, Z_W), np.dot(oE, Z_W)],
            ]
        )
        C = Contact(cOfE, rOfE, tangential_f_coef, torsional_f_coef, number_cone_faces)

        coordVertex = self.vertices[0]
        for vertex in self.vertices:
            temp_dist = np.linalg.norm(vertex - point)
            if temp_dist < dist:
                dist = temp_dist
                coordVertex = vertex

        trianglesOfVertex = []
        for triangle in self.triangles:
            for vertex in triangle:
                if (vertex == coordVertex).all():
                    trianglesOfVertex.append(triangle)
                    break
        triangleNormals = []
        for triangle in trianglesOfVertex:
            cX = (sum(triangle[:, 0])) / 3
            cY = (sum(triangle[:, 1])) / 3
            cZ = (sum(triangle[:, 2])) / 3
            ci = np.array([cX, cY, cZ])

            vector1 = triangle[0] - ci
            vector2 = triangle[2] - ci
            normal = np.cross(vector1, vector2)
            normal = normal / np.linalg.norm(normal)
            inArray = False
            for normalT in triangleNormals:
                if (normal == normalT).all():
                    inArray = True
                    break
            if not inArray:
                triangleNormals.append(normal)
        triangleNormals = np.array(triangleNormals)
        nX = (sum(triangleNormals[:, 0])) / 2
        nY = (sum(triangleNormals[:, 1])) / 2
        nZ = (sum(triangleNormals[:, 2])) / 2
        nV = np.array([nX, nY, nZ])
        nV = nV / np.linalg.norm(nV)

        ctX = (sum(trianglesOfVertex[0][:, 0])) / 3
        ctY = (sum(trianglesOfVertex[0][:, 1])) / 3
        ctZ = (sum(trianglesOfVertex[0][:, 2])) / 3
        cti = np.array([ctX, ctY, ctZ])

        vectorT = trianglesOfVertex[0][0] - cti
        vectorT = vectorT / np.linalg.norm(vectorT)

        tV = np.cross(nV, vectorT)
        tV = tV / np.linalg.norm(tV)

        oV = np.cross(nV, tV)
        oV = oV / np.linalg.norm(oV)

        rOfV = np.array(
            [
                [np.dot(nV, X_W), np.dot(tV, X_W), np.dot(oV, X_W)],
                [np.dot(nV, Y_W), np.dot(tV, Y_W), np.dot(oV, Y_W)],
                [np.dot(nV, Z_W), np.dot(tV, Z_W), np.dot(oV, Z_W)],
            ]
        )
        if np.linalg.norm(C.c - point) > np.linalg.norm(coordVertex - point):
            C = Contact(
                coordVertex,
                rOfV,
                tangential_f_coef,
                torsional_f_coef,
                number_cone_faces,
            )
            type_contact = "V"

        coordTriangle = self.triangles[0]
        for triangle in self.triangles:
            cX = (sum(triangle[:, 0])) / 3
            cY = (sum(triangle[:, 1])) / 3
            cZ = (sum(triangle[:, 2])) / 3
            ci = np.array([cX, cY, cZ])

            temp_dist = np.linalg.norm(ci - point)
            if temp_dist < dist:
                dist = temp_dist
                coordTriangle = triangle

        cX = (sum(coordTriangle[:, 0])) / 3
        cY = (sum(coordTriangle[:, 1])) / 3
        cZ = (sum(coordTriangle[:, 2])) / 3
        ci = np.array([cX, cY, cZ])

        vector1 = coordTriangle[0] - ci
        vector2 = coordTriangle[2] - ci
        normal = np.cross(vector1, vector2)

        ni = normal / np.linalg.norm(normal)
        ti = vector1 / np.linalg.norm(vector1)
        oi = np.cross(ni, ti)

        ri = np.array(
            [
                [np.dot(ni, X_W), np.dot(ti, X_W), np.dot(oi, X_W)],
                [np.dot(ni, Y_W), np.dot(ti, Y_W), np.dot(oi, Y_W)],
                [np.dot(ni, Z_W), np.dot(ti, Z_W), np.dot(oi, Z_W)],
            ]
        )
        if np.linalg.norm(C.c - point) > np.linalg.norm(ci - point):
            C = Contact(ci, ri, tangential_f_coef, torsional_f_coef, number_cone_faces)
            type_contact = "T"

        return C
        print(
            "point {} was assigned {} in the {} of a triangle of the object mesh".format(
                point,
                C.c,
                "center"
                if type_contact == "T"
                else " vertex"
                if type_contact == "V"
                else "edge",
            )
        )


def main():
    val = (
        __file__.replace(os.path.dirname(__file__), "")[1:]
        + " is meant to be imported not executed"
    )
    print(f"\033[91m {val}\033[00m")


if __name__ == "__main__":
    main()

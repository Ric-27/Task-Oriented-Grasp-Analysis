import sys, os
from matplotlib.figure import Figure
from stl import mesh
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import art3d
from pylab import figure
import random
from typing import List, Union, Dict
import keyboard

sys.path.append(os.path.dirname(__file__))
from data_types import Contact

LINE_PERC = 0.18
TEXT_SIZE = 10
X_W = np.array([1, 0, 0])
Y_W = np.array([0, 1, 0])
Z_W = np.array([0, 0, 1])
O = np.array([0, 0, 0])


def keypress(event):
    if keyboard.is_pressed("esc"):
        val = "EXECUTION CANCELLED" + 40 * " "
        sys.exit(f"\033[91m{val}\033[00m")
    if keyboard.is_pressed("q"):
        plt.close()


class STL:
    """The STL class uses the numpy-stl library as the reader for the *.stl files, the class allows for the visualization of meshes, the generation of contact points and their rotation frame for the use in Grasp Calculation"""

    def __init__(self, path: str, center_of_mass: List):
        """The constructor recieves 1 parameter, the path to the file as a string.
        Attributes:
        com is the geometric center of the mesh
        triangles is the array of triangles that make the mesh."""

        self.__mesh = mesh.Mesh.from_file(path)

        self.triangles = self.__mesh.vectors
        self.com = center_of_mass
        edges_temp = []
        for triangle in self.triangles:
            edges_temp.append([triangle[0], triangle[1]])
            edges_temp.append([triangle[1], triangle[2]])
            edges_temp.append([triangle[2], triangle[0]])
        self.edges = np.array(edges_temp)
        self.vertices = self.triangles.flatten().reshape(self.triangles.shape[0] * 3, 3)

    def view(
        self,
        plot_name: str = "Mesh View",
        contacts: List[Contact] = None,
        forces: List[Dict] = None,
        view_not_return: bool = True,
    ) -> Union[Figure, None]:

        """View of the object, its center of mass and the world origin, and if passed all the contact points"""
        fig = figure(figsize=(10, 10))
        fig.canvas.mpl_connect("key_press_event", keypress)
        ax = fig.add_subplot(projection="3d")
        ax.set_facecolor("white")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        minx = round(float(min(self.vertices[:, 0])), 3)
        maxx = round(float(max(self.vertices[:, 0])), 3)
        miny = round(float(min(self.vertices[:, 1])), 3)
        maxy = round(float(max(self.vertices[:, 1])), 3)
        minz = round(float(min(self.vertices[:, 2])), 3)
        maxz = round(float(max(self.vertices[:, 2])), 3)
        title = f"{plot_name.upper()} \n X=({minx},{maxx}) Y=({miny},{maxy}) Z=({minz},{maxz}) \n COM: {self.com}"
        plt.title(
            label=title,
            fontsize=10,
            ha="center",
            color="k",
            fontname="monospace",
            wrap=True,
        )

        collection = art3d.Poly3DCollection(self.triangles, linewidths=0.4)
        collection.set_facecolor((1.0, 1.0, 1.0, 0.0))
        collection.set_edgecolor((0.0, 0.0, 0.0, 0.2))

        ax.add_collection3d(collection)

        ax.view_init(20, 15)

        scale = self.triangles.flatten()
        ax.auto_scale_xyz(scale, scale, scale)

        biggest = max(abs(scale))

        line_size = biggest * LINE_PERC

        ax.scatter(O[0], O[1], O[2], color="k")
        if (self.com != O).any() or forces is None:
            ax.text(O[0], O[1], O[2], "O", size=TEXT_SIZE, zorder=1, color="k")
        ax.plot(
            (O[0], line_size * X_W[0]),
            (O[0], line_size * X_W[1]),
            (O[0], line_size * X_W[2]),
            color="red",
        )
        ax.plot(
            (O[1], line_size * Y_W[0]),
            (O[1], line_size * Y_W[1]),
            (O[1], line_size * Y_W[2]),
            color="green",
        )
        ax.plot(
            (O[2], line_size * Z_W[0]),
            (O[2], line_size * Z_W[1]),
            (O[2], line_size * Z_W[2]),
            color="blue",
        )
        if forces is None:
            ax.scatter(self.com[0], self.com[1], self.com[2], color="orange")
            ax.text(
                self.com[0],
                self.com[1],
                self.com[2],
                "COM",
                size=TEXT_SIZE,
                zorder=1,
            )
        if contacts is not None:
            for idx, contact in enumerate(contacts, 0):
                color = "darkred"
                n = np.dot(contact.r, X_W)
                cx = contact.c[0]
                cy = contact.c[1]
                cz = contact.c[2]
                txt = contact.name
                ax.text(cx, cy, cz, txt, size=TEXT_SIZE, zorder=1)

                ax.scatter(
                    cx,
                    cy,
                    cz,
                    color=color,
                    label=idx,
                )
                ax.plot(
                    (cx, (cx + n[0] * line_size)),
                    (cy, (cy + n[1] * line_size)),
                    (cz, (cz + n[2] * line_size)),
                    color=color,
                )
        if forces is not None:
            vec_helper = {
                "X": np.array([1, 0, 0], dtype=float),
                "Y": np.array([0, 1, 0], dtype=float),
                "Z": np.array([0, 0, 1], dtype=float),
            }
            for force in forces:
                color = "darkorange"
                n = vec_helper[force["dir"]]

                cx = force["pos"][0]
                cy = force["pos"][1]
                cz = force["pos"][2]
                dir_help = 1 if force["mag"] > 0 else -1
                txt = round(abs(force["mag"]), 2)
                ax.text(
                    cx,
                    cy,
                    cz,
                    txt,
                    size=TEXT_SIZE,
                    zorder=1,
                )
                ax.scatter(
                    cx,
                    cy,
                    cz,
                    color=color,
                    label=txt,
                )
                ax.plot(
                    (cx, (cx + n[0] * dir_help * line_size)),
                    (cy, (cy + n[1] * dir_help * line_size)),
                    (cz, (cz + n[2] * dir_help * line_size)),
                    color=color,
                )
            # ax.legend()

        if not view_not_return:
            plt.close(fig="all")
            return fig
        else:
            print("Press [q] to continue or [esc] to cancel execution", end="\r")
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

            if np.linalg.norm(ci + ni - self.com) < np.linalg.norm(ci - self.com):
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

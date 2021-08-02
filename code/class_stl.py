import sys
from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot as plt
import numpy as np
import random
from data_types import Contact


class STL:
    """The STL class uses the numpy-stl library as the reader for the *.stl files, the class allows for the visualization of meshes, the generation of contact points and their rotation frame for the use in Grasp Calculation"""

    def __init__(self, path):
        """The constructor recieves 1 parameter, the path to the file as a string.
        Attributes:
        cog is the geometric center of the mesh
        triangles is the array of triangles that make the mesh."""

        self.__mesh = mesh.Mesh.from_file(path)

        # self.volume, self.cog, self.inertia = self.__mesh.get_mass_properties()

        self.triangles = self.__mesh.vectors
        points = self.triangles.flatten().reshape(self.triangles.shape[0] * 3, 3)
        self.cog = np.array(
            [
                sum(points[:, 0]) / points.shape[0],
                sum(points[:, 1]) / points.shape[0],
                sum(points[:, 2]) / points.shape[0],
            ]
        )
        edges_temp = []
        for triangle in self.triangles:
            edges_temp.append([triangle[0], triangle[1]])
            edges_temp.append([triangle[1], triangle[2]])
            edges_temp.append([triangle[2], triangle[0]])
        self.edges = np.array(edges_temp)
        self.vertices = self.triangles.flatten().reshape(self.triangles.shape[0] * 3, 3)

    def view(self, contacts=None):
        """Shows the mesh as a surface in a matplot plot"""
        xj = np.array([1, 0, 0])
        yj = np.array([0, 1, 0])
        zj = np.array([0, 0, 1])
        figure = plt.figure()
        if sys.version_info >= (3, 7):
            ax = mplot3d.Axes3D(figure, auto_add_to_figure=False)  # Python 3.8
            figure.add_axes(ax)  # Python 3.8
        else:
            ax = mplot3d.Axes3D(figure)  # Python 3.6

        collection = mplot3d.art3d.Poly3DCollection(
            self.triangles, linewidths=0.2, alpha=0.3
        )
        collection.set_facecolor([0.5, 0.5, 0.5])
        collection.set_edgecolor([0, 0, 0])
        ax.add_collection3d(collection)
        scale = self.triangles.flatten()
        ax.auto_scale_xyz(scale, scale, scale)
        biggest = max(scale) if max(scale) > abs(min(scale)) else abs(min(scale))
        ax.scatter(0, 0, 0, color="magenta")
        ax.plot((0, biggest * 0.1), (0, 0), (0, 0), color="red")
        ax.plot((0, 0), (0, biggest * 0.1), (0, 0), color="green")
        ax.plot((0, 0), (0, 0), (0, biggest * 0.1), color="blue")
        ax.scatter(self.cog[0], self.cog[1], self.cog[2], color="darkorange")
        ax.plot(
            (self.cog[0], self.cog[0] + biggest * 0.1),
            (self.cog[1], self.cog[1]),
            (self.cog[2], self.cog[2]),
            color="red",
        )
        ax.plot(
            (self.cog[0], self.cog[0]),
            (self.cog[1], self.cog[1] + biggest * 0.1),
            (self.cog[2], self.cog[2]),
            color="green",
        )
        ax.plot(
            (self.cog[0], self.cog[0]),
            (self.cog[1], self.cog[1]),
            (self.cog[2], self.cog[2] + biggest * 0.1),
            color="blue",
        )
        if contacts is not None:
            for contact in contacts:
                n = np.dot(contact.r, xj)
                t = np.dot(contact.r, yj)
                o = np.dot(contact.r, zj)

                cx = contact.c[0]
                cy = contact.c[1]
                cz = contact.c[2]

                ax.scatter(cx, cy, cz, color="red")
                ax.plot(
                    (cx, (cx + n[0] * biggest * 0.1)),
                    (cy, (cy + n[1] * biggest * 0.1)),
                    (cz, (cz + n[2] * biggest * 0.1)),
                    color="red",
                )

                ax.plot(
                    (cx, (cx + t[0] * biggest * 0.1)),
                    (cy, (cy + t[1] * biggest * 0.1)),
                    (cz, (cz + t[2] * biggest * 0.1)),
                    color="green",
                )
                ax.plot(
                    (cx, (cx + o[0] * biggest * 0.1)),
                    (cy, (cy + o[1] * biggest * 0.1)),
                    (cz, (cz + o[2] * biggest * 0.1)),
                    color="blue",
                )

        plt.show()

    def gen_C_randomly(self, nc, mu=0.3, iota=0, ng=8):
        """Generates a random (nc) number of contact points and their respective
        rotational frame, the result of the method are three pairs of contact points and rotation frames, the first pair are contact points generated at the barycenter of the triangles, the secong at the middle of the edges and the third are located at the vertices.
        The sum of the pairs of contact points are 3*nc, if gen is false the contact and rotation pairs for edges and vertices are a copy of the triangles ones.
        Returns Ct, Rt, Ce, Re, Cv, Rv"""
        xj = np.array([1, 0, 0])
        yj = np.array([0, 1, 0])
        zj = np.array([0, 0, 1])

        # Triangles

        Ct = []
        triangles = self.triangles[random.sample(range(self.triangles.shape[0]), k=nc)]
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

            if np.linalg.norm(ci + ni - self.cog) > np.linalg.norm(ci - self.cog):
                ni *= -1

            oi = np.cross(ni, ti)

            ri = np.array(
                [
                    [np.dot(ni, xj), np.dot(ti, xj), np.dot(oi, xj)],
                    [np.dot(ni, yj), np.dot(ti, yj), np.dot(oi, yj)],
                    [np.dot(ni, zj), np.dot(ti, zj), np.dot(oi, zj)],
                ]
            )
            Ct.append(Contact(ci, ri, mu, iota, ng))
        Ct = np.array(Ct)

        # Edges

        Ce = []
        same = True
        while same:
            same = False
            edges = self.edges[random.sample(range(self.edges.shape[0]), k=nc)]
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
                    [np.dot(nE, xj), np.dot(tE, xj), np.dot(oE, xj)],
                    [np.dot(nE, yj), np.dot(tE, yj), np.dot(oE, yj)],
                    [np.dot(nE, zj), np.dot(tE, zj), np.dot(oE, zj)],
                ]
            )

            Ce.append(Contact(ci, ri, mu, iota, ng))
        Ce = np.array(Ce)

        # Points

        Cv = []
        same = True
        while same:
            same = False
            vertices = self.vertices[random.sample(range(self.vertices.shape[0]), k=nc)]
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
                    [np.dot(nV, xj), np.dot(tV, xj), np.dot(oV, xj)],
                    [np.dot(nV, yj), np.dot(tV, yj), np.dot(oV, yj)],
                    [np.dot(nV, zj), np.dot(tV, zj), np.dot(oV, zj)],
                ]
            )

            Cv.append(Contact(vertex, ri, mu, iota, ng))

        Cv = np.array(Cv)

        return Ct, Ce, Cv

    def gen_C_from_coordinates(self, coord, location="T", mu=0.3, iota=0, ng=8):
        """Returns the contact coordinates and respective rotation frame of the
        nearest point of the passed coordinates, can specify the desired location of the generated point, if the center of a triangle, an edge or a vertex, for the last two it is necessary that the gen parameters was true on the constructor"""
        xj = np.array([1, 0, 0])
        yj = np.array([0, 1, 0])
        zj = np.array([0, 0, 1])

        assert (
            location == "T" or location == "E" or location == "V"
        ), "Location must be T for triangle, E for Edge of V for Vertex"
        assert isinstance(
            coord, np.ndarray
        ), "coordinate (coord) must be a numpy array of shape [3,]"
        assert (
            coord.shape[0] == 3
        ), "coordinate (coord) must be a numpy array of shape [3,]"

        dist = float("inf")

        if location == "E":
            coordEdge = self.edges[0]
            for edge in self.edges:
                cX = (sum(edge[:, 0])) / 2
                cY = (sum(edge[:, 1])) / 2
                cZ = (sum(edge[:, 2])) / 2
                cOfE = np.array([cX, cY, cZ])
                temp_dist = np.linalg.norm(cOfE - coord)
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
                    [np.dot(nE, xj), np.dot(tE, xj), np.dot(oE, xj)],
                    [np.dot(nE, yj), np.dot(tE, yj), np.dot(oE, yj)],
                    [np.dot(nE, zj), np.dot(tE, zj), np.dot(oE, zj)],
                ]
            )

            Cc = Contact(cOfE, rOfE, mu, iota, ng)
        elif location == "V":
            coordVertex = self.vertices[0]
            for vertex in self.vertices:
                temp_dist = np.linalg.norm(vertex - coord)
                if temp_dist < dist:
                    dist = temp_dist
                    coordVertex = vertex

            trianglesOfVertex = []
            for triangle in self.triangles:
                for point in triangle:
                    if (point == coordVertex).all():
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
                    [np.dot(nV, xj), np.dot(tV, xj), np.dot(oV, xj)],
                    [np.dot(nV, yj), np.dot(tV, yj), np.dot(oV, yj)],
                    [np.dot(nV, zj), np.dot(tV, zj), np.dot(oV, zj)],
                ]
            )
            Cc = Contact(coordVertex, rOfV, mu, iota, ng)
        else:
            coordTriangle = self.triangles[0]
            for triangle in self.triangles:
                cX = (sum(triangle[:, 0])) / 3
                cY = (sum(triangle[:, 1])) / 3
                cZ = (sum(triangle[:, 2])) / 3
                ci = np.array([cX, cY, cZ])

                temp_dist = np.linalg.norm(ci - coord)
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
                    [np.dot(ni, xj), np.dot(ti, xj), np.dot(oi, xj)],
                    [np.dot(ni, yj), np.dot(ti, yj), np.dot(oi, yj)],
                    [np.dot(ni, zj), np.dot(ti, zj), np.dot(oi, zj)],
                ]
            )
            Cc = Contact(ci, ri, mu, iota, ng)
        """
        print(
            "point {} was assigned {} in the {} of a triangle of the object mesh".format(
                coord,
                Cc,
                "center"
                if location == "T"
                else " vertex"
                if location == "V"
                else "edge",
            )
        )
        """
        Cc = np.array([Cc])
        return Cc

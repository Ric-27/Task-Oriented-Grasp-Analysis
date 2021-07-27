from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot as plt
import numpy as np

class StlView:
    def __init__(self,path):
        self.mesh = mesh.Mesh.from_file(path)
        self.volume, self.cog, self.inertia = self.mesh.get_mass_properties()
        self.points = self.mesh.points
        self.vectors = self.mesh.vectors
    
    def view(self):
        figure = plt.figure()
        axes = mplot3d.Axes3D(figure,auto_add_to_figure=False)
        figure.add_axes(axes)
        axes.add_collection3d(mplot3d.art3d.Poly3DCollection(self.vectors))
        scale = self.points.flatten()
        axes.auto_scale_xyz(scale, scale, scale)
        plt.show()
   
    def printMassProperties(self):
        print("Volume                                  = {0}".format(self.volume))
        print("Position of the center of gravity (COG) = {0}".format(self.cog))
        print("Inertia matrix at expressed at the COG  = {0}".format(self.inertia[0,:]))
        print("                                          {0}".format(self.inertia[1,:]))
        print("                                          {0}".format(self.inertia[2,:]))


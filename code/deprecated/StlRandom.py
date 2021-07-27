from StlView import StlView
from GraspMap import GraspMap
import numpy as np
import random
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d

random.seed()

class StlRandom(StlView):
    def __init__(self,path,nc):
        super().__init__(path)
        self.nc = nc
        self.triangles = self.vectors[random.sample(range(self.vectors.shape[0]),k=nc)]
    
    def getCR(self):
        xj = np.array([1,0,0])
        yj = np.array([0,1,0])
        zj = np.array([0,0,1])

        C = []
        R = []
        for triangle in self.triangles:
            cX = (sum(triangle[:,0]))/3
            cY = (sum(triangle[:,1]))/3
            cZ = (sum(triangle[:,2]))/3
            ci = np.array([cX,cY,cZ])

            vector1 = triangle[0] - ci
            vector2 = triangle[2] - ci
            normal = np.cross(vector1,vector2)

            ni = normal / np.linalg.norm(normal)
            ti = vector1 / np.linalg.norm(vector1)

            #if np.linalg.norm(ci + ni - self.cog) > np.linalg.norm(ci - self.cog):
            #    ni *= -1
            
            oi = np.cross(ni,ti)

            ri = np.array([[np.dot(ni,xj),np.dot(ti,xj),np.dot(oi,xj)],
                        [np.dot(ni,yj),np.dot(ti,yj),np.dot(oi,yj)],
                        [np.dot(ni,zj),np.dot(ti,zj),np.dot(oi,zj)]])

            R.append(ri)
            C.append(ci)

        C = np.array(C)
        R = np.array(R)
        return C,R

    def viewWire(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        xj = np.array([1,0,0])
        yj = np.array([0,1,0])
        zj = np.array([0,0,1])
        for triangle in self.triangles:
            cX = (sum(triangle[:,0]))/3
            cY = (sum(triangle[:,1]))/3
            cZ = (sum(triangle[:,2]))/3
            ci = np.array([cX,cY,cZ])

            vector1 = triangle[0] - ci
            vector2 = triangle[2] - ci
            normal = np.cross(vector1,vector2)

            ni = normal / np.linalg.norm(normal)
            ti = vector1 / np.linalg.norm(vector1)            
            oi = np.cross(ni,ti)
            
            ax.scatter(cX,cY,cZ,color='black')
            ax.plot((cX,cX+ni[0]),(cY,cY+ni[1]),(cZ,cZ+ni[2]),color='red')
            ax.plot((cX,cX+ti[0]),(cY,cY+ti[1]),(cZ,cZ+ti[2]),color='green')
            ax.plot((cX,cX+oi[0]),(cY,cY+oi[1]),(cZ,cZ+oi[2]),color='blue')

        pts = self.vectors[0]
        for triangle in self.vectors:
            for point in triangle:
                inArray = False
                for pt in pts:
                    if point[0] == pt[0] and point[1] == pt[1] and point[2] == pt[2]:
                        inArray = True
                        break
                if not inArray: 
                    pts = np.concatenate((pts,[point]),axis=0)
                
        for point in pts:
            ax.scatter(point[0],point[1],point[2],color='purple') # plot the point (2,3,4) on the figure

        scale = self.points.flatten()
        ax.auto_scale_xyz(scale, scale, scale)

        ax.scatter(0,0,0,color='black')
        ax.plot((0,1),(0,0),(0,0),color='red')
        ax.plot((0,0),(0,1),(0,0),color='green')
        ax.plot((0,0),(0,0),(0,1),color='blue')

        for points in self.points:
            ax.plot((points[0],points[3]),(points[1],points[4]),(points[2],points[5]),'gray',linewidth=1,)
            ax.plot((points[0],points[6]),(points[1],points[7]),(points[2],points[8]),'gray',linewidth=1,)
            ax.plot((points[3],points[6]),(points[4],points[7]),(points[5],points[8]),'gray',linewidth=1,)
    
        plt.show()

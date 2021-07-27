import numpy as np
import math
from GraspMap import GraspMap
from StlClass import STL
from scipy.optimize import linprog
from mpl_toolkits import mplot3d
from matplotlib import pyplot as plt
from scipy.linalg import block_diag, null_space

np.set_printoptions(suppress=True)

nc = 7
ng = 8
mu = 0.3

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


S = []
for k in range(ng):
    sk = np.array([1,mu*math.cos(2*k*math.pi/ng),mu*math.sin(2*k*math.pi/ng)])
    if k == 0:
        ax.plot((0,sk[0]),(0,sk[1]),(0,sk[2]),color='gray')
    elif k == 1:
        ax.plot((0,sk[0]),(0,sk[1]),(0,sk[2]),color='gray')
    else:
        ax.plot((0,sk[0]),(0,sk[1]),(0,sk[2]),color='black')
    S.append(sk)

S = np.array(S).transpose()
#print(S)
F = []

for k in range(ng):
    if k != ng-1:
        kk = k+1
    else:
        kk = 0
    #print("k:{},k+1:{}".format(k,kk))
    Fk = np.cross(S[:,k],S[:,kk])
    if k == 0 and kk == 1:
        ax.plot((0,Fk[0]),(0,Fk[1]),(0,Fk[2]),color='red')
    F.append(Fk)

plt.show()

F = np.array(F)
F = block_diag(*([F]*nc))
#print(F)

#print("for ng: {}, F.shape is: {}".format(ng,F.shape))

#exit()

mesh = STL('../stl/cube_low.stl')
C,R,Ce,Re,Cv,Rv = mesh.genRandCR(nc)
C1,R1 = mesh.getCRofCoord(np.array([5,0,0]),'E')
C2,R2 = mesh.getCRofCoord(np.array([0,5,0]),'E')
C3,R3 = mesh.getCRofCoord(np.array([0,0,5]),'E')
C4,R4 = mesh.getCRofCoord(np.array([-5,0,0]),'E')
C5,R5 = mesh.getCRofCoord(np.array([0,-5,0]),'E')
C6,R6 = mesh.getCRofCoord(np.array([0,0,-5]),'E')
#C7,R7 = mesh.getCRofCoord(np.array([5,5,5]),'V')
#C = np.concatenate((C1,C2,C3,C4,C5,C6))
#R = np.concatenate((R1,R2,R3,R4,R5,R6))
#mesh.viewCR(C,R)
grasp = GraspMap(mesh.cog,C,R)
print("Rank G:",grasp.getRank())
G =  grasp.getGt().transpose()
grasp.printGraspClassification()
e = []
for i in range(nc):
    e.append([1,0,0])
e = np.array(e).flatten()
#print("F.shape",F.shape)
#print("G.shape",G.shape)
#print("e.shape",e.shape)
#print("-"*25)
#SCIPY
L = 3*nc
obj = np.concatenate((-1*np.ones((1,1)),np.zeros((1,L))),axis=1).flatten()

lhs_ineq = np.block([   [np.ones((F.shape[0],1)),   -F],
                        [-1*np.ones(1),             np.zeros((1,L))],
                        [np.zeros(1),               e]])

#print(lhs_ineq)

rhs_ineq = np.concatenate((np.zeros((1,F.shape[0] + 1)),10*nc*np.ones((1,1))),axis=1).flatten()

lhs_eq = np.concatenate((np.zeros((6,1)),G),axis=1)

rhs_eq = np.zeros((6,1)).flatten()      # Green constraint right side

bnd = [(None, None)]

#print("lhs_ineq.shape",lhs_ineq.shape)
#print("rhs_ineq.shape",rhs_ineq.shape)
#print("lhs_eq.shape",lhs_eq.shape)
#print("rhs_eq.shape",rhs_eq.shape)
#print("obj.shape",obj.shape)

opt = linprog(c=obj, A_ub=lhs_ineq, b_ub=rhs_ineq, A_eq=lhs_eq, b_eq=rhs_eq, bounds=bnd, method='revised simplex')
#print(opt)
print("Success: ",opt.success)
print("d: ",abs(opt.fun))
for i,var in enumerate(opt.x,0):
    if i == 0:
        pass
    else:
        print("lambda_{}: {}".format(i-1, var))


#print(G.shape)
#print(F.shape)
#print(e.shape)
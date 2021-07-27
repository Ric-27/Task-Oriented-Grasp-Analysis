import numpy as np
import math
from GraspMap import GraspMap
from StlClass import STL
from scipy.linalg import block_diag

np.set_printoptions(suppress=True)

nc = 3
ng = 4
mu = 0.3
S = []
for k in range(ng):
    sk = np.array([1,mu*math.cos(2*k*math.pi/ng),mu*math.sin(2*k*math.pi/ng)])
    S.append(sk)

S = np.array(S).transpose()
F = []
for k in range(ng):
    if k != ng-1:
        kk = k+1
    else:
        kk = 0
    Fk = np.cross(S[:,k],S[:,kk])
    F.append(Fk)

F = np.array(F)
F = block_diag(*([F]*nc))

#print("for ng: {}, F.shape is: {}".format(ng,F.shape))

#exit()

mesh = STL('../stl/cube_low.stl')
#Ct,Rt,Ce,Re,Cv,Rv = mesh.genRandCR(nc)
C1,R1 = mesh.getCRofCoord(np.array([5,0,0]),'E')
C2,R2 = mesh.getCRofCoord(np.array([0,5,0]),'E')
C3,R3 = mesh.getCRofCoord(np.array([0,0,5]),'E')
C = np.concatenate((C1,C2,C3))
R = np.concatenate((R1,R2,R3))
mesh.viewCR(C,R)
grasp = GraspMap(mesh.cog,C,R)
G =  grasp.getGt().transpose()
e = np.array([1,0,0,1,0,0,1,0,0])

#PULP
from pulp import LpMaximize, LpProblem, LpVariable, LpStatus

model = LpProblem(name="friction_form_closure", sense=LpMaximize)

# Initialize the decision variables
d = LpVariable(name="d")
lm = LpVariable(name="lambda")
#lm1 = LpVariable(name="lambda[1]")
#lm2 = LpVariable(name="lambda[2]")
#lm3 = LpVariable(name="lambda[3]")
#lm4 = LpVariable(name="lambda[4]")
#lm5 = LpVariable(name="lambda[5]")
#lm6 = LpVariable(name="lambda[6]")
#lm7 = LpVariable(name="lambda[7]")
#lm8 = LpVariable(name="lambda[8]")

# Add the constraints to the model
#constraint = G * force == 0
#print(type(constraint))
model += ( G[0]*lm == 0 , "C_1_0")
model += ( G[1]*lm == 0 , "C_1_1")
model += ( G[2]*lm == 0 , "C_1_2")
model += ( G[3]*lm == 0 , "C_1_3")
model += ( G[4]*lm == 0 , "C_1_4")
model += ( G[5]*lm == 0 , "C_1_5")

model += ( F[0]*lm - d >= 0 , "C_2_0")
model += ( F[1]*lm - d >= 0 , "C_2_1")
model += ( F[2]*lm - d >= 0 , "C_2_2")
model += ( F[3]*lm - d >= 0 , "C_2_3")
model += ( F[4]*lm - d >= 0 , "C_2_4")
model += ( F[5]*lm - d >= 0 , "C_2_5")
model += ( F[6]*lm - d >= 0 , "C_2_6")
model += ( F[7]*lm - d >= 0 , "C_2_7")
model += ( F[8]*lm - d >= 0 , "C_2_8")
model += ( F[9]*lm - d >= 0 , "C_2_9")
model += ( F[10]*lm - d >= 0 , "C_2_10")
model += ( F[11]*lm - d >= 0 , "C_2_11")

model += ( d >= 0 , "C_3")
model += ( e*lm <= 10*nc , "C_4")

# Add the objective function to the model
model += d

#print(model)
status = model.solve()
print("-"*25)
print(f"status: {model.status}, {LpStatus[model.status]}")

#print(f"objective: {model.objective.value()}")

for var in model.variables():
    print(f"{var.name}: {var.value()}")

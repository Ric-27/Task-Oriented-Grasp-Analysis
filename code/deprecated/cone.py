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
C,R,Ce,Re,Cv,Rv = mesh.genRandCR(nc)
C1,R1 = mesh.getCRofCoord(np.array([5,0,0]),'E')
C2,R2 = mesh.getCRofCoord(np.array([0,5,0]),'E')
C3,R3 = mesh.getCRofCoord(np.array([0,0,5]),'E')
C = np.concatenate((C1,C2,C3))
R = np.concatenate((R1,R2,R3))
#mesh.viewCR(C,R)
grasp = GraspMap(mesh.cog,C,R)
G =  grasp.getGt().transpose()
e = np.array([1,0,0,1,0,0,1,0,0])

#PULP
from pulp import LpMaximize, LpProblem, LpVariable, LpConstraint, LpStatus

model = LpProblem(name="friction_form_closure", sense=LpMaximize)

# Initialize the decision variables
d = LpVariable(name="d")
lm0 = LpVariable(name="lambda[0]")
lm1 = LpVariable(name="lambda[1]")
lm2 = LpVariable(name="lambda[2]")
lm3 = LpVariable(name="lambda[3]")
lm4 = LpVariable(name="lambda[4]")
lm5 = LpVariable(name="lambda[5]")
lm6 = LpVariable(name="lambda[6]")
lm7 = LpVariable(name="lambda[7]")
lm8 = LpVariable(name="lambda[8]")

# Add the constraints to the model
#constraint = G * force == 0
#print(type(constraint))
model += ( G[0,0]*lm0 + G[0,1]*lm1 + G[0,2]*lm2 + G[0,3]*lm3 + G[0,4]*lm4 + G[0,5]*lm5 + G[0,6]*lm6 + G[0,7]*lm7 + G[0,8]*lm8 == 0 , "C_1_0")
model += ( G[1,0]*lm0 + G[1,1]*lm1 + G[1,2]*lm2 + G[1,3]*lm3 + G[1,4]*lm4 + G[1,5]*lm5 + G[1,6]*lm6 + G[1,7]*lm7 + G[1,8]*lm8 == 0 , "C_1_1")
model += ( G[2,0]*lm0 + G[2,1]*lm1 + G[2,2]*lm2 + G[2,3]*lm3 + G[2,4]*lm4 + G[2,5]*lm5 + G[2,6]*lm6 + G[2,7]*lm7 + G[2,8]*lm8 == 0 , "C_1_2")
model += ( G[3,0]*lm0 + G[3,1]*lm1 + G[3,2]*lm2 + G[3,3]*lm3 + G[3,4]*lm4 + G[3,5]*lm5 + G[3,6]*lm6 + G[3,7]*lm7 + G[3,8]*lm8 == 0 , "C_1_3")
model += ( G[4,0]*lm0 + G[4,1]*lm1 + G[4,2]*lm2 + G[4,3]*lm3 + G[4,4]*lm4 + G[4,5]*lm5 + G[4,6]*lm6 + G[4,7]*lm7 + G[4,8]*lm8 == 0 , "C_1_4")
model += ( G[5,0]*lm0 + G[5,1]*lm1 + G[5,2]*lm2 + G[5,3]*lm3 + G[5,4]*lm4 + G[5,5]*lm5 + G[5,6]*lm6 + G[5,7]*lm7 + G[5,8]*lm8 == 0 , "C_1_5")

model += ( F[0,0]*lm0 + F[0,1]*lm1 + F[0,2]*lm2 + F[0,3]*lm3 + F[0,4]*lm4 + F[0,5]*lm5 + F[0,6]*lm6 + F[0,7]*lm7 + F[0,8]*lm8 - d >= 0 , "C_2_0")
model += ( F[1,0]*lm0 + F[1,1]*lm1 + F[1,2]*lm2 + F[1,3]*lm3 + F[1,4]*lm4 + F[1,5]*lm5 + F[1,6]*lm6 + F[1,7]*lm7 + F[1,8]*lm8 - d >= 0 , "C_2_1")
model += ( F[2,0]*lm0 + F[2,1]*lm1 + F[2,2]*lm2 + F[2,3]*lm3 + F[2,4]*lm4 + F[2,5]*lm5 + F[2,6]*lm6 + F[2,7]*lm7 + F[2,8]*lm8 - d >= 0 , "C_2_2")
model += ( F[3,0]*lm0 + F[3,1]*lm1 + F[3,2]*lm2 + F[3,3]*lm3 + F[3,4]*lm4 + F[3,5]*lm5 + F[3,6]*lm6 + F[3,7]*lm7 + F[3,8]*lm8 - d >= 0 , "C_2_3")
model += ( F[4,0]*lm0 + F[4,1]*lm1 + F[4,2]*lm2 + F[4,3]*lm3 + F[4,4]*lm4 + F[4,5]*lm5 + F[4,6]*lm6 + F[4,7]*lm7 + F[4,8]*lm8 - d >= 0 , "C_2_4")
model += ( F[5,0]*lm0 + F[5,1]*lm1 + F[5,2]*lm2 + F[5,3]*lm3 + F[5,4]*lm4 + F[5,5]*lm5 + F[5,6]*lm6 + F[5,7]*lm7 + F[5,8]*lm8 - d >= 0 , "C_2_5")
model += ( F[6,0]*lm0 + F[6,1]*lm1 + F[6,2]*lm2 + F[6,3]*lm3 + F[6,4]*lm4 + F[6,5]*lm5 + F[6,6]*lm6 + F[6,7]*lm7 + F[6,8]*lm8 - d >= 0 , "C_2_6")
model += ( F[7,0]*lm0 + F[7,1]*lm1 + F[7,2]*lm2 + F[7,3]*lm3 + F[7,4]*lm4 + F[7,5]*lm5 + F[7,6]*lm6 + F[7,7]*lm7 + F[7,8]*lm8 - d >= 0 , "C_2_7")
model += ( F[8,0]*lm0 + F[8,1]*lm1 + F[8,2]*lm2 + F[8,3]*lm3 + F[8,4]*lm4 + F[8,5]*lm5 + F[8,6]*lm6 + F[8,7]*lm7 + F[8,8]*lm8 - d >= 0 , "C_2_8")
model += ( F[9,0]*lm0 + F[9,1]*lm1 + F[9,2]*lm2 + F[9,3]*lm3 + F[9,4]*lm4 + F[9,5]*lm5 + F[9,6]*lm6 + F[9,7]*lm7 + F[9,8]*lm8 - d >= 0 , "C_2_9")
model += ( F[10,0]*lm0 + F[10,1]*lm1 + F[10,2]*lm2 + F[10,3]*lm3 + F[10,4]*lm4 + F[10,5]*lm5 + F[10,6]*lm6 + F[10,7]*lm7 + F[10,8]*lm8 - d >= 0 , "C_2_10")
model += ( F[11,0]*lm0 + F[11,1]*lm1 + F[11,2]*lm2 + F[11,3]*lm3 + F[11,4]*lm4 + F[11,5]*lm5 + F[11,6]*lm6 + F[11,7]*lm7 + F[11,8]*lm8 - d >= 0 , "C_2_11")

model += ( d >= 0 , "C_3")
model += ( e[0]*lm0 + e[1]*lm1 + e[2]*lm2 + e[3]*lm3 + e[4]*lm4 + e[5]*lm5 + e[6]*lm6 + e[7]*lm7 + e[8]*lm8 <= 10*nc , "C_4")

# Add the objective function to the model
model += d

#print(model)
status = model.solve()
print("-"*25)
print(f"status: {model.status}, {LpStatus[model.status]}")

print(f"objective: {model.objective.value()}")

for var in model.variables():
    print(f"{var.name}: {var.value()}")


print("F.shape",F.shape)
print("G.shape",G.shape)
print("e.shape",e.shape)
print("-"*25)
#SCIPY
from scipy.optimize import linprog
obj = np.array([-1,0,0,0,0,0,0,0,0,0]) #d, lambda

lhs_ineq = np.array([[1,-F[0,0],-F[0,1],-F[0,2],-F[0,3],-F[0,4],-F[0,5],-F[0,6],-F[0,7],-F[0,8]],
            [1,-F[1,0],-F[1,1],-F[1,2],-F[1,3],-F[1,4],-F[1,5],-F[1,6],-F[1,7],-F[1,8]],
            [1,-F[2,0],-F[2,1],-F[2,2],-F[2,3],-F[2,4],-F[2,5],-F[2,6],-F[2,7],-F[2,8]],
            [1,-F[3,0],-F[3,1],-F[3,2],-F[3,3],-F[3,4],-F[3,5],-F[3,6],-F[3,7],-F[3,8]],
            [1,-F[4,0],-F[4,1],-F[4,2],-F[4,3],-F[4,4],-F[4,5],-F[4,6],-F[4,7],-F[4,8]],
            [1,-F[5,0],-F[5,1],-F[5,2],-F[5,3],-F[5,4],-F[5,5],-F[5,6],-F[5,7],-F[5,8]],
            [1,-F[6,0],-F[6,1],-F[6,2],-F[6,3],-F[6,4],-F[6,5],-F[6,6],-F[6,7],-F[6,8]],
            [1,-F[7,0],-F[7,1],-F[7,2],-F[7,3],-F[7,4],-F[7,5],-F[7,6],-F[7,7],-F[7,8]],
            [1,-F[8,0],-F[8,1],-F[8,2],-F[8,3],-F[8,4],-F[8,5],-F[8,6],-F[8,7],-F[8,8]],
            [1,-F[9,0],-F[9,1],-F[9,2],-F[9,3],-F[9,4],-F[9,5],-F[9,6],-F[9,7],-F[9,8]],
            [1,-F[10,0],-F[10,1],-F[10,2],-F[10,3],-F[10,4],-F[10,5],-F[10,6],-F[10,7],-F[10,8]],
            [1,-F[11,0],-F[11,1],-F[11,2],-F[11,3],-F[11,4],-F[11,5],-F[11,6],-F[11,7],-F[11,8]],
            [-1,0,0,0,0,0,0,0,0,0],
            [0,e[0],e[1],e[2],e[3],e[4],e[5],e[6],e[7],e[8]]])

rhs_ineq = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,10*nc])

lhs_eq = np.array([[0, G[0,0],G[0,1],G[0,2],G[0,3],G[0,4],G[0,5],G[0,6],G[0,7],G[0,8]],
            [0, G[1,0],G[1,1],G[1,2],G[1,3],G[1,4],G[1,5],G[1,6],G[1,7],G[1,8]],
            [0, G[2,0],G[2,1],G[2,2],G[2,3],G[2,4],G[2,5],G[2,6],G[2,7],G[2,8]],
            [0, G[3,0],G[3,1],G[3,2],G[3,3],G[3,4],G[3,5],G[3,6],G[3,7],G[3,8]],
            [0, G[4,0],G[4,1],G[4,2],G[4,3],G[4,4],G[4,5],G[4,6],G[4,7],G[4,8]],
            [0, G[5,0],G[5,1],G[5,2],G[5,3],G[5,4],G[5,5],G[5,6],G[5,7],G[5,8]]]) # Green constraint left side
rhs_eq = np.array([0,0,0,0,0,0])      # Green constraint right side

print("lhs_ineq.shape",lhs_ineq.shape)
print("rhs_ineq.shape",rhs_ineq.shape)
print("lhs_eq.shape",lhs_eq.shape)
print("rhs_eq.shape",rhs_eq.shape)
print("obj.shape",obj.shape)

opt = linprog(c=obj, A_ub=lhs_ineq, b_ub=rhs_ineq,
               A_eq=lhs_eq, b_eq=rhs_eq,
               method="revised simplex")
print("Success: ",opt.success)
for i,var in enumerate(opt.x,0):
    if i == 0:
        print("d: ", var)
    else:
        print("lambda_{}: {}".format(i-1, var))


#print(grasp.getRank())
#print(G.shape)
#print(F.shape)
#print(e.shape)

##CVXOPT
from cvxopt.modeling import op, variable, dot

d = variable()
lm0 = variable()
lm1 = variable()
lm2 = variable()
lm3 = variable()
lm4 = variable()
lm5 = variable()
lm6 = variable()
lm7 = variable()
lm8 = variable()

c10 = ( G[0,0]*lm0 + G[0,1]*lm1 + G[0,2]*lm2 + G[0,3]*lm3 + G[0,4]*lm4 + G[0,5]*lm5 + G[0,6]*lm6 + G[0,7]*lm7 + G[0,8]*lm8 == 0 )
c11 = ( G[1,0]*lm0 + G[1,1]*lm1 + G[1,2]*lm2 + G[1,3]*lm3 + G[1,4]*lm4 + G[1,5]*lm5 + G[1,6]*lm6 + G[1,7]*lm7 + G[1,8]*lm8 == 0 )
c12 = ( G[2,0]*lm0 + G[2,1]*lm1 + G[2,2]*lm2 + G[2,3]*lm3 + G[2,4]*lm4 + G[2,5]*lm5 + G[2,6]*lm6 + G[2,7]*lm7 + G[2,8]*lm8 == 0 )
c13 = ( G[3,0]*lm0 + G[3,1]*lm1 + G[3,2]*lm2 + G[3,3]*lm3 + G[3,4]*lm4 + G[3,5]*lm5 + G[3,6]*lm6 + G[3,7]*lm7 + G[3,8]*lm8 == 0 )
c14 = ( G[4,0]*lm0 + G[4,1]*lm1 + G[4,2]*lm2 + G[4,3]*lm3 + G[4,4]*lm4 + G[4,5]*lm5 + G[4,6]*lm6 + G[4,7]*lm7 + G[0,8]*lm8 == 0 )
c15 = ( G[5,0]*lm0 + G[5,1]*lm1 + G[5,2]*lm2 + G[5,3]*lm3 + G[5,4]*lm4 + G[5,5]*lm5 + G[5,6]*lm6 + G[5,7]*lm7 + G[5,8]*lm8 == 0 )

c20 = ( F[0,0]*lm0 + F[0,1]*lm1 + F[0,2]*lm2 + F[0,3]*lm3 + F[0,4]*lm4 + F[0,5]*lm5 + F[0,6]*lm6 + F[0,7]*lm7 + F[0,8]*lm8 - d >= 0 )
c21 = ( F[1,0]*lm0 + F[1,1]*lm1 + F[1,2]*lm2 + F[1,3]*lm3 + F[1,4]*lm4 + F[1,5]*lm5 + F[1,6]*lm6 + F[1,7]*lm7 + F[1,8]*lm8 - d >= 0 )
c22 = ( F[2,0]*lm0 + F[2,1]*lm1 + F[2,2]*lm2 + F[2,3]*lm3 + F[2,4]*lm4 + F[2,5]*lm5 + F[2,6]*lm6 + F[2,7]*lm7 + F[2,8]*lm8 - d >= 0 )
c23 = ( F[3,0]*lm0 + F[3,1]*lm1 + F[3,2]*lm2 + F[3,3]*lm3 + F[3,4]*lm4 + F[3,5]*lm5 + F[3,6]*lm6 + F[3,7]*lm7 + F[3,8]*lm8 - d >= 0 )
c24 = ( F[4,0]*lm0 + F[4,1]*lm1 + F[4,2]*lm2 + F[4,3]*lm3 + F[4,4]*lm4 + F[4,5]*lm5 + F[4,6]*lm6 + F[4,7]*lm7 + F[4,8]*lm8 - d >= 0 )
c25 = ( F[5,0]*lm0 + F[5,1]*lm1 + F[5,2]*lm2 + F[5,3]*lm3 + F[5,4]*lm4 + F[5,5]*lm5 + F[5,6]*lm6 + F[5,7]*lm7 + F[5,8]*lm8 - d >= 0 )
c26 = ( F[6,0]*lm0 + F[6,1]*lm1 + F[6,2]*lm2 + F[6,3]*lm3 + F[6,4]*lm4 + F[6,5]*lm5 + F[6,6]*lm6 + F[6,7]*lm7 + F[6,8]*lm8 - d >= 0 )
c27 = ( F[7,0]*lm0 + F[7,1]*lm1 + F[7,2]*lm2 + F[7,3]*lm3 + F[7,4]*lm4 + F[7,5]*lm5 + F[7,6]*lm6 + F[7,7]*lm7 + F[7,8]*lm8 - d >= 0 )
c28 = ( F[8,0]*lm0 + F[8,1]*lm1 + F[8,2]*lm2 + F[8,3]*lm3 + F[8,4]*lm4 + F[8,5]*lm5 + F[8,6]*lm6 + F[8,7]*lm7 + F[8,8]*lm8 - d >= 0 )
c29 = ( F[9,0]*lm0 + F[9,1]*lm1 + F[9,2]*lm2 + F[9,3]*lm3 + F[9,4]*lm4 + F[9,5]*lm5 + F[9,6]*lm6 + F[9,7]*lm7 + F[9,8]*lm8 - d >= 0 )
c210 = ( F[10,0]*lm0 + F[10,1]*lm1 + F[10,2]*lm2 + F[10,3]*lm3 + F[10,4]*lm4 + F[10,5]*lm5 + F[10,6]*lm6 + F[10,7]*lm7 + F[10,8]*lm8 - d >= 0 )
c211 = ( F[11,0]*lm0 + F[11,1]*lm1 + F[11,2]*lm2 + F[11,3]*lm3 + F[11,4]*lm4 + F[11,5]*lm5 + F[11,6]*lm6 + F[11,7]*lm7 + F[11,8]*lm8 - d >= 0 )

c3 = ( d >= 0 )

c4 = ( e[0]*lm0 + e[1]*lm1 + e[2]*lm2 + e[3]*lm3 + e[4]*lm4 + e[5]*lm5 + e[6]*lm6 + e[7]*lm7 + e[8]*lm8 <= nc )


#lp1 = op(d, [c10,c11,c12,c13,c14,c15,c20,c21,c22,c23,c24,c25,c26,c27,c28,c29,c210,c211,c3,c4])
#lp1.solve()
#lp1.status
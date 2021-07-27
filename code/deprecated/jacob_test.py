from Jacobian import Jacobian, Joint, Finger
from GraspMap import GraspMap
from StlRandom import StlRandom
import numpy as np

np.set_printoptions(suppress=True)

path = "./stl/cube_low.stl"
mesh = StlRandom(path,3)
C,R = mesh.getCR()
p = mesh.cog
h = np.array(['H','H','S'])
grasp = GraspMap(p,C,R,h)

q1 = Joint(1,np.array([10,10,5]),np.array([0,0,1]),0,True)
q2 = Joint(2,np.array([10,20,3]),np.array([0,0,1]),2,True)
q3 = Joint(3,np.array([1,4,5]),np.array([0,0,1]),1,True)
q4 = Joint(4,np.array([3,3,2]),np.array([0,0,1]),1,True)
q5 = Joint(5,np.array([1,0,5]),np.array([0,0,1]),1,True)

#joints = np.array([q1,q2,q3,q4,q5])
finger1 = Finger(1,[q1,q2])
finger2 = Finger(2,[q3,q4,q5])
fingers = np.array([finger1,finger2])
Jacob = Jacobian(fingers,C,R,h)

#print("Gt: \n",grasp.getGt())
print(grasp.GraspClassification(True))
print("Rank G:",grasp.getRank())

J = Jacob.getJ()
#print(J.shape)
#print("J: \n",J)
Jacob.printJacobianClassification()
print("Rank J:",Jacob.getRank())

#print(q1)
Jacob.printHandSpecifications()

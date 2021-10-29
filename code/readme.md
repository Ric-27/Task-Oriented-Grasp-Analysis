# TASK-ORIENTED GRASP ANALYSIS

## _Analysis tool for the Tracebot project and multi-fingered robots_

This code allows for the grasp analysis of a task-oriented project by providing the force requirements of a multi-fingered manipulator at the object surface.

## Features

- Preview a .stl file on python and extract its information to be saved as attributes
- Transform object surface coordinates into fully constructed Contact Points
- From Contact Points obtain the grasp matrix and its classification
- From Contact Points and a manipulator architecture obtain the grasp jacobian matrix and its classification
- Test for the Friction Form Closure, Force Closure of the grasping system
- Obtain the maximum force alpha the grasping system resist in a given direction

## Requirements

This project uses Python **3.8**

install using

```bash
pip install -r ./code/requirements.txt
```

## **Usage**

### _Down below under the usage for the Quality Metrics, specifically getting Alpha, the code is a complete example on how to unite the different classes and functions_

## STL Class

```python
from class_stl import STL
import numpy as np

#declare a mesh object of type STL
mesh = STL("file path to the .stl file")

#preview mesh
mesh.view()

#create nc random points for triangles in the mesh, edges of the mesh and points of the mesh (resp) for a total of 3 x nc
Ct, Rt, Ce, Re, Cv, Rv = mesh.gen_C_randomly(nc)

 #from the point (5,0,0) create a contact point in the nearest edge ("E")
C1, R1 = mesh.gen_C_from_coordinates(np.array([5, 0, 0]), "E")

#correct way of joining different contact points
C = np.concatenate((Ct, Ce, Cv, C1), axis=0)
R = np.concatenate((Rt, Re, Rv, R1), axis=0)

#preview mesh with contact points
mesh.view_with_C(C, R) #deprecated, now view() accepts contact points as parameters

#access mesh attributes like geometric center (also available: triangles, edges and vertices)
center = mesh.cog
```

---

## Grasp Class

```python
from class_grasp import Grasp
import numpy as np

#declaration of the point inside the object, where the  object's frame is located
p = np.array([2, 10, 0])

#creation of contact points with their rotation frame
c1 = np.array([6, 10, 0])
R1 = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])

c2 = np.array([-3, 10, 0])
R2 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

#correct way of joining different contact points
C = np.array([c1, c2])
R = np.array([R1, R2])

#contact model declaration (both contacts are Hard Finger)
h = np.array(["H", "H"])

#grasp object creation
grasp = Grasp(p, C, R, h) #deprecated, C, R and h are combined into a new data structure called Contact

#calculating the Transposed Grasp Matrix of the grasp system
Gt = grasp.get_grasp_matrix_t()

#getting the grasp classification (in console because of the True argument passed)
grasp.get_grasp_classification(True)
```

---

## Jacobian Class

```python
from class_jacobian import Jacobian
from data_types import Finger, Joint
import numpy as np

#creation of contact points with their rotation frame
c1 = np.array([6, 10, 0])
R1 = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])

c2 = np.array([-3, 10, 0])
R2 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

#contact model declaration (both contacts are Hard Finger)
h = np.array(["H", "H"])

#manipulator declaration

zv = np.array([0, 0, 1]).reshape(3, 1) #unit vector of the joints

#joints locations
q1c = np.array([9, 0, 0])
q2c = np.array([8, 6, 0])
q3c = np.array([-8, 0, 0])
q4c = np.array([-8, 3, 0])
q5c = np.array([-6, 7, 0])


#joints declaration:unique id, center, unit vector direction, affected contact index

#joint with id 1, has center q1c, its z is pointing in zv and doesnt affect any contact point.
q1 = Joint(1, q1c, zv, -1)

#joint with id 2, has center q2c, its z is pointing in zv and is contacting the object at the contact point with index 0.
q2 = Joint(2, q2c, zv, 0)

q3 = Joint(3, q3c, zv, -1)
q4 = Joint(4, q4c, zv, -1)
q5 = Joint(5, q5c, zv, 1)

#joints into fingers
f1 = Finger(1, np.array([q1, q2]))
f2 = Finger(2, np.array([q3, q4, q5]))

#correct way of joining different fingers
f = np.array([f1, f2])

#declaration of a Jacobian Object
jacobian = Jacobian(f, C, R, h)

#calculating the grasp jacobian
J = jacobian.get_jacobian_matrix()

#geting the jacobian classification as variables
de, re = jacobian.get_jacobian_classification(False)

#printing the hand architecture (useful to check if the passed architecture is the same as the one intended or for randomly generated manipulators)
jacobian.get_hand_architecture()
```

---

## Quality Metrics

### Calculating Alpha

```python
import numpy as np
from class_stl import STL
from class_grasp import Grasp
from quality_metrics import task_oriented

mesh = STL("../stl/needle.stl") #declare a mesh object

c,r,un,un,un,un == mesh.gen_c_random(5) #create 5 random contact points and save only the ones located at triangles of the mesh

grasp = Grasp(mesh.cog, c, r) #declare a grasp system

al, forces = task_oriented(grasp, np.array([1, 0, 0, 0, 0, 0]), 10, 8, 0.3) #test the grasp system in the positive X direction, with a manipulator maximum force of 10N, 8 faces for the friction cones and a coefficient of friction of 0.3
print(al)
```

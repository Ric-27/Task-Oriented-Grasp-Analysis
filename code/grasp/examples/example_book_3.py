from grasp import *

zv = np.array([0, 0, 1]).reshape(3, 1)

p = np.array([0, 0, 0])

l = 2

c1 = np.array([math.cos(math.pi), math.sin(math.pi), 0]) * l

c2 = np.array([math.cos(math.pi / 2), math.sin(math.pi / 2), 0]) * l

c3 = np.array([math.cos(0), math.sin(0), 0]) * l

R1 = np.array(
    [
        [-math.cos(math.pi), math.sin(math.pi), 0],
        [-math.sin(math.pi), -math.cos(math.pi), 0],
        [0, 0, 1],
    ]
)

R2 = np.array(
    [
        [-math.cos(math.pi / 2), math.sin(math.pi / 2), 0],
        [-math.sin(math.pi / 2), -math.cos(math.pi / 2), 0],
        [0, 0, 1],
    ]
)

R3 = np.array(
    [[-math.cos(0), math.sin(0), 0], [-math.sin(0), -math.cos(0), 0], [0, 0, 1]]
)

q1c = np.array([-l, -l, 0])
q2c = np.array([-l, l, 0])
q3c = np.array([l, l, 0])

contact1 = Contact(c1, R1)
contact2 = Contact(c2, R2)
contact3 = Contact(c3, R3)


C = np.array([contact1, contact2, contact3])

grasp = Grasp(p, C)

Gt = grasp.Gt
print("Gt shape:", Gt.shape)
print("Gt:\n", Gt)
grasp.get_classification(True)

q1 = Joint(1, q1c, zv, c1)
q2 = Joint(2, q2c, zv, c2)
q3 = Joint(3, q3c, zv, c3)

f1 = Finger(1, np.array([q1, q2, q3]))

f = np.array([f1])

jacobian = Jacobian(f, C)
J = jacobian.J

print("J shape:", J.shape)
print("J:\n", J)

jacobian.get_classification(True)
jacobian.get_hand_architecture()

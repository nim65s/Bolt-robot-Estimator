import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import np.random as rd

x0 = 0.15
y0 = 0.2
z0 = 0.95



soa = np.array([[0, 0, 0, 1, 0, 0], 
                [0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 1], 
                [0, 0, 0, x0, y0, z0],
                [0, 0, 0, x1, y1, z1],
                [0, 0, 0, x2, y2, z2]])

X, Y, Z, U, V, W = zip(*soa)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.quiver(X, Y, Z, U, V, W)
ax.set_xlim([-1, 0.5])
ax.set_ylim([-1, 1.5])
ax.set_zlim([-1, 8])
plt.show()

plt.clf()
fig = plt.figure()
ax = plt.axes(projection='3d')


def f(x, y):
    return np.sin(np.sqrt(x ** 2 + y ** 2))

x = np.linspace(-6, 6, 30)
y = np.linspace(-6, 6, 30)

X, Y = np.meshgrid(x, y)
Z = f(X, Y)


fig = plt.figure()
ax = plt.axes(projection='3d')
ax.contour3D(X, Y, Z, 50, cmap='binary')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')














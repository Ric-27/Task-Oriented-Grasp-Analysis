from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot as plt
import numpy as np


def close(event):
    exit()


objects = [
    "petri_dish",
    "marker_capped",
    "marker_uncapped",
    "kit_pack",
    "kit_tab",
    "canister",
    "tube",
    "needle",
    "rinse_glass",
    "plug_red",
    "glass_vial",
    "plug_yellow",
    "rinse_glass_small",
    "tube_clipper",
    "scissors",
]

for object in objects:
    print(object)
    path = "./stl/" + object + ".stl"

    meshi = mesh.Mesh.from_file(path)
    triangles = meshi.vectors
    points = triangles.flatten().reshape(triangles.shape[0] * 3, 3)
    cog = np.array(
        [
            sum(points[:, 0]) / points.shape[0],
            sum(points[:, 1]) / points.shape[0],
            sum(points[:, 2]) / points.shape[0],
        ]
    )
    fig = plt.figure(figsize=(7, 7))
    ax = mplot3d.Axes3D(fig, auto_add_to_figure=False)  # Python 3.8
    fig.add_axes(ax)  # Python 3.8
    fig.canvas.callbacks.connect("scroll_event", close)
    collection = mplot3d.art3d.Poly3DCollection(triangles, linewidths=0.2, alpha=0.3)
    collection.set_facecolor([0.5, 0.5, 0.5])
    collection.set_edgecolor([0, 0, 0])
    ax.add_collection3d(collection)
    scale = triangles.flatten()
    ax.auto_scale_xyz(scale, scale, scale)
    biggest = max(scale) if max(scale) > abs(min(scale)) else abs(min(scale))
    ax.scatter(0, 0, 0, color="magenta")
    ax.plot((0, biggest * 0.5), (0, 0), (0, 0), color="red")
    ax.plot((0, 0), (0, biggest * 0.5), (0, 0), color="green")
    ax.plot((0, 0), (0, 0), (0, biggest * 0.5), color="blue")
    """
    ax.scatter(cog[0], cog[1], cog[2], color="darkorange")
    ax.plot(
        (cog[0], cog[0] + biggest * 0.1),
        (cog[1], cog[1]),
        (cog[2], cog[2]),
        color="red",
    )
    ax.plot(
        (cog[0], cog[0]),
        (cog[1], cog[1] + biggest * 0.1),
        (cog[2], cog[2]),
        color="green",
    )
    ax.plot(
        (cog[0], cog[0]),
        (cog[1], cog[1]),
        (cog[2], cog[2] + biggest * 0.1),
        color="blue",
    )
    """
    plt.show()

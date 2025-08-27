import gdstk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
from pathlib import Path as FilePath   # alias Pathlib Path
from PyQt5.QtWidgets import QApplication, QFileDialog
import sys
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MplPath   # alias Matplotlib Path

# -------------------
# File paths
# -------------------
GDS_DIR = FilePath("C:/HeatMapApp/gds_inputs")
NODES_FILE = "nodes.txt"
VOLTAGES_FILE = "voltages.txt"


# -------------------
# Select GDS file
# -------------------
def select_gds_file():
    app = QApplication(sys.argv)
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select a .gds file",
        str(GDS_DIR),
        "GDS Files (*.gds);;All Files (*)"
    )
    return file_path


# -------------------
# Load node coordinates
# -------------------
def load_nodes(filename):
    nodes = []
    with open(filename, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:       # expects: label x y
                x, y = map(float, parts[1:3])
                nodes.append((x, y))
    return np.array(nodes)


# -------------------
# Load voltages
# -------------------
def load_voltages(filename):
    voltages = []
    with open(filename, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:          # expects: label voltage
                v = float(parts[1])
                voltages.append(v)
    return np.array(voltages)


# -------------------
# Main
# -------------------
file_path = select_gds_file()
if not file_path:
    raise ValueError("No file selected!")

# Read GDS
lib = gdstk.read_gds(file_path)
all_cells = lib.cells
print("All cells:", [cell.name for cell in all_cells])

if not all_cells:
    raise ValueError("No cells found in the GDS file!")

cell = lib.cells[-1]  # pick last cell

# ---- Setup plot ----
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect("equal")

# ---- Heatmap from nodes + voltages ----
nodes = load_nodes(NODES_FILE)
voltages = load_voltages(VOLTAGES_FILE)

(xmin, ymin), (xmax, ymax) = cell.bounding_box()

# Create grid
grid_x, grid_y = np.mgrid[xmin:xmax:200j, ymin:ymax:200j]

# Interpolate voltages at grid points
grid_z = griddata(nodes, voltages, (grid_x, grid_y), method="cubic")

# Draw heatmap first (full bounding box)
im = ax.imshow(
    grid_z.T,
    extent=[xmin, xmax, ymin, ymax],
    origin="lower",
    cmap=plt.get_cmap("jet"),      # blue → green → yellow → red
    vmin=np.min(voltages),         # lowest voltage = blue
    vmax=np.max(voltages),         # highest voltage = red
    alpha=0.8
)

# ---- Build ONE clipping path from all polygons ----
all_paths = []
for polygon in cell.polygons:
    all_paths.append(MplPath(polygon.points))

# Combine into a compound path
compound_path = MplPath.make_compound_path(*all_paths)

# Use compound path as clip mask
patch = PathPatch(compound_path, facecolor="none", edgecolor="none")
ax.add_patch(patch)
im.set_clip_path(patch)

# ---- Draw polygon outlines for clarity ----
for polygon in cell.polygons:
    points = polygon.points
    ax.plot(points[:, 0], points[:, 1], color="black", linewidth=0.5)

# ---- Colorbar ----
plt.colorbar(im, ax=ax, label="Voltage")

plt.show()

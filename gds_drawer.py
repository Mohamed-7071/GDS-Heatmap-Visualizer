import gdstk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QFileDialog
import sys

# -------------------
# File paths
# -------------------
GDS_DIR = Path("C:/HeatMapApp/gds_inputs")
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

# ---- Draw GDS polygons ----
fig, ax = plt.subplots(figsize=(8, 8))

for polygon in cell.polygons:
    points = polygon.points
    ax.fill(points[:, 0], points[:, 1], edgecolor="black", fill=False)

ax.set_aspect("equal")

# ---- Heatmap from nodes + voltages ----
nodes = load_nodes(NODES_FILE)
voltages = load_voltages(VOLTAGES_FILE)

(xmin, ymin), (xmax, ymax) = cell.bounding_box()

# Create grid
grid_x, grid_y = np.mgrid[xmin:xmax:200j, ymin:ymax:200j]

# Interpolate voltages at grid points
grid_z = griddata(nodes, voltages, (grid_x, grid_y), method="cubic")

# Overlay heatmap
im = ax.imshow(
    grid_z.T,
    extent=[xmin, xmax, ymin, ymax],
    origin="lower",
    cmap="hot",
    alpha=0.6
)

# Add colorbar for reference
plt.colorbar(im, ax=ax, label="Voltage")

plt.show()

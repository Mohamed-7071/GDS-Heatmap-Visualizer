import gdstk
import matplotlib.pyplot as plt
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QFileDialog
import sys

# Constant folder path
GDS_DIR = Path("C:/HeatMapApp/gds_inputs")

def select_gds_file():
    app = QApplication(sys.argv)
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select a .gds file",
        str(GDS_DIR),   # Always start inside gds_inputs
        "GDS Files (*.gds);;All Files (*)"
    )
    return file_path

# Let the user choose a file
file_path = select_gds_file()

if not file_path:
    raise ValueError("No file selected!")

print("Selected file:", file_path)

# Read GDS file
lib = gdstk.read_gds(file_path)

# List all cells
all_cells = lib.cells
print("All cells:", [cell.name for cell in all_cells])

if not all_cells:
    raise ValueError("No cells found in the GDS file!")

# Pick last cell (or specific one by name)
cell = lib.cells[-1]

# Draw polygons
fig, ax = plt.subplots(figsize=(8, 8))

for polygon in cell.polygons:
    points = polygon.points
    ax.fill(points[:, 0], points[:, 1], edgecolor="black", fill=False)

ax.set_aspect("equal")
plt.show()

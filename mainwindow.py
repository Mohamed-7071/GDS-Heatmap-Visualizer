#!/usr/bin/env python3

import sys
import shutil
import subprocess
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QMessageBox, QApplication, QVBoxLayout,
    QLabel, QPushButton, QMainWindow, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


PREDEFINED_DIR = Path.home() / "Documents" / "HeatMapApp" / "gds_inputs"


# ----------------- Main Window -----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heat Map Generator")
        self.setGeometry(200, 200, 600, 400)

        # Label
        self.label = QLabel("Add your .gds file", self)
        self.label.setFont(QFont("Segoe UI", 16))
        self.label.setAlignment(Qt.AlignCenter)

        # Button
        self.button = QPushButton(" Files")
        self.button.setFixedSize(150, 40)
        self.button.clicked.connect(self.on_add_gds_clicked)

        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.addWidget(self.label)
        layout.addWidget(self.button, alignment=Qt.AlignCenter)

        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_add_gds_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a .gds file",
            str(Path.home()),
            "GDS Files (*.gds);;All Files (*)"
        )
        if not file_path:
            return  # canceled

        src = Path(file_path)
        if src.suffix.lower() != ".gds":
            QMessageBox.warning(self, "Invalid file", "Please select a .gds file.")
            return

        try:
            PREDEFINED_DIR.mkdir(parents=True, exist_ok=True)
            dest = PREDEFINED_DIR / src.name

            if dest.exists():
                choice = QMessageBox.question(
                    self,
                    "File exists",
                    f"'{dest.name}' already exists in:\n{PREDEFINED_DIR}\n\nOverwrite?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if choice == QMessageBox.No:
                    return

            shutil.copy2(src, dest)

            # Run gds_drawer.py in a subprocess, passing the file path
            script_dir = Path(__file__).resolve().parent
            gds_drawer_py = script_dir / "gds_drawer.py"

            subprocess.Popen([sys.executable, str(gds_drawer_py), str(dest)])

            # Close the main window once launched
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Something went wrong:\n{e}")


# ----------------- Main -----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

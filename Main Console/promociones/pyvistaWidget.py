from PySide2.QtWidgets import QGraphicsView
from PySide2.QtWidgets import QVBoxLayout
import numpy as np
import pyvista as pv


class PyVistaWidget(QGraphicsView):

    def __init__(self, parent=None):
        super(PyVistaWidget, self).__init__(parent)
        pv.set_plot_theme("document")
        self.vtk_widget = pv.QtInteractor()
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.vtk_widget)
        self.setLayout(vertical_layout)
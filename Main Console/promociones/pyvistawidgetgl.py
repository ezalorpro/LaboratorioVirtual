from PySide2.QtWidgets import QOpenGLWidget
from PySide2.QtWidgets import QVBoxLayout
import numpy as np
import pyvista as pv


class PyVistaWidgetGL(QOpenGLWidget):

    def __init__(self, parent=None):
        super(PyVistaWidgetGL, self).__init__(parent)
        pv.set_plot_theme("document")
        self.vtk_widget = pv.QtInteractor()
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.vtk_widget)
        self.setLayout(vertical_layout)
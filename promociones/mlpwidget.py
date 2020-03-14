""" 
Archivo para definir las clases MlpWidget, MlpWidgetNoToolbar, MlpWidgetSubplot y MlpWidget3D, estas clases son utilizadas por qtdesigner para promocionar un QGraphicsView a las clases aca definidas en orden de mostrar las gráficas en un QGraphicsView
"""


from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PySide2.QtWidgets import QWidget, QGraphicsView
from PySide2.QtWidgets import QVBoxLayout
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.figure import Figure


class MlpWidget(QGraphicsView):
    """
    Clase básica para mostrar gráficas utilizando Matplotlib
    
    :param QGraphicsView: Clase base del QGraphicsView
    :type QGraphicsView: objectType
    """

    def __init__(self, parent=None):
        super(MlpWidget, self).__init__(parent)
        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self)
        vertical_layout.addWidget(self.toolbar)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.figure.tight_layout()
        self.canvas.figure.subplots_adjust(top=0.95,
                                          bottom=0.095,
                                          left=0.1,
                                          right=0.97,
                                          hspace=0.2,
                                          wspace=0.2)
        self.canvas.axes.grid()
        self.setLayout(vertical_layout)


class MlpWidgetNoToolbar(QGraphicsView):
    """
    Clase para mostrar gráficas utilizando Matplotlib sin el toolbar
    
    :param QGraphicsView: Clase base del QGraphicsView
    :type QGraphicsView: objectType
    """

    def __init__(self, parent=None):
        super(MlpWidgetNoToolbar, self).__init__(parent)
        self.canvas = FigureCanvas(Figure(tight_layout=True))

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.figure.tight_layout()
        self.canvas.axes.grid()
        self.setLayout(vertical_layout)


class MlpWidgetSubplot(QGraphicsView):
    """
    Clase para mostrar gráficas en subplots utilizando Matplotlib
    
    :param QGraphicsView: Clase base del QGraphicsView
    :type QGraphicsView: objectType
    """

    def __init__(self, parent=None):
        super(MlpWidgetSubplot, self).__init__(parent)
        self.canvas = FigureCanvas(Figure(tight_layout=True))

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self)
        vertical_layout.addWidget(self.toolbar)

        self.canvas.axes1 = self.canvas.figure.add_subplot(211)
        self.canvas.axes1.grid()
        self.canvas.axes2 = self.canvas.figure.add_subplot(212, sharex=self.canvas.axes1)
        self.canvas.axes2.grid()
        self.canvas.figure.tight_layout()
        self.setLayout(vertical_layout)


class MlpWidget3D(QGraphicsView):
    """
    Clase básica para mostrar gráficas en 3D utilizando Matplotlib
    
    :param QGraphicsView: Clase base del QGraphicsView
    :type QGraphicsView: objectType
    """
    
    def __init__(self, parent=None):
        super(MlpWidget3D, self).__init__(parent)
        self.canvas = FigureCanvas(Figure(tight_layout=True))

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111, projection='3d')
        self.canvas.figure.tight_layout()
        self.canvas.axes.grid()
        self.colorbar = 0
        self.setLayout(vertical_layout)

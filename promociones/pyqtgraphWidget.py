""" 
Archivo para definir las clases PgraphWidget y PgraphWidgetpid, estas clases son utilizadas por qtdesigner para promocionar un QGraphicsView a las clases aca definidas en orden de mostrar las graficas en un QGraphicsView
"""


from PySide2.QtWidgets import QGraphicsView
from PySide2.QtWidgets import QVBoxLayout
from pyqtgraphmdf import PlotWidget

import pyqtgraphmdf as pg


class PgraphWidget(QGraphicsView):
    """
    Clase para las graficas utilizadas en la prueba de los controladores difusos, PyQtGraph es acto para realizar graficas en tiempo real
    
    :param QGraphicsView: Clase base del QGraphicsView
    :type QGraphicsView: objectType
    """
    
    def __init__(self, parent=None):
        super(PgraphWidget, self).__init__(parent)

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.plotwidget = PlotWidget()
        self.plotwidget.setMouseEnabled(False, False)
        self.plotwidget.setYRange(0, 1)
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.plotwidget)
        self.plotwidget.showGrid(x=True, y=True)
        self.setLayout(vertical_layout)


class PgraphWidgetpid(QGraphicsView):
    """
    Clase para las graficas utilizadas en el tunning de controladores PID, PyQtGraph es acto para realizar graficas en tiempo real
    
    :param QGraphicsView: Clase base del QGraphicsView
    :type QGraphicsView: objectType
    """

    def __init__(self, parent=None):
        super(PgraphWidgetpid, self).__init__(parent)

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)

        self.plotwidget = PlotWidget()
        self.plotwidget.setMouseEnabled(False, False)
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.plotwidget)
        self.plotwidget.showGrid(x=True, y=True)
        self.curva = self.plotwidget.plot(
            pen={
                'color': pg.mkColor('#1f77b4'), 'width': 3
            }
        )
        self.setLayout(vertical_layout)

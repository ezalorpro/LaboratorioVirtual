""" 
Archivo para definir la clase JupyterConsolePgraphWidget, estas clase es utilizada por qtdesigner para promocionar un QGraphicsView a la clase aca definida en orden de incrustar una consola jupyter en un QGraphicsView, actualmente solo funciona si el codigo es ejecutado utilizando el Python del usuario, i.e., no sirve al distribuir la aplicacion en .exe con Pyinstaller
"""


from qtconsole.rich_jupyter_widget import RichJupyterWidget
from PySide2.QtWidgets import QWidget, QGraphicsView
from qtconsole.manager import QtKernelManager
from PySide2.QtWidgets import QVBoxLayout


class JupyterConsole(QGraphicsView):
    """
    Clase para incrustar una consola jupyter
    
    :param QGraphicsView: Clase base del QGraphicsView
    :type QGraphicsView: objectType
    """
    
    def __init__(self, parent=None):
        super(JupyterConsole, self).__init__(parent)
        self.kernel_manager = QtKernelManager(kernel_name='python3')
        self.kernel_manager.start_kernel()

        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()

        self.jupyter_widget = RichJupyterWidget()
        self.jupyter_widget.kernel_manager = self.kernel_manager
        self.jupyter_widget.kernel_client = self.kernel_client
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.jupyter_widget)
        self.setLayout(vertical_layout)

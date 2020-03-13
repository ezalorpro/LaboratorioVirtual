""" Archivo principal, en orden de ejecutar la aplicacion, este es el archivo a ejecutar """


from handlers.jupyterConsoleHandler import jupyterConsoleHandler
from handlers.simulacionHandler import SimulacionHandler
from Ui_VentanaPrincipalConsole import Ui_MainWindow
from handlers.analisisHandler import AnalisisHandler
from handlers.TuningHandler import TuningHandler
from handlers.FuzzyHandler import FuzzyHandler
from PySide2 import QtGui, QtWidgets

import os


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """
    Clase principal del programa, esta clase hereda de QMainWindow y Ui_MainWindow, la primera es la clase base de ventanas que ofrece Qt mientras que la segunda es la clase que se crea a partir de qtdesigner y quien posee toda la definicion de toda la interfaz grafica. Desde aca se ejecutan los archivos Handler, quienes representan los enlaces entre las rutinas y la interfaz grafica de cada una de las funciones del laboratorio virtual, estos Handlers se tratan como si fueran una extension de esta clase, por tanto, se les envia self y se recibe self y se sigue tratando como si fuera parte de la clase
    
    :param QtWidgets: Clase base de ventana ofrecida por Qt
    :type QtWidgets: ObjectType
    :param Ui_MainWindow: Clase con la interfaz grafica autogenerada con qtdesigner
    :type Ui_MainWindow: ObjectType
    """

    def __init__(self, parent=None):
        """
        Constructor de la clase, aca se inicializan los objetos de las clases heredadas y se hacen los llamados a los Handlers
        
        :param parent: Sin efecto, defaults to None
        :type parent: NoneType, optional
        """

        super(MainWindow, self).__init__(parent)

        # Ventana principal, objeto de donde se manejara todo
        self.main = Ui_MainWindow()
        self.main.setupUi(self)
        self.showMaximized()
        
        # Estableciendo del icono de la aplicacion
        icon = QtGui.QIcon()
        image_path = self.resource_path("icono.ico")
        icon.addPixmap(QtGui.QPixmap(image_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        # Creacion de un dialogo, se usa para mostrar mensajes de error al usuario
        self.error_dialog = QtWidgets.QMessageBox()
        self.error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        self.error_dialog.setText("Error")
        self.error_dialog.setInformativeText('404')
        self.error_dialog.setWindowTitle("Error")

        AnalisisHandler(self)  # Handler para la pestaña de analisis de sistemas de control
        TuningHandler(self)  # Handler para la pestaña de Tunning
        FuzzyHandler(self)  # Handler para la pestaña de diseño de controladores difusos
        SimulacionHandler(self)  # Handler para la pestaña de simulacion de sistemas de control
        jupyterConsoleHandler(self)  # Handler para la pestaña de la qtconsole

    def resource_path(self, relative_path):
        """
        Funcion para generar direcciones absolutas a partir de direcciones relativas
        
        :param relative_path: direccion relativa
        :type relative_path: str
        """

        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def closeEvent(self, event):
        """ Evento para el cerrado de la ventana """

        error_dialog = QtWidgets.QMessageBox.question(
            self,
            "Laboratorio Virtual",
            '¿Cerrar el programa? Los cambios no guardados se perderán',
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
        )

        event.ignore()
        if error_dialog == QtWidgets.QMessageBox.Ok:
            self.main.jupyterWidget.jupyter_widget.kernel_client.stop_channels()
            self.main.jupyterWidget.jupyter_widget.kernel_manager.shutdown_kernel()
            event.accept()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()

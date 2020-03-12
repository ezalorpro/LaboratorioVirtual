""" 
Archivo para administrar la consola jupyter y los widgets asociadas a la misma
"""

from PySide2 import QtWidgets


def jupyterConsoleHandler(self):
    """
    Funcion principal para el manejo de la consola jupyter, se crean las señales a ejecutar cuando se interactua con los widgets
    """

    self.main.limpiarConsole.clicked.connect(lambda: limpiar_consola(self))
    self.main.agregarPathConsole.clicked.connect(lambda: agregar_path(self))


def limpiar_consola(self):
    """ Funcion para limpiar la consola """
    self.main.jupyterWidget.jupyter_widget._control.clear()


def agregar_path(self):
    """ 
    Funcion para agregar la direccion seleccionada al sys.path, la idea es agregar la carpeta de librerias del python del usuario para que se encuentren a disposicion del kernel 
    """
    
    path = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                      'Seleccionar carpeta:')
    self.main.jupyterWidget.jupyter_widget._execute(
        "sys.path.append(r'" + path + "')", True)

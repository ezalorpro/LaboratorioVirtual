""" 
Archivo para definir la clase FocusLineEdit, esta clases permite promocionar un lineEdit y agregar el evento focus con el fin de generar una señal al dar clic en un lineEdit
"""


from PySide2 import QtCore, QtWidgets


class FocusLineEdit(QtWidgets.QLineEdit):
    """ 
    Clase basica para promocionar el lineEdit   
    
    :param QtWidgets: Clase base de los Widgets
    :type QtWidgets: objectType
    """
    focusIn = QtCore.Signal()

    def focusInEvent(self, event):
        """
        Evento de focus para el lineEdit
        
        :param event: Evento generado
        :type event: tuple
        """ 
        
        super(FocusLineEdit, self).focusInEvent(event)
        self.focusIn.emit()
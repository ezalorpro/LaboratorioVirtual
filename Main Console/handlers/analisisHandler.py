""" 
Archivo para el manejo de la funcion de analisis de sistemas de control, sirve de intermediario entre la interfaz grafica y las rutinas de analisis 
"""


from rutinas.rutinas_analisis import *

import json


def AnalisisHandler(self):
    """
    Funcion principal para el manejo de la funcionalida de analisis de sistemas de control, se crean las señales a ejecutar cuando se interactua con los widgets incluyendo las validaciones de entradas
    """
    
    self.main.tfcalcButton1.clicked.connect(lambda: calcular_analisis(self))
    self.main.sscalcButton1.clicked.connect(lambda: calcular_analisis(self))

    self.main.tfradioButton1.toggled.connect(lambda: analisis_stacked_to_tf(self))
    self.main.ssradioButton1.toggled.connect(lambda: analisis_stacked_to_ss(self))

    # Validaciones de entradas

    self.main.tfnumEdit1.editingFinished.connect(lambda: tfnum_validator(self))
    self.main.tfdemEdit1.editingFinished.connect(lambda: tfdem_validator(self))
    self.main.tfdelayEdit1.editingFinished.connect(lambda: tfdelay_validator(self))
    self.main.tfperiodoEdit1.editingFinished.connect(lambda: tfperiodo_validator(self))

    self.main.ssAEdit1.editingFinished.connect(lambda: ssA_validator(self))
    self.main.ssBEdit1.editingFinished.connect(lambda: ssB_validator(self))
    self.main.ssCEdit1.editingFinished.connect(lambda: ssC_validator(self))
    self.main.ssDEdit1.editingFinished.connect(lambda: ssD_validator(self))
    self.main.ssdelayEdit1.editingFinished.connect(lambda: ssdelay_validator(self))
    self.main.ssperiodoEdit1.editingFinished.connect(lambda: ssperiodo_validator(self))


def tfnum_validator(self):
    """ Validacion del numerador de la funcion de transferencia """
    
    try:
        _ = json.loads(self.main.tfnumEdit1.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato no valido, los coeficientes deben estar entre corchetes y separados por comas.\n i.g., [1, 2, 3]"
        )
        self.error_dialog.exec_()
        self.main.tfnumEdit1.setFocus()
        return


def tfdem_validator(self):
    """ Validacion del denominador de la funcion de transferencia """
    
    try:
        _ = json.loads(self.main.tfdemEdit1.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato no valido, los coeficientes deben estar entre corchetes y separados por comas.\n i.g., [1, 2, 3]"
        )
        self.error_dialog.exec_()
        self.main.tfdemEdit1.setFocus()
        return


def tfdelay_validator(self):
    """ Validacion del delay de la funcion de transferencia """
    
    try:
        _ = float(self.main.tfdelayEdit1.text())
        if _ < 0:
            raise ValueError
    except ValueError:
        self.error_dialog.setInformativeText("Delay no valido, debe ser un número real mayor o igual que cero")
        self.error_dialog.exec_()
        self.main.tfdelayEdit1.setFocus()
        return


def tfperiodo_validator(self):
    """ Validacion del periodo de muestreo de la funcion de transferencia """
    
    try:
        _ = float(self.main.tfperiodoEdit1.text())
        if _ <= 0:
            raise ValueError
    except ValueError:
        self.error_dialog.setInformativeText(
            "Periodo de muestreo no valido, debe ser un numero real mayor que cero")
        self.error_dialog.exec_()
        self.main.tfperiodoEdit1.setFocus()
        return


def ssA_validator(self):
    """ Validacion de la matriz de estados de la ecuacion de espacio de estados """
    
    try:
        _ = json.loads(self.main.ssAEdit1.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato no valido, las matrices deben estar definidas entre corchetes con cada fila delimitada por otro par de corchetes y separadas entre si por comas, cada valor debera ir separado por coma.\n i.g., [[1, 1], [1, -1]]"
        )
        self.error_dialog.exec_()
        self.main.ssAEdit1.setFocus()
        return


def ssB_validator(self):
    """ Validacion de la matriz de entrada de la ecuacion de espacio de estados """
    
    try:
        _ = json.loads(self.main.ssBEdit1.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato no valido, las matrices deben estar definidas entre corchetes con cada fila delimitada por otro par de corchetes y separadas entre si por comas, cada valor debera ir separado por coma.\n i.g., [[1, 1], [1, -1]]"
        )
        self.error_dialog.exec_()
        self.main.ssBEdit1.setFocus()
        return


def ssC_validator(self):
    """ Validacion de la matriz de salida de la ecuacion de espacio de estados """
    
    try:
        _ = json.loads(self.main.ssCEdit1.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato no valido, las matrices deben estar definidas entre corchetes con cada fila delimitada por otro par de corchetes y separadas entre si por comas, cada valor debera ir separado por coma.\n i.g., [[1, 1], [1, -1]]"
        )
        self.error_dialog.exec_()
        self.main.ssCEdit1.setFocus()
        return


def ssD_validator(self):
    """ Validacion de la matriz de transmision directa de la ecuacion de espacio de estados """
    
    try:
        _ = json.loads(self.main.ssDEdit1.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato no valido, las matrices deben estar definidas entre corchetes con cada fila delimitada por otro par de corchetes y separadas entre si por comas, cada valor debera ir separado por coma.\n i.g., [[1, 1], [1, -1]]"
        )
        self.error_dialog.exec_()
        self.main.ssDEdit1.setFocus()
        return


def ssdelay_validator(self):
    """ Validacion del delay de la ecuacion de espacio de estados """
    
    try:
        _ = float(self.main.ssdelayEdit1.text())
        if _ < 0:
            raise ValueError
    except ValueError:
        self.error_dialog.setInformativeText("Delay no valido, debe ser un numero real mayor o igual que cero")
        self.error_dialog.exec_()
        self.main.ssdelayEdit1.setFocus()
        return


def ssperiodo_validator(self):
    """ Validacion del periodo de muestreo de la ecuacion de espacio de estados """
    
    try:
        _ = float(self.main.ssperiodoEdit1.text())
        if _ <= 0:
            raise ValueError
    except ValueError:
        self.error_dialog.setInformativeText(
            "Periodo de muestreo no valido, debe ser un numero real mayor que cero")
        self.error_dialog.exec_()
        self.main.ssperiodoEdit1.setFocus()
        return


def calcular_analisis(self):
    """
    Funcion para realizar el los calculos necesarios para la funcionalidad de analisis de sistemas de control, el llamado a esta funcion se realiza por medio del boton calcular
    """
    
    system_ss = 0

    if (
        self.main.tfdiscretocheckBox1.isChecked() and
        self.main.AnalisisstackedWidget.currentIndex() == 0
    ):
        self.dt = json.loads(self.main.tfperiodoEdit1.text())
    elif (
        self.main.ssdiscretocheckBox1.isChecked() and
        self.main.AnalisisstackedWidget.currentIndex() == 1
    ):
        self.dt = json.loads(self.main.ssperiodoEdit1.text())
    else:
        self.dt = None

    if self.main.AnalisisstackedWidget.currentIndex() == 0:
        # caso: Funcion de transferencia
        num = json.loads(self.main.tfnumEdit1.text())
        dem = json.loads(self.main.tfdemEdit1.text())

        # Validacion de funcion propia
        if len(num) > len(dem):
            self.error_dialog.setInformativeText(
                "Funcion de transferencia impropia, el numerador debe ser de un grado menor o igual al denominador")
            self.error_dialog.exec_()
            self.main.ssdelayEdit1.setFocus()
            return

        system, T, system_delay = system_creator_tf(self, num, dem)
    else:
        # caso: Ecuacion de espacio de estados
        A = json.loads(self.main.ssAEdit1.text())
        B = json.loads(self.main.ssBEdit1.text())
        C = json.loads(self.main.ssCEdit1.text())
        D = json.loads(self.main.ssDEdit1.text())
        system, T, system_delay, system_ss = system_creator_ss(self, A, B, C, D)

    if system_delay is None:
        # caso: Sistema sin delay
        t1, y1 = rutina_impulse_plot(self, system, T)
        t2, y2 = rutina_step_plot(self, system, T)
        mag, phase, omega = rutina_bode_plot(self, system)
        real, imag, freq = rutina_nyquist_plot(self, system)
        rutina_root_locus_plot(self, system)
        rutina_nichols_plot(self, system)
    else:
        # caso: Sistema con delay
        t1, y1 = rutina_impulse_plot(self, system_delay, T)
        t2, y2 = rutina_step_plot(self, system_delay, T)
        mag, phase, omega = rutina_bode_plot(self, system_delay)
        real, imag, freq = rutina_nyquist_plot(self, system_delay)
        rutina_root_locus_plot(self, system_delay)
        rutina_nichols_plot(self, system_delay)

    if not system_ss:
        rutina_system_info(self, system, T, mag, phase, omega)
    else:
        rutina_system_info(self, system_ss, T, mag, phase, omega)


def analisis_bool_discreto(self):
    """ Funcion para habilitar y deshabilitar el periodo de muestreo """
    
    if self.main.tfdiscretocheckBox1.isChecked():
        self.main.tfperiodoEdit1.setEnabled(True)
    else:
        self.main.tfperiodoEdit1.setDisabled(True)


def analisis_stacked_to_tf(self):
    """ Funcion para cambiar de ecuacion de espacio de estados a funcion de transferencia """
    self.main.AnalisisstackedWidget.setCurrentIndex(0)


def analisis_stacked_to_ss(self):
    """ Funcion para cambiar de funcion de transferencia a ecuacion de espacio de estados """
    self.main.AnalisisstackedWidget.setCurrentIndex(1)

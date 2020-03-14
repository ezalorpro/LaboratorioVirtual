""" 
Archivo para el manejo de la función de Tunning, sirve de intermediario entre la interfaz gráfica y las rutinas de entonación de controladores PID y la identificación de modelos a partir de un archivo CSV y entonación de PID para el mismo
"""


from rutinas.rutinas_PID import *
from rutinas.rutinas_CSV import *
from PySide2 import QtWidgets

import numpy as np

import json


def TuningHandler(self):
    """
    Función principal para el manejo de la funcionalida de Tunning, se crean las señales a ejecutar cuando se interactuá con los widgets incluyendo las validaciones de entradas
    """

    self.GraphObjets = 0
    self.tfSliderValue = self.main.tfreolutionSpin2.value()
    self.ssSliderValue = self.main.ssreolutionSpin2.value()

    self.main.tfcalcButton2.clicked.connect(lambda: chequeo_de_accion(self))
    self.main.sscalcButton2.clicked.connect(lambda: chequeo_de_accion(self))
    self.main.csvcalcButton2.clicked.connect(lambda: chequeo_de_accion(self))

    self.main.BtnFile.clicked.connect(lambda: csv_path(self))

    self.main.kpHSlider2.valueChanged.connect(lambda: chequeo_de_accion(self))
    self.main.kiHSlider2.valueChanged.connect(lambda: chequeo_de_accion(self))
    self.main.kdHSlider2.valueChanged.connect(lambda: chequeo_de_accion(self))

    self.main.pidTiempoSlider.valueChanged.connect(lambda: tiempo_slider_cambio(self))
    self.main.pidNSlider.valueChanged.connect(lambda: chequeo_de_accion(self))

    self.main.kpCheckBox2.stateChanged.connect(lambda: chequeo_de_accion(self))
    self.main.kiCheckBox2.stateChanged.connect(lambda: chequeo_de_accion(self))
    self.main.kdCheckBox2.stateChanged.connect(lambda: chequeo_de_accion(self))

    self.main.tfdiscretocheckBox2.stateChanged.connect(lambda: PID_bool_discreto(self))

    self.main.tfradioButton2.toggled.connect(lambda: PID_stacked_to_tf(self))
    self.main.ssradioButton2.toggled.connect(lambda: PID_stacked_to_ss(self))
    self.main.csvradioButton2.toggled.connect(lambda: PID_stacked_to_csv(self))

    self.main.tfAutoTuningcheckBox2.clicked['bool'].connect(
        lambda: tf_habilitar_sliders_checkbox(self)
    )
    self.main.ssAutoTuningcheckBox2.clicked['bool'].connect(
        lambda: ss_habilitar_sliders_checkbox(self)
    )

    self.main.tfreolutionSpin2.valueChanged.connect(lambda: actualizar_sliders_tf(self))
    self.main.ssreolutionSpin2.valueChanged.connect(lambda: actualizar_sliders_ss(self))

    # Validaciónes de entradas

    self.main.tfnumEdit2.editingFinished.connect(lambda: tfnum_validator(self))
    self.main.tfdemEdit2.editingFinished.connect(lambda: tfdem_validator(self))
    self.main.tfdelayEdit2.editingFinished.connect(lambda: tfdelay_validator(self))
    self.main.tfperiodoEdit2.editingFinished.connect(lambda: tfperiodo_validator(self))

    self.main.ssAEdit2.editingFinished.connect(lambda: ssA_validator(self))
    self.main.ssBEdit2.editingFinished.connect(lambda: ssB_validator(self))
    self.main.ssCEdit2.editingFinished.connect(lambda: ssC_validator(self))
    self.main.ssDEdit2.editingFinished.connect(lambda: ssD_validator(self))
    self.main.ssdelayEdit2.editingFinished.connect(lambda: ssdelay_validator(self))
    self.main.ssperiodoEdit2.editingFinished.connect(lambda: ssperiodo_validator(self))

    self.main.EditLVP.editingFinished.connect(lambda: LVP_validator(self))
    self.main.EditUVP.editingFinished.connect(lambda: UVP_validator(self))
    self.main.EditLEFC.editingFinished.connect(lambda: LEFC_validator(self))
    self.main.EditUEFC.editingFinished.connect(lambda: UEFC_validator(self))


def tfnum_validator(self):
    """ Validación del numerador de la función de transferencia """

    try:
        _ = json.loads(self.main.tfnumEdit2.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato no valido, los coeficientes deben estar entre corchetes y separados por comas.\n i.g., [1, 2, 3]"
        )
        self.error_dialog.exec_()
        self.main.tfnumEdit2.setFocus()
        return


def tfdem_validator(self):
    """ Validación del denominador de la función de transferencia """

    try:
        _ = json.loads(self.main.tfdemEdit2.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato no valido, los coeficientes deben estar entre corchetes y separados por comas.\n i.g., [1, 2, 3]"
        )
        self.error_dialog.exec_()
        self.main.tfdemEdit2.setFocus()
        return


def tfdelay_validator(self):
    """ Validación del delay de la función de transferencia """

    try:
        _ = float(self.main.tfdelayEdit2.text())
        if _ < 0:
            raise ValueError
    except ValueError:
        self.error_dialog.setInformativeText(
            "Delay no valido, debe ser un numero real mayor o igual que cero")
        self.error_dialog.exec_()
        self.main.tfdelayEdit2.setFocus()
        return


def tfperiodo_validator(self):
    """ Validación del periodo de muestreo de la función de transferencia """
    try:
        _ = float(self.main.tfperiodoEdit2.text())
        if _ <= 0:
            raise ValueError
    except ValueError:
        self.error_dialog.setInformativeText(
            "Periodo de muestreo no valido, debe ser un numero real mayor que cero")
        self.error_dialog.exec_()
        self.main.tfperiodoEdit2.setFocus()
        return


def ssA_validator(self):
    """ Validación de la matriz de estados de la ecuación de espacio de estados """

    try:
        _ = json.loads(self.main.ssAEdit2.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato no valido, las matrices deben estar definidas entre corchetes con cada fila delimitada por otro par de corchetes y separadas entre si por comas, cada valor deberá ir separado por coma.\n i.g., [[1, 1], [1, -1]]"
        )
        self.error_dialog.exec_()
        self.main.ssAEdit2.setFocus()
        return


def ssB_validator(self):
    """ Validación de la matriz de entrada de la ecuación de espacio de estados """

    try:
        _ = json.loads(self.main.ssBEdit2.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato no valido, las matrices deben estar definidas entre corchetes con cada fila delimitada por otro par de corchetes y separadas entre si por comas, cada valor deberá ir separado por coma.\n i.g., [[1, 1], [1, -1]]"
        )
        self.error_dialog.exec_()
        self.main.ssBEdit2.setFocus()
        return


def ssC_validator(self):
    """ Validación de la matriz de salida de la ecuación de espacio de estados """

    try:
        _ = json.loads(self.main.ssCEdit2.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato no valido, las matrices deben estar definidas entre corchetes con cada fila delimitada por otro par de corchetes y separadas entre si por comas, cada valor deberá ir separado por coma.\n i.g., [[1, 1], [1, -1]]"
        )
        self.error_dialog.exec_()
        self.main.ssCEdit2.setFocus()
        return


def ssD_validator(self):
    """ Validación de la matriz de transmisión directa de la ecuación de espacio de estados """

    try:
        _ = json.loads(self.main.ssDEdit2.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato no valido, las matrices deben estar definidas entre corchetes con cada fila delimitada por otro par de corchetes y separadas entre si por comas, cada valor deberá ir separado por coma.\n i.g., [[1, 1], [1, -1]]"
        )
        self.error_dialog.exec_()
        self.main.ssDEdit2.setFocus()
        return


def ssdelay_validator(self):
    """ Validación del delay de la ecuación de espacio de estados """

    try:
        _ = float(self.main.ssdelayEdit2.text())
        if _ < 0:
            raise ValueError
    except ValueError:
        self.error_dialog.setInformativeText(
            "Delay no valido, debe ser un numero real mayor o igual que cero")
        self.error_dialog.exec_()
        self.main.ssdelayEdit2.setFocus()
        return


def ssperiodo_validator(self):
    """ Validación del periodo de muestreo de la ecuación de espacio de estados """

    try:
        _ = float(self.main.ssperiodoEdit2.text())
        if _ <= 0:
            raise ValueError
    except ValueError:
        self.error_dialog.setInformativeText(
            "Periodo de muestreo no valido, debe ser un numero real mayor que cero")
        self.error_dialog.exec_()
        self.main.ssperiodoEdit2.setFocus()
        return


def tiempo_slider_cambio(self):
    """ Para discriminar entre entonación e identificación de modelo con archivo csv """

    if self.main.PIDstackedWidget.currentIndex() == 2:
        ajustar_atraso_manual(self)
    else:
        chequeo_de_accion(self)

def chequeo_de_accion(self):
    """
    Para discriminar entre entonación con función de transferencia, ecuación de espacio de estados o identificación de modelo con archivo csv 
    """

    if not self.main.tfAutoTuningcheckBox2.isChecked(
    ) and self.main.PIDstackedWidget.currentIndex() == 0:
        calcular_PID(self)
    elif not self.main.ssAutoTuningcheckBox2.isChecked(
    ) and self.main.PIDstackedWidget.currentIndex() == 1:
        calcular_PID(self)
    elif self.main.tfAutoTuningcheckBox2.isChecked(
    ) and self.main.PIDstackedWidget.currentIndex() == 0:
        calcular_autotuning(self)
    elif self.main.ssAutoTuningcheckBox2.isChecked(
    ) and self.main.PIDstackedWidget.currentIndex() == 1:
        calcular_autotuning(self)
    else:
        calcular_csv(self)


def calcular_PID(self):
    """
    Función para realizar el los calculos necesarios para la funcionalidad de entonación de controladores PID, el llamado a esta función se realizar por medio del botón calcular o cada vez que se modifique alguno de los sliders
    """

    system_ss = 0

    if (
        self.main.tfdiscretocheckBox2.isChecked() and
        self.main.PIDstackedWidget.currentIndex() == 0
    ):
        self.dt = json.loads(self.main.tfperiodoEdit2.text())
    elif (
        self.main.ssdiscretocheckBox2.isChecked() and
        self.main.PIDstackedWidget.currentIndex() == 1
    ):
        self.dt = json.loads(self.main.ssperiodoEdit2.text())
    else:
        self.dt = None

    if self.main.PIDstackedWidget.currentIndex() == 0:
        # caso: Función de transferencia
        num = json.loads(self.main.tfnumEdit2.text())
        dem = json.loads(self.main.tfdemEdit2.text())

        # Validación de función propia
        if len(num) > len(dem):
            self.error_dialog.setInformativeText(
                "Función de transferencia impropia, el numerador debe ser de un grado menor o igual al denominador")
            self.error_dialog.exec_()
            self.main.ssdelayEdit1.setFocus()
            return

        system_pid, T, system_delay, kp, ki, kd = system_creator_tf(self, num, dem)
    else:
        # caso: Ecuación de espacio de estados
        A = json.loads(self.main.ssAEdit2.text())
        B = json.loads(self.main.ssBEdit2.text())
        C = json.loads(self.main.ssCEdit2.text())
        D = json.loads(self.main.ssDEdit2.text())
        system_pid, T, system_delay, system_ss, kp, ki, kd = system_creator_ss(self, A, B, C, D)

    if system_delay is None:
        # caso: Sistema sin delay
        t2, y2 = rutina_step_plot(self, system_pid, T, kp, ki, kd)
    else:
        # caso: Sistema con delay
        t2, y2 = rutina_step_plot(self, system_delay, T, kp, ki, kd)

    if not system_ss:
        rutina_system_info(self, system_pid, T, y2)
        update_gain_labels(self, resolution=self.tfSliderValue)
        update_time_and_N_labels(self)
    else:
        rutina_system_info(self, system_ss, T, y2)
        update_gain_labels(self, resolution=self.ssSliderValue)
        update_time_and_N_labels(self)


def calcular_autotuning(self):
    """
    Función para realizar el los calculos necesarios para la funcionalidad de entonación de controladores PID con auto tunning, el llamado a esta función se realizar por medio del botón calcular si previamente se habilito la funcionalidad de auto tunning
    """

    system_ss = 0

    if (
        self.main.tfdiscretocheckBox2.isChecked() and
        self.main.PIDstackedWidget.currentIndex() == 0
    ):
        self.dt = json.loads(self.main.tfperiodoEdit2.text())
    elif (
        self.main.ssdiscretocheckBox2.isChecked() and
        self.main.PIDstackedWidget.currentIndex() == 1
    ):
        self.dt = json.loads(self.main.ssperiodoEdit2.text())
    else:
        self.dt = None

    if self.main.PIDstackedWidget.currentIndex() == 0:
        # caso: Función de transferencia
        num = json.loads(self.main.tfnumEdit2.text())
        dem = json.loads(self.main.tfdemEdit2.text())

        # Validación de función propia
        if len(num) > len(dem):
            self.error_dialog.setInformativeText(
                "Función de transferencia impropia, el numerador debe ser de un grado menor o igual al denominador")
            self.error_dialog.exec_()
            self.main.ssdelayEdit1.setFocus()
            return

        try:
            system_pid, T, system_delay, kp, ki, kd = system_creator_tf_tuning(self, num, dem)
        except TypeError:
            self.error_dialog.setInformativeText(
                "El alfa calculado es igual o menor a 0.05, lo cual es invalido para auto-tuning, se recomienda agregar un Delay mayor a 0.3"
            )
            self.error_dialog.exec_()
            return
    else:
        # caso: Ecuación de espacio de estados
        A = json.loads(self.main.ssAEdit2.text())
        B = json.loads(self.main.ssBEdit2.text())
        C = json.loads(self.main.ssCEdit2.text())
        D = json.loads(self.main.ssDEdit2.text())
        try:
            system_pid, T, system_delay, system_ss, kp, ki, kd = system_creator_ss_tuning(self, A, B, C, D)
        except TypeError:
            self.error_dialog.setInformativeText(
                "El alfa calculado es igual o menor a 0.05, lo cual es invalido para auto-tuning, se recomienda agregar un Delay mayor a 0.3"
            )
            self.error_dialog.exec_()
            return

    if system_delay is None:
        # caso: Sistema sin delay
        t2, y2 = rutina_step_plot(self, system_pid, T, kp, ki, kd)
    else:
        # caso: Sistema con delay
        t2, y2 = rutina_step_plot(self, system_delay, T, kp, ki, kd)

    if not system_ss:
        rutina_system_info(self, system_pid, T, y2, kp, ki, kd, autotuning=True)
        update_gain_labels(
            self, kp, ki, kd, autotuning=True, resolution=self.tfSliderValue
        )
        update_time_and_N_labels(self)
    else:
        rutina_system_info(self, system_ss, T, y2, kp, ki, kd, autotuning=True)
        update_gain_labels(
            self, kp, ki, kd, autotuning=True, resolution=self.ssSliderValue
        )
        update_time_and_N_labels(self)


def calcular_csv(self):
    """
    Función para realizar el los calculos necesarios para la funcionalidad de identificación de modelos y entonación de controlador PID, el llamado a esta función se realizar por medio del botón calcular
    """

    try:
        csv_data = np.genfromtxt(self.main.pathCSVedit.text(),
                                delimiter=self.main.EditSeparador.text(),
                                encoding=None,
                                autostrip=True,
                                dtype=None)
    except OSError:
        self.error_dialog.setInformativeText(
            "Archivo no valido"
        )
        self.error_dialog.exec_()
        self.main.tfdelayEdit1.setFocus()
        return

    try:
        csv_data, info = procesar_csv(self, csv_data)
    except UnboundLocalError:
        self.error_dialog.setInformativeText(
            "Error en el formato del CSV, verifique los nombres de los encabezados y/o el separador asignado")
        self.error_dialog.exec_()
        self.main.tfdelayEdit1.setFocus()
        return

    Kc, tau, y1, y2, t0, t1, t2, anclaT, anclaY = calcular_modelo(self, csv_data, *info)
    self.GraphObjets, self.model_info = entonar_y_graficar(self, csv_data, Kc, tau, y1, y2, t0, t1, t2)
    self.model_info.extend([anclaT, anclaY])
    self.main.pidTiempoSlider.setEnabled(True)


def LVP_validator(self):
    """ Validación del limite inferior del span de VP """

    try:
        _ = float(self.main.EditLVP.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Valor no valido, deber se un numero real")
        self.error_dialog.exec_()
        self.main.EditLVP.setFocus()
        return


def UVP_validator(self):
    """ Validación del limite superior del span de VP """

    try:
        _ = float(self.main.EditUVP.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Valor no valido, deber se un numero real")
        self.error_dialog.exec_()
        self.main.EditUVP.setFocus()
        return


def LEFC_validator(self):
    """ Validación del limite inferior del span de EFC """

    try:
        _ = float(self.main.EditLEFC.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Valor no valido, deber se un numero real")
        self.error_dialog.exec_()
        self.main.EditLEFC.setFocus()
        return


def UEFC_validator(self):
    """ Validación del limite superior del span de EFC """

    try:
        _ = float(self.main.EditUEFC.text())
    except ValueError:
        self.error_dialog.setInformativeText(
            "Valor no valido, deber se un numero real")
        self.error_dialog.exec_()
        self.main.EditUEFC.setFocus()
        return


def ajustar_atraso_manual(self):
    """
    Función para ajustar el tiempo t1, despues de realizar el calculo para un archivo csv, se utiliza en caso de que la estimación automática no sea lo suficientemente buena
    """

    Kc, t0, t1, t2 , y2, y1, anclaT, anclaY = self.model_info
    t1_new = self.main.pidTiempoSlider.value()
    t1_new = np.round(t0 + (t2-t0) * t1_new / 1000, 3)
    self.main.pidTiempoLabelValue.setText(str(t1_new))
    slop = (anclaY-y1) / (anclaT-t1_new)
    calculos_manual(self, self.GraphObjets, Kc, t0, t1_new, t2, slop, y1)


def csv_path(self):
    """ Función para cargar el archivo csv """
    path_csv = QtWidgets.QFileDialog.getOpenFileName(filter="CSV (*.csv)")
    self.main.pathCSVedit.setText(path_csv[0])


def PID_bool_discreto(self):
    """ Función para habilitar y deshabilitar el periodo de muestreo """

    if self.main.tfdiscretocheckBox2.isChecked():
        self.main.tfperiodoEdit2.setEnabled(True)
    else:
        self.main.tfperiodoEdit2.setDisabled(True)


def PID_stacked_to_tf(self):
    """ Función para cambiar a función de transferencia """

    self.main.PIDstackedWidget.setCurrentIndex(0)
    self.main.GraphStakedTuning.setCurrentIndex(0)
    self.main.pidTiempoLabel.setText('Tiempo')
    self.main.pidLabelController.setText(
        "<html><head/><body><p><span style=\" font-size:12pt;\">PID = K</span><span style=\" font-size:12pt; vertical-align:sub;\">p </span><span style=\" font-size:12pt;\">* e(s) + K</span><span style=\" font-size:12pt; vertical-align:sub;\">i  </span><span style=\" font-size:12pt;\">/ s + K</span><span style=\" font-size:12pt; vertical-align:sub;\">d * </span><span style=\" font-size:12pt;\">N/(1 + s/N) </span></p></body></html>"
    )
    tf_habilitar_sliders_checkbox(self)
    update_gain_labels(self, resolution=self.tfSliderValue)


def tf_habilitar_sliders_checkbox(self):
    """ Función para habilitar ganancias antes y despues del auto tuning con función de transferencia """

    self.main.pidNSlider.setEnabled(True)
    self.main.pidTiempoSlider.setEnabled(True)

    if self.main.tfAutoTuningcheckBox2.isChecked():
        self.main.kpCheckBox2.setDisabled(True)
        self.main.kiCheckBox2.setDisabled(True)
        self.main.kdCheckBox2.setDisabled(True)
        self.main.kpHSlider2.setDisabled(True)
        self.main.kiHSlider2.setDisabled(True)
        self.main.kdHSlider2.setDisabled(True)
    else:
        self.main.kpCheckBox2.setEnabled(True)
        self.main.kiCheckBox2.setEnabled(True)
        self.main.kdCheckBox2.setEnabled(True)

        if self.main.kpCheckBox2.isChecked():
            self.main.kpHSlider2.setEnabled(True)
        else:
            self.main.kpHSlider2.setDisabled(True)

        if self.main.kiCheckBox2.isChecked():
            self.main.kiHSlider2.setEnabled(True)
        else:
            self.main.kiHSlider2.setDisabled(True)

        if self.main.kdCheckBox2.isChecked():
            self.main.kdHSlider2.setEnabled(True)
        else:
            self.main.kdHSlider2.setDisabled(True)


def PID_stacked_to_ss(self):
    """ Función para cambiar a ecuación de espacio de estados """

    self.main.PIDstackedWidget.setCurrentIndex(1)
    self.main.GraphStakedTuning.setCurrentIndex(0)
    self.main.pidTiempoLabel.setText('Tiempo')
    self.main.pidLabelController.setText(
        "<html><head/><body><p><span style=\" font-size:12pt;\">PID = K</span><span style=\" font-size:12pt; vertical-align:sub;\">p </span><span style=\" font-size:12pt;\">* e(s) + K</span><span style=\" font-size:12pt; vertical-align:sub;\">i  </span><span style=\" font-size:12pt;\">/ s + K</span><span style=\" font-size:12pt; vertical-align:sub;\">d * </span><span style=\" font-size:12pt;\">N/(1 + s/N) </span></p></body></html>"
    )
    ss_habilitar_sliders_checkbox(self)
    update_gain_labels(self, resolution=self.ssSliderValue)


def ss_habilitar_sliders_checkbox(self):
    """ Función para habilitar ganancias antes y despues del auto tuning con ecuación de espacio de estados """

    self.main.pidNSlider.setEnabled(True)
    self.main.pidTiempoSlider.setEnabled(True)

    if self.main.ssAutoTuningcheckBox2.isChecked():
        self.main.kpCheckBox2.setDisabled(True)
        self.main.kiCheckBox2.setDisabled(True)
        self.main.kdCheckBox2.setDisabled(True)
        self.main.kpHSlider2.setDisabled(True)
        self.main.kiHSlider2.setDisabled(True)
        self.main.kdHSlider2.setDisabled(True)
    else:
        self.main.kpCheckBox2.setEnabled(True)
        self.main.kiCheckBox2.setEnabled(True)
        self.main.kdCheckBox2.setEnabled(True)

        if self.main.kpCheckBox2.isChecked():
            self.main.kpHSlider2.setEnabled(True)
        else:
            self.main.kpHSlider2.setDisabled(True)

        if self.main.kiCheckBox2.isChecked():
            self.main.kiHSlider2.setEnabled(True)
        else:
            self.main.kiHSlider2.setDisabled(True)

        if self.main.kdCheckBox2.isChecked():
            self.main.kdHSlider2.setEnabled(True)
        else:
            self.main.kdHSlider2.setDisabled(True)


def actualizar_sliders_tf(self):
    """ Función para ajustar la resolución de los sliders con función de transferencia """
    self.tfSliderValue = self.main.tfreolutionSpin2.value()
    update_gain_labels(self, resolution=self.tfSliderValue)


def actualizar_sliders_ss(self):
    """ Función para ajustar la resolución de los sliders con ecuación de espacio de estados """
    self.ssSliderValue = self.main.ssreolutionSpin2.value()
    update_gain_labels(self, resolution=self.ssSliderValue)


def update_gain_labels(self, kp=0, ki=0, kd=0, autotuning=False, resolution=50):
    """
    Función para actualizar los labels que representan las ganancias, se ejecuta cada vez que un slider de ganancias cambia.
    
    :param kp: Ganancia proporcional, defaults to 0
    :type kp: float, opcional
    :param ki: Ganancia integral, defaults to 0
    :type ki: float, opcional
    :param kd: Ganancia derivativa, defaults to 0
    :type kd: float, opcional
    :param autotuning: Bandera para señalar si es o no una operación con autotunning, defaults to False
    :type autotuning: bool, opcional
    :param resolution: Resolución de los sliders, defaults to 50
    :type resolution: int, opcional
    """

    if autotuning:
        self.main.kpHSlider2.blockSignals(True)
        self.main.kiHSlider2.blockSignals(True)
        self.main.kdHSlider2.blockSignals(True)

        self.main.kpHSlider2.setValue(kp * resolution)
        self.main.kiHSlider2.setValue(ki * resolution)
        self.main.kdHSlider2.setValue(kd * resolution)

        self.main.kpHSlider2.blockSignals(False)
        self.main.kiHSlider2.blockSignals(False)
        self.main.kdHSlider2.blockSignals(False)

    self.main.kpValueLabel2.setText(str(np.around(self.main.kpHSlider2.value() / resolution, 3)))
    self.main.kiValueLabel2.setText(str(np.around(self.main.kiHSlider2.value() / resolution, 3)))
    self.main.kdValueLabel2.setText(str(np.around(self.main.kdHSlider2.value() / resolution, 3)))


def update_time_and_N_labels(self):
    """ Función para actualizar los labels que representan al tiempo y al valor N """
    self.main.pidTiempoLabelValue.setText(
        str(np.around(self.main.pidTiempoSlider.value(), 3)))
    self.main.pidNLabelValue.setText(str(np.around(self.main.pidNSlider.value(), 3)))


def PID_stacked_to_csv(self):
    """ Función para cambiar a csv """

    self.main.pidTiempoLabel.setText('t1')
    self.main.pidLabelController.setText("")
    self.main.PIDstackedWidget.setCurrentIndex(2)
    self.main.GraphStakedTuning.setCurrentIndex(1)
    self.main.kpCheckBox2.setDisabled(True)
    self.main.kiCheckBox2.setDisabled(True)
    self.main.kdCheckBox2.setDisabled(True)
    self.main.kpHSlider2.setDisabled(True)
    self.main.kiHSlider2.setDisabled(True)
    self.main.kdHSlider2.setDisabled(True)
    self.main.pidNSlider.setDisabled(True)

    if not self.GraphObjets:
        self.main.pidTiempoSlider.setDisabled(True)
    else:
        self.main.pidTiempoSlider.setEnabled(True)

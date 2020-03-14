""" Archivo que contiene todas las rutinas necesarias para la funcionalidad de tunning de PID """


from collections import deque
from scipy import real

import controlmdf as ctrl
import numpy as np

import json


def system_creator_tf(self, numerador, denominador):
    """
    Función para la creación del sistema a partir de los coeficientes del numerador y del denominador de la función de transferencia.
    
    :param numerador: Coeficientes del numerador
    :type numerador: list
    :param denominador: Coeficientes del denominador
    :type denominador: list
    """

    if not self.main.tfdiscretocheckBox2.isChecked(
    ) and self.main.tfdelaycheckBox2.isChecked():
        delay = json.loads(self.main.tfdelayEdit2.text())
    else:
        delay = 0

    system = ctrl.TransferFunction(numerador, denominador, delay=delay)

    if self.main.kpCheckBox2.isChecked():
        kp = self.main.kpHSlider2.value() / self.tfSliderValue
    else:
        kp = 0
    if self.main.kiCheckBox2.isChecked():
        ki = self.main.kiHSlider2.value() / self.tfSliderValue
    else:
        ki = 0
    if self.main.kdCheckBox2.isChecked():
        kd = self.main.kdHSlider2.value() / self.tfSliderValue
    else:
        kd = 0

    t = self.main.pidTiempoSlider.value()

    # En caso de que el sistema sea discreto
    if self.main.tfdiscretocheckBox2.isChecked():
        pid = ctrl.TransferFunction([
            2*kd + 2 * self.dt * kp + ki * self.dt**2,
            -2 * self.dt * kp - 4*kd + ki * self.dt**2,
            2 * kd
        ], [2 * self.dt, -2 * self.dt, 0],
                                    self.dt)

        system = ctrl.sample_system(system, self.dt, self.main.tfcomboBox2.currentText())

        if self.main.tfdelaycheckBox2.isChecked():
            delayV = [0] * (int(json.loads(self.main.tfdelayEdit2.text()) / self.dt) + 1)
            delayV[0] = 1
            system_delay = system * ctrl.TransferFunction([1], delayV, self.dt)
            system_delay = ctrl.feedback(pid * system_delay)
        else:
            system_delay = None

        system = ctrl.feedback(pid * system)
    else:
        system_delay = system

    try:
        if ctrl.isdtime(system, strict=True):
            T = np.arange(0, t+self.dt, self.dt)
        else:
            T = np.arange(0, t+0.05, 0.05)

    except ValueError:
        T = np.arange(0, 100, 0.05)

    return system, T, system_delay, kp, ki, kd


def system_creator_ss(self, A, B, C, D):
    """
    Función para la creación del sistema a partir de la matriz de estado, matriz de entrada, matriz de salida y la matriz de transmisión directa.
    
    :param A: Matriz de estados
    :type A: list
    :param B: Matriz de entrada
    :type B: list
    :param C: Matriz de salida
    :type C: list
    :param D: Matriz de transmisión directa
    :type D: list
    """

    if not self.main.ssdiscretocheckBox2.isChecked(
    ) and self.main.ssdelaycheckBox2.isChecked():
        delay = json.loads(self.main.ssdelayEdit2.text())
    else:
        delay = 0

    system = ctrl.StateSpace(A, B, C, D, delay=delay)

    if self.main.kpCheckBox2.isChecked():
        kp = self.main.kpHSlider2.value() / self.ssSliderValue
    else:
        kp = 0
    if self.main.kiCheckBox2.isChecked():
        ki = self.main.kiHSlider2.value() / self.ssSliderValue
    else:
        ki = 0
    if self.main.kdCheckBox2.isChecked():
        kd = self.main.kdHSlider2.value() / self.ssSliderValue
    else:
        kd = 0

    t = self.main.pidTiempoSlider.value()

    # En caso de que el sistema sea discreto
    if self.main.ssdiscretocheckBox2.isChecked():
        pid = ctrl.TransferFunction([
            2*kd + 2 * self.dt * kp + ki * self.dt**2,
            -2 * self.dt * kp - 4*kd + ki * self.dt**2,
            2 * kd
        ], [2 * self.dt, -2 * self.dt, 0],
                                    self.dt)

        system = ctrl.sample_system(system, self.dt, self.main.sscomboBox2.currentText())

        system_ss = system
        system = ctrl.ss2tf(system)

        if self.main.ssdelaycheckBox2.isChecked():
            delayV = [0] * (int(json.loads(self.main.ssdelayEdit2.text()) / self.dt) + 1)
            delayV[0] = 1
            system_delay = system * ctrl.TransferFunction([1], delayV, self.dt)
            system_delay = ctrl.feedback(pid * system_delay)
        else:
            system_delay = None

        system = ctrl.feedback(pid * system)
    else:
        system_ss = system
        system = ctrl.ss2tf(system)
        system_delay = None

    try:
        if ctrl.isdtime(system, strict=True):
            T = np.arange(0, t+self.dt, self.dt)
        else:
            T = np.arange(0, t+0.05, 0.05)

    except ValueError:
        T = np.arange(0, 100, 0.05)

    return system, T, system_delay, system_ss, kp, ki, kd


def system_creator_tf_tuning(self, numerador, denominador):
    """
    Función para la creación del sistema a partir de los coeficientes del numerador y del denominador de la función de transferencia, adicionalmente se realiza el auto tuning utilizando el método escogido por el usuario.
    
    :param A: Matriz de estados
    :type A: list
    :param B: Matriz de entrada
    :type B: list
    :param C: Matriz de salida
    :type C: list
    :param D: Matriz de transmisión directa
    :type D: list
    """

    if not self.main.tfdiscretocheckBox2.isChecked(
    ) and self.main.tfdelaycheckBox2.isChecked():
        delay = json.loads(self.main.tfdelayEdit2.text())
    else:
        delay = 0

    system = ctrl.TransferFunction(numerador, denominador, delay=delay)

    t = self.main.pidTiempoSlider.value()
    T = np.arange(0, t, 0.05)
    U = np.ones_like(T)

    t_temp, y, _ = ctrl.forced_response(system, T, U)
    dc_gain = ctrl.dcgain(system)

    # Parametros del modelo
    K_proceso, tau, alpha = model_method(self, t_temp, y, dc_gain)

    # Auto tunning
    try:
        kp, ki, kd = auto_tuning_method(self, K_proceso, tau, alpha, self.main.tfAutoTuningcomboBox2.currentText())
    except TypeError:
        raise TypeError('Alfa es muy pequeño')

    # En caso de que el sistema sea discreto
    if self.main.tfdiscretocheckBox2.isChecked():
        pid = ctrl.TransferFunction([
            2*kd + 2 * self.dt * kp + ki * self.dt**2,
            -2 * self.dt * kp - 4*kd + ki * self.dt**2,
            2 * kd
        ], [2 * self.dt, -2 * self.dt, 0],
                                    self.dt)

        system = ctrl.sample_system(system, self.dt, self.main.tfcomboBox2.currentText())

        if self.main.tfdelaycheckBox2.isChecked():
            delayV = [0] * (int(json.loads(self.main.tfdelayEdit2.text()) / self.dt) + 1)
            delayV[0] = 1
            system_delay = system * ctrl.TransferFunction([1], delayV, self.dt)
            system_delay = ctrl.feedback(pid * system_delay)
        else:
            system_delay = None

        system = ctrl.feedback(pid * system)
    else:
        system_delay = system

    try:
        if ctrl.isdtime(system, strict=True):
            T = np.arange(0, t+self.dt, self.dt)
        else:
            T = np.arange(0, t+0.05, 0.05)

    except ValueError:
        T = np.arange(0, 100, 0.05)

    return system, T, system_delay, kp, ki, kd


def system_creator_ss_tuning(self, A, B, C, D):
    """
    Función para la creación del sistema a partir de la matriz de estado, matriz de entrada, matriz de salida y la matriz de transmisión directa, adicionalmente se realiza el auto tuning utilizando el método escogido por el usuario.
    
    :param A: Matriz de estados
    :type A: list
    :param B: Matriz de entrada
    :type B: list
    :param C: Matriz de salida
    :type C: list
    :param D: Matriz de transmisión directa
    :type D: list
    """

    if not self.main.ssdiscretocheckBox2.isChecked(
    ) and self.main.ssdelaycheckBox2.isChecked():
        delay = json.loads(self.main.ssdelayEdit2.text())
    else:
        delay = 0

    system = ctrl.StateSpace(A, B, C, D, delay=delay)

    t = self.main.pidTiempoSlider.value()
    T = np.arange(0, t, 0.05)
    U = np.ones_like(T)

    t_temp, y, _ = ctrl.forced_response(system, T, U)
    dc_gain = ctrl.dcgain(system)

    # Parametros del modelo
    K_proceso, tau, alpha = model_method(self, t_temp, y, dc_gain)

    # Auto tunning
    try:
        kp, ki, kd = auto_tuning_method(self, K_proceso, tau, alpha, self.main.ssAutoTuningcomboBox2.currentText())
    except TypeError:
        raise TypeError('Alfa es muy pequeño')

    # En caso de que el sistema sea discreto
    if self.main.ssdiscretocheckBox2.isChecked():
        pid = ctrl.TransferFunction([
            2*kd + 2 * self.dt * kp + ki * self.dt**2,
            -2 * self.dt * kp - 4*kd + ki * self.dt**2,
            2 * kd
        ], [2 * self.dt, -2 * self.dt, 0],
                                    self.dt)

        system = ctrl.sample_system(system, self.dt, self.main.sscomboBox2.currentText())

        if self.main.ssdelaycheckBox2.isChecked():
            delayV = [0] * (int(json.loads(self.main.ssdelayEdit2.text()) / self.dt) + 1)
            delayV[0] = 1
            system_delay = system * ctrl.TransferFunction([1], delayV, self.dt)
            system_delay = ctrl.feedback(pid * system_delay)
        else:
            system_delay = None

        system_ss = system
        system = ctrl.feedback(pid * system)
    else:
        system_ss = system
        system_delay = system

    try:
        if ctrl.isdtime(system, strict=True):
            T = np.arange(0, t+self.dt, self.dt)
        else:
            T = np.arange(0, t+0.05, 0.05)

    except ValueError:
        T = np.arange(0, 100, 0.05)

    return system, T, system_delay, system_ss, kp, ki, kd


def model_method(self, t, y, dc_gain):
    """
    Función para obtener los parametros del modelo de primer orden de un sistema a partir de su respuesta escalón.
    
    :param t: Vector de tiempo
    :type t: numpyArray
    :param y: Vector de respuesta
    :type y: numpyArray
    :param dc_gain: Ganancia DC del sistema
    :type dc_gain: float
    """

    i_max = np.argmax(np.abs(np.gradient(y)))

    for index, i in enumerate(y):
        if i >= 0.63 * dc_gain:
            indexv = index
            break

    slop = (y[i_max] - y[i_max - 1]) / (t[i_max] - t[i_max - 1])
    x1 = (0 - y[i_max]) / (slop) + t[i_max]
    x2 = t[indexv]
    y2 = slop * (x2 - t[i_max]) + y[i_max]

    tau = x2 - x1

    if self.main.tfdelaycheckBox2.isChecked():
        alpha = x1 + json.loads(self.main.tfdelayEdit2.text())
    else:
        alpha = x1

    K_proceso = y[-1] / 1

    return K_proceso, tau, alpha


def auto_tuning_method(self, k_proceso, tau, alpha, metodo):
    """
    Función para obtener las ganancias del controlador PID a partir de los parametros del modelo de primer orden obtenidos de una respuesta escalón, las formulas son las dadas por Ziegler-Nichols y Cohen-Coon para una respuesta escalón en lazo abierto.
    
    :param k_proceso: Ganancia del proceso
    :type k_proceso: float
    :param tau: Constante de tiempo del proceso
    :type tau: float
    :param alpha: Tiempo muerto o delay del proceso
    :type alpha: float
    :param metodo: Método a utilizar
    :type metodo: str
    """

    if alpha <= 0.05:
        print('Alfa es demasiado pequeño')
        raise TypeError(' Alfa es demasiado pequeño')

    if 'ZN' in metodo:
        if 'P--' in metodo:
            kp = (1/k_proceso) * (tau/alpha)
            ti = np.infty
            td = 0

            self.main.kpCheckBox2.setChecked(True)
            self.main.kiCheckBox2.setChecked(False)
            self.main.kdCheckBox2.setChecked(False)

        if 'PI-' in metodo:
            kp = (0.9/k_proceso) * (tau/alpha)
            ti = alpha * 3.33
            td = 0

            self.main.kpCheckBox2.setChecked(True)
            self.main.kiCheckBox2.setChecked(True)
            self.main.kdCheckBox2.setChecked(False)

        if 'PID' in metodo:
            kp = (1.2/k_proceso) * (tau/alpha)
            ti = alpha * 2
            td = alpha * 0.5

            self.main.kpCheckBox2.setChecked(True)
            self.main.kiCheckBox2.setChecked(True)
            self.main.kdCheckBox2.setChecked(True)

        kp = kp
        ki = kp / ti
        kd = kp * td

    if 'CC' in metodo:
        if 'P--' in metodo:
            kp = (1/k_proceso) * (tau/alpha) * (1 + (1/3) * (alpha/tau))
            ti = np.infty
            td = 0

            self.main.kpCheckBox2.setChecked(True)
            self.main.kiCheckBox2.setChecked(False)
            self.main.kdCheckBox2.setChecked(False)

        if 'PI-' in metodo:
            kp = (1/k_proceso) * (tau/alpha) * (0.9 + (1/12) * (alpha/tau))
            ti = alpha * ((30 + 3 * (alpha/tau)) / (9 + 20 * (alpha/tau)))
            td = 0

            self.main.kpCheckBox2.setChecked(True)
            self.main.kiCheckBox2.setChecked(True)
            self.main.kdCheckBox2.setChecked(False)

        if 'PD-' in metodo:
            kp = ((1/k_proceso) * (tau/alpha) * ((5/4) + (1/6) * (alpha/tau)))
            ti = np.infty
            td = alpha * ((6 - 2 * (alpha/tau)) / (22 + 3 * (alpha/tau)))

            self.main.kpCheckBox2.setChecked(True)
            self.main.kiCheckBox2.setChecked(False)
            self.main.kdCheckBox2.setChecked(True)

        if 'PID' in metodo:
            kp = ((1/k_proceso) * (tau/alpha) * ((4/3) + (1/4) * (alpha/tau)))
            ti = alpha * ((32 + 6 * (alpha/tau)) / (13 + 8 * (alpha/tau)))
            td = alpha * (4 / (11 + 2 * (alpha/tau)))

            self.main.kpCheckBox2.setChecked(True)
            self.main.kiCheckBox2.setChecked(True)
            self.main.kdCheckBox2.setChecked(True)

        kp = kp / 2
        ki = kp / ti
        kd = kp * td

    return kp, ki, kd


def rutina_step_plot(self, system, T, kp, ki, kd):
    """
    Función para obtener la respuesta escalón del sistema en lazo cerrado en combinación con un controlador PID y su respectiva graficacion.
    
    :param system: Representacion del sistema
    :type system: LTI
    :param T: Vector de tiempo
    :type T: numpyArray
    :param kp: Ganancia proporcional
    :type kp: float
    :param ki: Ganancia integral
    :type ki: float
    :param kd: Ganancia derivativa
    :type kd: float
    """

    U = np.ones_like(T)

    # Discriminación entre continue y discreto, con delay o sin delay, delay realizado con pade
    if ctrl.isdtime(system, strict=True):
        t, y, _ = ctrl.forced_response(system, T, U)
    elif (
        self.main.tfdelaycheckBox2.isChecked() and
        self.main.PIDstackedWidget.currentIndex() == 0
    ):
        pade = ctrl.TransferFunction(
            *ctrl.pade(json.loads(self.main.tfdelayEdit2.text()), 10)
        )
        N = self.main.pidNSlider.value()
        pid = ctrl.TransferFunction([N*kd+kp, N*kp+ki, N*ki], [1, N, 0])
        system = ctrl.feedback(pid * system * pade)
        t, y, _ = ctrl.forced_response(system, T, U)
    elif (
        self.main.ssdelaycheckBox2.isChecked() and
        self.main.PIDstackedWidget.currentIndex() == 1
    ):
        pade = ctrl.TransferFunction(
            *ctrl.pade(json.loads(self.main.ssdelayEdit2.text()), 10)
        )
        N = self.main.pidNSlider.value()
        pid = ctrl.TransferFunction([N*kd+kp, N*kp+ki, N*ki], [1, N, 0])
        system = ctrl.feedback(pid * system * pade)
        t, y, _ = ctrl.forced_response(system, T, U)
    else:
        N = self.main.pidNSlider.value()
        pid = ctrl.TransferFunction([N*kd + kp, N*kp + ki, N * ki], [1, N, 0])
        system = ctrl.feedback(pid * system)
        t, y, _ = ctrl.forced_response(system, T, U)

    if ctrl.isdtime(system, strict=True):
        y = y[0]
        y = np.clip(y, -1e12, 1e12)
        self.main.stepGraphicsView2.curva.setData(t, y[:-1], stepMode=True)
    else:
        y = np.clip(y, -1e12, 1e12)
        self.main.stepGraphicsView2.curva.setData(t, y, stepMode=False)

    return t, y


def rutina_system_info(self, system, T, y, kp=0, ki=0, kd=0, autotuning=False):
    """
    Función para mostrar los resultados obtenidos de los calculos en un TextEdit
    
    :param system: Representacion del sistema
    :type system: LTI
    :param T: Vector de tiempo
    :type T: numpyArray
    :param y: Vector de respuesta
    :type y: numpyArray
    :param kp: Ganancia proporcional, defaults to 0
    :type kp: float, opcional
    :param ki: Ganancia integral, defaults to 0
    :type ki: float, opcional
    :param kd: Ganancia derivativa, defaults to 0
    :type kd: float, opcional
    :param autotuning: Bandera para señalar si es o no una operación con auto tunning, defaults to False
    :type autotuning: bool, opcional
    """

    # Informacion del step
    try:
        info = ctrl.step_info(system, T=T, yout=y)
    except:
        info = {
            'RiseTime':np.NaN,
            'SettlingTime':np.NaN,
            'SettlingMax': np.NaN,
            'SettlingMin': np.NaN,
            'Overshoot': np.NaN,
            'Undershoot': np.NaN,
            'Peak': np.NaN,
            'PeakTime': np.NaN,
            'SteadyStateValue': np.NaN
        }

    Datos = ""

    Datos += str(system) + "\n"

    if self.main.tfdelaycheckBox2.isChecked() and self.main.PIDstackedWidget.currentIndex(
    ) == 0:
        delay = json.loads(self.main.tfdelayEdit2.text())
        Datos += f"Delay: {delay}\n"
    elif self.main.ssdelaycheckBox2.isChecked(
    ) and self.main.PIDstackedWidget.currentIndex() == 1:
        delay = json.loads(self.main.ssdelayEdit2.text())
        Datos += f"Delay: {delay}\n"
    else:
        delay = 0

    Datos += "----------------------------------------------\n"

    for k, v in info.items():
        Datos += f"{k} : {v:5.3f}\n"

    dcgain = ctrl.dcgain(system)
    Datos += f"Ganancia DC: {real(dcgain):5.3f}\n"

    if autotuning:
        Datos += "----------------------------------------------\n"
        Datos += f"Kp: {kp:.4f}\n"
        Datos += f"Ki: {ki:.4f}\n"
        Datos += f"Kd: {kd:.4f}\n"

    if self.main.PIDstackedWidget.currentIndex() == 0:
        self.main.tfdatosTextEdit2.setPlainText(Datos)
    else:
        self.main.ssdatosTextEdit2.setPlainText(Datos)

""" 
Archivo que contiene la clase SimpleThread la cual ejecuta la simulación de sistemas de control en hilo diferente al principal, esto se realiza de esta forma debido a que la simulación puede tardar en algunos casos varios segundos, de ejecutarse en el hilo principal presentaria un comportamiento de bloqueo en la ventana principal 
"""


from rutinas.rutinas_fuzzy import FuzzyController
from rutinas.rutinas_fuzzy import FISParser
from rutinas.discreto_sim import ss_discreta, PID_discreto, derivadas_discretas
from collections import deque
from PySide2 import QtCore

import controlmdf as ctrl
import numpy as np

import copy
import json


class SimpleThread(QtCore.QThread):
    """
    Clase para realizar la simulación de sistemas de control en un hilo diferente al principal
    
    :param QThread: Clase para crear un hilo paralelo al principal
    :type QThread: ObjectType
    """

    finished = QtCore.Signal(object, list)
    update_progresBar = QtCore.Signal(object, float)
    error_gui = QtCore.Signal(object, int)

    def __init__(self, window, regresar, update_bar, error_gui, list_info, parent=None):
        """
        Constructor para recibir las variables y funciones del hilo principal
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param regresar: Función a la que regresa una vez terminada la simulación, plot_final_results de simulacionHandler.py
        :type regresar: function
        :param update_bar: Función para actualizar la barra de progreso, update_progresBar_function de simulacionHandler.py
        :type update_bar: function
        :param error_gui: Función para mostrar los errores ocurridos durante la simulación, error_gui de simulacionHandler.py
        :type error_gui: function
        :param list_info: Lista con toda la información necesaria
        :type list_info: list
        :param parent: Sin efecto, defaults to None
        :type parent: NoneType, opcional
        """

        QtCore.QThread.__init__(self, parent)

        self.window = window
        self.window.main.principalTab.setDisabled(True)
        self.window.main.progressBar.show()
        self.finished.connect(regresar)
        self.update_progresBar.connect(update_bar)
        self.error_gui.connect(error_gui)
        self.list_info = copy.deepcopy(list_info)

        self.esquema = self.list_info[0]
        self.system = self.list_info[1]
        self.Tiempo = self.list_info[2]
        self.dt = self.list_info[3]
        self.escalon = self.list_info[4]
        self.sensor_flag = self.list_info[5]
        self.accionador_flag = self.list_info[6]
        self.saturador_flag = self.list_info[7]
        self.kp, self.ki, self.kd, self.N = map(float, self.list_info[8])
        self.fuzzy_path1, self.fuzzy_path2 = self.list_info[9]
        self.rk_base = self.list_info[10]
        self.metodo_adaptativo = self.list_info[11]
        self.solver_configuration = self.list_info[12]
        self.flag_filtro = self.list_info[13]

    def stop(self):
        """ Función para detener el hilo """
        self._isRunning = False

    def run(self):
        """ Función a ejecutar cuando se hace el llamado a self.start() """

        # PID Clásico
        if self.esquema in [0]:
            try:
                Tiempo, y, sc, u = self.run_pid()
                self.finished.emit(
                    self.window,
                    [Tiempo, y, sc, u, ctrl.isdtime(self.system, strict=True)])
                self.stop()
            except:
                self.error_gui.emit(self.window, 0)
                self.stop()

        # Esquemas difusos
        if self.esquema in [1,2,3,4,5,6,7,8]:
            try:
                Tiempo, y, sc, u = self.run_fuzzy()
                self.finished.emit(
                    self.window,
                    [Tiempo, y, sc, u, ctrl.isdtime(self.system, strict=True)])
                self.stop()

            except IndexError:
                self.error_gui.emit(self.window, 1)
                self.stop()

            except AssertionError:
                self.error_gui.emit(self.window, 2)
                self.stop()

    def run_pid(self):
        """ 
        Función para realizar la simulación de sistemas de control con controlador PID clásico
        
        :return: Respuesta obtenida en la simulación dividida en vector de tiempo, vector de salida, vector de la señal de control y vector del setpoint
        :rtype: tuple(list[float], deque[float], deque[float], list[float])
        """

        # Captura de las ganancias
        if self.window.main.kpCheck.isChecked():
            kp = float(self.kp)
        else:
            kp = 0.0

        if self.window.main.kiCheck.isChecked():
            ki = float(self.ki)
        else:
            ki = 0.0

        if self.window.main.kdCheck.isChecked():
            kd = float(self.kd)
        else:
            kd = 0.0

        # Transformando a ecuaciones de espacio de estados en caso de que sea función de transferencia
        if isinstance(self.system, ctrl.TransferFunction):
            self.system = ctrl.tf2ss(self.system)

        x = np.zeros_like(self.system.B).astype('float64')
        system = self.system.A.astype('float64'), self.system.B.astype('float64'), self.system.C.astype('float64'), self.system.D.astype('float64')
        
        tiempo_total = self.Tiempo
        tiempo = 0

        if isinstance(self.escalon, float):
            # Escalón simple
            u = self.escalon
            max_tiempo = [self.Tiempo]
        else:
            # Escalón avanzado
            it = iter(self.escalon)
            u_value = deque([0])
            max_tiempo = []
            for i, valor in enumerate(it):
                max_tiempo.append(next(it))
                u_value.append(valor)
            index_tbound = len(max_tiempo)
            max_tiempo.append(tiempo_total)

            # Necesario para evitar tamaños de paso excesivos dado el algoritmo adaptativo
            if ctrl.isdtime(self.system, strict=True):
                tiempo += max_tiempo[0] - self.dt - self.dt/10
            else:
                tiempo += max_tiempo[0] - 0.0000011

        # Representacion del 20% de la simulación
        porcentajeBar = int(tiempo_total * 33 / 100)
        if porcentajeBar == 0:
            porcentajeBar = 1

        h = 0.000001  # Tamaño de paso inicial
        salida = deque([0])  # Lista de salida, se utiliza deque para mejorar la velocidad
        sc_f = deque([0])  # Lista de la señal de control, se utiliza deque para mejorar la velocidad
        sc_t = 0.0  # Señal de control cambiante
        si_t = 0.0  # Acumulador de la señal integral

        # Distinción entre continuo y discreto
        if ctrl.isdtime(self.system, strict=True):
            error_a = np.asarray([0.0, 0.0])
            solve = ss_discreta
            PIDf = PID_discreto
            h_new = self.dt
            h = self.dt
        else:
            error_a = np.asarray([0.0, 0.0])
            solve = self.rk_base
            PIDf = self.metodo_adaptativo

        # En caso de que se habilite el accionador
        if self.accionador_flag:
            acc_num = json.loads(self.window.main.numAccionador.text())
            acc_dem = json.loads(self.window.main.demAccionador.text())
            acc_system = ctrl.TransferFunction(acc_num, acc_dem, delay=0)
            
            if ctrl.isdtime(
                    self.system, strict=True
            ) and self.window.main.SimulacionstackedWidget.currentIndex() == 0:
                acc_system = ctrl.sample_system(
                    acc_system, self.dt, self.window.main.tfcomboBox4.currentText())
            elif ctrl.isdtime(self.system, strict=True):
                acc_system = ctrl.sample_system(
                    acc_system, self.dt, self.window.main.sscomboBox4.currentText())

            acc_system = ctrl.tf2ss(acc_system)
            acc_x = np.zeros_like(acc_system.B).astype('float64')
            acc_system = acc_system.A.astype('float64'), acc_system.B.astype('float64'), acc_system.C.astype('float64'), acc_system.D.astype('float64')

        # En caso de que se habilite el saturador
        if self.saturador_flag:
            lim_inferior = float(self.window.main.inferiorSaturador.text())
            lim_superior = float(self.window.main.superiorSaturador.text())

        # En caso de que se habilite el sensor
        if self.sensor_flag:
            sensor_num = json.loads(self.window.main.numSensor.text())
            sensor_dem = json.loads(self.window.main.demSensor.text())
            sensor_system = ctrl.TransferFunction(sensor_num, sensor_dem, delay=0)
            
            if ctrl.isdtime(
                    self.system, strict=True
            ) and self.window.main.SimulacionstackedWidget.currentIndex() == 0:
                sensor_system = ctrl.sample_system(
                    sensor_system, self.dt, self.window.main.tfcomboBox4.currentText())
            elif ctrl.isdtime(self.system, strict=True):
                sensor_system = ctrl.sample_system(
                    sensor_system, self.dt, self.window.main.sscomboBox4.currentText())
            
            sensor_system = ctrl.tf2ss(sensor_system)
            sensor_x = np.zeros_like(sensor_system.B).astype('float64')
            sensor_system = sensor_system.A.astype('float64'), sensor_system.B.astype('float64'), sensor_system.C.astype('float64'), sensor_system.D.astype('float64')
            salida2 = deque([0])

        if self.N*kd == 0:
            # N debe mantenerse debido al algoritmo utilizado por la libreria de control para llevar de función
			# de transferencia a ecuaciones de espacio de estados
            # Controlador PID con la forma:
            #    PID = kp + ki/s + (kd*N*s/(s + N))

            self.N = 50
            kd = 0.0
            pid = ctrl.tf2ss(ctrl.TransferFunction(
                    [self.N * kd + kp, self.N * kp + ki, self.N * ki], [1, self.N, 0]))

        elif not self.flag_filtro:
            # Controlador PID con la forma:
            #    PID = kp + ki/s + (kd*N*s/(s + N))

            pid = ctrl.tf2ss(ctrl.TransferFunction(
                    [self.N * kd + kp, self.N * kp + ki, self.N * ki], [1, self.N, 0]))

        else:
            # Controlador PID con la forma:
            #    PID = kp + ki/s + (kd*N*s/(s + N))*(1/(10/(N*kd) + 1))

            pid = ctrl.tf2ss(
                ctrl.TransferFunction([
                    10 * kp,
                    self.N**2 * kd**2 + self.N * kd * kp + 10 * self.N * kp + 10*ki,
                    self.N**2 * kd * kp + kd * self.N * ki + 10 * self.N * ki,
                    self.N**2 * kd * ki
                ], [10, 10 * self.N + self.N * kd, self.N**2 * kd, 0]))

        x_pid = np.zeros_like(pid.B).astype('float64')
        pid = pid.A.astype('float64'), pid.B.astype('float64'), pid.C.astype('float64'), pid.D.astype('float64')

        i = 0
        setpoint_window = 0
        Tiempo_list = [0]
        setpoint = [0]

        # Inicio de la simulación
        while tiempo < tiempo_total:

            # Para alternar los valores del setpoint avanzado
            if not isinstance(self.escalon, float):
                if tiempo + h >= max_tiempo[
                        setpoint_window] and setpoint_window < index_tbound:
                    setpoint_window += 1
                u = u_value[setpoint_window]

            # Calculo del error
            error = u - salida[i]
            
            # Distinción de PID entre continuo y discreto
            if ctrl.isdtime(self.system, strict=True):
                sc_t, si_t, error_a = PIDf(error, h, si_t, error_a, kp, ki, kd)
            else:
                h, h_new, sc_t, x_pid = PIDf(pid, h, tiempo, max_tiempo[setpoint_window], x_pid, error, *self.solver_configuration)

            # En caso de que se habilite el accionador
            if self.accionador_flag:
                sc_t, acc_x = solve(*acc_system, acc_x, h, sc_t)

            # En caso de que se habilite el saturador
            if self.saturador_flag:
                sc_t = min(max(sc_t, lim_inferior), lim_superior)

            # Salida del sistema
            y, x = solve(*system, x, h, sc_t)

            # Acumulación de la señal de control
            sc_f.append(sc_t)

            # En caso de que se habilite el sensor
            if self.sensor_flag:
                salida2.append(y)
                y, sensor_x = solve(*sensor_system, sensor_x, h, salida2[-1])

            # Acumulación de la salida
            salida.append(y)

            # Actualizacion de la barra de progreso cada 20% de avance
            if int(tiempo) % porcentajeBar == 0:
                self.update_progresBar.emit(self.window, int(tiempo) * 100 / tiempo_total)

            # Acumulación del setpoint
            setpoint.append(u)

            # Acumulación del tiempo
            tiempo +=h
            Tiempo_list.append(tiempo)
            h = h_new
            i +=1

        # En caso de que se habilite el sensor
        if self.sensor_flag:
            salida = salida2

        return copy.deepcopy(Tiempo_list), copy.deepcopy(salida), copy.deepcopy(sc_f), copy.deepcopy(setpoint)

    def run_fuzzy(self):
        """ 
        Función para realizar la simulación de sistemas de control de esquemas difusos
        
        :return: Respuesta obtenida en la simulación dividida en vector de tiempo, vector de salida, vector de la señal de control y vector del setpoint
        :rtype: tuple(list[float], deque[float], deque[float], list[float])
        
        """

        # Captura de las ganancias
        if self.window.main.kpCheck.isChecked():
            kp = float(self.kp)
        else:
            kp = 0.0

        if self.window.main.kiCheck.isChecked():
            ki = float(self.ki)
        else:
            ki = 0.0

        if self.window.main.kdCheck.isChecked():
            kd = float(self.kd)
        else:
            kd = 0.0

        # Creación del controlador difuso
        if len(self.fuzzy_path1) > 1 and self.esquema in [1, 2, 3, 4, 5, 6, 7, 8]:
            if '.json' in self.fuzzy_path1:
                with open(self.fuzzy_path1, "r") as f:
                    InputList1, OutputList1, RuleEtiquetas1 = json.load(f)
            else:
                temp_parser = FISParser(self.fuzzy_path1)
                try:
                    InputList1, OutputList1, RuleEtiquetas1 = temp_parser.fis_to_json()
                except TypeError:
                    raise IndexError

            try:
                controlador_validator(self, self.esquema, InputList1, OutputList1, RuleEtiquetas1)
            except AssertionError:
                raise AssertionError

            fuzzy_c1 = FuzzyController(InputList1, OutputList1, RuleEtiquetas1)

        # Creación del controlador difuso 2 (PD)
        if len(self.fuzzy_path2) > 1 and self.esquema in [4]:
            if '.json' in self.fuzzy_path2:
                with open(self.fuzzy_path2, "r") as f:
                    InputList2, OutputList2, RuleEtiquetas2 = json.load(f)
            else:
                temp_parser = FISParser(self.fuzzy_path2)
                try:
                    InputList2, OutputList2, RuleEtiquetas2 = temp_parser.fis_to_json()
                except TypeError:
                    raise IndexError

            try:
                controlador_validator(self, self.esquema, InputList2, OutputList2, RuleEtiquetas2)
            except AssertionError:
                raise AssertionError

            fuzzy_c2 = FuzzyController(InputList2, OutputList2, RuleEtiquetas2)

        # Transformando a ecuaciones de espacio de estados en caso de que sea función de transferencia
        if isinstance(self.system, ctrl.TransferFunction):
            self.system = ctrl.tf2ss(self.system)

        x = np.zeros_like(self.system.B).astype('float64')
        system = self.system.A.astype('float64'), self.system.B.astype('float64'), self.system.C.astype('float64'), self.system.D.astype('float64')

        tiempo_total = self.Tiempo
        tiempo = 0

        if isinstance(self.escalon, float):
            # Escalón simple
            u = self.escalon
            max_tiempo = [self.Tiempo]
        else:
            # Escalón avanzado
            it = iter(self.escalon)
            u_value = deque([0])
            max_tiempo = []
            for i, valor in enumerate(it):
                max_tiempo.append(next(it))
                u_value.append(valor)
            index_tbound = len(max_tiempo)
            max_tiempo.append(tiempo_total)

            # Necesario para evitar tamaños de paso excesivos dado el algoritmo adaptativo
            if ctrl.isdtime(self.system, strict=True):
                tiempo += max_tiempo[0] - self.dt - self.dt/10
            else:
                tiempo += max_tiempo[0] - 0.0000011

        # Representacion del 20% de la simulación
        porcentajeBar = int(tiempo_total * 20 / 100)
        if porcentajeBar == 0:
            porcentajeBar = 1

        h = 0.000001  # Tamaño de paso inicial
        salida = deque([0])  # Lista de salida, se utiliza deque para mejorar la velocidad
        sc_f = deque([0])  # Lista de la señal de control, se utiliza deque para mejorar la velocidad
        sc_t = 0.0  # Señal de control cambiante
        si_t = 0.0  # Acumulador de la señal integral

        # Distinción entre continuo y discreto
        if ctrl.isdtime(self.system, strict=True):
            error_a = np.asarray([0.0, 0.0])
            solve = ss_discreta
            PIDf = PID_discreto
            h_new = self.dt
            h = self.dt
        else:
            error_a = np.asarray([0.0, 0.0])
            solve = self.rk_base
            PIDf = self.metodo_adaptativo

        # En caso de que se habilite el accionador
        if self.accionador_flag:
            acc_num = json.loads(self.window.main.numAccionador.text())
            acc_dem = json.loads(self.window.main.demAccionador.text())
            acc_system = ctrl.tf2ss(ctrl.TransferFunction(acc_num, acc_dem, delay=0))
            if ctrl.isdtime(
                    self.system, strict=True
            ) and self.window.main.SimulacionstackedWidget.currentIndex() == 0:
                acc_system = ctrl.sample_system(
                    acc_system, self.dt, self.window.main.tfcomboBox4.currentText())
            elif ctrl.isdtime(self.system, strict=True):
                acc_system = ctrl.sample_system(
                    acc_system, self.dt, self.window.main.sscomboBox4.currentText())

            acc_x = np.zeros_like(acc_system.B).astype('float64')
            acc_system = acc_system.A.astype('float64'), acc_system.B.astype('float64'), acc_system.C.astype('float64'), acc_system.D.astype('float64')

        # En caso de que se habilite el saturador
        if self.saturador_flag:
            lim_inferior = float(self.window.main.inferiorSaturador.text())
            lim_superior = float(self.window.main.superiorSaturador.text())

        # En caso de que se habilite el sensor
        if self.sensor_flag:
            sensor_num = json.loads(self.window.main.numSensor.text())
            sensor_dem = json.loads(self.window.main.demSensor.text())
            sensor_system = ctrl.tf2ss(
                ctrl.TransferFunction(sensor_num, sensor_dem, delay=0))
            if ctrl.isdtime(
                    self.system, strict=True
            ) and self.window.main.SimulacionstackedWidget.currentIndex() == 0:
                sensor_system = ctrl.sample_system(
                    sensor_system, self.dt, self.window.main.tfcomboBox4.currentText())
            elif ctrl.isdtime(self.system, strict=True):
                sensor_system = ctrl.sample_system(
                    sensor_system, self.dt, self.window.main.sscomboBox4.currentText())
            
            sensor_x = np.zeros_like(sensor_system.B).astype('float64')
            sensor_system = sensor_system.A.astype('float64'), sensor_system.B.astype('float64'), sensor_system.C.astype('float64'), sensor_system.D.astype('float64')
            
            salida2 = deque([0])

        i = 0
        setpoint_window = 0
        Tiempo_list = [0]
        setpoint = [0]

        # Particularización por cada esquema
        if self.esquema == 1:  # PID difuso

            f_signal_anterior = 0
            
            if not self.N == 0 and self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([1], [10 / self.N, 1]) *
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

                # Para la segunda derivada del error
                derivada2 = ctrl.tf2ss(
                    ctrl.TransferFunction([1], [10 / self.N, 1]) *
                    ctrl.TransferFunction([self.N, 0], [1, self.N]) *
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada2 = np.zeros_like(derivada2.B).astype('float64')
                derivada2 = derivada2.A.astype('float64'), derivada2.B.astype('float64'), derivada2.C.astype('float64'), derivada2.D.astype('float64')

            elif not self.N == 0 and not self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

                # Para la segunda derivada del error
                derivada2 = ctrl.tf2ss(
                    ctrl.TransferFunction([self.N, 0], [1, self.N]) *
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada2 = np.zeros_like(derivada2.B).astype('float64')
                derivada2 = derivada2.A.astype('float64'), derivada2.B.astype('float64'), derivada2.C.astype('float64'), derivada2.D.astype('float64')

            else:
                # En caso de que N sea igual a cero
                derivada = ctrl.tf2ss(ctrl.TransferFunction([0], [1]))
                x_derivada = np.zeros_like(derivada.B)
                derivada2 = ctrl.tf2ss(ctrl.TransferFunction([0], [1]))
                x_derivada2 = np.zeros_like(derivada2.B)
                h = 0.05
                h_new = h

            # Inicio de la simulación
            while tiempo < tiempo_total:

                # Para alternar los valores del setpoint avanzado
                if not isinstance(self.escalon, float):
                    if tiempo + h >= max_tiempo[
                            setpoint_window] and setpoint_window < index_tbound:
                        setpoint_window += 1
                    u = u_value[setpoint_window]

                # Calculo del error
                error = u - salida[-1]

                # Distinción entre continuo y discreto
                if ctrl.isdtime(self.system, strict=True):
                    d_error, d2_error, error_a = derivadas_discretas(error, h, error_a)
                else:
                    if self.N != 0:
                        h, h_new2, d2_error, x_derivada2 = PIDf(derivada2, h, tiempo,
                                                            max_tiempo[setpoint_window], x_derivada2, error, *self.solver_configuration)

                        htemp, h_new1, d_error, x_derivada = PIDf(derivada, h, tiempo,
                                                            max_tiempo[setpoint_window], x_derivada, error, *self.solver_configuration)
                        h = min(h, htemp)
                        h_new = min(h_new1, h_new2)
                    else:
                        d_error = 0
                        d2_error = 0

                # Calculo del controlador difuso
                f_signal = fuzzy_c1.calcular_valor([error, d_error, d2_error],
                                                   [0] * 1)[0]
                sc_t = sc_t + (f_signal + f_signal_anterior)*h/2
                f_signal_anterior = f_signal

                # En caso de que se habilite el accionador
                if self.accionador_flag:
                    sc_t, acc_x = solve(*acc_system, acc_x, h, sc_t)

                # En caso de que se habilite el saturador
                if self.saturador_flag:
                    sc_t = min(max(sc_t, lim_inferior), lim_superior)

                # Salida del sistema
                y, x = solve(*system, x, h, sc_t)

                # Acumulación de la señal de control
                sc_f.append(sc_t)

                # En caso de que se habilite el sensor
                if self.sensor_flag:
                    salida2.append(y)
                    y, sensor_x = solve(*sensor_system, sensor_x, h, salida2[-1])

                # Acumulación de la salida
                salida.append(y)

                # Actualizacion de la barra de progreso cada 20% de avance
                if int(tiempo) % porcentajeBar == 0:
                    self.update_progresBar.emit(self.window, int(tiempo) * 100 / tiempo_total)

                # Acumulación del setpoint
                setpoint.append(u)

                # Acumulación del tiempo
                tiempo +=h
                Tiempo_list.append(tiempo)
                h = h_new
                i +=1

            # En caso de que se habilite el sensor
            if self.sensor_flag:
                salida = salida2

            return copy.deepcopy(Tiempo_list), copy.deepcopy(salida), copy.deepcopy(sc_f), copy.deepcopy(setpoint)

        if self.esquema == 2:  # PI difuso

            f_signal_anterior = 0
            
            if not self.N == 0 and self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([1], [10 / self.N, 1]) *
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

            elif not self.N == 0 and not self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

            else:
                # En caso de que N sea igual a cero
                derivada = ctrl.tf2ss(ctrl.TransferFunction([0], [1]))
                x_derivada = np.zeros_like(derivada.B)
                h = 0.05
                h_new = h

            # Inicio de la simulación
            while tiempo < tiempo_total:

                # Para alternar los valores del setpoint avanzado
                if not isinstance(self.escalon, float):
                    if tiempo + h >= max_tiempo[
                            setpoint_window] and setpoint_window < index_tbound:
                        setpoint_window += 1
                    u = u_value[setpoint_window]

                # Calculo del error
                error = u - salida[i]

                # Distinción entre continuo y discreto
                if ctrl.isdtime(self.system, strict=True):
                    d_error, d2_error, error_a = derivadas_discretas(error, h, error_a)
                else:
                    if self.N != 0:
                        h, h_new, d_error, x_derivada = PIDf(derivada, h, tiempo,
                                                           max_tiempo[setpoint_window], x_derivada, error, *self.solver_configuration)
                    else:
                        d_error = 0

                # Calculo del controlador difuso
                f_signal = fuzzy_c1.calcular_valor([error, d_error], [0] * 1)[0]
                sc_t = sc_t + (f_signal + f_signal_anterior)*h/2
                f_signal_anterior = f_signal
                
                # En caso de que se habilite el accionador
                if self.accionador_flag:
                    sc_t, acc_x = solve(*acc_system, acc_x, h, sc_t)

                # En caso de que se habilite el saturador
                if self.saturador_flag:
                    sc_t = min(max(sc_t, lim_inferior), lim_superior)

                # Salida del sistema
                y, x = solve(*system, x, h, sc_t)

                # Acumulación de la señal de control
                sc_f.append(sc_t)

                # En caso de que se habilite el sensor
                if self.sensor_flag:
                    salida2.append(y)
                    y, sensor_x = solve(*sensor_system, sensor_x, h, salida2[-1])

                # Acumulación de la salida
                salida.append(y)

                # Actualizacion de la barra de progreso cada 20% de avance
                if int(tiempo) % porcentajeBar == 0:
                    self.update_progresBar.emit(self.window, int(tiempo) * 100 / tiempo_total)

                # Acumulación del setpoint
                setpoint.append(u)

                # Acumulación del tiempo
                tiempo +=h
                Tiempo_list.append(tiempo)
                h = h_new
                i +=1

            # En caso de que se habilite el sensor
            if self.sensor_flag:
                salida = salida2

            return copy.deepcopy(Tiempo_list), copy.deepcopy(salida), copy.deepcopy(sc_f), copy.deepcopy(setpoint)

        if self.esquema == 3:  # PD difuso

            if not self.N == 0 and self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([1], [10 / self.N, 1]) *
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

            elif not self.N == 0 and not self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

            else:
                # En caso de que N sea igual a cero
                derivada = ctrl.tf2ss(ctrl.TransferFunction([0], [1]))
                x_derivada = np.zeros_like(derivada.B)
                h = 0.05
                h_new = h

            # Inicio de la simulación
            while tiempo < tiempo_total:

                # Para alternar los valores del setpoint avanzado
                if not isinstance(self.escalon, float):
                    if tiempo + h >= max_tiempo[
                            setpoint_window] and setpoint_window < index_tbound:
                        setpoint_window += 1
                    u = u_value[setpoint_window]

                # Calculo del error
                error = u - salida[i]

                # Distinción entre continuo y discreto
                if ctrl.isdtime(self.system, strict=True):
                    d_error, d2_error, error_a = derivadas_discretas(error, h, error_a)
                else:
                    if self.N != 0:
                        h, h_new, d_error, x_derivada = PIDf(derivada, h, tiempo,
                                                           max_tiempo[setpoint_window], x_derivada, error, *self.solver_configuration)
                    else:
                        d_error = 0

                # Calculo del controlador difuso
                sc_t = fuzzy_c1.calcular_valor([error, d_error], [0] * 1)[0]

                # En caso de que se habilite el accionador
                if self.accionador_flag:
                    sc_t, acc_x = solve(*acc_system, acc_x, h, sc_t)

                # En caso de que se habilite el saturador
                if self.saturador_flag:
                    sc_t = min(max(sc_t, lim_inferior), lim_superior)

                # Salida del sistema
                y, x = solve(*system, x, h, sc_t)

                # Acumulación de la señal de control
                sc_f.append(sc_t)

                # En caso de que se habilite el sensor
                if self.sensor_flag:
                    salida2.append(y)
                    y, sensor_x = solve(*sensor_system, sensor_x, h, salida2[-1])

                # Acumulación de la salida
                salida.append(y)

                # Actualizacion de la barra de progreso cada 20% de avance
                if int(tiempo) % porcentajeBar == 0:
                    self.update_progresBar.emit(self.window, int(tiempo) * 100 / tiempo_total)

                # Acumulación del setpoint
                setpoint.append(u)

                # Acumulación del tiempo
                tiempo +=h
                Tiempo_list.append(tiempo)
                h = h_new
                i +=1

            # En caso de que se habilite el sensor
            if self.sensor_flag:
                salida = salida2

            return copy.deepcopy(Tiempo_list), copy.deepcopy(salida), copy.deepcopy(sc_f), copy.deepcopy(setpoint)

        if self.esquema == 4:  # PI difuso + PD difuso

            spi = 0
            f_signal_anterior = 0

            if not self.N == 0 and self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([1], [10 / self.N, 1]) *
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

            elif not self.N == 0 and not self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

            else:
                # En caso de que N sea igual a cero
                derivada = ctrl.tf2ss(ctrl.TransferFunction([0], [1]))
                x_derivada = np.zeros_like(derivada.B)
                h = 0.05
                h_new = h

            # Inicio de la simulación
            while tiempo < tiempo_total:

                # Para alternar los valores del setpoint avanzado
                if not isinstance(self.escalon, float):
                    if tiempo + h >= max_tiempo[
                            setpoint_window] and setpoint_window < index_tbound:
                        setpoint_window += 1
                    u = u_value[setpoint_window]

                # Calculo del error
                error = u - salida[i]

                # Distinción entre continuo y discreto
                if ctrl.isdtime(self.system, strict=True):
                    d_error, d2_error, error_a = derivadas_discretas(error, h, error_a)
                else:
                    if self.N != 0:
                        h, h_new, d_error, x_derivada = PIDf(derivada, h, tiempo,
                                                           max_tiempo[setpoint_window], x_derivada, error, *self.solver_configuration)
                    else:
                        d_error = 0

                # Calculo de los controladores difusos
                f_signal = fuzzy_c1.calcular_valor([error, d_error], [0] * 1)[0]
                spi = spi + (f_signal + f_signal_anterior) * h/2
                f_signal_anterior = f_signal
                
                spd = fuzzy_c2.calcular_valor([error, d_error], [0] * 1)[0]
                sc_t = spi + spd

                # En caso de que se habilite el accionador
                if self.accionador_flag:
                    sc_t, acc_x = solve(*acc_system, acc_x, h, sc_t)

                # En caso de que se habilite el saturador
                if self.saturador_flag:
                    sc_t = min(max(sc_t, lim_inferior), lim_superior)

                # Salida del sistema
                y, x = solve(*system, x, h, sc_t)

                # Acumulación de la señal de control
                sc_f.append(sc_t)

                # En caso de que se habilite el sensor
                if self.sensor_flag:
                    salida2.append(y)
                    y, sensor_x = solve(*sensor_system, sensor_x, h, salida2[-1])

                # Acumulación de la salida
                salida.append(y)

                # Actualizacion de la barra de progreso cada 20% de avance
                if int(tiempo) % porcentajeBar == 0:
                    self.update_progresBar.emit(self.window, int(tiempo) * 100 / tiempo_total)

                # Acumulación del setpoint
                setpoint.append(u)

                # Acumulación del tiempo
                tiempo +=h
                Tiempo_list.append(tiempo)
                h = h_new
                i +=1

            # En caso de que se habilite el sensor
            if self.sensor_flag:
                salida = salida2

            return copy.deepcopy(Tiempo_list), copy.deepcopy(salida), copy.deepcopy(sc_f), copy.deepcopy(setpoint)

        if self.esquema == 5:  # PI difuso + D clásico

            spi = 0
            f_signal_anterior = 0

            if not self.N == 0 and self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([1], [10 / self.N, 1]) *
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

            elif not self.N == 0 and not self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

            else:
                # En caso de que N sea igual a cero
                derivada = ctrl.tf2ss(ctrl.TransferFunction([0], [1]))
                x_derivada = np.zeros_like(derivada.B)
                h = 0.05
                h_new = h

            # Inicio de la simulación
            while tiempo < tiempo_total:

                # Para alternar los valores del setpoint avanzado
                if not isinstance(self.escalon, float):
                    if tiempo + h >= max_tiempo[
                            setpoint_window] and setpoint_window < index_tbound:
                        setpoint_window += 1
                    u = u_value[setpoint_window]

                # Calculo del error
                error = u - salida[i]

                # Distinción entre continuo y discreto
                if ctrl.isdtime(self.system, strict=True):
                    d_error, d2_error, error_a = derivadas_discretas(error, h, error_a)
                else:
                    if self.N != 0:
                        h, h_new, d_error, x_derivada = PIDf(derivada, h, tiempo,
                                                           max_tiempo[setpoint_window], x_derivada, error, *self.solver_configuration)
                    else:
                        d_error = 0

                # Calculo del controlador difuso
                f_signal = fuzzy_c1.calcular_valor([error, d_error], [0] * 1)[0]
                spi = spi + (f_signal + f_signal_anterior) * h/2
                f_signal_anterior = f_signal
                
                sc_t = spi + d_error*kd

                # En caso de que se habilite el accionador
                if self.accionador_flag:
                    sc_t, acc_x = solve(*acc_system, acc_x, h, sc_t)

                # En caso de que se habilite el saturador
                if self.saturador_flag:
                    sc_t = min(max(sc_t, lim_inferior), lim_superior)

                # Salida del sistema
                y, x = solve(*system, x, h, sc_t)

                # Acumulación de la señal de control
                sc_f.append(sc_t)

                # En caso de que se habilite el sensor
                if self.sensor_flag:
                    salida2.append(y)
                    y, sensor_x = solve(*sensor_system, sensor_x, h, salida2[-1])

                # Acumulación de la salida
                salida.append(y)

                # Actualizacion de la barra de progreso cada 20% de avance
                if int(tiempo) % porcentajeBar == 0:
                    self.update_progresBar.emit(self.window,
                                                int(tiempo) * 100 / tiempo_total)

                # Acumulación del setpoint
                setpoint.append(u)

                # Acumulación del tiempo
                tiempo += h
                Tiempo_list.append(tiempo)
                h = h_new
                i += 1

            # En caso de que se habilite el sensor
            if self.sensor_flag:
                salida = salida2

            return copy.deepcopy(Tiempo_list), copy.deepcopy(salida), copy.deepcopy(sc_f), copy.deepcopy(setpoint)

        if self.esquema == 6:  # PD difuso + I Clásico

            spi = 0
            error_integral = 0

            if not self.N == 0 and self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([1], [10 / self.N, 1]) *
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

            elif not self.N == 0 and not self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

            else:
                # En caso de que N sea igual a cero
                derivada = ctrl.tf2ss(ctrl.TransferFunction([0], [1]))
                x_derivada = np.zeros_like(derivada.B)
                h = 0.05
                h_new = h

            # Inicio de la simulación
            while tiempo < tiempo_total:

                # Para alternar los valores del setpoint avanzado
                if not isinstance(self.escalon, float):
                    if tiempo + h >= max_tiempo[
                            setpoint_window] and setpoint_window < index_tbound:
                        setpoint_window += 1
                    u = u_value[setpoint_window]

                # Calculo del error
                error = u - salida[i]

                # Distinción entre continuo y discreto
                if ctrl.isdtime(self.system, strict=True):
                    d_error, d2_error, error_a = derivadas_discretas(error, h, error_a)
                else:
                    if self.N != 0:
                        h, h_new, d_error, x_derivada = PIDf(derivada, h, tiempo,
                                                           max_tiempo[setpoint_window], x_derivada, error, *self.solver_configuration)
                    else:
                        d_error = 0

                # Calculo del controlador difuso
                spi = spi + (error + error_integral)*h/2
                error_integral = error
                
                spd = fuzzy_c1.calcular_valor([error, d_error], [0] * 1)[0]
                sc_t = spi*ki + spd

                # En caso de que se habilite el accionador
                if self.accionador_flag:
                    sc_t, acc_x = solve(*acc_system, acc_x, h, sc_t)

                # En caso de que se habilite el saturador
                if self.saturador_flag:
                    sc_t = min(max(sc_t, lim_inferior), lim_superior)

                # Salida del sistema
                y, x = solve(*system, x, h, sc_t)

                # Acumulación de la señal de control
                sc_f.append(sc_t)

                # En caso de que se habilite el sensor
                if self.sensor_flag:
                    salida2.append(y)
                    y, sensor_x = solve(*sensor_system, sensor_x, h, salida2[-1])

                # Acumulación de la salida
                salida.append(y)

                # Actualizacion de la barra de progreso cada 20% de avance
                if int(tiempo) % porcentajeBar == 0:
                    self.update_progresBar.emit(self.window,
                                                int(tiempo) * 100 / tiempo_total)

                # Acumulación del setpoint
                setpoint.append(u)

                # Acumulación del tiempo
                tiempo += h
                Tiempo_list.append(tiempo)
                h = h_new
                i += 1

            # En caso de que se habilite el sensor
            if self.sensor_flag:
                salida = salida2

            return copy.deepcopy(Tiempo_list), copy.deepcopy(salida), copy.deepcopy(sc_f), copy.deepcopy(setpoint)

        if self.esquema == 7:  # Programador de ganancias

            spi = 0
            error_integral = 0

            if not self.N == 0 and self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([1], [10 / self.N, 1]) *
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

            elif not self.N == 0 and not self.flag_filtro:
                # Para la derivada del error
                derivada = ctrl.tf2ss(
                    ctrl.TransferFunction([self.N, 0], [1, self.N]))
                
                x_derivada = np.zeros_like(derivada.B).astype('float64')
                derivada = derivada.A.astype('float64'), derivada.B.astype('float64'), derivada.C.astype('float64'), derivada.D.astype('float64')

            else:
                # En caso de que N sea igual a cero
                derivada = ctrl.tf2ss(ctrl.TransferFunction([0], [1]))
                x_derivada = np.zeros_like(derivada.B)
                h = 0.05
                h_new = h
            
            # Inicio de la simulación
            while tiempo < tiempo_total:

                # Para alternar los valores del setpoint avanzado
                if not isinstance(self.escalon, float):
                    if tiempo + h >= max_tiempo[
                            setpoint_window] and setpoint_window < index_tbound:
                        setpoint_window += 1
                    u = u_value[setpoint_window]

                # Calculo del error
                error = u - salida[i]

                # Distinción entre continuo y discreto
                if ctrl.isdtime(self.system, strict=True):
                    d_error, d2_error, error_a = derivadas_discretas(error, h, error_a)
                else:
                    if self.N != 0:
                        h, h_new, d_error, x_derivada = PIDf(derivada, h, tiempo,
                                                            max_tiempo[setpoint_window], x_derivada, error, *self.solver_configuration)
                    else:
                        d_error = 0

                # Calculo del controlador difuso
                kp, ki, kd = fuzzy_c1.calcular_valor([error, d_error], [0] * 3)

                spi = spi + (error + error_integral)*h/2
                error_integral = error
                
                sc_t = spi*ki + d_error*kd + error*kp
                

                # En caso de que se habilite el accionador
                if self.accionador_flag:
                    sc_t, acc_x = solve(*acc_system, acc_x, h, sc_t)

                # En caso de que se habilite el saturador
                if self.saturador_flag:
                    sc_t = min(max(sc_t, lim_inferior), lim_superior)

                # Salida del sistema
                y, x = solve(*system, x, h, sc_t)

                # Acumulación de la señal de control
                sc_f.append(sc_t)

                # En caso de que se habilite el sensor
                if self.sensor_flag:
                    salida2.append(y)
                    y, sensor_x = solve(*sensor_system, sensor_x, h, salida2[-1])

                # Acumulación de la salida
                salida.append(y)

                # Actualizacion de la barra de progreso cada 20% de avance
                if int(tiempo) % porcentajeBar == 0:
                    self.update_progresBar.emit(self.window,
                                                int(tiempo) * 100 / tiempo_total)

                # Acumulación del setpoint
                setpoint.append(u)

                # Acumulación del tiempo
                tiempo += h
                Tiempo_list.append(tiempo)
                h = h_new
                i += 1

            # En caso de que se habilite el sensor
            if self.sensor_flag:
                salida = salida2

            return copy.deepcopy(Tiempo_list), copy.deepcopy(salida), copy.deepcopy(sc_f), copy.deepcopy(setpoint)

        if self.esquema == 8:  # PID clásico + difuso simple

            if self.N*kd == 0:
                # N debe mantenerse debido al algoritmo utilizado por la libreria de control para llevar de función
				# de transferencia a ecuaciones de espacio de estados
                # Controlador PID con la forma:
                #    PID = kp + ki/s + (kd*N*s/(s + N))

                self.N = 50
                kd = 0.0
                pid = ctrl.tf2ss(ctrl.TransferFunction(
                        [self.N * kd + kp, self.N * kp + ki, self.N * ki], [1, self.N, 0]))

            elif not self.flag_filtro:
                # Controlador PID con la forma:
                #    PID = kp + ki/s + (kd*N*s/(s + N))

                pid = ctrl.tf2ss(ctrl.TransferFunction(
                        [self.N * kd + kp, self.N * kp + ki, self.N * ki], [1, self.N, 0]))

            else:
                # Controlador PID con la forma:
                #    PID = kp + ki/s + (kd*N*s/(s + N))*(1/(10/(N*kd) + 1))

                pid = ctrl.tf2ss(
                    ctrl.TransferFunction([
                        10 * kp,
                        self.N**2 * kd**2 + self.N * kd * kp + 10 * self.N * kp + 10*ki,
                        self.N**2 * kd * kp + kd * self.N * ki + 10 * self.N * ki,
                        self.N**2 * kd * ki
                    ], [10, 10 * self.N + self.N * kd, self.N**2 * kd, 0]))

            x_pid = np.zeros_like(pid.B).astype('float64')
            pid = pid.A.astype('float64'), pid.B.astype('float64'), pid.C.astype('float64'), pid.D.astype('float64')

            # Inicio de la simulación
            while tiempo < tiempo_total:

                # Para alternar los valores del setpoint avanzado
                if not isinstance(self.escalon, float):
                    if tiempo + h >= max_tiempo[
                            setpoint_window] and setpoint_window < index_tbound:
                        setpoint_window += 1
                    u = u_value[setpoint_window]

                # Calculo del error
                error = u - salida[i]

                # Distinción entre continuo y discreto
                if ctrl.isdtime(self.system, strict=True):
                    s_pid, si_t, error_a = PIDf(error, h, si_t, error_a, kp, ki, kd)
                else:
                    h, h_new, s_pid, x_pid = PIDf(pid, h, tiempo,
                                                 max_tiempo[setpoint_window], x_pid, error, *self.solver_configuration)

                # calculo del controlador difuso
                s_fuzzy = fuzzy_c1.calcular_valor([error], [0] * 1)[0]

                # Suma del controlador clásico y difuso
                sc_t = s_pid + s_fuzzy

                # En caso de que se habilite el accionador
                if self.accionador_flag:
                    sc_t, acc_x = solve(*acc_system, acc_x, h, sc_t)

                # En caso de que se habilite el saturador
                if self.saturador_flag:
                    sc_t = min(max(sc_t, lim_inferior), lim_superior)

                # Salida del sistema
                y, x = solve(*system, x, h, sc_t)

                # Acumulación de la señal de control
                sc_f.append(sc_t)

                # En caso de que se habilite el sensor
                if self.sensor_flag:
                    salida2.append(y)
                    y, sensor_x = solve(*sensor_system, sensor_x, h, salida2[-1])

                # Acumulación de la salida
                salida.append(y)

                # Actualizacion de la barra de progreso cada 20% de avance
                if int(tiempo) % porcentajeBar == 0:
                    self.update_progresBar.emit(self.window,
                                                int(tiempo) * 100 / tiempo_total)

                # Acumulación del setpoint
                setpoint.append(u)

                # Acumulación del tiempo
                tiempo += h
                Tiempo_list.append(tiempo)
                h = h_new
                i += 1

            # En caso de que se habilite el sensor
            if self.sensor_flag:
                salida = salida2

            return copy.deepcopy(Tiempo_list), copy.deepcopy(salida), copy.deepcopy(sc_f), copy.deepcopy(setpoint)


def system_creator_tf(self, numerador, denominador):
    """
    Función para la creación del sistema a partir de los coeficientes del numerador y del denominador de la función de transferencia.
    
    :param numerador: Coeficientes del numerador
    :type numerador: list
    :param denominador: Coeficientes del denominador
    :type denominador: list
    :return: El sistema creado
    :rtype: LTI
    """

    if self.main.tfdelaycheckBox4.isChecked():
        delay = json.loads(self.main.tfdelayEdit4.text())
    else:
        delay = 0

    system = ctrl.TransferFunction(numerador, denominador, delay=delay)

    # Agregando delay con aproximación por pade para sistemas continuos
    if delay and not self.main.tfdiscretocheckBox4.isChecked():
        pade = ctrl.TransferFunction(*ctrl.pade(delay, int(self.main.padeOrder.text())))
        system = system*pade

    # En caso de que el sistema sea discreto
    if self.main.tfdiscretocheckBox4.isChecked():
        system = ctrl.sample_system(system,
                                    self.dt,
                                    self.main.tfcomboBox4.currentText(),
                                    delay=delay)
        if delay:
            delayV = [0] * (int(delay / self.dt) + 1)
            delayV[0] = 1
            system = system * ctrl.TransferFunction([1], delayV, self.dt)

    return system


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
    :return: El sistema creado
    :rtype: LTI
    """

    if self.main.ssdelaycheckBox4.isChecked():
        delay = json.loads(self.main.ssdelayEdit4.text())
    else:
        delay = 0

    system = ctrl.StateSpace(A, B, C, D, delay=delay)

    # Agregando delay con aproximación por pade para sistemas continuos
    if delay and not self.main.ssdiscretocheckBox4.isChecked():
        pade = ctrl.TransferFunction(*ctrl.pade(delay, int(self.main.padeOrder.text())))
        system = system*pade

    # En caso de que el sistema sea discreto
    if self.main.ssdiscretocheckBox4.isChecked():
        system = ctrl.sample_system(system,
                                    self.dt,
                                    self.main.sscomboBox4.currentText(),
                                    delay=delay)
        if delay:
            delayV = [0] * (int(delay / self.dt) + 1)
            delayV[0] = 1
            system = system * ctrl.TransferFunction([1], delayV, self.dt)

    return system


def controlador_validator(self, esquema, InputList, OutputList, RuleEtiquetas):
    """
    Función para validar los controladores difusos con respecto al esquema de control seleccionado
    
    :param esquema: Esquema de control seleccionado representado por un valor
    :type esquema: int
    :param InputList: Lista de entradas
    :type InputList: list
    :param OutputList: Lista de salidas
    :type OutputList: list
    :param RuleEtiquetas: Lista con set de reglas
    :type RuleEtiquetas: list
    """

    if esquema == 1: # PID difuso
        if len(InputList) == 3 and len(OutputList) == 1 and len(RuleEtiquetas) != 0:
            return
        else:
            raise AssertionError

    if esquema in [2, 3, 4, 5, 6]:  # PI difuso, PD difuso, PI difuso + PD difuso, PI difuso + D Clásico, PD difuso + I Clásico
        if len(InputList) == 2 and len(OutputList) == 1 and len(RuleEtiquetas) != 0:
            return
        else:
            raise AssertionError

    if esquema == 7:  # Programador de ganancias
        if len(InputList) == 2 and len(OutputList) == 3 and len(RuleEtiquetas) != 0:
            return
        else:
            raise AssertionError

    if esquema == 8:  # PID Clásico + Difuso simple
        if len(InputList) == 1 and len(OutputList) == 1 and len(RuleEtiquetas) != 0:
            return
        else:
            raise AssertionError

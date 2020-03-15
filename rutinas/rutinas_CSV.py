""" 
Archivo que contiene todas las rutinas necesarias para la funcionalidad de identificación de modelo y tunning con csv
"""

from scipy.ndimage import gaussian_filter

import matplotlib.ticker as mticker
import controlmdf as ctrl
import numpy as np


def procesar_csv(self, csv_data):
    """
    Función para procesar la data del archivo csv, se crea una nueva data en un diccionario, se normalizan las escalas con el span y se transforma el tiempo a segundos. Para la transformación de tiempo a segundos los formatos aceptados son:
    
    hh:mm:ss
    
    mm:ss
    
    ss
    
    En cualquiera de los casos se llevara a segundos y se restara el tiempo inicial para que empiece en cero.
    
    :param csv_data: Data del csv
    :type csv_data: numpyArray
    :return: Data extraida del archivo CSV asi como indices, máximos y mínimos de la data
    :rtype: tuple(dict, list[int, int, int, float, float, float, float])
    """

    # Identificacion de columnas
    for i, header in enumerate(csv_data[0]):
        if 'time' in header.lower():
            indexTime = i
        if 'vp' in header.lower():
            indexVp = i
        if 'efc' in header.lower():
            indexEFC = i

    csv_data = np.delete(csv_data, 0, 0)

    dict_data = dict()
    try:
        dict_data['time'] = np.array(csv_data[:, indexTime])
        dict_data['vp'] = np.array(list(map(float, csv_data[:, indexVp])))
        dict_data['efc'] = np.array(list(map(float, csv_data[:, indexEFC])))
    except UnboundLocalError:
        raise UnboundLocalError

    Tiempo = []

    # Transformación de tiempo a segundos
    for time_entry in dict_data['time']:
        my_time = str(time_entry)
        t1 = sum(i * j for i, j in zip(list(map(float, my_time.split(':')))[::-1], [1, 60, 3600]))
        Tiempo.append(t1)

    dict_data['time'] = np.array(Tiempo) - Tiempo[0]

    MinVP = float(self.main.EditLVP.text())
    MaxVP = float(self.main.EditUVP.text())
    MinEFC = float(self.main.EditLEFC.text())
    MaxEFC = float(self.main.EditUEFC.text())

    # Normalización
    FactorVP = 100 / MaxVP - MinVP
    FactorEFC = 100 / MaxEFC - MinEFC

    dict_data['vp'] = (dict_data['vp']-MinVP)*FactorVP
    dict_data['efc'] = (dict_data['efc']-MinEFC)*FactorEFC

    dict_data['time'] = dict_data['time']
    dict_data['vp'] = gaussian_filter(dict_data['vp'], 5)
    dict_data['efc'] = gaussian_filter(dict_data['efc'], 2)

    return dict_data, [indexTime, indexVp, indexEFC, MinVP, MaxVP, MinEFC, MaxEFC]


def calcular_modelo(self,
                    dict_data,
                    indexTime,
                    indexVp,
                    indexEFC,
                    MinVP,
                    MaxVP,
                    MinEFC,
                    MaxEFC):
    """
    Función para calcular los parametros del modelo de primer orden
    
    :param dict_data: Diccionario con la data procesada del csv
    :type dict_data: dict
    :param indexTime: Indice que identifica al tiempo
    :type indexTime: int
    :param indexVp: Indice que identifica a Vp
    :type indexVp: int
    :param indexEFC: Indice que identifica al EFC
    :type indexEFC: int
    :param MinVP: Limite inferior de Vp
    :type MinVP: float
    :param MaxVP: Limite superior de Vp
    :type MaxVP: float
    :param MinEFC: Limite inferior de EFC
    :type MinEFC: float
    :param MaxEFC: Limite superior de EFC
    :type MaxEFC: float
    :return: Datos del modelo de primer orden, recta tangente y puntos asociados a la recta
    :rtype: tuple(float, float, float, float, float, float, float, float, float)
    """

    y = dict_data['vp']
    t = dict_data['time']

    vpmin = np.min(dict_data['vp'][0])
    vpmax = np.max(dict_data['vp'][-1])
    efcmin = np.min(dict_data['efc'][0])
    efcmax = np.max(dict_data['efc'][-1])

    i_max = np.argmax(np.abs(np.gradient(y)))
    efc_max = np.argmax(np.abs(np.gradient(dict_data['efc'])))

    for index, i in enumerate(y):
        if i >= 0.63 * (vpmax-vpmin) + vpmin:
            indexv = index
            break

    Kc = (vpmax - vpmin)/(efcmax - efcmin)

    slop_efc = (dict_data['efc'][efc_max] - dict_data['efc'][efc_max - 1]) / (t[efc_max] - t[efc_max - 1])
    t0 = ((efcmin - dict_data['efc'][efc_max]) / (slop_efc) + t[efc_max])
    
    slop = (y[i_max] - y[i_max - 1]) / (t[i_max] - t[i_max - 1])
    t1 = ((vpmin - y[i_max]) / (slop) + t[i_max])
    
    t2 = t[indexv]
    y1 = vpmin
    y2 = slop * (t2 - t[i_max]) + y[i_max]
    tau = t2 - t1
    anclaT = t[i_max]
    anclaY = y[i_max]

    return Kc, tau, y1, y2, t0, t1, t2, anclaT, anclaY


def entonar_y_graficar(self, dict_data, Kc, tau, y1, y2, t0, t1, t2):
    """
    Función para calcular el controlador PID a partir de los datos del modelo de primer orden, ademas, se graficá la data del csv junto con algunos parametros de la identificación del modelo
    
    :param dict_data: Diccionario con la data procesada del csv
    :type dict_data: dict
    :param Kc: Ganancia del proceso
    :type Kc: float
    :param tau: Constante de tiempo del proceso
    :type tau: float
    :param y1: Punto y1 de la recta de identificación, en este punto se encuentra el mayor cambio respecto al tiempo
    :type y1: float
    :param y2: Punto y2 de la recta de identificación
    :type y2: float
    :param t0: Tiempo del inicio del escalón
    :type t0: float
    :param t1: Tiempo del inicio de la respuesta del proceso ante el escalón
    :type t1: float
    :param t2: Tiempo en el que el proceso alcanza el 63% de su valor final respecto al cambio
    :type t2: float
    :return: Lista de objetos de gráficas y lista de parametros de la recta para el modelado
    :rtype: tuple(list[ObjectType, ObjectType, ObjectType, ObjectType, ObjectType, ObjectType, ObjectType, ObjectType], list[float, float, float, float, float, float])
    """

    kp, ki, kd = auto_tuning_method_csv(self, Kc, tau, t1-t0, self.main.csvMetodo.currentText())

    self.main.csvGraphicsView.canvas.axes1.clear()
    self.main.csvGraphicsView.canvas.axes1.plot(dict_data['time'],
                                                dict_data['efc'],
                                                label='EFC')

    t0_efc = self.main.csvGraphicsView.canvas.axes1.axvline(x=t0,
                                                            color='k',
                                                            linestyle=':',
                                                            zorder=-20,
                                                            label='t0, t1, t2')
    t1_efc = self.main.csvGraphicsView.canvas.axes1.axvline(x=t1,
                                                            color='k',
                                                            linestyle=':',
                                                            zorder=-20)
    t2_efc = self.main.csvGraphicsView.canvas.axes1.axvline(x=t2,
                                                            color='k',
                                                            linestyle=':',
                                                            zorder=-20)

    self.main.csvGraphicsView.canvas.axes1.grid(True, which="both", color="lightgray")
    self.main.csvGraphicsView.canvas.axes1.legend()
    self.main.csvGraphicsView.canvas.axes1.yaxis.set_major_formatter(
        mticker.FormatStrFormatter("%.1f %%")
    )

    self.main.csvGraphicsView.canvas.axes2.clear()
    self.main.csvGraphicsView.canvas.axes2.plot(dict_data['time'],
                                                dict_data['vp'],
                                                label='Vp')

    recta, = self.main.csvGraphicsView.canvas.axes2.plot([t1, t2], [y1, y2], label='recta')

    t0_vp = self.main.csvGraphicsView.canvas.axes2.axvline(x=t0,
                                                           color='k',
                                                           linestyle=':',
                                                           zorder=-20,
                                                           label='t0, t1, t2')
    t1_vp = self.main.csvGraphicsView.canvas.axes2.axvline(x=t1,
                                                           color='k',
                                                           linestyle=':',
                                                           zorder=-20)
    t2_vp = self.main.csvGraphicsView.canvas.axes2.axvline(x=t2,
                                                           color='k',
                                                           linestyle=':',
                                                           zorder=-20)

    self.main.csvGraphicsView.canvas.axes2.grid(True, which="both", color="lightgray")
    self.main.csvGraphicsView.canvas.axes2.legend()
    self.main.csvGraphicsView.canvas.axes2.yaxis.set_major_formatter(
        mticker.FormatStrFormatter("%.1f %%")
    )

    self.main.csvGraphicsView.canvas.draw()
    self.main.csvGraphicsView.toolbar.update()

    actualizar_Datos(self, Kc, t0, t1, t2, kp, ki, kd)
    self.main.pidTiempoSlider.blockSignals(True)
    self.main.pidTiempoSlider.setValue(np.round(1000*(t1-t0)/(t2-t0), 3))
    self.main.pidTiempoLabelValue.setText(str(np.round(t1, 3)))
    self.main.pidTiempoSlider.blockSignals(False)


    return [t0_efc, t1_efc, t2_efc, recta, t0_vp, t1_vp, t2_vp], [Kc, t0, t1, t2, y2, y1]


def calculos_manual(self, GraphObjets, Kc, t0, t1, t2, slop, y1):
    """
    Función para recalcular el controlador PID a partir de los datos del modelo de primer orden con el nuevo tiempo t1, ademas, se grafica la data del csv junto con algunos parametros de la identificación del modelo y la nueva recta
    
    :param GraphObjets: Lista de objetos de graficacion
    :type GraphObjets: list
    :param Kc: Ganancia del proceso
    :type Kc: float
    :param t0: Tiempo del inicio del escalón
    :type t0: float
    :param t1: Tiempo del inicio de la respuesta del proceso ante el escalón
    :type t1: float
    :param t2: Tiempo en el que el proceso alcanza el 63% de su valor final respecto al cambio
    :type t2: float
    :param slop: Pendiente de la recta de identificación
    :type slop: float
    :param y1: Punto y1 de la recta de identificación, en este punto se encuentra el mayor cambio respecto al tiempo
    :type y1: float
    """
    kp, ki, kd = auto_tuning_method_csv(self, Kc, t2-t1, t1-t0, self.main.csvMetodo.currentText())

    GraphObjets[1].set_data(t1, [0, 1])
    GraphObjets[5].set_data(t1, [0, 1])
    new_y2 = slop * (t2 - t1) + y1
    GraphObjets[3].set_data([t1, t2], [y1, new_y2])
    self.main.csvGraphicsView.canvas.draw()
    actualizar_Datos(self, Kc, t0, t1, t2, kp, ki, kd)


def actualizar_Datos(self, Kc, t0, t1, t2, kp, ki, kd):
    """
    Función para mostrar los resultados obtenidos del modelo en un TextEdit
    
    :param Kc: Ganancia del proceso
    :type Kc: float
    :param t0: Tiempo del inicio del escalón
    :type t0: float
    :param t1: Tiempo del inicio de la respuesta del proceso ante el escalón
    :type t1: float
    :param t2: Tiempo en el que el proceso alcanza el 63% de su valor final respecto al cambio
    :type t2: float
    :param kp: Ganancia proporcional
    :type kp: float
    :param ki: Ganancia integral
    :type ki: float
    :param kd: Ganancia derivativa
    :type kd: float
    """
    
    Datos = "Modelo:\n"
    Datos += str(ctrl.TransferFunction([Kc], [t2-t1, 1])) + "\n"
    Datos += f"Delay: {t1-t0:.3f}\n"
    Datos += "----------------------------------------------\n"
    Datos += f"Kp: {kp:.4f}\n"
    Datos += f"Ki: {ki:.4f}\n"
    Datos += f"Kd: {kd:.4f}\n"
    self.main.csvdatosTextEdit2.setPlainText(Datos)
    self.main.pidLabelController.setText(
        f" Kc = {Kc:.3f} -- Tau = {t2-t1:.3f} -- Alpha = {t1-t0:.3f}")


def auto_tuning_method_csv(self, k_proceso, tau, alpha, metodo):
    """
    Función para obtener las ganancias del controlador PID a partir de los parametros del modelo de primer orden obtenidos de una respuesta escalón, las formulas son las dadas por Ziegler-Nichols y Cohen-Coon para una respuesta escalón en lazo abierto
    
    :param k_proceso: Ganancia del proceso
    :type k_proceso: float
    :param tau: Constante de tiempo del proceso
    :type tau: float
    :param alpha: Tiempo muerto o delay del proceso
    :type alpha: float
    :param metodo: Método a utilizar
    :type metodo: str
    :return: Ganancias kp, ki y kd
    :rtype: tuple(float, float, float)
    """
    
    if alpha <= 0.05:
        print('Alfa es demasiado pequeño')
        raise TypeError('Alfa es demasiado pequeño')

    if 'ZN' in metodo:
        if 'P--' in metodo:
            kp = (1/k_proceso) * (tau/alpha)
            ti = np.infty
            td = 0

        if 'PI-' in metodo:
            kp = (0.9/k_proceso) * (tau/alpha)
            ti = alpha * 3.33
            td = 0

        if 'PID' in metodo:
            kp = (1.2/k_proceso) * (tau/alpha)
            ti = alpha * 2
            td = alpha * 0.5

        kp = kp
        ki = kp / ti
        kd = kp * td

    if 'CC' in metodo:
        if 'P--' in metodo:
            kp = (1/k_proceso) * (tau/alpha) * (1 + (1/3) * (alpha/tau))
            ti = np.infty
            td = 0

        if 'PI-' in metodo:
            kp = (1/k_proceso) * (tau/alpha) * (0.9 + (1/12) * (alpha/tau))
            ti = alpha * ((30 + 3 * (alpha/tau)) / (9 + 20 * (alpha/tau)))
            td = 0

        if 'PD-' in metodo:
            kp = ((1/k_proceso) * (tau/alpha) * ((5/4) + (1/6) * (alpha/tau)))
            ti = np.infty
            td = alpha * ((6 - 2 * (alpha/tau)) / (22 + 3 * (alpha/tau)))


        if 'PID' in metodo:
            kp = ((1/k_proceso) * (tau/alpha) * ((4/3) + (1/4) * (alpha/tau)))
            ti = alpha * ((32 + 6 * (alpha/tau)) / (13 + 8 * (alpha/tau)))
            td = alpha * (4 / (11 + 2 * (alpha/tau)))

        kp = kp / 2
        ki = kp / ti
        kd = kp * td

    return kp, ki, kd

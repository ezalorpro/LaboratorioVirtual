""" 
Archivo para definir los algoritmos de ajuste del tamaño de paso para los Runge-kutta explícitos y embebidos, en el caso de los métodos explícitos se utiliza el método de doble paso
"""


import numpy as np
from rutinas.metodos_RK import norm


def rk_doble_paso_adaptativo(systema,
                             h_ant,
                             tiempo,
                             tbound,
                             xVectB,
                             entrada,
                             metodo,
                             ordenq,
                             rtol,
                             atol,
                             max_step_increase,
                             min_step_decrease,
                             safety_factor):
    """
    Función para definir y manejar el ajuste del tamaño de paso por el método de doble paso para Runge-kutta's explícitos, la función está realizada de forma específica para trabajar con sistemas de control representados con ecuaciones de espacio de estados
    
    :param systema: Representación del sistema de control
    :type systema: LTI
    :param h_ant: Tamaño de paso actual
    :type h_ant: float
    :param tiempo: Tiempo actual
    :type tiempo: float
    :param tbound: Tiempo máximo de simulación
    :type tbound: float
    :param xVectB: Vector de estado
    :type xVectB: numpyArray
    :param entrada: Valor de entrada al sistema
    :type entrada: float
    :param metodo: Runge-Kutta a utilizar: RK2, Rk3, etc.
    :type metodo: function
    :param ordenq: Orden del método
    :type ordenq: int
    :param rtol: Tolerancia relativa
    :type rtol: float
    :param atol: Tolerancia absoluta
    :type atol: float
    :param max_step_increase: Máximo incremento del tamaño de paso
    :type max_step_increase: float
    :param min_step_decrease: Mínimo decremento del tamaño de paso
    :type min_step_decrease: float
    :param safety_factor: Factor de seguridad
    :type safety_factor: float
    """

    while True:
        # Para asegurar el tiempo máximo
        if tiempo + h_ant >= tbound:
            h_ant = tbound - tiempo
            yS, xVectSn = metodo(*systema, xVectB, h_ant, entrada)
            h_est = h_ant
        else:
            # Paso de tamaño regular
            yB, xVectBn = metodo(*systema, xVectB, h_ant, entrada)

            # Dos pasos de tamaño medio
            yS, xVectSn = metodo(*systema, xVectB, h_ant / 2, entrada)
            yS, xVectSn = metodo(*systema, xVectSn, h_ant / 2, entrada)

            # Ajuste del tamaño de paso
            scale = atol + rtol * (np.abs(xVectBn) + np.abs(xVectSn)) / 2
            delta1 = np.abs(xVectBn - xVectSn)
            error_norm = norm(delta1 / scale)

            if error_norm == 0:
                # Incremento máximo dado el bajo error
                h_est = h_ant * max_step_increase
            elif error_norm <= 1:
                # Incremento normal
                h_est = h_ant * min(max_step_increase,
                                    max(1, safety_factor * error_norm**(-1 / (ordenq+1))))
            else:
                # Decremento normal y se vuelve a calcular la salida
                h_ant = h_ant * min(
                    1,
                    max(min_step_decrease, safety_factor * error_norm**(-1 / (ordenq+1))))
                continue
        break
    return h_ant, h_est, yS, xVectSn


def rk_embebido_adaptativo(systema,
                           h_ant,
                           tiempo,
                           tbound,
                           xVectr,
                           entrada,
                           metodo,
                           ordenq,
                           rtol,
                           atol,
                           max_step_increase,
                           min_step_decrease,
                           safety_factor):
    """
    Función para definir y manejar el ajuste del tamaño de paso para Runge-kutta's embebidos, la función esta realizada de forma específica para trabajar con sistemas de control representados con ecuaciones de espacio de estados
    
    :param systema: Representación del sistema de control
    :type systema: LTI
    :param h_ant: Tamaño de paso actual
    :type h_ant: float
    :param tiempo: Tiempo actual
    :type tiempo: float
    :param tbound: Tiempo máximo de simulación
    :type tbound: float
    :param xVectB: Vector de estado
    :type xVectB: numpyArray
    :param entrada: Valor de entrada al sistema
    :type entrada: float
    :param metodo: Runge-Kutta a utilizar: DOPRI54, RKF45, etc.
    :type metodo: function
    :param ordenq: Valor del método de menor orden
    :type ordenq: int
    :param rtol: Tolerancia relativa
    :type rtol: float
    :param atol: Tolerancia absoluta
    :type atol: float
    :param max_step_increase: Máximo incremento del tamaño de paso
    :type max_step_increase: float
    :param min_step_decrease: Mínimo decremento del tamaño de paso
    :type min_step_decrease: float
    :param safety_factor: Factor de seguridad
    :type safety_factor: float
    """

    while True:
        # Para asegurar el tiempo máximo
        if tiempo + h_ant >= tbound:
            h_ant = tbound - tiempo
            yr, xr, xtemp = metodo(*systema, xVectr, h_ant, entrada)
            h_est = h_ant
        else:
            # Método embebido, la integración se continua con yr y xr
            yr, xr, xtemp = metodo(*systema, xVectr, h_ant, entrada)

            # Ajuste del tamaño de paso
            scale = atol + np.maximum(np.abs(xVectr), np.abs(xr)) * rtol
            delta1 = np.abs(xr - xtemp)
            error_norm = norm(delta1 / scale)

            if error_norm == 0:
                # Incremento máximo dado el bajo error
                h_est = h_ant * max_step_increase
            elif error_norm <= 1:
                # Incremento normal
                h_est = h_ant * min(max_step_increase,
                                    max(1, safety_factor * error_norm**(-1 / (ordenq+1))))
            else:
                # Decremento normal y se vuelve a calcular la salida
                h_ant = h_ant * min(
                    1,
                    max(min_step_decrease, safety_factor * error_norm**(-1 / (ordenq+1))))
                continue
        break
    return h_ant, h_est, yr, xr


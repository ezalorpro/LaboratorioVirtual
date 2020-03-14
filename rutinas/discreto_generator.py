""" 
Archivo para compilar las funciones encargadas de la simulación en tiempo discreto utilizando numba, las funciones quedan guardadas en el archivo: discreto_sim.cp37-win32.pyd y pueden ser importadas desde el archivo como una función de un modulo
"""
 

from numba.pycc import CC
import numpy as np


cc = CC('discreto_sim')


@cc.export('ss_discreta', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def ss_discreta(A, B, C, D, x, _, inputValue):
    """
    Función para calcular la respuesta del sistema por medio de la representacion discreta de las ecuaciones de espacio de estados
    
    :param ss: Representacion del sistema
    :type ss: LTI
    :param x: Vector de estado
    :type x: numpyArray
    :param _: No importa
    :type _: float
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float
    """
    x = np.dot(A, x) + B*inputValue
    y = np.dot(C, x) + D*inputValue

    return y[0, 0], x


@cc.export('PID_discreto', '(f8, f8, f8, f8[::1], f8, f8, f8)')
def PID_discreto(error, ts, s_integral, error_anterior, kp, ki, kd):
    """
    Función para calcular el PID en forma discreta
    
    :param error: Señal de error
    :type error: float
    :param ts: Periodo de muestreo
    :type ts: float
    :param s_integral: Acumulador de la señal integral
    :type s_integral: float
    :param error_anterior: deque con el error anterior
    :type error_anterior: deque Object
    :param kp: Ganancia proporcional
    :type kp: float
    :param ki: Ganancia integral
    :type ki: float
    :param kd: Ganancia derivativa
    :type kd: float
    """
    s_proporcional = error
    s_integral = s_integral + (error + error_anterior[0])*ts/2
    s_derivativa = (error - error_anterior[0]) / ts
    s_control = s_proporcional*kp + s_integral*ki + s_derivativa*kd
    error_anterior[0] = error
    
    return s_control, s_integral, error_anterior


@cc.export('derivadas_discretas', '(f8, f8, f8[::1])')
def derivadas_discretas(error, ts, error_anterior):
    """
    Función para calcular la derivada del error y la segunda derivada del error
    
    :param error: Señal de error
    :type error: float
    :param ts: Periodo de muestreo
    :type ts: float
    :param error_anterior: deque con el error anterior
    :type error_anterior: deque Object
    """
    s_derivativa = (error-error_anterior[0]) / ts
    s_derivativa2 = (error - 2 * error_anterior[0] + error_anterior[1]) / (ts**2)
    error_anterior[1] = error_anterior[0]
    error_anterior[0] = error
    
    return s_derivativa, s_derivativa2, error_anterior


if __name__ == '__main__':
    cc.compile()
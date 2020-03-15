""" 
Archivo para compilar los Runge-kutta explícitos y embebidos utilizando numba, los metodos quedan guardados en el archivo: metodos_RK.cp37-win32.pyd o metodos_RK.cpython-37m-x86_64-linux-gnu.so dependiendo del sistema operativo utilizado y pueden ser importados como un modulo cualquiera y utilizar las funciones allí definidas. 
"""


from numba.pycc import CC
import numpy as np


cc = CC('metodos_RK')


@cc.export('norm', 'f8(f8[:,::1])')
def norm(x):
    """
    Función para calcular la norma RMS de un vector. Función tomada de SciPy
    
    :param x: Vector
    :type x: numpyArray
    :return: Norma rms del vector ingresado
    :rtype: float
    """
    return np.linalg.norm(x) / x.size**0.5


@cc.export('dopri54', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def dopri54(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta embebido de Dormand-Prince 5(4), la integración se continua con la salida de orden 5, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """
    k1 = h*(np.dot(A, x) + B*inputValue)
    k2 = h*(np.dot(A, x + k1/5) + B*inputValue)
    k3 = h*(np.dot(A, x + k1*3/40 + k2*9/40) + B*inputValue)
    k4 = h*(np.dot(A, x + k1*44/45 - k2*56/15 + k3*32/9) + B*inputValue)
    k5 = h*(np.dot(A, x + k1*19372/6561 - k2*25360/2187 + k3*64448/6561 - k4*212/729) +
            B*inputValue)
    k6 = h*(np.dot(A, x + k1*9017/3168 - k2*355/33 + k3*46732/5247 + k4*49/176 - k5*5103/18656) +
            B*inputValue)
    k7 = h*(np.dot(A, x + k1*35/384 + k3*500/1113 + k4*125/192 - k5*2187/6784 + k6*11/84) +
            B*inputValue)

    x5th = x + (k1*35/384 + k3*500/1113 + k4*125/192 - k5*2187/6784 + k6*11/84)
    x4th = x + (k1*5179/57600 + k3*7571/16695 + k4*393/640 - k5*92097/339200 +
                k6*187/2100 + k7/40)
    y5th = np.dot(C, x5th) + D*inputValue

    return y5th[0, 0], x5th, x4th


@cc.export('cash_karp45', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def cash_karp45(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta embebido de Cash-Karp 4(5), la integración se continua con la salida de orden 4, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """

    k1 = h*(np.dot(A, x) + B*inputValue)
    k2 = h*(np.dot(A, x + k1/5) + B*inputValue)
    k3 = h*(np.dot(A, x + k1*3/40 + k2*9/40) + B*inputValue)
    k4 = h*(np.dot(A, x + k1*3/10 - k2*9/10 + k3*6/5) +B*inputValue)
    k5 = h*(np.dot(A, x - k1*11/54 + k2*5/2 - k3*70/27 + k4*35/27) + B*inputValue)
    k6 = h*(np.dot(A, x + k1*1631/55296 + k2*175/512 + k3*575/13824 + k4*44275/110592 +
                   k5*253/4096) + B*inputValue)

    x5th = x + (k1*37/378 + k3*250/621 + k4*125/594 + k6*512/1771)
    x4th = x + (k1*2825/27648 + k3*18575/48384 + k4*13525/55296 + k5*277/14336 + k6/4)
    y4th = np.dot(C, x4th) + D*inputValue

    return y4th[0, 0], x4th, x5th


@cc.export('fehlberg45', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def fehlberg45(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta embebido de Fehlberg 4(5), la integración se continua con la salida de orden 4, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """

    k1 = h*(np.dot(A, x) + B*inputValue)
    k2 = h*(np.dot(A, x + k1/4) + B*inputValue)
    k3 = h*(np.dot(A, x + k1*3/32 + k2*9/32) + B*inputValue)
    k4 = h*(np.dot(A, x + k1*1932/2197 - k2*7200/2197 + k3*7296/2197) + B*inputValue)
    k5 = h*(np.dot(A, x + k1*439/216 - k2*8 + k3*3680/513 - k4*845/4104) + B*inputValue)
    k6 = h*(np.dot(A, x - k1*8/27 + k2*2 - k3*3544/2565 + k4*1859/4104 - k5*11/40) +
            B*inputValue)

    x5th = x + (k1*16/135 + k3*6656/12825 + k4*28561/56430 - k5*9/50 + k6*2/55)
    x4th = x + (k1*25/216 + k3*1408/2565 + k4*2197/4104 - k5/5)
    y4th = np.dot(C, x4th) + D*inputValue

    return y4th[0, 0], x4th, x5th


@cc.export('bogacki_shampine23', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def bogacki_shampine23(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta embebido de Bogacki-Shampine 3(2), la integración se continua con la salida de orden 3, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """

    k1 = h*(np.dot(A, x) + B*inputValue)
    k2 = h*(np.dot(A, x + k1/2) + B*inputValue)
    k3 = h*(np.dot(A, x + k2*3/4) + B*inputValue)
    k4 = h*(np.dot(A, x + k1*2/9 + k2/3 + k3*4/9) + B*inputValue)

    x3th = x + (k1*2/9 + k2/3 + k3*4/9)
    x2th = x + (k1*7/24 + k2/4 + k3/3 + k4/8)
    y2th = np.dot(C, x3th) + D*inputValue

    return y2th[0, 0], x3th, x2th


@cc.export('runge_kutta5', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def runge_kutta5(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta de orden 5, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """
    
    k1 = h*(np.dot(A, x) + B*inputValue)
    k2 = h*(np.dot(A, x + k1/4) + B*inputValue)
    k3 = h*(np.dot(A, x + k1/8 + k2/8) + B*inputValue)
    k4 = h*(np.dot(A, x - k2/2 + k3) + B*inputValue)
    k5 = h*(np.dot(A, x + k1*3/16 + k4*9/16) + B*inputValue)
    k6 = h*(np.dot(A, x - k1*3/7 + k2*2/7 + k3*12/7 - k4*12/7 + k5*8/7) + B*inputValue)

    x = x + (k1*7/90 + k3*32/90 + k4*12/90 + k5*32/90 + k6*7/90)
    y = np.dot(C, x) + D*inputValue

    return y[0, 0], x


@cc.export('ralston4', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def ralston4(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta Ralston con mínimo error de truncamiento de orden 4, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """

    k1 = h*(np.dot(A, x) + B*inputValue)
    k2 = h*(np.dot(A, x + k1*0.4) + B*inputValue)
    k3 = h*(np.dot(A, x + k1*0.29697761 + k2*0.15875964) + B*inputValue)
    k4 = h*(np.dot(A, x + k1*0.21810040 - k2*3.05096516 + k3*3.83286476) + B*inputValue)

    x = x + (k1*0.17476028 - k2*0.55148066 + k3*1.20553560 + k4*0.17118478)
    y = np.dot(C, x) + D*inputValue

    return y[0, 0], x


@cc.export('tres_octavos4', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def tres_octavos4(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta 3/8 de orden 4, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """

    k1 = h*(np.dot(A, x) + B*inputValue)
    k2 = h*(np.dot(A, x + k1/3) + B*inputValue)
    k3 = h*(np.dot(A, x - k1/3 + k2) + B*inputValue)
    k4 = h*(np.dot(A, x + k1 - k2 + k3) + B*inputValue)

    x = x + (k1/8 + k2*3/8 + k3*3/8 + k4/8)
    y = np.dot(C, x) + D*inputValue

    return y[0, 0], x


@cc.export('runge_kutta4', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def runge_kutta4(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta de orden 4, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """

    k1 = h*(np.dot(A, x) + B * inputValue)
    k2 = h*(np.dot(A, x + k1/2) + B * inputValue)
    k3 = h*(np.dot(A, x + k2/2) + B * inputValue)
    k4 = h*(np.dot(A, x + k3) + B * inputValue)

    x = x + (k1/6 + k2/3 + k3/3 + k4/6)
    y = np.dot(C, x) + D*inputValue

    return y[0, 0], x


@cc.export('SSPRK3', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def SSPRK3(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta con preservado de estabilidad fuerte de orden 3, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """

    k1 = h*(np.dot(A, x) + B * inputValue)
    k2 = h*(np.dot(A, x + k1) + B * inputValue)
    k3 = h*(np.dot(A, x + k1/4 + k2/4) + B*inputValue)

    x = x + (k1/6 + k2/6 + k3*2/3)
    y = np.dot(C, x) + D*inputValue

    return y[0, 0], x


@cc.export('ralston3', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def ralston3(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta Ralston de orden 3, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """

    k1 = h*(np.dot(A, x) + B * inputValue)
    k2 = h*(np.dot(A, x + k1/2) + B * inputValue)
    k3 = h*(np.dot(A, x + k2*3/4) + B*inputValue)

    x = x + (k1*2/9 + k2/3 + k3*4/9)
    y = np.dot(C, x) + D*inputValue

    return y[0, 0], x


@cc.export('heun3', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def heun3(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta Heun de orden 3, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """

    k1 = h*(np.dot(A, x) + B * inputValue)
    k2 = h*(np.dot(A, x + k1/3) + B * inputValue)
    k3 = h*(np.dot(A, x + k2*2/3) + B*inputValue)

    x = x + (k1/4 + k3*3/4)
    y = np.dot(C, x) + D*inputValue

    return y[0, 0], x


@cc.export('runge_kutta3', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def runge_kutta3(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta de orden 3, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """

    k1 = h*(np.dot(A, x) + B * inputValue)
    k2 = h*(np.dot(A, x + k1/2) + B * inputValue)
    k3 = h*(np.dot(A, x - k1 + k2*2) + B*inputValue)

    x = x + (k1/6 + k2*2/3 + k3/6)
    y = np.dot(C, x) + D*inputValue

    return y[0, 0], x


@cc.export('runge_kutta2', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
def runge_kutta2(A, B, C, D, x, h, inputValue):
    """
    Runge-Kutta de orden 2, en el método se asumió entrada constante, por lo que se descarta t + h*cs
    
    :param A: Matriz de estados
    :type A: float64, 2d, F
    :param B: Matriz de entrada
    :type B: float64, 2d, C
    :param C: Matriz de salida
    :type C: float64, 2d, C
    :param D: Matriz de transmisión directa
    :type D: float64, 2d, C
    :param x: Vector de estado
    :type x: float64, 2d, C
    :param h: Tamaño de paso
    :type h: float64
    :param inputValue: Valor de entrada al sistema
    :type inputValue: float64
    """

    k1 = h*(np.dot(A, x) + B * inputValue)
    k2 = h*(np.dot(A, x + k1/2) + B * inputValue)

    x = x + k2
    y = np.dot(C, x) + D*inputValue

    return y[0, 0], x


if __name__ == '__main__':
    cc.compile()
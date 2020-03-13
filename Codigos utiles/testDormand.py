import numpy as np
import control as ctrl
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
import time
import copy
import pickle
# from metodos_RK import dopri54

def dopri54(A, B, C, D, x, h, inputValue, fun, tiempo, tval, yval):
    k1 = h*(np.dot(A, x) + B*inputValue)
    k2 = h*(np.dot(A, x + k1/5) + B*fun(tiempo+h/5))
    k3 = h*(np.dot(A, x + k1*3/40 + k2*9/40) + B*fun(tiempo+h*3/10))
    k4 = h*(np.dot(A, x + k1*44/45 - k2*56/15 + k3*32/9) + B*fun(tiempo+h*4/5))
    k5 = h*(np.dot(A, x + k1*19372/6561 - k2*25360/2187 + k3*64448/6561 - k4*212/729) +
         B*fun(tiempo+h*8/9))
    k6 = h*(np.dot(A, x + k1*9017/3168 - k2*355/33 + k3*46732/5247 + k4*49/176 -
         k5*5103/18656) + B*fun(tiempo + h))
    k7 = h*(np.dot(A, x + k1*35/384 + k3*500/1113 + k4*125/192 - k5*2187/6784 + k6*11/84) +
         B*fun(tiempo + h))


    x5th = x + (k1*35/384 + k3*500/1113 + k4*125/192 - k5*2187/6784 + k6*11/84)
    x4th = x + (k1*5179/57600 + k3*7571/16695 + k4*393/640 - k5*92097/339200 + k6*187/2100 + k7/40)
    y5th = np.dot(C, x5th) + D*inputValue

    return y5th, x5th, x4th


def dopri54t(A, B, C, D, x, h, inputValue, fun, tiempo, *args):
    k1 = h*(np.dot(A, x) + B*inputValue)
    k2 = h*(np.dot(A, x + k1/5) + B*inputValue)
    k3 = h*(np.dot(A, x + k1*3/40 + k2*9/40) + B*inputValue)
    k4 = h*(np.dot(A, x + k1*44/45 - k2*56/15 + k3*32/9) + B*inputValue)
    k5 = h*(np.dot(A, x + k1*19372/6561 - k2*25360/2187 + k3*64448/6561 - k4*212/729) +
         B*inputValue)
    k6 = h*(np.dot(A, x + k1*9017/3168 - k2*355/33 + k3*46732/5247 + k4*49/176 -
         k5*5103/18656) + B*inputValue)
    k7 = h*(np.dot(A, x + k1*35/384 + k3*500/1113 + k4*125/192 - k5*2187/6784 + k6*11/84) +
         B*inputValue)

    y5th = np.dot(C, x) + D * inputValue
    x5th = x + (k1*35/384 + k3*500/1113 + k4*125/192 - k5*2187/6784 + k6*11/84)
    x4th = x + (k1*5179/57600 + k3*7571/16695 + k4*393/640 - k5*92097/339200 + k6*187/2100 + k7/40)

    return y5th, x5th, x4th

def runge_kutta2(A, B, C, D, x, h, inputValue, fun, tiempo, *args):
    k1 = h * (np.dot(A, x) + B*inputValue)
    k2 = h * (np.dot(A, x + k1/2) + B*fun(tiempo+h/2))

    x = x + k2
    y = np.dot(C, x) + D*inputValue

    return y, x, 1

def runge_kutta2t2(A, B, C, D, x, h, inputValue, fun, tiempo, tval, yval):
    k1 = h * (np.dot(A, x) + B*inputValue)
    k2 = h * (np.dot(A, x + k1/2) + B*linfunction(tiempo+h/2, *tval, *yval))

    x = x + k2
    y = np.dot(C, x) + D*inputValue

    return y, x, 1

def runge_kutta2t(A, B, C, D, x, h, inputValue, fun, tiempo, *args):
    k1 = h * (np.dot(A, x) + B*inputValue)
    k2 = h * (np.dot(A, x + k1/2) + B*inputValue)

    x = x + k2
    y = np.dot(C, x) + D*inputValue

    return y, x, 1

def runge_kutta5(A, B, C, D, x, h, inputValue, fun, tiempo, *args):  # Mejor: rtol = 1e-3, atol = 5e-6
    k1 = h*(np.dot(A, x) + B*inputValue)
    k2 = h*(np.dot(A, x + k1/ 4) + B*inputValue)
    k3 = h*(np.dot(A, x + k1/8 + k2/8) + B*inputValue)
    k4 = h*(np.dot(A, x - k2/2 + k3) + B*inputValue)
    k5 = h*(np.dot(A, x - k1*3/ 16 + k4*9 / 16) + B*inputValue)
    k6 = h*(np.dot(A, x + -k1*3 / 7 + k2*2 / 7 + k3*12/7 - k4*12/7 + k5*8/ 7) +
            B*inputValue)

    y = np.dot(C, x) + D*inputValue
    x = x + (k1*7 / 90 + k3*32/90 + k4*12/90 +
                k5*32/90 + k6*7/90)
    return y, x , 1

def linfunction(xn, x1, x2, y1, y2):
    if x1 == 0 and x2 == 0:
        return 0
    yn = (y2 - y1)/(x2-x1)*(xn - x2) + y2
    plt.plot([x2, xn], [y2, yn], 'b')
    return yn

def norm(x):
    """Compute RMS norm."""
    x = np.asarray(x)
    x = x.ravel()
    return np.sqrt(np.dot(x,x)) / x.size**0.5

def nula(a):
    return 1

def ejecutar():
    N = 100.0
    kp = 1.0
    ki = 1.0
    kd = 1.0

    pid = ctrl.tf2ss(ctrl.TransferFunction([N*kd + kp, N*kp + ki, N * ki], [1.0, N, 0.0]))

    x_pidB = np.zeros_like(pid.B).astype('float64')
    A2, B2, C2, D2 = pid.A.astype('float64'), pid.B.astype('float64'), pid.C.astype('float64'), pid.D.astype('float64')

    sistema = ctrl.tf2ss(ctrl.TransferFunction([1], [1, 1, 1]))
    A1, B1, C1, D1 = sistema.A.astype('float64'), sistema.B.astype('float64'), sistema.C.astype('float64'), sistema.D.astype('float64')
    vstadosB = np.zeros_like(sistema.B).astype('float64')

    min_step_decrease = 0.2
    max_step_increase = 5
    h_ant = 0.000001
    rtol = 1e-6
    atol = 1e-6
    tiempo = 0.0
    tbound = 30
    sp = 1
    salida = [0]
    tiempo_out = [0]
    yb = 0
    sf1 = 0.9
    counter = 0.0
    sc_t = [0]
    error_ac = [0]

    with open('dataDormand.pkl', 'rb') as f:
        dataT, dataSc, dataError = pickle.load(f)

    print(dataError)
    funcion1 = interp1d(dataT, dataSc, fill_value="extrapolate")
    funcion2 = interp1d(dataT, dataError, fill_value="extrapolate")
    # 3.84, 7.24
    #  runge_kutta2
    RK = dopri54

    def nula2(b):
        return error

    outboleta = [50]
    start = time.time()
    while tiempo < tbound:
        counter += 1
        error = sp - yb
        while True:
            if tiempo + h_ant >= tbound:
                h_ant = tbound - tiempo

            ypidb, x_five, x_four = RK(A2, B2, C2, D2, x_pidB, h_ant, error, funcion2, tiempo, 1, 1)

            scale = atol + np.maximum(np.abs(x_five), np.abs(x_pidB)) * rtol
            # scale = atol + rtol * (np.abs(x_five) + np.abs(x_pidB)) / 2
            delta1 = np.abs(x_five - x_four)
            error_norm = norm(delta1/scale)

            if error_norm == 0:
                h_est = h_ant * max_step_increase
            elif error_norm <= 1:
                h_est = h_ant * min(max_step_increase, max(1, sf1 * error_norm**(-1 / (4+1))))
            else:
                h_ant = h_ant * min(1, max(min_step_decrease, sf1 * error_norm**(-1 / (4+1))))
                continue

            error_ac.append(error_norm)
            sc_t.append(ypidb)
            yb, vstadosB, _ = RK(A1, B1, C1, D1, vstadosB, h_ant, ypidb, funcion1, tiempo, 1, 1)
            break

        print(tiempo)
        salida.append(yb)
        tiempo += h_ant
        tiempo_out.append(tiempo)
        h_ant = h_est
        x_pidB = x_five

    print(counter)
    print(len(tiempo_out))
    transcurrido = time.time() - start
    print(transcurrido)
    plt.plot(tiempo_out, salida)
    # with open('dataDormand.pkl', 'wb', ) as f:
    #     pickle.dump([t, y], f)


if __name__ == '__main__':
    ejecutar()
    plt.grid()
    plt.show()
import numpy as np
import control as ctrl
from matplotlib import pyplot as plt
from scipy.integrate import RK45
# from my_module import dopri5
# from numba.pycc import CC
import time
from numba import jit
import numba
import copy

# cc = CC('my_module')

# @cc.export('dopri5', '(f8[::1,:], f8[:,::1], f8[:,::1], f8[:,::1], f8[:,::1], f8, f8)')
@jit
def dopri5(A, B, C, D, x, h, inputValue):
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

    x5th = x + (k1*35/384 + k3*500/1113 + k4*125/192 - k5*2187/6784 + k6*11/84)
    x4th = x + (k1*5179/57600 + k3*7571/16695 + k4*393/640 - k5*92097/339200 + k6*187/2100 + k7/40)
    y5th = np.dot(C, x) + D*inputValue

    return y5th[0, 0], x5th, x4th


def fehlberg45(A, B , C, D, x, h, inputValue):
    k1 = np.dot(h, (np.dot(A, x) + np.dot(B, inputValue)))
    k2 = np.dot(h, (np.dot(A, (x + np.dot(k1, 1 / 4))) + np.dot(B, inputValue)))
    k3 = np.dot(h,
                (np.dot(A, (x + np.dot(k1, 3 / 32) + np.dot(k2, 9 / 32))) +
                 np.dot(B, inputValue)))
    k4 = np.dot(h,
                (np.dot(A,
                        (x + np.dot(k1, 1932 / 2197) + np.dot(k2, -7200 / 2197) +
                         np.dot(k3, 7296 / 2197))) + np.dot(B, inputValue)))
    k5 = np.dot(
        h,
        (np.dot(A,
                (x + np.dot(k1, 439 / 216) + np.dot(k2, -8) + np.dot(k3, 3680 / 513) +
                 np.dot(k4, -845 / 4104))) + np.dot(B, inputValue)))
    k6 = np.dot(
        h,
        (np.dot(A,
                (x + np.dot(k1, -8 / 27) + np.dot(k2, 2) + np.dot(k3, -3544 / 2565) +
                 np.dot(k4, 1859 / 4104) + np.dot(k5, -11 / 40))) +
         np.dot(B, inputValue)))

    y4th = C * x + D * inputValue

    x5th = x + (np.dot(k1, 16 / 135) + np.dot(k3, 6656 / 12825) +
                np.dot(k4, 28561 / 56430) + np.dot(k5, -9 / 50) + np.dot(k6, 2 / 55))

    x4th = x + (np.dot(k1, 25 / 216) + np.dot(k3, 1408 / 2565) + np.dot(k4, 2197 / 4104) +
                np.dot(k5, -1 / 5))


    return y4th.item(), x4th, x5th


@jit
def bogacki_shampine23(ss, x, h, inputValue):
    k1 = np.dot(h, (np.dot(ss.A, x) + np.dot(ss.B, inputValue)))
    k2 = np.dot(h, (np.dot(ss.A, (x + np.dot(k1, 1 / 2))) + np.dot(ss.B, inputValue)))
    k3 = np.dot(h,
                (np.dot(ss.A, (x + np.dot(k2, 3 / 4))) +
                 np.dot(ss.B, inputValue)))
    k4 = np.dot(h,
                (np.dot(ss.A,
                        (x + np.dot(k1, 2/9) + np.dot(k2, 1/3) +
                         np.dot(k3, 4/9))) + np.dot(ss.B, inputValue)))

    y2th = ss.C * x + ss.D * inputValue

    x3th = x + (np.dot(k1, 2 / 9) + np.dot(k2, 1 / 3) + np.dot(k3, 4 / 9))

    x2th = x + (np.dot(k1, 7/24) + np.dot(k2, 1/4) + np.dot(k3, 1/3) +
                np.dot(k4, 1/8))

    return y2th.item(), x2th, x3th

@jit
def cash_karp(ss, x, h, inputValue):
    k1 = np.dot(h, (np.dot(ss.A, x) + np.dot(ss.B, inputValue)))
    k2 = np.dot(h, (np.dot(ss.A, (x + np.dot(k1, 1 / 5))) + np.dot(ss.B, inputValue)))
    k3 = np.dot(h,
                (np.dot(ss.A, (x + np.dot(k1, 3 / 40) + np.dot(k2, 9 / 40))) +
                 np.dot(ss.B, inputValue)))
    k4 = np.dot(h,
                (np.dot(ss.A,
                        (x + np.dot(k1, 3/10) + np.dot(k2, -9/10) +
                         np.dot(k3, 6/5))) + np.dot(ss.B, inputValue)))
    k5 = np.dot(
        h,
        (np.dot(ss.A,
                (x + np.dot(k1, -11/54) + np.dot(k2, 5/2) + np.dot(k3, -70/27) +
                 np.dot(k4, 35/27))) + np.dot(ss.B, inputValue)))
    k6 = np.dot(h,
                (np.dot(ss.A,
                        (x + np.dot(k1, 1631 / 55296) + np.dot(k2, 175 / 512) +
                         np.dot(k3, 575 / 13824) + np.dot(k4, 44275 / 110592) +
                         np.dot(k5, 253 / 4096))) + np.dot(ss.B, inputValue)))

    y4th = ss.C * x + ss.D * inputValue

    x5th = x + (np.dot(k1, 37 / 378) + np.dot(k3, 250 / 621) + np.dot(k4, 125 / 594) + np.dot(k6, 512 / 1771))

    x4th = x + (np.dot(k1, 2825 / 27648) + np.dot(k3, 18575 / 48384) +
                np.dot(k4, 13525 / 55296) + np.dot(k5, 277 / 14336) + np.dot(k6, 1 / 4))

    return y4th.item(), x4th, x5th


# @jit
def norm(x):
    """Compute RMS norm."""
    x = np.asarray(x)
    x = x.ravel()
    return np.sqrt(np.dot(x,x)) / x.size**0.5


def ejecutar(orden=5):
    N = 100.0
    kp = 1.0
    ki = 1.0
    kd = 1.0

    pid = ctrl.tf2ss(ctrl.TransferFunction([N*kd + kp, N*kp + ki, N * ki], [1.0, N, 0.0]))

    # pid = ctrl.tf2ss(
    #     ctrl.TransferFunction([1], [0.01, 1]) *
    #     ctrl.TransferFunction([N*kd + kp, N*kp + ki, N * ki], [1, N, 0]))

    # pid = ctrl.tf2ss(ctrl.TransferFunction([1], [10/(N*kd), 1])*
    #         ctrl.TransferFunction([N * kd + kp, N * kp + ki, N * ki],
    #                             [1, N, 0]))

    # pid = ctrl.tf2ss(
    #     ctrl.TransferFunction([
    #         10 * kp,
    #         N**2 * kd**2 + N*kd*kp + 10*N*kp + 10*ki,
    #         N**2 * kd * kp + kd*N*ki + 10*N*ki,
    #         N**2 * kd * ki
    #     ], [10, 10*N + N*kd, N**2 * kd, 0]))

    x_pidB = np.zeros_like(pid.B).astype('float64')
    A2, B2, C2, D2 = pid.A.astype('float64'), pid.B.astype('float64'), pid.C.astype('float64'), pid.D.astype('float64')

    sistema = ctrl.tf2ss(ctrl.TransferFunction([1], [1, 1, 1]))
    A1, B1, C1, D1 = sistema.A.astype('float64'), sistema.B.astype('float64'), sistema.C.astype('float64'), sistema.D.astype('float64')
    vstadosB = np.zeros_like(sistema.B).astype('float64')

    min_step_decrease = 0.2
    max_step_increase = 5
    h_ant = 0.000001
    rtol = 1e-4
    atol = 1e-6
    tiempo = 0.0
    tbound = 30
    sp = 1
    salida = []
    tiempo_out = []
    yb = 0
    sf1 = 0.8
    counter = 0.0
    sc_t = []
    ypidb = 0
    # dopri5
    # fehlberg45dot
    RK = dopri5

    start = time.time()
    while tiempo < tbound:
        sc_t.append(ypidb)
        yb, vstadosB, _ = RK(A1, B1, C1, D1, vstadosB, h_ant, ypidb)
        salida.append(yb)
        error = sp - yb
        while True:
            counter += 1

            if tiempo + h_ant >= tbound:
                h_ant = tbound - tiempo

            ypidb, x_five, x_four = RK(A2, B2, C2, D2, x_pidB, h_ant, error)

            scale = atol + np.maximum(np.abs(x_five), np.abs(x_pidB)) * rtol
            delta1 = np.abs(x_five - x_four)
            error_norm = norm(delta1/scale)

            if error_norm == 0:
                h_est = h_ant * max_step_increase
            elif error_norm < 1 :
                h_est = h_ant * min(
                    max_step_increase, max(1, sf1 * error_norm**(-1 / (orden+1))))
            else:
                h_ant = h_ant * min(
                    1, max(min_step_decrease, sf1 * error_norm**(-1 / (orden+1))))
                continue
            break

        sp = 1
        print(tiempo)
        tiempo += h_ant
        tiempo_out.append(tiempo)
        h_ant = h_est
        x_pidB = x_five

    print(counter)
    print(len(tiempo_out))
    transcurrido = time.time() - start
    print(transcurrido)
    plt.plot(tiempo_out, salida)

    # tf = ctrl.tf([1], [1, 1, 1])
    # t = np.linspace(0, tbound, 200)
    # pid = ctrl.TransferFunction([N*kd + kp, N*kp + ki, N * ki], [1, N, 0])
    # tf = ctrl.feedback(pid*tf)
    # t, y = ctrl.step_response(tf, t)
    # plt.plot(t, y)
    # plt.grid()
    # plt.show()

    # plt.plot(tiempo_out, sc_t)
    # plt.grid()
    # plt.show()

    # plt.plot(tiempo_out, error_ac)
    # plt.grid()
    # plt.show()


if __name__ == '__main__':
    ejecutar(orden=4)
    plt.show()
    # cc.compile()

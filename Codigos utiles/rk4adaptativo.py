import numpy as np
import control as ctrl
from matplotlib import pyplot as plt
from numba import jit
import time
from math import factorial
import pickle



def norm(x):
    """Compute RMS norm."""
    return np.linalg.norm(x) / x.size**0.5

def tres_octavos4(ss, x, h, inputValue):
    k1 = np.dot(h, (np.dot(ss.A, x) + np.dot(ss.B, inputValue)))
    k2 = np.dot(h, (np.dot(ss.A, (x + np.dot(k1, 1 / 3))) + np.dot(ss.B, inputValue)))
    k3 = np.dot(h,
                (np.dot(ss.A,
                        (x + np.dot(k1, -1 / 3) + k2)) + np.dot(ss.B, inputValue)))
    k4 = np.dot(h, (np.dot(ss.A, (x + k1 - k2 + k3)) + np.dot(ss.B, inputValue)))

    y = np.dot(ss.C, x) + np.dot(ss.D, inputValue)
    x = x + (np.dot(k1, 1 / 8) + np.dot(k2, 3 / 8) + np.dot(k3, 3 / 8) +
                np.dot(k4, 1 / 8))

    return y.item(), x

@jit(nopython=True)
def runge_kutta2(A, B, C, D, x, h, inputValue):
    k1 = h * (np.dot(A, x) + B*inputValue)
    k2 = h * (np.dot(A, x + k1/2) + B*inputValue)

    y = np.dot(C, x) + D*inputValue
    x = x + k2

    return y, x


@jit(nopython=True)
def runge_kutta2a(A, B, C, D, x, h, inputValue):
    k1 = h * (np.dot(A, x) + B*inputValue)
    k2 = h * (np.dot(A + k1/2, x + k1/2) + B*inputValue)

    y = np.dot(C, x) + D*inputValue
    x = x + k2

    return y, x

def runge_kutta3(ss, x, h, inputValue):
    k1 = np.dot(h, (np.dot(ss.A, x) + np.dot(ss.B, inputValue)))
    k2 = np.dot(h, (np.dot(ss.A, (x + np.dot(k1, 1 / 2))) + np.dot(ss.B, inputValue)))
    k3 = np.dot(h, (np.dot(ss.A,
                            (x - k1 + np.dot(k2, 2))) + np.dot(ss.B, inputValue)))

    y = np.dot(ss.C, x) + np.dot(ss.D, inputValue)
    x = x + (np.dot(k1, 1 / 6) + np.dot(k2, 2 / 3) + np.dot(k3, 1 / 6))

    return y.item(), x


def runge_kutta4(A, B, C, D, x, h, inputValue):
    k1 = h*(np.dot(A, x) + B * inputValue)
    k2 = h*(np.dot(A, x + k1/4) + B * inputValue)
    k3 = h*(np.dot(A, x + k2/4) + B * inputValue)
    k4 = h*(np.dot(A, x + k3/2) + B * inputValue)

    y = np.dot(C, x) + D*inputValue
    x = x + (k1/12 + k2/6 + k3/6 + k4/12)
    return y, x


@jit(nopython=True)
def runge_kutta5(A, B, C, D, x, h, inputValue):  # Mejor: rtol = 1e-3, atol = 5e-6
    k1 = h*(np.dot(A, x) + B*inputValue)
    k2 = h*(np.dot(A, x + k1/4) + B*inputValue)
    k3 = h*(np.dot(A, x + k1/8 + k2/8) + B*inputValue)
    k4 = h*(np.dot(A, x - k2/2 + k3) + B*inputValue)
    k5 = h*(np.dot(A, x + k1*3/ 16 + k4*9 / 16) + B*inputValue)
    k6 = h*(np.dot(A, x - k1*3 / 7 + k2*2 / 7 + k3*12/7 - k4*12/7 + k5*8/ 7) +
            B*inputValue)

    y = np.dot(C, x) + D*inputValue
    x = x + (k1*7 / 90 + k3*32/90 + k4*12/90 +
                k5*32/90 + k6*7/90)
    return y, x

@jit(nopython=True)
def runge_kutta5a(A, B, C, D, x, h, inputValue):  # Mejor: rtol = 1e-3, atol = 5e-6
    k1 = h*(np.dot(A, x) + B*inputValue)
    k2 = h*(np.dot(A, x + k1/2) + B*inputValue)
    k3 = h*(np.dot(A, x + k2/2) + B*inputValue)
    k4 = h*(np.dot(A, x + k3*3/4) + B*inputValue)
    k5 = h*(np.dot(A, x + k4*4/5) + B*inputValue)
    k6 = h*(np.dot(A, x + k5*5/6) + B*inputValue)

    y = np.dot(C, x) + D*inputValue
    x = x + (k1*7 / 90 + k3*32/90 + k4*12/90 +
                k5*32/90 + k6*7/90)
    return y, x

def heun3(ss, x, h, inputValue):
    k1 = np.dot(h, (np.dot(ss.A, x) + np.dot(ss.B, inputValue)))
    k2 = np.dot(h, (np.dot(ss.A, (x + np.dot(k1, 1 / 3))) + np.dot(ss.B, inputValue)))
    k3 = np.dot(h, (np.dot(ss.A, (x + np.dot(k2, 2 / 3))) + np.dot(ss.B, inputValue)))

    y = np.dot(ss.C, x) + np.dot(ss.D, inputValue)
    x = x + (np.dot(k1, 1 / 4) + np.dot(k3, 3 / 4))

    return y.item(), x

def ralston4(ss, x, h, inputValue):  # Mejor: rtol = 1e-5, atol = 5e-6
    k1 = np.dot(h, (np.dot(ss.A, x) + np.dot(ss.B, inputValue)))
    k2 = np.dot(h, (np.dot(ss.A, (x + np.dot(k1, 0.4))) + np.dot(ss.B, inputValue)))
    k3 = np.dot(h,
                (np.dot(ss.A, (x + np.dot(k1, 0.29697761) + np.dot(k2, 0.15875964))) +
                    np.dot(ss.B, inputValue)))
    k4 = np.dot(h,
                (np.dot(ss.A,
                        (x + np.dot(k1, 0.21810040) + np.dot(k2, -3.05096516) +
                            np.dot(k3, 3.83286476))) + np.dot(ss.B, inputValue)))

    y = np.dot(ss.C, x) + np.dot(ss.D, inputValue)
    x = x + (np.dot(k1, 0.17476028) + np.dot(k2, -0.55148066) +
                np.dot(k3, 1.20553560) + np.dot(k4, 0.17118478))

    return y.item(), x

def ralston3(ss, x, h, inputValue):
    k1 = np.dot(h, (np.dot(ss.A, x) + np.dot(ss.B, inputValue)))
    k2 = np.dot(h, (np.dot(ss.A, (x + np.dot(k1, 1/2))) + np.dot(ss.B, inputValue)))
    k3 = np.dot(h, (np.dot(ss.A, (x + np.dot(k2, 3/4))) + np.dot(ss.B, inputValue)))

    y = np.dot(ss.C, x) + np.dot(ss.D, inputValue)
    x = x + (np.dot(k1, 2 / 9) + np.dot(k2, 1 / 3) + np.dot(k3, 4 / 9))

    return y.item(), x

def SSPRK3(ss, x, h, inputValue):
    k1 = np.dot(h, (np.dot(ss.A, x) + np.dot(ss.B, inputValue)))
    k2 = np.dot(h, (np.dot(ss.A, (x + k1)) + np.dot(ss.B, inputValue)))
    k3 = np.dot(h, (np.dot(ss.A, (x + np.dot(k1, 1/4) + np.dot(k2, 1/4))) + np.dot(ss.B, inputValue)))

    y = np.dot(ss.C, x) + np.dot(ss.D, inputValue)
    x = x + (np.dot(k1, 1 / 6) + np.dot(k2, 1 / 6) + np.dot(k3, 2 / 3))

    return y.item(), x


def ejecutar(figindex=0, kp=1, ki=1, kd=1, metodo=runge_kutta2, orden=2):

    N = 100

    pid = ctrl.tf2ss(
    ctrl.TransferFunction([N * kd + kp, N * kp + ki, N * ki],
                        [1, N, 0]))

    # pid = ctrl.tf2ss(ctrl.TransferFunction([1], [10/(N*kd), 1])*
    #     ctrl.TransferFunction([N * kd + kp, N * kp + ki, N * ki],
    #                         [1, N, 0]))

    # pid = ctrl.tf2ss(
    #     ctrl.TransferFunction(
    #         [kp, N**2 * kd + 2*N*kp + ki, N**2 * kp + 2*N*ki, N**2 * ki],
    #         [1, 2 * N, N**2, 0]))

    # pid = ctrl.tf2ss(
    #     ctrl.TransferFunction([
    #         10 * kp,
    #         N**2 * kd**2 + N*kd*kp + 10*N*kp + 10*ki,
    #         N**2*kd * kp + kd*N*ki + 10*N*ki,
    #         N**2 * kd * ki
    #     ], [10, 10*N + N*kd, N**2 * kd, 0]))

    x_pidB = np.zeros_like(pid.B).astype('float64')
    x_pidS = np.zeros_like(pid.B).astype('float64')
    A2, B2, C2, D2 = pid.A.astype('float64'), pid.B.astype('float64'), pid.C.astype('float64'), pid.D.astype('float64')

    num = [1]
    dem = [1, 1, 1]

    sistema = ctrl.tf2ss(ctrl.TransferFunction(num, dem))
    A1, B1, C1, D1 = sistema.A.astype('float64'), sistema.B.astype('float64'), sistema.C.astype('float64'), sistema.D.astype('float64')
    vstadosB = np.zeros_like(sistema.B).astype('float64')

    min_step_decrease = 0.2
    max_step_increase = 5
    h_ant = 0.0000001
    rtol = 1e-3
    atol = 1e-6
    tiempo = 0
    tbound = 30
    sp = 1
    salida = [0]
    tiempo_out = [0]
    yb = 0
    sf1 = 0.9
    error_ac = [0]
    sc_t = [0]
    start = time.time()
    counter = 0
    error = sp - yb

    RK = metodo

    while tiempo < tbound:
        error = sp - yb
        while True:
            counter +=1
            if tiempo + h_ant >= tbound:
                h_ant = tbound - tiempo
                ypids, x_pidSn = RK(A2, B2, C2, D2, x_pidS, h_ant, error)
            else:
                ypidb, x_pidBn = RK(A2, B2, C2, D2, x_pidB, h_ant, error)
                ypids, x_pidSn = RK(A2, B2, C2, D2, x_pidS, h_ant / 2, error)
                ypids, x_pidSn = RK(A2, B2, C2, D2, x_pidSn, h_ant / 2, error)

                scale = atol + rtol * (np.abs(x_pidSn) + np.abs(x_pidBn)) / 2
                delta1 = np.abs(x_pidBn - x_pidSn)
                error_norm = np.max(delta1 / scale)

                if error_norm == 0:
                    h_est = h_ant * max_step_increase
                elif error_norm <= 1:
                    h_est = h_ant * min(max_step_increase, max(1, sf1 * error_norm**(-1 / (orden+1))))
                else:
                    h_ant = h_ant * min(1, max(min_step_decrease, sf1 * error_norm**(-1 / (orden+1))))
                    continue

            # error_ac.append(error_norm)
            # sc_t.append(ypids)

            error_ac.extend([error])
            sc_t.extend([ypids])
            yb, vstadosB = RK(A1, B1, C1, D1, vstadosB, h_ant, ypids)
            break

        # salida.append(yb)
        # tiempo_out.append(tiempo)
        print(tiempo)
        salida.extend([np.hstack(yb)])
        tiempo_out.extend([tiempo])
        tiempo += h_ant


        h_ant = h_est
        x_pidB = x_pidSn
        x_pidS = x_pidSn
        input_a1 = error
        input_a2 = ypids

    print(counter)
    print(len(tiempo_out))
    print(f'Tiempo:{time.time() - start}')
    # plt.figure(figindex)
    plt.plot(tiempo_out, salida)

    # with open('dataDormand.pkl', 'wb', ) as f:
    #     pickle.dump([tiempo_out, sc_t, error_ac], f)

    # tf = ctrl.tf(num, dem)
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

if __name__ == "__main__":
    ejecutar(metodo=runge_kutta2, orden=2)
    plt.show()
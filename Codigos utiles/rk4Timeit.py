import numpy as np
import control as ctrl
from matplotlib import pyplot as plt
import time
from math import factorial
from numba import jit


def ejecutar():

    def norm(x):
        """Compute RMS norm."""
        return np.linalg.norm(x) / x.size**0.5

    def tres_octavos4(A, B, C, D, x, h, inputValue):
        k1 = np.dot(h, (np.dot(A, x) + np.dot(B, inputValue)))
        k2 = np.dot(h, (np.dot(A, (x + np.dot(k1, 1 / 3))) + np.dot(B, inputValue)))
        k3 = np.dot(h,
                    (np.dot(A,
                            (x + np.dot(k1, -1 / 3) + k2)) + np.dot(B, inputValue)))
        k4 = np.dot(h, (np.dot(A, (x + k1 - k2 + k3)) + np.dot(B, inputValue)))

        y = np.dot(C, x) + np.dot(D, inputValue)
        x = x + (np.dot(k1, 1 / 8) + np.dot(k2, 3 / 8) + np.dot(k3, 3 / 8) +
                 np.dot(k4, 1 / 8))

        return y.item(), x

    @jit
    def runge_kutta2(A, B, C, D, x, h, inputValue):
        k1 = h*(np.dot(A, x) + B*inputValue)
        k2 = h*(np.dot(A, x + k1/ 2) + B*inputValue)

        y = np.dot(C, x) + D*inputValue
        x = x + k2
        return y, x

    def runge_kutta3(A, B, C, D, x, h, inputValue):
        k1 = np.dot(h, (np.dot(A, x) + np.dot(B, inputValue)))
        k2 = np.dot(h, (np.dot(A, (x + np.dot(k1, 1 / 2))) + np.dot(B, inputValue)))
        k3 = np.dot(h, (np.dot(A,
                               (x - k1 + np.dot(k2, 2))) + np.dot(B, inputValue)))

        y = np.dot(C, x) + np.dot(D, inputValue)
        x = x + (np.dot(k1, 1 / 6) + np.dot(k2, 2 / 3) + np.dot(k3, 1 / 6))

        return y.item(), x

    def runge_kutta4(A, B, C, D, x, h, inputValue):
        k1 = np.dot(h, (np.dot(A, x) + np.dot(B, inputValue)))
        k2 = np.dot(h, (np.dot(A, (x + np.dot(k1, 1 / 2))) + np.dot(B, inputValue)))
        k3 = np.dot(h, (np.dot(A, (x + np.dot(k2, 1 / 2))) + np.dot(B, inputValue)))
        k4 = np.dot(h, (np.dot(A, (x + k3)) + np.dot(B, inputValue)))

        y = np.dot(C, x) + np.dot(D, inputValue)
        x = x + (np.dot(k1, 1 / 6) + np.dot(k2, 1 / 3) + np.dot(k3, 1 / 3) +
                 np.dot(k4, 1 / 6))

        return y.item(), x

    def runge_kutta5(A, B, C, D, x, h, inputValue):  # Mejor: rtol = 1e-3, atol = 5e-6
        k1 = np.dot(h, (np.dot(A, x) + np.dot(B, inputValue)))
        k2 = np.dot(h, (np.dot(A, (x + np.dot(k1, 1 / 4))) + np.dot(B, inputValue)))
        k3 = np.dot(h,
                    (np.dot(A, (x + np.dot(k1, 1 / 8) + np.dot(k2, 1 / 8))) +
                     np.dot(B, inputValue)))
        k4 = np.dot(h,
                    (np.dot(A,
                            (x + np.dot(k2, -1 / 2) + k3)) + np.dot(B, inputValue)))
        k5 = np.dot(h,
                    (np.dot(A, (x + np.dot(k1, -3 / 16) + np.dot(k4, 9 / 16))) +
                     np.dot(B, inputValue)))
        k6 = np.dot(
            h,
            (np.dot(A,
                    (x + np.dot(k1, -3 / 7) + np.dot(k2, 2 / 7) + np.dot(k3, 12 / 7) +
                     np.dot(k4, -12 / 7) + np.dot(k5, 8 / 7))) +
             np.dot(B, inputValue)))
        y = np.dot(C, x) + np.dot(D, inputValue)
        x = x + (np.dot(k1, 7 / 90) + np.dot(k3, 32 / 90) + np.dot(k4, 12 / 90) +
                 np.dot(k5, 32 / 90) + np.dot(k6, 7 / 90))

        return y.item(), x

    def heun3(A, B, C, D, x, h, inputValue):
        k1 = np.dot(h, (np.dot(A, x) + np.dot(B, inputValue)))
        k2 = np.dot(h, (np.dot(A, (x + np.dot(k1, 1 / 3))) + np.dot(B, inputValue)))
        k3 = np.dot(h, (np.dot(A, (x + np.dot(k2, 2 / 3))) + np.dot(B, inputValue)))

        y = np.dot(C, x) + np.dot(D, inputValue)
        x = x + (np.dot(k1, 1 / 4) + np.dot(k3, 3 / 4))

        return y.item(), x

    def ralston4(A, B, C, D, x, h, inputValue):  # Mejor: rtol = 1e-5, atol = 5e-6
        k1 = np.dot(h, (np.dot(A, x) + np.dot(B, inputValue)))
        k2 = np.dot(h, (np.dot(A, (x + np.dot(k1, 0.4))) + np.dot(B, inputValue)))
        k3 = np.dot(h,
                    (np.dot(A, (x + np.dot(k1, 0.29697761) + np.dot(k2, 0.15875964))) +
                     np.dot(B, inputValue)))
        k4 = np.dot(h,
                    (np.dot(A,
                            (x + np.dot(k1, 0.21810040) + np.dot(k2, -3.05096516) +
                             np.dot(k3, 3.83286476))) + np.dot(B, inputValue)))

        y = np.dot(C, x) + np.dot(D, inputValue)
        x = x + (np.dot(k1, 0.17476028) + np.dot(k2, -0.55148066) +
                 np.dot(k3, 1.20553560) + np.dot(k4, 0.17118478))

        return y.item(), x

    def ralston3(A, B, C, D, x, h, inputValue):
        k1 = np.dot(h, (np.dot(A, x) + np.dot(B, inputValue)))
        k2 = np.dot(h, (np.dot(A, (x + np.dot(k1, 1/2))) + np.dot(B, inputValue)))
        k3 = np.dot(h, (np.dot(A, (x + np.dot(k2, 3/4))) + np.dot(B, inputValue)))

        y = np.dot(C, x) + np.dot(D, inputValue)
        x = x + (np.dot(k1, 2 / 9) + np.dot(k2, 1 / 3) + np.dot(k3, 4 / 9))

        return y.item(), x

    def SSPRK3(A, B, C, D, x, h, inputValue):
        k1 = np.dot(h, (np.dot(A, x) + np.dot(B, inputValue)))
        k2 = np.dot(h, (np.dot(A, (x + k1)) + np.dot(B, inputValue)))
        k3 = np.dot(h, (np.dot(A, (x + np.dot(k1, 1/4) + np.dot(k2, 1/4))) + np.dot(B, inputValue)))

        y = np.dot(C, x) + np.dot(D, inputValue)
        x = x + (np.dot(k1, 1 / 6) + np.dot(k2, 1 / 6) + np.dot(k3, 2 / 3))

        return y.item(), x

    N = 100
    kp = 1
    ki = 1
    kd = 1

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
    print(x_pidB)

    num = [1]
    dem = [1, 1, 1]

    sistema = ctrl.tf2ss(ctrl.TransferFunction(num, dem))
    A1, B1, C1, D1 = sistema.A.astype('float64'), sistema.B.astype('float64'), sistema.C.astype('float64'), sistema.D.astype('float64')
    vstadosB = np.zeros_like(sistema.B).astype('float64')
    print(vstadosB)

    min_step_decrease = 0.2
    max_step_increase = 5.0
    h_ant = 30/10000
    rtol = 1e-6
    atol = 1e-6
    tiempo = 0.0
    tbound = 30.0
    sp = 1.0
    salida = [0.0]
    tiempo_out = [0.0]
    yb = 0.0
    sf1 = 0.9
    error_ac = [0.0]
    sc_t = [0.0]
    start = time.time()
    counter = 0.0

    RK = runge_kutta2

    while tiempo < tbound:
        error = sp - yb
        yc, x_pidB = RK(A2, B2, C2, D2, x_pidB, h_ant, error)
        yb, vstadosB = RK(A1, B1, C1, D1, vstadosB, h_ant, yc)
        # print(tiempo)
        salida.extend([yb])
        tiempo_out.extend([tiempo])
        tiempo += h_ant
        h_ant = h_ant


    print(f'Tiempo:{time.time() - start}')
    plt.plot(tiempo_out, salida)

    # tf = ctrl.tf(num, dem)
    # t = np.linspace(0, tbound, 200)
    # pid = ctrl.TransferFunction([N*kd + kp, N*kp + ki, N * ki], [1, N, 0])
    # tf = ctrl.feedback(pid*tf)
    # t, y = ctrl.step_response(tf, t)
    # plt.plot(t, y)
    plt.grid()
    plt.show()

    # plt.plot(tiempo_out, sc_t)
    # plt.grid()
    # plt.show()

    # plt.plot(tiempo_out, error_ac)
    # plt.grid()
    # plt.show()

if __name__ == "__main__":
    ejecutar()
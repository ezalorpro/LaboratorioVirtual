import numpy as np
import control as ctrl
from matplotlib import pyplot as plt
import time
from numba import jit, complex64, float64
from math import factorial

def ejecutar():

    @jit
    def norm(x):
        """Compute RMS norm."""
        return np.linalg.norm(x) / x.size**0.5

    def tres_octavos4(ss, x, h, inputValue):
        k1 = dot_py(h, (dot_py(A, x) + dot_py(B, inputValue)))
        k2 = dot_py(h, (dot_py(A, (x + dot_py(k1, 1 / 3))) + dot_py(B, inputValue)))
        k3 = dot_py(h,
                    (dot_py(A,
                            (x + dot_py(k1, -1 / 3) + k2)) + dot_py(B, inputValue)))
        k4 = dot_py(h, (dot_py(A, (x + k1 - k2 + k3)) + dot_py(B, inputValue)))

        y = dot_py(C, x) + dot_py(D, inputValue)
        x = x + (dot_py(k1, 1 / 8) + dot_py(k2, 3 / 8) + dot_py(k3, 3 / 8) +
                 dot_py(k4, 1 / 8))

        return y.item(), x

    @jit
    def dot_py(A, B):
        m, n = A.shape
        p = B.shape[1]

        C = np.zeros((m, p))

        for i in range(0, m):
            for j in range(0, p):
                for k in range(0, n):
                    C[i, j] += A[i, k] * B[k, j]
        return C

    @jit
    def dot_py2(A, B):
        m, n = A.shape
        p = 1

        C = np.zeros((m, p))

        for i in range(0, m):
            for j in range(0, p):
                for k in range(0, n):
                    C[i, j] += A[i, k] * B
        return C

    @jit
    def runge_kutta2(A, B, C, D, x, h, inputValue):
        k1 = dot_py2((dot_py(A, x) + dot_py2(B, inputValue)), h)
        k2 = dot_py2((dot_py(A,
                                  (x + dot_py2(k1, 1 / 2))) + dot_py2(B, inputValue)), h)

        y = dot_py(C, x) + dot_py2(D, inputValue)
        x = x + k2

        return y, x

    def runge_kutta3(ss, x, h, inputValue):
        k1 = dot_py(h, (dot_py(A, x) + dot_py(B, inputValue)))
        k2 = dot_py(h, (dot_py(A, (x + dot_py(k1, 1 / 2))) + dot_py(B, inputValue)))
        k3 = dot_py(h, (dot_py(A,
                               (x - k1 + dot_py(k2, 2))) + dot_py(B, inputValue)))

        y = dot_py(C, x) + dot_py(D, inputValue)
        x = x + (dot_py(k1, 1 / 6) + dot_py(k2, 2 / 3) + dot_py(k3, 1 / 6))

        return y.item(), x

    def runge_kutta4(ss, x, h, inputValue):
        k1 = dot_py(h, (dot_py(A, x) + dot_py(B, inputValue)))
        k2 = dot_py(h, (dot_py(A, (x + dot_py(k1, 1 / 2))) + dot_py(B, inputValue)))
        k3 = dot_py(h, (dot_py(A, (x + dot_py(k2, 1 / 2))) + dot_py(B, inputValue)))
        k4 = dot_py(h, (dot_py(A, (x + k3)) + dot_py(B, inputValue)))

        y = dot_py(C, x) + dot_py(D, inputValue)
        x = x + (dot_py(k1, 1 / 6) + dot_py(k2, 1 / 3) + dot_py(k3, 1 / 3) +
                 dot_py(k4, 1 / 6))

        return y.item(), x

    @jit
    def runge_kutta5(A, B, C, D, x, h, inputValue):  # Mejor: rtol = 1e-3, atol = 5e-6
        k1 = dot_py2((dot_py(A, x) + dot_py2(B, inputValue)), h)
        k2 = dot_py2((dot_py(A, (x + dot_py2(k1, 1 / 4))) + dot_py2(B, inputValue)), h)
        k3 = dot_py2((dot_py(A, (x + dot_py2(k1, 1 / 8) + dot_py2(k2, 1 / 8))) +
                     dot_py2(B, inputValue)),
                    h)
        k4 = dot_py2((dot_py(A, (x + dot_py2(k2, -1 / 2) + k3)) + dot_py2(B, inputValue)),
                    h)
        k5 = dot_py2(
                    (dot_py(A, (x + dot_py2(k1, -3 / 16) + dot_py2(k4, 9 / 16))) +
                     dot_py2(B, inputValue)), h)
        k6 = dot_py2(
            (dot_py(A,
                    (x + dot_py2(k1, -3 / 7) + dot_py2(k2, 2 / 7) + dot_py2(k3, 12 / 7) +
                     dot_py2(k4, -12 / 7) + dot_py2(k5, 8 / 7))) +
             dot_py2(B, inputValue)),
            h)
        y = dot_py(C, x) + dot_py2(D, inputValue)
        x = x + (dot_py2(k1, 7 / 90) + dot_py2(k3, 32 / 90) + dot_py2(k4, 12 / 90) +
                 dot_py2(k5, 32 / 90) + dot_py2(k6, 7 / 90))

        return y, x

    def heun3(ss, x, h, inputValue):
        k1 = dot_py(h, (dot_py(A, x) + dot_py(B, inputValue)))
        k2 = dot_py(h, (dot_py(A, (x + dot_py(k1, 1 / 3))) + dot_py(B, inputValue)))
        k3 = dot_py(h, (dot_py(A, (x + dot_py(k2, 2 / 3))) + dot_py(B, inputValue)))

        y = dot_py(C, x) + dot_py(D, inputValue)
        x = x + (dot_py(k1, 1 / 4) + dot_py(k3, 3 / 4))

        return y.item(), x

    def ralston4(ss, x, h, inputValue):  # Mejor: rtol = 1e-5, atol = 5e-6
        k1 = dot_py(h, (dot_py(A, x) + dot_py(B, inputValue)))
        k2 = dot_py(h, (dot_py(A, (x + dot_py(k1, 0.4))) + dot_py(B, inputValue)))
        k3 = dot_py(h,
                    (dot_py(A, (x + dot_py(k1, 0.29697761) + dot_py(k2, 0.15875964))) +
                     dot_py(B, inputValue)))
        k4 = dot_py(h,
                    (dot_py(A,
                            (x + dot_py(k1, 0.21810040) + dot_py(k2, -3.05096516) +
                             dot_py(k3, 3.83286476))) + dot_py(B, inputValue)))

        y = dot_py(C, x) + dot_py(D, inputValue)
        x = x + (dot_py(k1, 0.17476028) + dot_py(k2, -0.55148066) +
                 dot_py(k3, 1.20553560) + dot_py(k4, 0.17118478))

        return y.item(), x

    def ralston3(ss, x, h, inputValue):
        k1 = dot_py(h, (dot_py(A, x) + dot_py(B, inputValue)))
        k2 = dot_py(h, (dot_py(A, (x + dot_py(k1, 1/2))) + dot_py(B, inputValue)))
        k3 = dot_py(h, (dot_py(A, (x + dot_py(k2, 3/4))) + dot_py(B, inputValue)))

        y = dot_py(C, x) + dot_py(D, inputValue)
        x = x + (dot_py(k1, 2 / 9) + dot_py(k2, 1 / 3) + dot_py(k3, 4 / 9))

        return y.item(), x

    def SSPRK3(ss, x, h, inputValue):
        k1 = dot_py(h, (dot_py(A, x) + dot_py(B, inputValue)))
        k2 = dot_py(h, (dot_py(A, (x + k1)) + dot_py(B, inputValue)))
        k3 = dot_py(h, (dot_py(A, (x + dot_py(k1, 1/4) + dot_py(k2, 1/4))) + dot_py(B, inputValue)))

        y = dot_py(C, x) + dot_py(D, inputValue)
        x = x + (dot_py(k1, 1 / 6) + dot_py(k2, 1 / 6) + dot_py(k3, 2 / 3))

        return y.item(), x

    N = 100
    kp = 1
    ki = 1
    kd = 0

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

    print(pid)
    x_pidB = np.zeros_like(pid.B, np.float64)
    x_pidS = np.zeros_like(pid.B, np.float64)

    num = [1]
    dem = [1, 1, 1]

    sistema = ctrl.tf2ss(ctrl.TransferFunction(num, dem))
    vstadosB = np.zeros_like(sistema.B, np.float64, order='A')

    min_step_decrease = 0.2
    max_step_increase = 5
    h_ant = 0.000001
    rtol = 1e-6
    atol = 1e-6
    tiempo = 0
    tbound = 30
    sp = 1.0
    salida = [0]
    tiempo_out = [0]
    yb = 0
    sf1 = 0.9
    error_ac = [0]
    sc_t = [0]
    start = time.time()
    counter = 0

    RK = runge_kutta5
    pid.A = pid.A.astype(np.float64, order='A')
    pid.B = pid.B.astype(np.float64, order='A')
    pid.C = pid.C.astype(np.float64, order='A')
    pid.D = pid.D.astype(np.float64, order='A')
    
    sistema.A = sistema.A.astype(np.float64, order='A')
    sistema.B = sistema.B.astype(np.float64, order='A')
    sistema.C = sistema.C.astype(np.float64, order='A')
    sistema.D = sistema.D.astype(np.float64, order='A')
    
    while tiempo < tbound:
        error = sp - yb
        while True:
            counter +=1
            if tiempo + h_ant >= tbound:
                h_ant = tbound - tiempo
                ypids, x_pidSn = RK(pid.A, pid.B, pid.C, pid.D, x_pidS, h_ant, error)
            else:
                ypidb, x_pidBn = RK(pid.A, pid.B, pid.C, pid.D, x_pidB, h_ant, error)
                ypids, x_pidSn = RK(pid.A, pid.B, pid.C, pid.D, x_pidS, h_ant / 2, error)
                ypids, x_pidSn = RK(pid.A, pid.B, pid.C, pid.D, x_pidSn, h_ant / 2, error)

                scale = atol + rtol * (np.abs(x_pidSn) + np.abs(x_pidBn)) / 2
                delta1 = np.abs(x_pidBn - x_pidSn)
                error_norm = norm(delta1 / scale)

                if error_norm == 0:
                    h_est = h_ant * max_step_increase
                elif error_norm <= 1:
                    h_est = h_ant * min(max_step_increase, max(1, sf1 * error_norm**(-1 / (5+1))))
                else:
                    h_ant = h_ant * min(1, max(min_step_decrease, sf1 * error_norm**(-1 / (5+1))))
                    continue

            error_ac.append(error_norm)
            print(tiempo)
            sc_t.append(ypids)
            yb, vstadosB = RK(sistema.A, sistema.B, sistema.C, sistema.D, vstadosB, h_ant, ypids)
            break

        salida.append(yb)
        tiempo_out.append(tiempo)
        tiempo += h_ant


        h_ant = h_est
        x_pidB = x_pidSn
        x_pidS = x_pidSn
        input_a1 = error
        input_a2 = ypids

    print(counter)
    print(len(tiempo_out))
    print(f'{time.time() - start}')
    plt.plot(tiempo_out, salida)

    tf = ctrl.tf(num, dem)
    t = np.linspace(0, tbound, 200)
    pid = ctrl.TransferFunction([N*kd + kp, N*kp + ki, N * ki], [1, N, 0])
    tf = ctrl.feedback(pid*tf)
    t, y = ctrl.step_response(tf, t)
    plt.plot(t, y)
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
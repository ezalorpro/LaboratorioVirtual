from matplotlib import pyplot as plt
import control as ctrl
import numpy as np
import sympy
from tqdm import tqdm

tf = ctrl.tf([1], [1, 1, 1])
N = 100
kp = 1
ki = 1
kd = 1

pid = ctrl.TransferFunction([N*kd + kp, N*kp + ki, N * ki], [1, N, 0])
tf = ctrl.feedback(pid*tf)
t, y = ctrl.step_response(tf)

plt.plot(t, y)
ss = ctrl.tf2ss(tf)
print(ss)

x = np.zeros_like(ss.B)
h = 0.01
total_t = 50
t = np.linspace(0, total_t, int(total_t / h))
u = np.ones_like(t)
u[2500:] = 0.5
result = []

for i, _ in tqdm(enumerate(t)):
    k1 = h * (ss.A * x + ss.B * u[i])
    k2 = h * (ss.A * (x + k1/2) + ss.B * u[i])
    k3 = h * (ss.A * (x + k2/2) + ss.B * u[i])
    k4 = h * (ss.A * (x+k3) + ss.B * u[i])

    y = ss.C * x + ss.D * u[i]
    x = x + (1/6) * (k1 + 2*k2 + 2*k3 + k4)

    result.append(np.asscalar(y[0]))

plt.plot(t, np.reshape(result, [len(t)]))
plt.show()

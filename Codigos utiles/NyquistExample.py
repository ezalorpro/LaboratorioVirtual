import controlmdf as ctrl
import numpy as np
from numpy import real as REAL
from numpy import imag as IMAG
from matplotlib import pyplot as plt

# plt.style.use("seaborn-dark-palette")

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = "Times New Roman"

plt.rcParams["mathtext.rm"] = "serif"
plt.rcParams["mathtext.it"] = "serif:italic"
plt.rcParams["mathtext.bf"] = "serif:bold"
plt.rcParams["mathtext.fontset"] = "custom"

plt.rc("text", usetex=True)
plt.rcParams["text.latex.preamble"] = [
    r"\usepackage{mathptmx} \usepackage{newtxmath} \usepackage{amsmath}"
]

w = np.logspace(-np.pi, 2 * np.pi, 5000)

GsS = ctrl.TransferFunction([1, 2], [1, 2, 3])

GsI = ctrl.TransferFunction([3, -1.5], [1, -2, 3])

real, imag, freq = ctrl.nyquist_plot(GsS, w, Plot=False)
poles, zeros = ctrl.pzmap(GsS, Plot=False)

plt.scatter(REAL(poles), IMAG(poles), s=50, marker='x', facecolors="r", edgecolors='k')
plt.scatter(REAL(zeros), IMAG(zeros), s=50, marker='o', facecolors="r", edgecolors='k')

plt.plot([-1], [0], color="#12711C", marker='+')

plt.arrow(real[0],
          imag[0], (real[1] - real[0]) / 2, (imag[1] - imag[0]) / 2,
          width=0.02,
          facecolor='r',
          edgecolor='k')

mindex = int(len(real) / 2.5)

plt.arrow(real[mindex],
          imag[mindex], (real[mindex + 1] - real[mindex]) / 2,
          (imag[mindex + 1] - imag[mindex]) / 2,
          width=0.02,
          facecolor='r',
          edgecolor='k')

plt.plot(real, imag, "r", label=r'$G_1(s) = \frac{s + 2}{s^2 + 2s + 3}$')
plt.plot(real, -imag, "r")

real, imag, freq = ctrl.nyquist_plot(GsI, w, Plot=False)
poles, zeros = ctrl.pzmap(GsI, Plot=False)

plt.scatter(REAL(poles),
            IMAG(poles),
            s=50,
            marker='x',
            facecolors="#001C7F",
            edgecolors='k')
plt.scatter(REAL(zeros),
            IMAG(zeros),
            s=50,
            marker='o',
            facecolors="#001C7F",
            edgecolors='k')

plt.arrow(real[0],
          imag[0], (real[1] - real[0]) / 2, (imag[1] - imag[0]) / 2,
          width=0.02,
          facecolor='#001C7F',
          edgecolor='k')
plt.arrow(real[-1],
          imag[-1], (real[-1] - real[-2]) / 2, (imag[-1] - imag[-2]) / 2,
          width=0.02,
          facecolor='#001C7F',
          edgecolor='k')

mindex = int(len(real) / 2)

plt.plot(real, imag, "#001C7F", label=r'$G_2(s) = \frac{3s - 1.5}{s^2 - 2s + 3}$')
plt.plot(real, -imag, "#001C7F")

plt.legend()
plt.grid()
plt.gcf().tight_layout()
plt.show()
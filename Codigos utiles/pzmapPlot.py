import controlmdf as ctrl
import numpy as np
from numpy import real, imag
from matplotlib import pyplot as plt

plt.style.use("seaborn-dark-palette")

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

GsS = ctrl.TransferFunction([1, 2], [1, 2, 3])
GsI = ctrl.TransferFunction([3, -1.5], [1, -2, 3])
poles, zeros, ax = ctrl.pzmap(GsS, Plot=True, grid=True, title='Plano complejo', axr=True)

poles, zeros = ctrl.pzmap(GsI, Plot=False)

ax.scatter(real(poles), imag(poles), s=50, marker='x', facecolors='b', edgecolors='k')
ax.scatter(real(zeros), imag(zeros), s=50, marker='o', facecolors='b', edgecolors='k')

plt.text(-2.5, 0.8, r'$G_1(s) = \frac{s + 2}{s^2 + 2s + 3}$', fontsize=20)
plt.text(0.7, 0.8, r'$G_2(s) = \frac{s - 0.5}{s^2 - 2s + 3}$', fontsize=20)
plt.gcf().tight_layout()
plt.show()
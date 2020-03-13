import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
from skfuzzy import control as ctrl

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

names = ["Muy frio", "Frio", "Tibio", "Caliente", "Muy caliente"]

plt.plot([-10, -10 + 27.5], [1, 0], linestyle=":")
plt.plot([-10, -10 + 27.5, -10 + 27.5 + 27.5], [0, 1, 0], linestyle="--")
plt.plot(
    [-10 + 27.5, -10 + 27.5 + 27.5, -10 + 27.5 * 2 + 27.5],
    [0, 1, 0],
    linestyle="-.",
)
plt.plot(
    [-10 + 27.5 * 2, -10 + 27.5 * 2 + 27.5, -10 + 27.5 * 3 + 27.5],
    [0, 1, 0],
    linestyle="-",
)
plt.plot(
    [-10 + 27.5 * 2 + 27.5, -10 + 27.5 * 3 + 27.5], [0, 1], dashes=[10, 5, 20, 5]
)
plt.plot([-12, 102], [0, 0], "k")
fig = plt.gcf()
fig.set_size_inches(11, 8)
plt.legend(labels=names, prop={"size": 14})

plt.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter(r"%d $^{\circ}$C"))
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['bottom'].set_visible(False)
plt.gca().spines['left'].set_visible(False)

plt.xlabel("Temperatura")
plt.ylabel(r"$\mu\ (x)$", fontsize=14)
plt.savefig("FuzzySet.pdf", bbox_inches="tight", pad_inches=0.1)
plt.show()

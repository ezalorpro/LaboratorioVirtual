import numpy as np
from matplotlib import pyplot as plt
from skfuzzymdf import control as fuzzy
from skfuzzymdf.membership import generatemf

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

antecedente = fuzzy.Antecedent(np.linspace(-10, 10, 1000), 'e_entrada')
mfvalues = generatemf.gbellmf(antecedente.universe, 1.7, 1.3, 0)
antecedente['etiqueta'] = mfvalues
fig, ax = fuzzy.visualization.FuzzyVariableVisualizer(antecedente).view(legend=False)

zeros = np.zeros_like(antecedente.universe)
ax.fill_between(antecedente.universe, zeros, mfvalues, alpha=0.4)

# ax.text(-5.2, 1.02, r'$a$', fontsize=18)
# ax.text(4.83, -0.05, r'$b$', fontsize=18)
# ax.text(2.33, 1.02, r'$c$', fontsize=18)
ax.legend(['gbellmf'], fontsize=18)

ax.get_xaxis().set_ticks([])
ax.get_yaxis().set_ticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

fig.tight_layout()
plt.show()

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import correlate
from scipy.stats import energy_distance
from scipy.integrate import cumtrapz
from scipy import io
from matplotlib import pyplot as plt
import pickle

MatFile = io.loadmat('comparisonFiles/Data MATLAB/Analisis/S1DImp', squeeze_me=True)

with open('comparisonFiles/Data LVSCCD/Analisis/Set1DImp.pkl', 'rb') as f:
    T1, Y1 = pickle.load(f)

t2 = MatFile['Impulse_t']

T2, Y2 = MatFile['Impulse_t'], MatFile['Impulse_y']

funcion = interp1d(T1, Y1)
Y1 = funcion(T2)

indice = np.argmax(np.abs(Y2 - Y1))
print(f'{"Tiempo de diferencia maxima: ":<38}{T2[indice]:.4f}')

fig, ax = plt.subplots(figsize=(5.1, 4.2))
ax.step(T2, Y2, where='mid', color="#001C7F", label='MATLAB', linewidth=2)
ax.plot([T2[indice]]*2, [Y1[indice], Y2[indice]], color='k', linewidth=3, label='Diferencia maxima')
ax.step(T2, Y1, 'r', where='mid', dashes=[1, 2], label='Laboratorio Virtual', linewidth=3)
ax.fill_between(T2, Y1, Y2, step='mid', alpha=0.4, color="#001C7F", label='Area de diferencia')
ax.set_xlabel('tiempo')
ax.set_title('Respuesta impulso para el Sistema 1')
ax.legend(loc=7, bbox_to_anchor=(0.97, 0.85))
ax.grid()

axins = ax.inset_axes([0.54, 0.31, 0.41, 0.33])
axins.step(T2, Y2, where='mid', color="#001C7F", label='MATLAB', linewidth=2)
axins.plot([T2[indice]]*2, [Y1[indice], Y2[indice]], color='k', linewidth=3, label='Diferencia maxima')
axins.step(T2, Y1, 'r', where='mid', dashes=[1, 2], label='Laboratorio Virtual', linewidth=3)
axins.fill_between(T2, Y1, Y2, step='mid', alpha=0.4, color="#001C7F", label='Area de diferencia')
axins.xaxis.set_major_locator(plt.MaxNLocator(2))
# axins.yaxis.major.formatter.set_powerlimits((0, 0))

x1, x2 = T2[indice] - np.abs(Y1[indice] - Y2[indice])*10, T2[indice] + np.abs(Y1[indice] - Y2[indice])*10

if Y2[indice] >= Y1[indice]:
    y1, y2 = Y1[indice] - np.abs(Y1[indice] - Y2[indice]), Y2[indice] + np.abs(Y1[indice] - Y2[indice])
else:
    y1, y2 = Y2[indice] - np.abs(Y1[indice] - Y2[indice]), Y1[indice] + np.abs(Y1[indice] - Y2[indice])

axins.set_xlim(x1, x2)
axins.set_ylim(y1, y2)
ax.indicate_inset_zoom(axins)
axins.grid()

fig.tight_layout()
plt.savefig('comparisonFiles/plots/Analisis/MATLAB/Set1DImp.png', dpi=200)
plt.show()

print(f'{"Error absoluto: ":<38}{np.abs(Y2[indice]-Y1[indice]):.3E}')
print(f'{"Error porcentual maximo: ":<38}{np.abs(Y2[indice]-Y1[indice])*100/Y2[indice]:.3E} %')
print(f'{"Distancia de energia: ":<38}{energy_distance(Y1, Y2):.3E}')
print(f'{"Diferencia de areas: ":<38}{np.abs(cumtrapz(Y1, T2)[-1] - cumtrapz(Y2, T2)[-1]):.3E}')
print(f'{"Raiz del Error cuadratico medio: ":<38}{np.sqrt((np.subtract(Y1, Y2)**2).mean()):.3E}')
print(f'{"Distancia euclidiana: ":<38}{np.linalg.norm(Y1-Y2):.3E}')

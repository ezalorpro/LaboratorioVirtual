import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import correlate
from scipy.stats import energy_distance
from scipy.integrate import cumtrapz
from scipy import io
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import pickle

MatFile = io.loadmat('comparisonFiles/Data MATLAB/Analisis/S3DNichols', squeeze_me=True)

with open('comparisonFiles/Data LVSCCD/Analisis/Set3DNichols.pkl', 'rb') as f:
    Pha1, Db1, WN1 = pickle.load(f)

Db2, Pha2, WN2 = MatFile['MagN'], MatFile['PhaN'], MatFile['WN']

mask1 = WN1 >= min(WN2)
mask2 = WN1[mask1] <= max(WN2)
WN1 = WN1[mask1][mask2]
Pha1 = Pha1[mask1][mask2]
Db1 = Db1[mask1][mask2]

funcion1 = interp1d(WN2, Pha2)
Pha2 = funcion1(WN1)

funcion2 = interp1d(WN2, Db2)
Db2 = funcion2(WN1)

indice = np.argmax(np.abs(Db2 - Db1))
print(f'{"Frecuencia diferencia maxima: ":<38}{WN1[indice]:.4f}')

fig, ax = plt.subplots(figsize=(5.1, 4.2))
ax.plot(Pha1, Db2, color="#001C7F", label='MATLAB', linewidth=2)
ax.plot([Pha2[indice]]*2, [Db1[indice], Db2[indice]], color='k', linewidth=3, label='Diferencia maxima')
ax.plot(Pha1, Db1, 'r', dashes=[1, 2], label='Laboratorio Virtual', linewidth=3)
ax.fill_between(Pha1, Db1, Db2, alpha=0.4, color="#001C7F", label='Area de diferencia')
ax.set_title('Diagrama de Nichols para el Sistema 3')
ax.xaxis.set_major_locator(plt.MaxNLocator(4))
ax.xaxis.set_major_formatter(mtick.FormatStrFormatter("%.1f °"))
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.1f dB"))
ax.legend(loc=7, bbox_to_anchor=(0.5, 0.7))
ax.grid()

# from nicholschart import nichols_grid

# nichols_grid(figure=fig, ax=ax)

axins = ax.inset_axes([0.55, 0.1, 0.35, 0.3])
axins.plot(Pha1, Db2, color="#001C7F", label='MATLAB', linewidth=2)
axins.plot([Pha1[indice]]*2, [Db1[indice], Db2[indice]], color='k', linewidth=3, label='Diferencia maxima')
axins.plot(Pha1, Db1, 'r', dashes=[1, 2], label='Laboratorio Virtual', linewidth=3)
axins.fill_between(Pha1, Db1, Db2, alpha=0.4, color="#001C7F", label='Area de diferencia', interpolate=True)
axins.xaxis.set_major_locator(plt.MaxNLocator(2))
# axins.yaxis.major.formatter.set_powerlimits((0, 0))

x1, x2 = Pha1[indice] - np.abs(Db1[indice] - Db2[indice])*50, Pha2[indice] + np.abs(Db1[indice] - Db2[indice])*50

if Db2[indice] >= Db1[indice]:
    y1, y2 = Db1[indice] - np.abs(Db1[indice] - Db2[indice]), Db2[indice] + np.abs(Db1[indice] - Db2[indice])
else:
    y1, y2 = Db2[indice] - np.abs(Db1[indice] - Db2[indice]), Db1[indice] + np.abs(Db1[indice] - Db2[indice])

axins.set_xlim(x1, x2)
axins.set_ylim(y1, y2)
ax.indicate_inset_zoom(axins)
axins.grid()

# ax.set_xlim(-900, 0)
fig.tight_layout()
fig.subplots_adjust(right=0.95, left=0.15)
plt.savefig('comparisonFiles/plots/Analisis/MATLAB/Set3DNichols.png', dpi=200)
plt.show()

print(f'{"Error absoluto: ":<38}{np.abs(Db2[indice]-Db1[indice]):.3E}')
print(f'{"Error porcentual maximo: ":<38}{np.abs(np.abs(Db2[indice]-Db1[indice])*100/Db2[indice]):.3E} %')
print(f'{"Distancia de energia: ":<38}{energy_distance(Db1, Db2):.3E}')
print(f'{"Diferencia de areas: ":<38}{np.abs(cumtrapz(Db1, Pha1)[-1] - cumtrapz(Db2, Pha1)[-1]):.3E}')
print(f'{"Raiz del Error cuadratico medio: ":<38}{np.sqrt((np.subtract(Db1, Db2)**2).mean()):.3E}')
print(f'{"Distancia euclidiana: ":<38}{np.linalg.norm(Db1-Db2):.3E}')

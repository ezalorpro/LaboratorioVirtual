import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import correlate
from scipy.stats import energy_distance
from scipy.integrate import cumtrapz
from scipy import io
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import pickle


with open('comparisonFiles/Data LVSCCD/Analisis/Set3Margin.pkl', 'rb') as f:
    GM1, GP1, WM1, WP1 = pickle.load(f)

with open('comparisonFiles/Data LVSCCD/Analisis/Set3Bode.pkl', 'rb') as f:
    Freq1, Mag1, Pha1 = pickle.load(f)

MatFile = io.loadmat('comparisonFiles/Data MATLAB/Analisis/S3Bode', squeeze_me=True)
Mag2, Pha2, Freq2 = MatFile['MagB'], MatFile['PhaB'], MatFile['FreqB']

MatFile2 = io.loadmat('comparisonFiles/Data MATLAB/Analisis/S3Margin', squeeze_me=True)
GM2, GP2, WM2, WP2 = MatFile2['GM'], MatFile2['GP'], MatFile2['Wg'], MatFile2['Wp']

mask = Freq2 >= min(Freq1)
Freq2 = Freq2[mask]
Mag2 = Mag2[mask]
Pha2 = Pha2[mask]

funcionMag = interp1d(Freq1, Mag1)
Mag1 = funcionMag(Freq2)

funcionPha = interp1d(Freq1, Pha1)
Pha1 = funcionPha(Freq2)

indiceMag = np.argmax(np.abs(Mag2 - Mag1))
indicePha = np.argmax(np.abs(Pha2 - Pha1))
print(f'{"Frecuencia de diferencia maxima Magnitud: ":<38}{Freq2[indiceMag]:.4f}')
print(f'{"Frecuencia de diferencia maxima Phase: ":<38}{Freq2[indicePha]:.4f}\n')

fig, axObj = plt.subplots(2, 1, figsize=(5.4, 6.8))

ax1 = axObj[0]
ax1.plot(Freq2, Mag2, color="#001C7F", label='MATLAB', linewidth=2)
ax1.plot([Freq2[indiceMag]] * 2, [Mag1[indiceMag], Mag2[indiceMag]],
          color='k',
          linewidth=3,
          label='Diferencia maxima')
ax1.plot(Freq2, Mag1, 'r', dashes=[1, 2], label='Laboratorio Virtual', linewidth=3)
ax1.fill_between(Freq2, Mag1, Mag2, alpha=0.4, color="#001C7F", label='Area de diferencia')
ax1.set_xscale('log')
ax1.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.1f dB"))
ax1.set_title('Bode para el Sistema 3')
ax1.legend(loc=7, bbox_to_anchor=(0.99, 0.75))
ax1.grid()

axins1 = ax1.inset_axes([0.15, 0.16, 0.4, 0.37])
axins1.plot(Freq2, Mag2, color="#001C7F", label='MATLAB', linewidth=2)
axins1.plot([Freq2[indiceMag]]*2, [Mag1[indiceMag], Mag2[indiceMag]], color='k', linewidth=3, label='Diferencia maxima')
axins1.plot(Freq2, Mag1, 'r', dashes=[1, 2], label='Laboratorio Virtual', linewidth=3)
axins1.fill_between(Freq2, Mag1, Mag2, alpha=0.4, color="#001C7F", label='Area de diferencia')
axins1.xaxis.major.formatter.set_powerlimits((0, 0))
axins1.yaxis.major.formatter.set_powerlimits((0, 0))

x1, x2 = Freq2[indiceMag] - np.abs(Mag1[indiceMag] - Mag2[indiceMag])*0.2, Freq2[indiceMag] + np.abs(Mag1[indiceMag] - Mag2[indiceMag])*0.2

if Mag2[indiceMag] >= Mag1[indiceMag]:
    y1, y2 = Mag1[indiceMag] - np.abs(Mag1[indiceMag] - Mag2[indiceMag]), Mag2[indiceMag] + np.abs(Mag1[indiceMag] - Mag2[indiceMag])
else:
    y1, y2 = Mag2[indiceMag] - np.abs(Mag1[indiceMag] - Mag2[indiceMag]), Mag1[indiceMag] + np.abs(Mag1[indiceMag] - Mag2[indiceMag])

axins1.set_xticks([x1, x2])
axins1.set_xlim(x1, x2)
axins1.set_ylim(y1, y2)
ax1.indicate_inset_zoom(axins1)
axins1.grid()

ax2 = axObj[1]
ax2.plot(Freq2, Pha2, color="#001C7F", label='MATLAB', linewidth=2)
ax2.plot([Freq2[indicePha]] * 2, [Pha1[indicePha], Pha2[indicePha]],
         color='k',
         linewidth=3,
         label='Diferencia maxima')
ax2.plot(Freq2, Pha1, 'r', dashes=[1, 2], label='Laboratorio Virtual', linewidth=3)
ax2.fill_between(Freq2,
                 Pha1,
                 Pha2,
                 alpha=0.4,
                 color="#001C7F",
                 label='Area de diferencia')
ax2.set_xlabel('rad/s')
ax2.set_xscale('log')
ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.1f °"))
# ax2.legend(loc=7, bbox_to_anchor=(0.97, 0.75))
ax2.grid()

axins2 = ax2.inset_axes([0.16, 0.2, 0.4, 0.4])
axins2.plot(Freq2, Pha2, color="#001C7F", label='MATLAB', linewidth=2)
axins2.plot([Freq2[indicePha]] * 2, [Pha1[indicePha], Pha2[indicePha]],
            color='k',
            linewidth=3,
            label='Diferencia maxima')
axins2.plot(Freq2, Pha1, 'r', dashes=[1, 2], label='Laboratorio Virtual', linewidth=3)
axins2.fill_between(Freq2,
                    Pha1,
                    Pha2,
                    alpha=0.4,
                    color="#001C7F",
                    label='Area de diferencia')
axins2.xaxis.major.formatter.set_powerlimits((0, 0))
axins2.yaxis.major.formatter.set_powerlimits((0, 0))

x1, x2 = Freq2[indicePha] - np.abs(Pha1[indicePha] - Pha2[indicePha])*0.01, Freq2[indicePha] + np.abs(Pha1[indicePha] - Pha2[indicePha])*0.01

if Pha2[indicePha] >= Pha1[indicePha]:
    y1, y2 = Pha1[indicePha] - np.abs(Pha1[indicePha] - Pha2[indicePha]), Pha2[indicePha] + np.abs(Pha1[indicePha] - Pha2[indicePha])
else:
    y1, y2 = Pha2[indicePha] - np.abs(Pha1[indicePha] - Pha2[indicePha]), Pha1[indicePha] + np.abs(Pha1[indicePha] - Pha2[indicePha])

axins2.set_xticks([x1, x2])
axins2.set_xlim(x1, x2)
axins2.set_ylim(y1, y2)
ax2.indicate_inset_zoom(axins2)
axins2.grid()

fig.tight_layout()
fig.subplots_adjust(hspace=0, bottom=0.1, top=0.95, left=0.16)
plt.savefig('comparisonFiles/plots/Analisis/MATLAB/Set3Bode.png', dpi=200)
plt.show()

print('Magnitud')
print(f'{"Error absoluto bode: ":<38}{np.abs(Mag2[indiceMag]-Mag1[indiceMag]):.3E}')
print(f'{"Error porcentual maximo: ":<38}{np.abs(Mag2[indiceMag]-Mag1[indiceMag])*100/Mag2[indiceMag]:.3E} %')
print(f'{"Distancia de energia: ":<38}{energy_distance(Mag1, Mag2):.3E}')
print(f'{"Diferencia de areas: ":<38}{np.abs(cumtrapz(Mag1, Freq2)[-1] - cumtrapz(Mag2, Freq2)[-1]):.3E}')
print(f'{"Raiz del Error cuadratico medio: ":<38}{np.sqrt((np.subtract(Mag1, Mag2)**2).mean()):.3E}')
print(f'{"Distancia euclidiana: ":<38}{np.linalg.norm(Mag1-Mag2):.3E}')
print(f'{"Error absoluto GM: ":<38}{np.abs(GM2-GM1):.3E}')
print(f'{"Error porcentual GM: ":<38}{np.abs(GM2-GM1)*100/GM2:.3E}')
print(f'{"Error absoluto frecuencia GM: ":<38}{np.abs(WM2-WM1):.3E}\n')

print('Fase')
print(f'{"Error absoluto bode: ":<38}{np.abs(Pha2[indicePha]-Pha1[indicePha]):.3E}')
print(f'{"Error porcentual maximo: ":<38}{np.abs(Pha2[indicePha]-Pha1[indicePha])*100/Pha2[indicePha]:.3E} %')
print(f'{"Distancia de energia: ":<38}{energy_distance(Pha1, Pha2):.3E}')
print(f'{"Diferencia de areas: ":<38}{np.abs(cumtrapz(Pha1, Freq2)[-1] - cumtrapz(Pha2, Freq2)[-1]):.3E}')
print(f'{"Raiz del Error cuadratico medio: ":<38}{np.sqrt((np.subtract(Pha1, Pha2)**2).mean()):.3E}')
print(f'{"Distancia euclidiana: ":<38}{np.linalg.norm(Pha1-Pha2):.3E}')
print(f'{"Error absoluto margen PM: ":<38}{np.abs(GP2-GP1):.3E}')
print(f'{"Error porcentual margen PM: ":<38}{np.abs(GP2-GP1)*100/GP2:.3E}')
print(f'{"Error absoluto frecuencia PM: ":<38}{np.abs(WP2-WP1):.3E}')

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import correlate
from scipy.stats import energy_distance
from scipy.integrate import cumtrapz
from scipy import real, imag
from scipy import io
from matplotlib import pyplot as plt
import pickle

MatFile = io.loadmat('comparisonFiles/Data MATLAB/Analisis/S2DRlocus', squeeze_me=True)

with open('comparisonFiles/Data LVSCCD/Analisis/Set2DRlocus.pkl', 'rb') as f:
    data1, ganancias1 = pickle.load(f)

data2, ganancias2 = MatFile['r'], MatFile['k']

Re1 = real(data1)
Img1 = imag(data1)
Re2 = real(data2)
Img2 = imag(data2)

NRe1 = []
NRe2 = []
NImg1 = []
NImg2 = []

Re1 = np.swapaxes(Re1, 0, 1)
Img1 = np.swapaxes(Img1, 0, 1)

mask1 = ganancias2 >= min(ganancias1)
mask2 = ganancias2 <= max(ganancias1)
ganancias2 = ganancias2[mask1][mask2]

for index, col in enumerate(zip(Re1, Img1)):
    reC, imgC = col
    NImg2.append(Img2[index][mask1][mask2])
    NRe2.append(Re2[index][mask1][mask2])

    funcion1 = interp1d(ganancias1, reC)
    NRe1.append(funcion1(ganancias2))

    funcion2 = interp1d(ganancias1, imgC)
    NImg1.append(funcion2(ganancias2))

NRe1 = np.asarray(NRe1)
NRe2 = np.asarray(NRe2)
NImg1 = np.asarray(NImg1)
NImg2 = np.asarray(NImg2)

tempRe1 = np.sort(np.hstack(NRe1))
tempRe2 = np.sort(np.hstack(NRe2))
tempImg1 = np.sort(np.hstack(NImg1))
tempImg2 = np.sort(np.hstack(NImg2))

error = np.abs(NImg2 - NImg1)
indice = np.argmax(np.abs(tempImg1 - tempImg2))
index_max = np.where(NImg2 == tempImg2[indice])

print(f'{"Valor real de diferencia maxima: ":<38}{tempRe2[indice]:.4f}')

fig, ax = plt.subplots(figsize=(5.1, 4.2))

for index, _ in enumerate(Img2):
    if index == 0:
        ax.plot(Re2[index], Img2[index], color="#001C7F", label='MATLAB', linewidth=2)
    else:
        ax.plot(Re2[index], Img2[index], color="#001C7F", linewidth=2)

for index, _ in enumerate(Img1):
    if index == 0:
        ax.plot(Re1[index],
                Img1[index],
                'r',
                dashes=[1, 2],
                label='Laboratorio Virtual',
                linewidth=3)
    else:
        ax.plot(Re1[index], Img1[index], 'r', dashes=[1, 2], linewidth=3)

# ax.set_xlim(-10, 1)
ax.set_title('Lugar de las raíces para el sistema 2')
ax.legend()
ax.grid()

fig.tight_layout()
plt.savefig('comparisonFiles/plots/Analisis/MATLAB/Set2DRlocus.png', dpi=200)
plt.show()

print(f'{"Error absoluto: ":<38}{np.abs(tempImg2[indice]-tempImg1[indice]):.3E}')
print(
    f'{"Error porcentual maximo: ":<38}{np.abs(np.abs(tempImg2[indice]-tempImg1[indice])*100/tempImg2[indice]):.3E} %'
)
print(
    f'{"Distancia de energia: ":<38}{energy_distance(np.hstack(Img1), np.hstack(Img2)):.3E}'
)
print(
    f'{"Raiz del Error cuadratico medio: ":<38}{np.sqrt((np.subtract(tempImg1, tempImg2)**2).mean()):.3E}'
)
print(f'{"Distancia euclidiana: ":<38}{np.linalg.norm(tempImg1-tempImg2):.3E}')
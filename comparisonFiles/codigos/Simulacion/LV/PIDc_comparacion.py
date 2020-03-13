import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import correlate
from scipy.stats import energy_distance
from scipy.integrate import cumtrapz
from scipy import io
from matplotlib import pyplot as plt
import pickle

MatFileMATLAB = io.loadmat('comparisonFiles/Data MATLAB/Simulacion/PIDc3', squeeze_me=True)
MatFileSciLab = io.loadmat('comparisonFiles/Data SciLab/Simulacion/PIDc3', squeeze_me=True)

with open('comparisonFiles/Data LVSCCD/Simulacion/Controlador4.pkl', 'rb') as f:
    t_lv, yout_lv, yc_lv, set_point, _ = pickle.load(f)

with open('comparisonFiles/Data LVSCCD/Simulacion/Controlador3.pkl', 'rb') as f:
    t_lvf, yout_lvf, yc_lvf, set_pointf, _f = pickle.load(f)

t_lv = np.asarray(t_lv)
yout_lv = np.asarray(yout_lv)
yc_lv = np.asarray(yc_lv)
set_point = np.asarray(set_point)

t_lvf = np.asarray(t_lvf)
yout_lvf = np.asarray(yout_lvf)
yc_lvf = np.asarray(yc_lvf)
set_pointf = np.asarray(set_pointf)

t_mat = MatFileMATLAB['t']
yout_mat = MatFileMATLAB['yout']
yc_mat = MatFileMATLAB['yc']

t_sci = MatFileSciLab['t']
yout_sci = MatFileSciLab['yout']
yc_sci = MatFileSciLab['yc']


if len(t_sci) > len(t_mat) and len(t_sci) > len(t_lv) and len(t_sci) > len(t_lvf):

    mask1 = t_sci <= max(t_mat)
    mask2 = t_sci[mask1] <= max(t_lv)
    mask3 = t_sci[mask1][mask2] <= max(t_lvf)

    t_sci = t_sci[mask1][mask2][mask3]
    yout_sci = yout_sci[mask1][mask2][mask3]

    funcion1 = interp1d(t_mat, yout_mat)
    yout_mat = funcion1(t_sci)

    funcion2 = interp1d(t_lv, yout_lv)
    yout_lv = funcion2(t_sci)

    funcion3 = interp1d(t_lvf, yout_lvf)
    yout_lvf = funcion3(t_sci)

    t_comun = t_sci

if len(t_lv) > len(t_mat) and len(t_lv) > len(t_sci) and len(t_lv) > len(t_lvf):

    mask1 = t_lv <= max(t_mat)
    mask2 = t_lv[mask1] <= max(t_sci)
    mask3 = t_lv[mask1][mask2] <= max(t_lvf)

    t_lv = t_lv[mask1][mask2][mask3]
    yout_lv = yout_lv[mask1][mask2][mask3]

    funcion1 = interp1d(t_mat, yout_mat)
    yout_mat = funcion1(t_lv)

    funcion2 = interp1d(t_sci, yout_sci)
    yout_sci = funcion2(t_lv)

    funcion3 = interp1d(t_lvf, yout_lvf)
    yout_lvf = funcion3(t_lv)

    t_comun = t_lv

if len(t_mat) > len(t_sci) and len(t_mat) > len(t_lv) and len(t_mat) > len(t_lvf):
    mask1 = t_mat <= max(t_sci)
    mask2 = t_mat[mask1] <= max(t_lv)
    mask3 = t_mat[mask1][mask2] <= max(t_lvf)

    t_mat = t_mat[mask1][mask2][mask3]
    yout_mat = yout_mat[mask1][mask2][mask3]

    funcion1 = interp1d(t_lv, yout_lv)
    yout_lv = funcion1(t_mat)

    funcion2 = interp1d(t_sci, yout_sci)
    yout_sci = funcion2(t_mat)

    funcion3 = interp1d(t_lvf, yout_lvf)
    yout_lvf = funcion3(t_mat)

    t_comun = t_mat

if len(t_lvf) > len(t_mat) and len(t_lvf) > len(t_sci) and len(t_lvf) > len(t_lv):
    mask1 = t_lvf <= max(t_mat)
    mask2 = t_lvf[mask1] <= max(t_sci)
    mask3 = t_lvf[mask1][mask2] <= max(t_lv)

    t_lvf = t_lvf[mask1][mask2][mask3]
    yout_lvf = yout_lvf[mask1][mask2][mask3]

    funcion1 = interp1d(t_mat, yout_mat)
    yout_mat = funcion1(t_lvf)

    funcion2 = interp1d(t_sci, yout_sci)
    yout_sci = funcion2(t_lvf)

    funcion3 = interp1d(t_lv, yout_lv)
    yout_lv = funcion3(t_lvf)

    t_comun = t_lvf

index_m = np.argmax([
    abs(yout_lv - yout_mat),
    abs(yout_lv - yout_sci),
    abs(yout_lvf - yout_mat),
    abs(yout_lvf - yout_sci)
],
                    axis=1)

index_temp = np.argmax([
    abs(yout_lv[index_m[0]] - yout_mat[index_m[0]]),
    abs(yout_lv[index_m[1]] - yout_sci[index_m[1]]),
    abs(yout_lvf[index_m[2]] - yout_mat[index_m[2]]),
    abs(yout_lvf[index_m[3]] - yout_sci[index_m[3]])
])

index_temp2 = np.argmax([
    yout_lv[index_m[index_temp]],
    yout_mat[index_m[index_temp]],
    yout_sci[index_m[index_temp]],
    yout_lvf[index_m[index_temp]]
])

index_temp3 = np.argmin([
    yout_lv[index_m[index_temp]],
    yout_mat[index_m[index_temp]],
    yout_sci[index_m[index_temp]],
    yout_lvf[index_m[index_temp]]
])

index_max = index_m[index_temp]
index_min = index_m[index_temp]

if index_temp2 == 0:
    YMAX = yout_lv
elif index_temp2 == 1:
    YMAX = yout_mat
elif index_temp2 == 2:
    YMAX = yout_sci
else:
    YMAX = yout_lvf

if index_temp3 == 0:
    YMIN = yout_lv
elif index_temp3 == 1:
    YMIN = yout_mat
elif index_temp3 == 2:
    YMIN = yout_sci
else:
    YMIN = yout_lvf


fig, ax = plt.subplots(figsize=(5.1, 4.2))
ax.plot(t_comun, yout_mat, color="#001C7F", label='MATLAB/ode45', linewidth=2)
ax.plot(t_comun, yout_lv, 'r', dashes=[1, 2], label='LV/RK2 sin Filtro', linewidth=3)
ax.plot(t_comun, yout_lvf, 'orange', dashes=[1, 2], alpha=0.4, label='LV/RK2 con Filtro', linewidth=3)
ax.plot(t_comun, yout_sci, color="#12711C", dashes=[2, 2], label='SciLab/BDF-Newton', linewidth=2)
ax.set_title('Controlador PID')
ax.legend(loc=5, bbox_to_anchor=(0.97, 0.65))
ax.grid()

axins = ax.inset_axes([0.55, 0.12, 0.4, 0.33])
axins.plot(t_comun, yout_mat, color="#001C7F", linewidth=2)
axins.plot(t_comun, yout_lv, 'r', dashes=[1, 2], linewidth=3)
axins.plot(t_comun, yout_lvf, 'orange', alpha=0.4, dashes=[1, 2], linewidth=3)
axins.plot(t_comun, yout_sci, color="#12711C", dashes=[2, 2], linewidth=2)
axins.grid()
axins.set_xlim(t_comun[index_max] - 0.1, t_comun[index_min] + 0.1)
axins.set_ylim(YMIN[index_min] - 1 * abs(YMIN[index_min] - YMAX[index_min]) / 2,
               YMAX[index_max] + 1 * abs(YMIN[index_min] - YMAX[index_min]) / 2)

ax.indicate_inset_zoom(axins)
fig.tight_layout()
plt.savefig('comparisonFiles/plots/Simulacion/PIDc.pdf')
plt.show()
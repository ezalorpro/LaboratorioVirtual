import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import correlate
from scipy.stats import energy_distance
from scipy.integrate import cumtrapz
from scipy import io
from matplotlib import pyplot as plt
import pickle

MatFileMATLAB1 = io.loadmat('comparisonFiles/Data MATLAB/Simulacion/PIDcf4', squeeze_me=True)
MatFileMATLAB2 = io.loadmat('comparisonFiles/Data MATLAB/Simulacion/PIDcf6', squeeze_me=True)
MatFileSciLab1 = io.loadmat('comparisonFiles/Data SciLab/Simulacion/PIDcf4', squeeze_me=True)
MatFileSciLab2 = io.loadmat('comparisonFiles/Data SciLab/Simulacion/PIDcf6', squeeze_me=True)

with open('comparisonFiles/Data LVSCCD/Simulacion/Controlador5.pkl', 'rb') as f:
    t_lvf, yout_lvf, yc_lvf, set_pointf, _f = pickle.load(f)

with open('comparisonFiles/Data LVSCCD/Simulacion/Controlador7.pkl', 'rb') as f:
    t_lv, yout_lv, yc_lv, set_point, _ = pickle.load(f)

with open('comparisonFiles/Data LVSCCD/Simulacion/Controlador8.pkl', 'rb') as f:
    t_lvr, yout_lvr, yc_lvr, set_pointr, _r = pickle.load(f)

t_lv = np.asarray(t_lv)
yout_lv = np.asarray(yout_lv)
yc_lv = np.asarray(yc_lv)
set_point = np.asarray(set_point)

t_lvf = np.asarray(t_lvf)
yout_lvf = np.asarray(yout_lvf)
yc_lvf = np.asarray(yc_lvf)
set_pointf = np.asarray(set_pointf)

t_lvr = np.asarray(t_lvr)
yout_lvr = np.asarray(yout_lvr)
yc_lvr = np.asarray(yc_lvr)
set_pointr = np.asarray(set_pointr)

t_mat1 = MatFileMATLAB1['t']
yout_mat1 = MatFileMATLAB1['yout']
yc_mat1 = MatFileMATLAB1['yc']

t_mat = MatFileMATLAB2['t']
yout_mat = MatFileMATLAB2['yout']
yc_mat = MatFileMATLAB2['yc']

t_sci1 = MatFileSciLab1['t']
yout_sci1 = MatFileSciLab1['yout']
yc_sci1 = MatFileSciLab1['yc']

t_sci = MatFileSciLab2['t']
yout_sci = MatFileSciLab2['yout']
yc_sci = MatFileSciLab2['yc']

funcion1 = interp1d(t_lv, yout_lv, fill_value='extrapolate')
yout_lv = funcion1(t_mat)

funcion2 = interp1d(t_lvf, yout_lvf, fill_value='extrapolate')
yout_lvf = funcion2(t_mat)

funcion3 = interp1d(t_lvr, yout_lvr, fill_value='extrapolate')
yout_lvr = funcion3(t_mat)

funcion4 = interp1d(t_sci, yout_sci, fill_value='extrapolate')
yout_sci = funcion4(t_mat)

funcion5 = interp1d(t_sci1, yout_sci1, fill_value='extrapolate')
yout_sci1 = funcion5(t_mat)

funcion6 = interp1d(t_mat1, yout_mat1, fill_value='extrapolate')
yout_mat1 = funcion6(t_mat)

t_comun = t_mat


index_m = np.argmax([
    abs(yout_lv - yout_mat),
    abs(yout_lv - yout_sci),
    abs(yout_lv - yout_mat1),
    abs(yout_lv - yout_sci1),
    abs(yout_lvf - yout_mat),
    abs(yout_lvf - yout_sci),
    abs(yout_lvf - yout_mat1),
    abs(yout_lvf - yout_sci1),
    abs(yout_lvr - yout_mat),
    abs(yout_lvr - yout_sci),
    abs(yout_lvr - yout_mat1),
    abs(yout_lvr - yout_sci1)
],
                    axis=1)

index_temp = np.argmax([
    abs(yout_lv[index_m[0]] - yout_mat[index_m[0]]),
    abs(yout_lv[index_m[1]] - yout_sci[index_m[1]]),
    abs(yout_lv[index_m[2]] - yout_mat1[index_m[2]]),
    abs(yout_lv[index_m[3]] - yout_sci1[index_m[3]]),
    abs(yout_lvf[index_m[4]] - yout_mat[index_m[4]]),
    abs(yout_lvf[index_m[5]] - yout_sci[index_m[5]]),
    abs(yout_lvf[index_m[6]] - yout_mat1[index_m[6]]),
    abs(yout_lvf[index_m[7]] - yout_sci1[index_m[7]]),
    abs(yout_lvr[index_m[8]] - yout_mat[index_m[8]]),
    abs(yout_lvr[index_m[9]] - yout_sci[index_m[9]]),
    abs(yout_lvr[index_m[10]] - yout_mat1[index_m[10]]),
    abs(yout_lvr[index_m[11]] - yout_sci1[index_m[11]])
])

index_temp2 = np.argmax([
    yout_lv[index_m[index_temp]],
    yout_lvf[index_m[index_temp]],
    yout_lvr[index_m[index_temp]],
    yout_mat[index_m[index_temp]],
    yout_mat1[index_m[index_temp]],
    yout_sci[index_m[index_temp]],
    yout_sci1[index_m[index_temp]],
])

index_temp3 = np.argmin([
    yout_lv[index_m[index_temp]],
    yout_lvf[index_m[index_temp]],
    yout_lvr[index_m[index_temp]],
    yout_mat[index_m[index_temp]],
    yout_mat1[index_m[index_temp]],
    yout_sci[index_m[index_temp]],
    yout_sci1[index_m[index_temp]],
])

index_max = index_m[index_temp]
index_min = index_m[index_temp]

YMAX = yout_mat1
YMIN = yout_lvf

fig, ax = plt.subplots(figsize=(5.1, 4.2))
ax.plot(t_comun, yout_mat1, color="#001C7F", label='MATLAB/ode45', linewidth=2)
ax.plot(t_comun, yout_mat, color="#001C7F", alpha=0.4, label='MATLAB/ode23tb', linewidth=2)

ax.plot(t_comun, yout_lvf, 'orange', dashes=[1, 2], alpha=0.4, label='LV/SSPRK3 con Filtro', linewidth=3)
ax.plot(t_comun, yout_lv, 'r', dashes=[1, 2], label='LV/SSPRK3 sin Filtro', linewidth=3)
ax.plot(t_comun, yout_lvr, 'r', dashes=[1, 2], alpha=0.4, label='LV/DOPRI5(4) sin Filtro', linewidth=3)

ax.plot(t_comun, yout_sci1, color="#12711C", dashes=[2, 2], label='SciLab/BDF-Newton', linewidth=2)
ax.plot(t_comun, yout_sci, color="#12711C", alpha=0.4, dashes=[2, 2], label='SciLab/LSODAR', linewidth=2)

ax.set_title('Controlador PID difuso')
ax.legend(loc=5, bbox_to_anchor=(0.99, 0.25))
ax.grid()

axins = ax.inset_axes([0.76, 0.73, 0.22, 0.25])
axins.plot(t_comun, yout_mat1, color="#001C7F", label='MATLAB/ode45', linewidth=2)
axins.plot(t_comun, yout_mat, color="#001C7F", alpha=0.4, label='MATLAB/ode23tb', linewidth=2)

axins.plot(t_comun, yout_lvf, 'orange', dashes=[1, 2], alpha=0.4, label='LV/SSPRK3 con Filtro', linewidth=3)
axins.plot(t_comun, yout_lv, 'r', dashes=[1, 2], label='LV/SSPRK3 sin Filtro', linewidth=3)
axins.plot(t_comun, yout_lvr, 'r', dashes=[1, 2], alpha=0.4, label='LV/DOPRI5(4) sin Filtro', linewidth=3)

axins.plot(t_comun, yout_sci1, color="#12711C", dashes=[2, 2], label='SciLab/BDF-Newton', linewidth=2)
axins.plot(t_comun, yout_sci, color="#12711C", alpha=0.4, dashes=[2, 2], label='SciLab/LSODAR', linewidth=2)

axins.grid()
axins.set_xlim(5.8 - 0.4, 6.8)
axins.set_ylim(1, 1.23)

ax.indicate_inset_zoom(axins)
fig.tight_layout()
plt.savefig('comparisonFiles/plots/Simulacion/PIDcf1.pdf')
plt.show()
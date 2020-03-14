""" Archivo que contiene todas las rutinas necesarias para la funcionalidad de analisis de sistemas de control """


from matplotlib import pyplot as plt
from collections import deque
from scipy import real, imag

import matplotlib.ticker as mticker
import controlmdf as ctrl
import numpy as np

import json


def system_creator_tf(self, numerador, denominador):
    """
    Función para la creación del sistema a partir de los coeficientes del numerador y del denominador de la función de transferencia.
    
    :param numerador: Coeficientes del numerador
    :type numerador: list
    :param denominador: Coeficientes del denominador
    :type denominador: list
    """

    if not self.main.tfdiscretocheckBox1.isChecked(
    ) and self.main.tfdelaycheckBox1.isChecked():
        delay = json.loads(self.main.tfdelayEdit1.text())
    else:
        delay = 0

    system = ctrl.TransferFunction(numerador, denominador, delay=delay)

    # Para obtener un tiempo aproximado
    t, y = ctrl.impulse_response(system)

    # En caso de que el sistema sea discreto
    if self.main.tfdiscretocheckBox1.isChecked():
        system = ctrl.sample_system(system, self.dt, self.main.tfcomboBox1.currentText())

        if self.main.tfdelaycheckBox1.isChecked():
            delay = [0] * (int(json.loads(self.main.tfdelayEdit1.text()) / self.dt) + 1)
            delay[0] = 1
            system_delay = system * ctrl.TransferFunction([1], delay, self.dt)
        else:
            system_delay = None
    else:
        system_delay = system

    try:
        if ctrl.isdtime(system, strict=True):
            T = np.arange(0, 2 * np.max(t), self.dt)
        else:
            T = np.arange(0, 2 * np.max(t), 0.01)
    except ValueError:
        T = np.arange(0, 100, 0.01)

    return system, T, system_delay


def system_creator_ss(self, A, B, C, D):
    """
    Función para la creación del sistema a partir de la matriz de estado, matriz de entrada, matriz de salida y la matriz de transmisión directa la ecuación de espacio de estados.
    
    :param A: Matriz de estados
    :type A: list
    :param B: Matriz de entrada
    :type B: list
    :param C: Matriz de salida
    :type C: list
    :param D: Matriz de transmisión directa
    :type D: list
    """

    if not self.main.ssdiscretocheckBox1.isChecked(
    ) and self.main.ssdelaycheckBox1.isChecked():
        delay = json.loads(self.main.ssdelayEdit1.text())
    else:
        delay = 0

    system = ctrl.StateSpace(A, B, C, D, delay=delay)

    # Para obtener un tiempo aproximado
    t, y = ctrl.impulse_response(system)

    # En caso de que el sistema sea discreto
    if self.main.ssdiscretocheckBox1.isChecked():
        system = ctrl.sample_system(system, self.dt, self.main.sscomboBox1.currentText())

        system_ss = system
        system = ctrl.ss2tf(system)

        if self.main.ssdelaycheckBox1.isChecked():
            delay = [0] * (int(json.loads(self.main.ssdelayEdit1.text()) / self.dt) + 1)
            delay[0] = 1
            system_delay = system * ctrl.TransferFunction([1], delay, self.dt)
        else:
            system_delay = None
    else:
        system_ss = system
        system = ctrl.ss2tf(system)
        system_delay = None

    try:
        if ctrl.isdtime(system, strict=True):
            T = np.arange(0, 2 * np.max(t), self.dt)
        else:
            T = np.arange(0, 2 * np.max(t), 0.01)
    except ValueError:
        T = np.arange(0, 100, 0.01)

    return system, T, system_delay, system_ss


def rutina_step_plot(self, system, T):
    """
    Función para obtener la respuesta escalón del sistema y su respectiva graficacion.
    
    
    :param system: Representacion del sistema
    :type system: LTI
    :param T: Vector de tiempo
    :type T: numpyArray
    """

    U = np.ones_like(T)

    # Desplazamiento en el tiempo en caso de delay
    if system.delay:
        U[:int(system.delay / 0.01) + 1] = 0

    t, y, _ = ctrl.forced_response(system, T, U)

    self.main.stepGraphicsView1.canvas.axes.clear()

    if ctrl.isdtime(system, strict=True):
        y = y[0]
        y = np.clip(y, -1e300, 1e300)
        self.main.stepGraphicsView1.canvas.axes.step(t, y, where="mid")
    else:
        y = np.clip(y, -1e300, 1e300)
        self.main.stepGraphicsView1.canvas.axes.plot(t, y)

    self.main.stepGraphicsView1.canvas.axes.grid(color="lightgray")
    self.main.stepGraphicsView1.canvas.axes.set_title("Respuesta escalón")
    self.main.stepGraphicsView1.canvas.axes.xaxis.set_major_formatter(
        mticker.FormatStrFormatter("%.2f s")
    )
    self.main.stepGraphicsView1.canvas.axes.set_xlabel("Tiempo")
    self.main.stepGraphicsView1.canvas.axes.set_ylabel("Respuesta")
    self.main.stepGraphicsView1.canvas.draw()
    self.main.stepGraphicsView1.toolbar.update()

    return t, y


def rutina_impulse_plot(self, system, T):
    """
    Función para obtener la respuesta impulso del sistema y su respectiva graficacion.
    
    
    :param system: Representacion del sistema
    :type system: LTI
    :param T: Vector de tiempo
    :type T: numpyArray
    """

    U = np.zeros_like(T)

    # Tomado de la libreria de control
    if ctrl.isdtime(system, strict=True):
        U[0] = 1/self.dt
        new_X0 = 0
    else:
        temp_sys = ctrl.tf2ss(system)
        n_states = temp_sys.A.shape[0]
        X0 = ctrl.timeresp._check_convert_array(0, [(n_states,), (n_states, 1)],
                              'Parameter ``X0``: \n', squeeze=True)
        B = np.asarray(temp_sys.B).squeeze()
        new_X0 = B + X0

    t, y, _ = ctrl.forced_response(system, T, U, X0=new_X0)

    # Desplazamiento en el tiempo en caso de delay
    if system.delay:
        y_delay = np.zeros(int(system.delay / 0.01)).tolist()
        y_delay.extend(y[:-int(system.delay / 0.01)].tolist())
        y = y_delay
        
    self.main.impulseGraphicsView1.canvas.axes.clear()

    if ctrl.isdtime(system, strict=True):
        y = y[0]
        y = np.clip(y, -1e300, 1e300)
        self.main.impulseGraphicsView1.canvas.axes.step(t, y, where="mid")
    else:
        y = np.clip(y, -1e300, 1e300)
        self.main.impulseGraphicsView1.canvas.axes.plot(t, y)

    self.main.impulseGraphicsView1.canvas.axes.grid(color="lightgray")
    self.main.impulseGraphicsView1.canvas.axes.set_title("Respuesta impulso")
    self.main.impulseGraphicsView1.canvas.axes.xaxis.set_major_formatter(
        mticker.FormatStrFormatter("%.2f s")
    )
    self.main.impulseGraphicsView1.canvas.axes.set_xlabel("Tiempo")
    self.main.impulseGraphicsView1.canvas.axes.set_ylabel("Respuesta")
    self.main.impulseGraphicsView1.canvas.draw()
    self.main.impulseGraphicsView1.toolbar.update()

    return t, y


def rutina_bode_plot(self, system):
    """
    Función para obtener la respuesta en frecuencia del sistema y su respectiva graficacion en diagrama de bode.
    
    :param system: Representacion del sistema
    :type system: LTI
    """

    if ctrl.isdtime(system, strict=True):
        mag, phase, omega = ctrl.bode(system)
    else:
        mag, phase, omega = ctrl.bode(system)

    # Gráfica de amplitud en dB
    bodeDb = 20 * np.log10(mag)
    self.main.BodeGraphicsView1.canvas.axes1.clear()
    self.main.BodeGraphicsView1.canvas.axes1.semilogx(omega, bodeDb, "tab:blue")
    self.main.BodeGraphicsView1.canvas.axes1.grid(True, which="both", color="lightgray")
    self.main.BodeGraphicsView1.canvas.axes1.set_title("Magnitud")
    self.main.BodeGraphicsView1.canvas.axes1.yaxis.set_major_formatter(
        mticker.FormatStrFormatter("%.1f dB")
    )

    # Transformación de grados mayores a 180
    if np.any((phase * 180.0 / np.pi) >= 180):
        phase = phase - 2*np.pi

    # Gráfica de fase en grados
    self.main.BodeGraphicsView1.canvas.axes2.clear()
    self.main.BodeGraphicsView1.canvas.axes2.semilogx(omega,
                                                      phase * 180.0 / np.pi,
                                                      "tab:blue")
    self.main.BodeGraphicsView1.canvas.axes2.grid(True, which="both", color="lightgray")
    self.main.BodeGraphicsView1.canvas.axes2.set_title("Fase")
    self.main.BodeGraphicsView1.canvas.axes2.yaxis.set_major_formatter(
        mticker.FormatStrFormatter("%.1f °")
    )
    self.main.BodeGraphicsView1.canvas.axes2.set_xlabel("rad/s")

    # Cálculo y graficacion del margen de ganancia y de fase
    gm, pm, wg, wp = margenes_ganancias(self, system, mag, phase, omega)

    self.main.BodeGraphicsView1.canvas.axes1.axhline(
        y=0, color='k', linestyle=':', zorder=-20
    )
    self.main.BodeGraphicsView1.canvas.axes2.axhline(
        y=-180, color='k', linestyle=':', zorder=-20
    )

    if not gm == np.infty:
        self.main.BodeGraphicsView1.canvas.axes1.axvline(
            x=wg, color='k', linestyle=':', zorder=-20
        )
        self.main.BodeGraphicsView1.canvas.axes2.semilogx(
            [wg, wg], [-180, 0], color='k', linestyle=':', zorder=-20
        )
        self.main.BodeGraphicsView1.canvas.axes1.semilogx(
            [wg, wg], [-gm, 0], color='k', linewidth=3
        )
    if not pm == np.infty:
        self.main.BodeGraphicsView1.canvas.axes2.axvline(
            x=wp, color='k', linestyle=':', zorder=-20
        )
        self.main.BodeGraphicsView1.canvas.axes1.semilogx(
            [wp, wp], [np.min(bodeDb), 0], color='k', linestyle=':', zorder=-20
        )
        self.main.BodeGraphicsView1.canvas.axes2.semilogx(
            [wp, wp], [-180, pm - 180], color='k', linewidth=3
        )

    self.main.BodeGraphicsView1.canvas.draw()
    self.main.BodeGraphicsView1.toolbar.update()

    return mag, phase, omega


def rutina_nyquist_plot(self, system):
    """
    Función para obtener la respuesta en frecuencia del sistema y su respectiva graficacion en diagrama de Nyquist.
    
    :param system: Representacion del sistema
    :type system: LTI
    """

    if ctrl.isdtime(system, strict=True):
        real, imag, freq = ctrl.nyquist_plot(system)
    else:
        real, imag, freq = ctrl.nyquist_plot(system)

    self.main.NyquistGraphicsView1.canvas.axes.cla()
    self.main.NyquistGraphicsView1.canvas.axes.plot([-1], [0], "r+")

    # Flechas para la dirección
    self.main.NyquistGraphicsView1.canvas.axes.arrow(
        real[0],
        imag[0],
        (real[1] - real[0]) / 2,
        (imag[1] - imag[0]) / 2,
        width=np.max(np.abs(real)) / 70,
    )

    self.main.NyquistGraphicsView1.canvas.axes.arrow(
        real[-1],
        imag[-1],
        (real[-1] - real[-2]) / 2,
        (imag[-1] - imag[-2]) / 2,
        width=np.max(np.abs(real)) / 70,
    )

    mindex = int(len(real) / 2)

    self.main.NyquistGraphicsView1.canvas.axes.arrow(
        real[mindex],
        imag[mindex],
        (real[mindex + 1] - real[mindex]) / 2,
        (imag[mindex + 1] - imag[mindex]) / 2,
        width=np.max(np.abs(real)) / 70,
    )

    self.main.NyquistGraphicsView1.canvas.axes.arrow(
        real[-mindex],
        -imag[-mindex],
        (real[-mindex] - real[-mindex + 1]) / 2,
        (imag[-mindex + 1] - imag[-mindex]) / 2,
        width=np.max(np.abs(real)) / 70,
    )

    # Graficacion del diagrama de Nyquist
    self.main.NyquistGraphicsView1.canvas.axes.plot(real, imag, "tab:blue")
    self.main.NyquistGraphicsView1.canvas.axes.plot(real, -imag, "tab:blue")
    self.main.NyquistGraphicsView1.canvas.axes.grid(color="lightgray")
    self.main.NyquistGraphicsView1.canvas.axes.set_title("Diagrama de Nyquist")
    self.main.NyquistGraphicsView1.canvas.draw()
    self.main.NyquistGraphicsView1.toolbar.update()

    return real, imag, freq


def rutina_root_locus_plot(self, system):
    """
    Función para obtener el lugar de la raíces del sistema y su respectiva graficacion, la graficacion se realizo de forma interna en la libreria de control, para esto se modificó la función root_locus para poder enviar el axis y la figura.
    
    :param system: Representacion del sistema
    :type system: LTI
    """

    self.main.rlocusGraphicsView1.canvas.axes.cla()

    # Distinción entre discreto y continuo, con delay y sin delay.
    if not ctrl.isdtime(system, strict=True):
        if self.main.tfdelaycheckBox1.isChecked(
        ) and self.main.AnalisisstackedWidget.currentIndex() == 0:
            pade_delay = ctrl.TransferFunction(
                *ctrl.pade(json.loads(self.main.tfdelayEdit1.text()), 4)
            )
            t, y = ctrl.root_locus(pade_delay*system, figure=self.main.rlocusGraphicsView1, ax=self.main.rlocusGraphicsView1.canvas.axes)

        if self.main.ssdelaycheckBox1.isChecked(
        ) and self.main.AnalisisstackedWidget.currentIndex() == 1:
            pade_delay = ctrl.TransferFunction(
                *ctrl.pade(json.loads(self.main.ssdelayEdit1.text()), 4)
            )
            t, y = ctrl.root_locus(pade_delay*system, figure=self.main.rlocusGraphicsView1, ax=self.main.rlocusGraphicsView1.canvas.axes)

        if not self.main.tfdelaycheckBox1.isChecked(
        ) and self.main.AnalisisstackedWidget.currentIndex() == 0:
            t, y = ctrl.root_locus(system, figure=self.main.rlocusGraphicsView1, ax=self.main.rlocusGraphicsView1.canvas.axes)

        if not self.main.ssdelaycheckBox1.isChecked(
        ) and self.main.AnalisisstackedWidget.currentIndex() == 1:
            t, y = ctrl.root_locus(system, figure=self.main.rlocusGraphicsView1, ax=self.main.rlocusGraphicsView1.canvas.axes)
    else:
        t, y = ctrl.root_locus(system, figure=self.main.rlocusGraphicsView1, ax=self.main.rlocusGraphicsView1.canvas.axes)

    self.main.rlocusGraphicsView1.canvas.axes.set_title("Lugar de las raíces")
    self.main.rlocusGraphicsView1.canvas.draw()
    self.main.rlocusGraphicsView1.toolbar.update()

    return


def rutina_nichols_plot(self, system):
    """
    Función para obtener el diagrama de nichols del sistema y su respectiva graficacion, la graficacion se realizo de forma interna en la libreria de control, para esto se modificó la función nichols_plot para poder enviar el axis y la figura, adicionalmente se realizaron algunas modificaciones para una mejor presentación de la gráfica.
    
    :param system: Representacion del sistema
    :type system: LTI
    """

    self.main.nicholsGraphicsView1.canvas.axes.cla()

    if ctrl.isdtime(system, strict=True):
        if (
            self.main.tfdelaycheckBox1.isChecked() and
            self.main.AnalisisstackedWidget.currentIndex() == 0
        ) or (
            self.main.ssdelaycheckBox1.isChecked() and
            self.main.AnalisisstackedWidget.currentIndex() == 1
        ):

            ctrl.nichols_plot(
                system,
                figure=self.main.nicholsGraphicsView1,
                ax=self.main.nicholsGraphicsView1.canvas.axes,
                delay=True
            )
        else:
            ctrl.nichols_plot(
                system,
                figure=self.main.nicholsGraphicsView1,
                ax=self.main.nicholsGraphicsView1.canvas.axes
            )
    else:
        if (
            self.main.tfdelaycheckBox1.isChecked() and
            self.main.AnalisisstackedWidget.currentIndex() == 0
        ) or (
            self.main.ssdelaycheckBox1.isChecked() and
            self.main.AnalisisstackedWidget.currentIndex() == 1
        ):

            ctrl.nichols_plot(
                system,
                figure=self.main.nicholsGraphicsView1,
                ax=self.main.nicholsGraphicsView1.canvas.axes,
                delay=True
            )
        else:
            ctrl.nichols_plot(
                system,
                figure=self.main.nicholsGraphicsView1,
                ax=self.main.nicholsGraphicsView1.canvas.axes
            )

    self.main.nicholsGraphicsView1.canvas.draw()
    self.main.nicholsGraphicsView1.toolbar.update()

    return


def rutina_system_info(self, system, T, mag, phase, omega):
    """
    Función para mostrar los resultados obtenidos de los calculos en un TextEdit.
    
    :param system: Representacion del sistema
    :type system: LTI
    :param T: Vector de tiempo
    :type T: numpyArray
    :param mag: Magnitud de la respuesta en frecuencia
    :type mag: numpyArray
    :param phase: Fase de la respuesta en frecuencia
    :type phase: numpyArray
    :param omega: Frecuencias utilizadas para la respuesta en frecuencia
    :type omega: numpyArray
    """

    # Información del step
    try:
        info = ctrl.step_info(system, T)
    except:
        info = {
            'RiseTime':np.NaN,
            'SettlingTime':np.NaN,
            'SettlingMax': np.NaN,
            'SettlingMin': np.NaN,
            'Overshoot': np.NaN,
            'Undershoot': np.NaN,
            'Peak': np.NaN,
            'PeakTime': np.NaN,
            'SteadyStateValue': np.NaN
        }

    Datos = ""

    Datos += str(system) + "\n"

    if self.main.tfdelaycheckBox1.isChecked(
    ) and self.main.AnalisisstackedWidget.currentIndex() == 0:
        delay = json.loads(self.main.tfdelayEdit1.text())
        Datos += f"Delay: {delay}\n"
    elif self.main.ssdelaycheckBox1.isChecked(
    ) and self.main.AnalisisstackedWidget.currentIndex() == 1:
        delay = json.loads(self.main.ssdelayEdit1.text())
        Datos += f"Delay: {delay}\n"
    else:
        delay = 0

    Datos += "----------------------------------------------\n"

    for k, v in info.items():
        if 'PeakTime' in k or 'SettlingTime' in k:
            Datos += f"{k} : {v+delay:5.3f}\n"
        else:
            Datos += f"{k} : {v:5.3f}\n"

    Datos += "----------------------------------------------\n"
    dcgain = ctrl.dcgain(system)
    Datos += f"Ganancia DC: {real(dcgain):5.3f}\n"

    # Cálculo del margen de ganancia y de fase
    gm, pm, wg, wp = margenes_ganancias(self, system, mag, phase, omega)

    if not gm == np.infty:
        Datos += f"Margen de ganancia: {gm:5.3f} dB\n"
        Datos += f"Frecuencia de ganancia: {wg:5.3f} rad/sec\n"
    else:
        Datos += f"Margen de ganancia: {gm:5.3f}\n"
        Datos += f"Frecuencia de ganancia: {wg:5.3f}\n"

    if not pm == np.infty:
        Datos += f"Margen de fase: {pm:5.3f} °\n"
        Datos += f"Frecuencia de fase: {wp:5.3f} rad/sec\n"
    else:
        Datos += f"Margen de fase: {pm:5.3f}\n"
        Datos += f"Frecuencia de fase: {wp:5.3f}\n"

    # Valores Eigen
    Datos += "----------------------------------------------\n"
    Datos += f"  {'Valores eigen':<18}  {'Damping':<16}  Wn\n"
    wn, damping, eigen = ctrl.damp(system, doprint=False)
    for wni, dampingi, eigeni in zip(wn, damping, eigen):

        if imag(eigeni) >= 0:
            Datos += f"{real(eigeni):5.3f} {imag(eigeni):+5.3f}j {dampingi:11.3f} {wni:15.3f} \n"
        else:
            Datos += f"{real(eigeni):5.3f} {imag(eigeni):7.3f}j {dampingi:11.3f} {wni:15.3f} \n"

    if self.main.AnalisisstackedWidget.currentIndex() == 0:
        self.main.tfdatosTextEdit1.setPlainText(Datos)
    else:
        self.main.ssdatosTextEdit1.setPlainText(Datos)

    return


def margenes_ganancias(self, system, mag, phase, omega):
    """
    Función para obtener el margen de ganancia y el margen de fase.
    
    :param system: Representación del sistema
    :type system: LTI
    :param mag: Magnitud de la respuesta en frecuencia
    :type mag: numpyArray
    :param phase: Fase de la respuesta en frecuencia
    :type phase: numpyArray
    :param omega: Frecuencias utilizadas para la respuesta en frecuencia
    :type omega: numpyArray
    """

    gainDb = 20 * np.log10(mag)
    degPhase = phase * 180.0 / np.pi

    # Transformado la fase a : -360 < phase < 360, para +/- 360  phase -> 0
    comp_phase = np.copy(degPhase)
    degPhase = degPhase - (degPhase/360).astype(int) * 360

    # Para evitar la detección de cruces al llevar las fases al rango -360 < phase < 360
    crossHack1 = np.diff(1 * (degPhase > -183) != 0)
    crossHack2 = np.diff(1 * (degPhase > -177) != 0)
    crossHack = ~crossHack1 * ~crossHack2

    # Detección de cruce
    indPhase = np.diff(1 * (gainDb > 0) != 0)
    indGain = np.diff(1 * (degPhase > -180) != 0)
    indGain = indGain * crossHack

    # Cálculo de la respuesta en frecuencia para omega = 0 rad/s y pi en caso de ser discreto
    if ctrl.isdtime(system, strict=True):
        zero_freq_response = ctrl.evalfr(system, 1)
        
        nyquist_freq_response = ctrl.evalfr(system, np.exp(np.pi*1j))
        nyquistMag = np.abs(nyquist_freq_response)
        nyquistPhase = np.angle(nyquist_freq_response)
        
        if nyquistPhase * 180.0 / np.pi >= 180:
            nyquistPhase = nyquistPhase - 2 * np.pi
        
        omega = np.insert(omega, len(omega), np.pi/self.dt)
        gainDb = np.insert(gainDb, len(gainDb), 20 * np.log10(nyquistMag))
        degPhase = np.insert(degPhase, len(degPhase), nyquistPhase * 180.0 / np.pi)
        
        # Verificando "cruce" por -180 grados para la frecuencia de Nyquist
        if np.isclose(nyquistPhase * 180.0 / np.pi, -180):
            indGain = np.insert(indGain, len(indGain), True)
        else:
            indGain = np.insert(indGain, len(indGain), False)
        
        # Verificando "cruce" por 0 dB para la frecuencia de Nyquist
        if np.isclose(20 * np.log10(nyquistMag), 0):
            indPhase = np.insert(indPhase, len(indPhase), True)
        else:
            indPhase = np.insert(indPhase, len(indPhase), False)
    else:
        zero_freq_response = ctrl.evalfr(system, 0j)
    
    omega = np.insert(omega, 0, 0)
    zeroPhase = np.angle(zero_freq_response)
    zeroMag = np.abs(zero_freq_response)
    if zeroPhase * 180.0 / np.pi >= 180:
        zeroPhase = zeroPhase - 2 * np.pi
    gainDb = np.insert(gainDb, 0, 20 * np.log10(zeroMag))
    degPhase = np.insert(degPhase, 0, zeroPhase * 180.0 / np.pi)

    # Verificando "cruce" por -180 grados para omega = 0 rad/s
    if np.isclose(zeroPhase * 180.0 / np.pi, -180):
        indGain = np.insert(indGain, 0, True)
    else:
        indGain = np.insert(indGain, 0, False)

    # Verificando "cruce" por 0 dB para omega = 0 rad/s
    if np.isclose(20 * np.log10(zeroMag), 0):
        indPhase = np.insert(indPhase, 0, True)
    else:
        indPhase = np.insert(indPhase, 0, False)

    # Margen de ganancia
    if len(omega[:-1][indGain]) > 0:
        newGainIndex = np.argmin(np.abs(gainDb[:-1][indGain]))
        omegaGain = omega[:-1][indGain][newGainIndex]
        GainMargin = -gainDb[:-1][indGain][newGainIndex]
    else:
        omegaGain = np.nan
        GainMargin = np.infty

    # Margen de Fase
    if len(omega[:-1][indPhase]) > 0:
        newPhaIndex = min(range(len(degPhase[:-1][indPhase])),
                        key=lambda i: abs(np.abs(degPhase[:-1][indPhase][i]) - 180))
        omegaPhase = omega[:-1][indPhase][newPhaIndex]
        PhaseMargin = 180 + degPhase[:-1][indPhase][newPhaIndex]
    else:
        omegaPhase = np.nan
        PhaseMargin = np.infty

    return GainMargin, PhaseMargin, omegaGain, omegaPhase


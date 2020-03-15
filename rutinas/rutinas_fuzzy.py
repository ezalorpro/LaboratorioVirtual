""" 
Archivo que contiene las clases FuzzyController y FISParser, para administrar el controlador difuso y cargar y exportar archivos .fis respectivamente
"""


from skfuzzymdf.control.visualization import FuzzyVariableVisualizer
from skfuzzymdf.control.controlsystem import CrispValueCalculator
from skfuzzymdf.fuzzymath.fuzzy_ops import interp_membership
from skfuzzymdf.membership import generatemf
from skfuzzymdf import control as fuzz
from collections import OrderedDict
from parse import parse

import pyqtgraphmdf as pg
import numpy as np

import ast
import copy
import re


class FuzzyController:
    """
    Clase para administrar el controlador difuso, a partir de la misma se puede crear el controlador difuso e ir creandolo de forma programática por medio de la interfaz grafica definida en Ui_VentanaPrincipal.py y manejada en FuzzyHandler.py
    """

    def __init__(self, inputlist, outputlist, rulelist=[]):
        """
        Se utiliza para inicializar el controlador con las entradas y salidas del mismo, en caso de que se envié el parametro opcional, rulelist, se crea el controlador a partir de las reglas suministradas y queda listo para usar
        
        :param inputlist: Lista de variables de entrada
        :type inputlist: list
        :param outputlist: Lista de variables de salida
        :type outputlist: list
        :param rulelist: Lista de reglas, defaults to []
        :type rulelist: list, opcional
        """

        self.fuzz_inputs = self.crear_input(inputlist)
        self.fuzz_outputs = self.crear_output(outputlist)
        self.flagpyqt = 1

        # Rotación de colores para las funciones de membresía
        self.colors = [
            '#1f77b4',
            '#ff7f0e',
            '#2ca02c',
            '#d62728',
            '#9467bd',
            '#8c564b',
            '#e377c2',
            '#7f7f7f',
            '#bcbd22',
            '#17becf'
        ]

        self.inlabelsplot = []
        self.inareas = []
        self.invalues = []

        self.outlabelsplot = []
        self.outareas = []
        self.outvalues = []

        self.rulelist = []

        self.crear_etiquetas_input(inputlist)
        self.crear_etiquetas_output(outputlist)

        if len(rulelist) > 0:
            self.crear_reglas(rulelist)
            self.crear_controlador()

    def crear_input(self, inputlist):
        """
        Función para crear las variables de entrada a partir de la lista de variables de entrada
        
        :param inputlist: Lista de variables de entrada
        :type inputlist: list
        :return: Variables de entrada
        :rtype: list
        """

        vector = []
        for i, ins in enumerate(inputlist):
            temp_in = fuzz.Antecedent(np.linspace(*ins['rango'], 501), ins['nombre'])
            vector.append(temp_in)
        return vector

    def crear_output(self, outputlist):
        """
        Función para crear las variables de salida a partir de la lista de variables de salida
        
        :param outputlist: Lista de variables de salida
        :type outputlist: list
        :return: Variables de de salida
        :rtype: list
        """

        vector = []
        for i, ins in enumerate(outputlist):
            temp_in = fuzz.Consequent(np.linspace(*ins['rango'], 501),
                                      ins['nombre'],
                                      ins['metodo'])
            vector.append(temp_in)
        return vector

    def crear_etiquetas_input(self, inputlist):
        """
        Función para crear las etiquetas de una entrada a partir de la lista de variables de entrada
        
        :param inputlist: Lista de variables de entrada
        :type inputlist: list
        """

        for n, i in enumerate(inputlist):
            for eti in i['etiquetas']:
                self.fuzz_inputs[n][eti['nombre']] = getattr(generatemf, eti['mf'])(
                    self.fuzz_inputs[n].universe, *eti['definicion'])

    def crear_etiquetas_output(self, outputlist):
        """
        Función para crear las etiquetas de una salida a partir de la lista de variables de salida
        
        :param outputlist: Lista de variables de salida
        :type outputlist: list
        """

        for n, i in enumerate(outputlist):
            for eti in i['etiquetas']:
                self.fuzz_outputs[n][eti['nombre']] = getattr(generatemf, eti['mf'])(
                    self.fuzz_outputs[n].universe, *eti['definicion'])

    def graficar_mf_in(self, window, i):
        """
        Función para graficar las funciones de membresía de una entrada
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param i: Numero de entrada
        :type i: int
        """

        window.main.inputgraphicsView.canvas.axes.clear()
        FuzzyVariableVisualizer(self.fuzz_inputs[i],
                                window.main.inputgraphicsView,
                                window.main.inputgraphicsView.canvas.axes).view_gui()
        window.main.inputgraphicsView.canvas.axes.grid(color="lightgray")
        window.main.inputgraphicsView.canvas.draw()
        window.main.inputgraphicsView.toolbar.update()

    def graficar_mf_out(self, window, o):
        """
        Función para graficar las funciones de membresía de una salida
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param o: Numero de salida
        :type o: int
        """

        window.main.outputgraphicsView.canvas.axes.clear()
        FuzzyVariableVisualizer(self.fuzz_outputs[o],
                                window.main.outputgraphicsView,
                                window.main.outputgraphicsView.canvas.axes).view_gui()
        window.main.outputgraphicsView.canvas.axes.grid(color="lightgray")
        window.main.outputgraphicsView.canvas.draw()
        window.main.outputgraphicsView.toolbar.update()

    def cambiar_nombre_input(self, window, i, nombre):
        """
        Función para cambiar el nombre de una entrada
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param i: Numero de entrada
        :type i: int
        :param nombre: Nuevo nombre de la entrada
        :type nombre: str
        """

        self.fuzz_inputs[i].label = nombre
        self.graficar_mf_in(window, i)

    def cambiar_nombre_output(self, window, o, nombre):
        """
        Función para cambiar el nombre de una salida
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param o: Numero de salida
        :type o: int
        :param nombre: Nuevo nombre de la salida
        :type nombre: str
        """

        self.fuzz_outputs[o].label = nombre
        self.graficar_mf_out(window, o)

    def cambio_etiquetas_input(self, window, inputlist, i):
        """
        Función para actualizar las etiquetas de entrada del controlador
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param inputlist: Lista de variables de entrada
        :type inputlist: list
        :param i: Numero de entrada
        :type i: int
        """

        self.fuzz_inputs[i].terms = OrderedDict()
        self.crear_etiquetas_input(inputlist)
        self.graficar_mf_in(window, i)

    def cambio_etiquetas_output(self, window, outputlist, o):
        """
        Función para actualizar las etiquetas de salida del controlador
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param outputlist: Lista de variables de salida
        :type outputlist: list
        :param o: Numero de salida
        :type o: int
        """

        self.fuzz_outputs[o].terms = OrderedDict()
        self.crear_etiquetas_output(outputlist)
        self.graficar_mf_out(window, o)

    def update_rango_input(self, window, inputlist, i):
        """
        Función para actualizar el universo de discurso de una entrada
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param inputlist: Lista de variables de entrada
        :type inputlist: list
        :param i: Numero de entrada
        :type i: int
        """

        self.fuzz_inputs[i].universe = np.asarray(np.linspace(*inputlist[i]['rango'],
                                                              501))
        self.graficar_mf_in(window, i)

    def update_rango_output(self, window, outputlist, o):
        """
        Función para actualizar el universo de discurso de una salida
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param outputlist: Lista de variables de salida
        :type outputlist: list
        :param o: Numero de salida
        :type o: int
        """

        self.fuzz_outputs[o].universe = np.asarray(
            np.linspace(*outputlist[o]['rango'], 501))
        self.graficar_mf_out(window, o)

    def cambiar_metodo(self, window, o, metodo):
        """ 
        Función para cambiar el método defuzzificacion de una salida
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param o: Numero de salida
        :type o: int
        :param metodo: Nombre del nuevo método de defuzzificacion
        :type o: str
        """
        self.fuzz_inputs[o].defuzzify_method = metodo

    def cambio_etinombre_input(self, window, inputlist, i, n, old_name):
        """
        Función para cambiar el nombre de una etiqueta en la entrada seleccionada
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param inputlist: Lista de variables de entrada
        :type inputlist: list
        :param i: Numero de entrada
        :type i: int
        :param n: Numero de etiqueta
        :type n: int
        :param old_name: Nombre anterior
        :type old_name: str
        """

        eti = inputlist[i]['etiquetas'][n]
        self.fuzz_inputs[i].terms.pop(old_name)
        self.fuzz_inputs[i][eti['nombre']] = getattr(generatemf, eti['mf'])(
            self.fuzz_inputs[i].universe, *eti['definicion'])
        self.graficar_mf_in(window, i)

    def cambio_etinombre_output(self, window, outputlist, o, n, old_name):
        """
        Función para cambiar el nombre de una etiqueta en la salida seleccionada
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param outputlist: Lista de variables de salida
        :type outputlist: list
        :param o: Numero de salida
        :type o: int
        :param n: Numero de etiqueta
        :type n: int
        :param old_name: Nombre anterior
        :type old_name: str
        """

        eti = outputlist[o]['etiquetas'][n]
        self.fuzz_outputs[o].terms.pop(old_name)
        self.fuzz_outputs[o][eti['nombre']] = getattr(generatemf, eti['mf'])(
            self.fuzz_outputs[o].universe, *eti['definicion'])
        self.graficar_mf_out(window, o)

    def update_definicion_input(self, window, inputlist, i, n):
        """
        Función para actualizar la definicion de una función de membresía en la entrada seleccionada
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param inputlist: Lista de variables de entrada
        :type inputlist: list
        :param i: Numero de entrada
        :type i: int
        :param n: Numero de etiqueta
        :type n: int
        """

        eti = inputlist[i]['etiquetas'][n]
        self.fuzz_inputs[i][eti['nombre']] = getattr(generatemf, eti['mf'])(
            self.fuzz_inputs[i].universe, *eti['definicion'])
        self.graficar_mf_in(window, i)

    def update_definicion_output(self, window, outputlist, o, n):
        """
        Función para actualizar la definicion de una función de membresía en la salida seleccionada
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param outputlist: Lista de variables de salida
        :type outputlist: list
        :param o: Numero de salida
        :type o: int
        :param n: Numero de etiqueta
        :type n: int
        """

        eti = outputlist[o]['etiquetas'][n]
        self.fuzz_outputs[o][eti['nombre']] = getattr(generatemf, eti['mf'])(
            self.fuzz_outputs[o].universe, *eti['definicion'])
        self.graficar_mf_out(window, o)

    def crear_reglas(self, rulelistC):
        """
        Función para crear las reglas a partir de una lista que contiene toda la información necesaria, esta lista es creada en FuzzyHandler.py:
        
        Cada posición en la lista contiene un set de entradas, salidas y la lógica a utilizar (AND o OR), a su vez, cada set es una lista que posee en cada posición otra lista con la etiqueta, el numero de entrada/salida y si esta o no negada para el caso de las entradas, en caso de ser salida contiene el peso asignado
        
        :param rulelistC: Lista con la información necesaria para crear las reglas
        :type rulelistC: list
        :return: Lista de reglas
        :rtype: list
        """

        # Un set por cada regla
        for sets in rulelistC:
            Etiquetasin, Etiquetasout, lógica = copy.deepcopy(sets)

            # Creación del objeto de regla de Scikit-Fuzzy
            self.rulelist.append(fuzz.Rule())

            # Los antecedentes deben inicializarce antes de poder expandirse de forma programática
            inetiqueta_ini, ni_ini, negacion_ini = Etiquetasin[0]

            if not negacion_ini:
                self.rulelist[-1].antecedent = self.fuzz_inputs[ni_ini][inetiqueta_ini]
            else:
                self.rulelist[-1].antecedent = ~self.fuzz_inputs[ni_ini][inetiqueta_ini]

            # Los consecuentes deben inicializarce antes de poder expandirse de forma programática
            outetiqueta_oni, no_ini, weight_ini = Etiquetasout[0]

            self.rulelist[
                -1].consequent = self.fuzz_outputs[no_ini][outetiqueta_oni] % weight_ini

            # Expansión del antecedente de forma programática
            for i in Etiquetasin[1:len(Etiquetasin)]:
                if lógica:
                    if not i[2]:
                        self.rulelist[-1].antecedent = self.rulelist[
                            -1].antecedent & self.fuzz_inputs[i[1]][i[0]]
                    else:
                        self.rulelist[-1].antecedent = self.rulelist[
                            -1].antecedent & ~self.fuzz_inputs[i[1]][i[0]]
                else:
                    if not i[2]:
                        self.rulelist[-1].antecedent = self.rulelist[
                            -1].antecedent | self.fuzz_inputs[i[1]][i[0]]
                    else:
                        self.rulelist[-1].antecedent = self.rulelist[
                            -1].antecedent | ~self.fuzz_inputs[i[1]][i[0]]

            # Expansión del consecuente de forma programática
            for o in Etiquetasout[1:len(Etiquetasout)]:
                self.rulelist[-1].consequent.append(self.fuzz_outputs[o[1]][o[0]] % o[2])

        return self.rulelist

    def agregar_regla(self, window, Etiquetasin, Etiquetasout, lógica):
        """
        Función para crear una regla a partir de un set
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param Etiquetasin: set de entrada
        :type Etiquetasin: list
        :param Etiquetasout: set de salida
        :type Etiquetasout: list
        :param lógica: Lógica a utilizar
        :type lógica: bool
        :return: Ultima regla agregada
        :rtype: ObjectType
        """

        # Creación del objeto de regla de Scikit-Fuzzy
        self.rulelist.append(fuzz.Rule())

        # Los antecedentes deben inicializarce antes de poder expandirse de forma programática
        inetiqueta_ini, ni_ini, negacion_ini = Etiquetasin[0]

        if not negacion_ini:
            self.rulelist[-1].antecedent = self.fuzz_inputs[ni_ini][inetiqueta_ini]
        else:
            self.rulelist[-1].antecedent = ~self.fuzz_inputs[ni_ini][inetiqueta_ini]

        # Los consecuentes deben inicializarce antes de poder expandirse de forma programática
        outetiqueta_oni, no_ini, weight_ini = Etiquetasout[0]

        self.rulelist[
            -1].consequent = self.fuzz_outputs[no_ini][outetiqueta_oni] % weight_ini

        # Expansión del antecedente de forma programática
        for i in Etiquetasin[1:len(Etiquetasin)]:
            if lógica:
                if not i[2]:
                    self.rulelist[-1].antecedent = self.rulelist[
                        -1].antecedent & self.fuzz_inputs[i[1]][i[0]]
                else:
                    self.rulelist[-1].antecedent = self.rulelist[
                        -1].antecedent & ~self.fuzz_inputs[i[1]][i[0]]
            else:
                if not i[2]:
                    self.rulelist[-1].antecedent = self.rulelist[
                        -1].antecedent | self.fuzz_inputs[i[1]][i[0]]
                else:
                    self.rulelist[-1].antecedent = self.rulelist[
                        -1].antecedent | ~self.fuzz_inputs[i[1]][i[0]]

        # Expansión del consecuente de forma programática
        for o in Etiquetasout[1:len(Etiquetasout)]:
            self.rulelist[-1].consequent.append(self.fuzz_outputs[o[1]][o[0]] % o[2])

        return self.rulelist[-1]

    def eliminar_regla(self, index_rule):
        """
        Función para eliminar una regla
        
        :param index_rule: Indice indicando la regla a eliminar
        :type index_rule: int
        """
        del self.rulelist[index_rule]

    def cambiar_regla(self, window, Etiquetasin, Etiquetasout, index_rule, lógica):
        """
        Función para cambiar una regla a partir de un nuevo set
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param Etiquetasin: set de entrada
        :type Etiquetasin: list
        :param Etiquetasout: set de salida
        :type Etiquetasout: list
        :param index_rule: Indice indicando la regla a cambiar
        :type index_rule: int
        :param lógica: Lógica a utilizar
        :type lógica: bool
        :return: Regla cambiada
        :rtype: ObjectType
        """

        del self.rulelist[index_rule]

        # Creación del objeto de regla de Scikit-Fuzzy
        self.rulelist.insert(index_rule, fuzz.Rule())

        # Los antecedentes deben inicializarce antes de poder expandirse de forma programática
        inetiqueta_ini, ni_ini, negacion_ini = Etiquetasin[0]

        if not negacion_ini:
            self.rulelist[index_rule].antecedent = self.fuzz_inputs[ni_ini][
                inetiqueta_ini]
        else:
            self.rulelist[
                index_rule].antecedent = ~self.fuzz_inputs[ni_ini][inetiqueta_ini]

        # Los consecuentes deben inicializarce antes de poder expandirse de forma programática
        outetiqueta_oni, no_ini, weight_ini = Etiquetasout[0]

        self.rulelist[index_rule].consequent = self.fuzz_outputs[no_ini][
            outetiqueta_oni] % weight_ini

        # Expansión del antecedente de forma programática
        for i in Etiquetasin[1:len(Etiquetasin)]:
            if lógica:
                if not i[2]:
                    self.rulelist[index_rule].antecedent = self.rulelist[
                        index_rule].antecedent & self.fuzz_inputs[i[1]][i[0]]
                else:
                    self.rulelist[index_rule].antecedent = self.rulelist[
                        index_rule].antecedent & ~self.fuzz_inputs[i[1]][i[0]]
            else:
                if not i[2]:
                    self.rulelist[index_rule].antecedent = self.rulelist[
                        index_rule].antecedent | self.fuzz_inputs[i[1]][i[0]]
                else:
                    self.rulelist[index_rule].antecedent = self.rulelist[
                        index_rule].antecedent | ~self.fuzz_inputs[i[1]][i[0]]

        # Expansión del consecuente de forma programática
        for o in Etiquetasout[1:len(Etiquetasout)]:
            self.rulelist[index_rule].consequent.append(self.fuzz_outputs[o[1]][o[0]] %
                                                        o[2])

        return self.rulelist[index_rule]

    def crear_controlador(self):
        """ Función para crear el controlador difuso a partir de todas las reglas creadas """
        
        temp = fuzz.ControlSystem(self.rulelist)
        self.Controlador = fuzz.ControlSystemSimulation(temp, flush_after_run=20000)

    def prueba_de_controlador(self, window, values, ni, no):
        """
        Función para realizar la prueba del controlador
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param values: Valores de entradas dados por el usuario con los sliders
        :type values: list
        :param ni: Numero de entradas
        :type ni: int
        :param no: Numero de salidas
        :type no: int
        """

        for i in range(ni):
            self.Controlador.input[self.fuzz_inputs[i].label] = values[i]

        try:
            self.Controlador.compute()
        except:
            pass

        # Para crear los objetos de graficacion de PyQtGraph una sola vez
        if self.flagpyqt:
            self.crear_plots_in(window, ni)
            self.crear_plots_out(window, no)
            self.flagpyqt = 0

        self.graficar_prueba_pyqtgraph(window, ni, no)

    def crear_plots_in(self, window, ni):
        """
        Función para crear los objetos de graficacion de PyQtGraph de la entrada, el código para la obtención de los valores de salida y el graficado es una version altamente modificada de la función .view() de Scikit-Fuzzy. Las modificaciones realizadas fueron necesarias para cambiar matplotlib por PyQtGraph
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param ni: Numero de entradas
        :type ni: int
        """

        for i in range(ni):
            window.ingraphs[i].plotwidget.clear()
            window.ingraphs[i].plotwidget.setXRange(*window.InputList[i]['rango'], 0.02)

            entradas = []
            areas = []

            crispy = CrispValueCalculator(self.fuzz_inputs[i], self.Controlador)
            ups_universe, output_mf, cut_mfs = crispy.find_memberships()
            zeros = np.zeros_like(ups_universe, dtype=np.float64)

            color = 0
            for key, term in self.fuzz_inputs[i].terms.items():
                entradas.append(window.ingraphs[i].plotwidget.plot(
                    self.fuzz_inputs[i].universe,
                    term.mf,
                    pen={'width': 2, 'color': pg.mkColor(self.colors[color])}
                    )
                )

                under_plot = window.ingraphs[i].plotwidget.plot(
                    ups_universe,
                    zeros,
                    pen={'width': 0.1, 'color': pg.mkColor(self.colors[color] + '6A')}
                )

                over_plot = window.ingraphs[i].plotwidget.plot(
                    ups_universe,
                    cut_mfs[key],
                    pen={'width': 0.1, 'color': pg.mkColor(self.colors[color] + '6A')}
                )

                fillItem = pg.FillBetweenItem(under_plot,
                                              over_plot,
                                              brush=pg.mkColor(self.colors[color] + '6A'))

                window.ingraphs[i].plotwidget.addItem(fillItem)
                areas.append(copy.copy([under_plot, over_plot]))
                color += 1

            # Código tomado de la función .view() de Scikit-Fuzzy y adaptado para su uso con PyQtGraph
            if len(cut_mfs) > 0 and not all(output_mf == 0):
                crisp_value = self.fuzz_inputs[i].input[self.Controlador]
                if crisp_value is not None:
                    y = 0.
                    for key, term in self.fuzz_inputs[i].terms.items():
                        if key in cut_mfs:
                            y = max(
                                y,
                                interp_membership(self.fuzz_inputs[i].universe,
                                                  term.mf,
                                                  crisp_value))
                    if y < 0.1:
                        y = 1.

                    crispPlot = window.ingraphs[i].plotwidget.plot([crisp_value] * 2,
                                                                   np.asarray([0, y]),
                                                                   pen={
                                                                       'width': 6,
                                                                       'color': 'k'
                                                                   })

                else:
                    crisp_value = 0
            else:
                crisp_value = 0

            self.invalues.append(crispPlot)
            self.inlabelsplot.append(copy.copy(entradas))
            self.inareas.append(copy.copy(areas))

    def crear_plots_out(self, window, no):
        """
        Función para crear los objetos de graficacion de PyQtGraph de la salida, el código para la obtención de los valores de salida y el graficado es una version altamente modificada de la función .view() de Scikit-Fuzzy. Las modificaciones realizadas fueron necesarias para cambiar matplotlib por PyQtGraph
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param no: Numero de salidas
        :type no: int
        """

        for i in range(no):
            window.outgraphs[i].plotwidget.clear()
            window.outgraphs[i].plotwidget.setXRange(*window.OutputList[i]['rango'], 0.02)

            salidas = []
            areas = []

            crispy = CrispValueCalculator(self.fuzz_outputs[i], self.Controlador)
            ups_universe, output_mf, cut_mfs = crispy.find_memberships()
            zeros = np.zeros_like(ups_universe, dtype=np.float64)

            color = 0
            for key, term in self.fuzz_outputs[i].terms.items():
                salidas.append(window.outgraphs[i].plotwidget.plot(
                    self.fuzz_outputs[i].universe,
                    term.mf,
                    pen={
                        'width': 2, 'color': pg.mkColor(self.colors[color])
                    }))

                under_plot = window.outgraphs[i].plotwidget.plot(
                    ups_universe,
                    zeros,
                    pen={
                        'width': 0.1, 'color': pg.mkColor(self.colors[color] + '6A')
                    })
                if key in cut_mfs:
                    over_plot = window.outgraphs[i].plotwidget.plot(
                        ups_universe,
                        cut_mfs[key],
                        pen={
                            'width': 0.1, 'color': pg.mkColor(self.colors[color] + '6A')
                        })
                else:
                    over_plot = window.outgraphs[i].plotwidget.plot(
                        ups_universe,
                        zeros,
                        pen={
                            'width': 0.1, 'color': pg.mkColor(self.colors[color] + '6A')
                        })
                fillItem = pg.FillBetweenItem(under_plot,
                                            over_plot,
                                            brush=pg.mkColor(self.colors[color] + '6A'))

                window.outgraphs[i].plotwidget.addItem(fillItem)
                areas.append(copy.copy([under_plot, over_plot]))
                color += 1

            # Código tomado de la función .view() de Scikit-Fuzzy y adaptado para su uso con PyQtGraph
            if len(cut_mfs) > 0 and not all(output_mf == 0):
                crisp_value = self.fuzz_outputs[i].output[self.Controlador]
                if crisp_value is not None:
                    y = 0.
                    for key, term in self.fuzz_outputs[i].terms.items():
                        if key in cut_mfs:
                            y = max(
                                y,
                                interp_membership(self.fuzz_outputs[i].universe,
                                                  term.mf,
                                                  crisp_value))
                    if y < 0.1:
                        y = 1.

                    crispPlot = window.outgraphs[i].plotwidget.plot([crisp_value] * 2,
                                                                    np.asarray([0, y]),
                                                                    pen={
                                                                        'width': 6,
                                                                        'color': 'k'
                                                                    })

                else:
                    crisp_value = 0
                    crispPlot = window.outgraphs[i].plotwidget.plot([crisp_value] * 2,
                                                                    np.asarray([0, 0]),
                                                                    pen={
                                                                        'width': 6,
                                                                        'color': 'k'
                                                                    })
            else:
                crisp_value = 0
                crispPlot = window.outgraphs[i].plotwidget.plot([crisp_value] * 2,
                                                                    np.asarray([0, 0]),
                                                                    pen={
                                                                        'width': 6,
                                                                        'color': 'k'
                                                                    })

            self.outvalues.append(crispPlot)
            self.outlabelsplot.append(copy.copy(salidas))
            self.outareas.append(copy.copy(areas))

    def graficar_prueba_pyqtgraph(self, window, ni, no):
        """
        Función para actualizar la grafica en función de las nuevas entradas, código tomado y modificado de la función .view() de Scikit-Fuzzy y adaptado para su uso con PyQtGraph
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param ni: Numero de entradas
        :type ni: int
        :param no: Numero de salidas
        :type no: int
        """

        for i in range(ni):
            crispy = CrispValueCalculator(self.fuzz_inputs[i], self.Controlador)
            ups_universe, output_mf, cut_mfs = crispy.find_memberships()
            zeros = np.zeros_like(ups_universe, dtype=np.float64)

            for etiq, label in enumerate(window.InputList[i]['etiquetas']):
                self.inlabelsplot[i][etiq].setData(
                    self.fuzz_inputs[i].universe,
                    self.fuzz_inputs[i].terms[label['nombre']].mf)
                under_plot, over_plot = self.inareas[i][etiq]
                under_plot.setData(ups_universe, zeros)
                over_plot.setData(ups_universe, cut_mfs[label['nombre']])

            # Código tomado de la función .view() de Scikit-Fuzzy y adaptado para su uso con PyQtGraph
            if len(cut_mfs) > 0 and not all(output_mf == 0):
                crisp_value = self.fuzz_inputs[i].input[self.Controlador]
                if crisp_value is not None:
                    y = 0.
                    for key, term in self.fuzz_inputs[i].terms.items():
                        if key in cut_mfs:
                            y = max(
                                y,
                                interp_membership(self.fuzz_inputs[i].universe,
                                                  term.mf,
                                                  crisp_value))
                    if y < 0.1:
                        y = 1.

                    self.invalues[i].setData([crisp_value] * 2, np.asarray([0, y]))
                else:
                    crisp_value = 0
            else:
                crisp_value = 0

        for i in range(no):
            crispy = CrispValueCalculator(self.fuzz_outputs[i], self.Controlador)
            ups_universe, output_mf, cut_mfs = crispy.find_memberships()
            zeros = np.zeros_like(ups_universe, dtype=np.float64)

            for etiq, label in enumerate(window.OutputList[i]['etiquetas']):
                self.outlabelsplot[i][etiq].setData(
                    self.fuzz_outputs[i].universe,
                    self.fuzz_outputs[i].terms[label['nombre']].mf)
                under_plot, over_plot = self.outareas[i][etiq]
                under_plot.setData(ups_universe, zeros)
                if label['nombre'] in cut_mfs:
                    over_plot.setData(ups_universe, cut_mfs[label['nombre']])
                else:
                    over_plot.setData(ups_universe, zeros)

            # Código tomado de la función .view() de Scikit-Fuzzy y adaptado para su uso con PyQtGraph
            if len(cut_mfs) > 0 and not all(output_mf == 0):
                crisp_value = self.fuzz_outputs[i].output[self.Controlador]
                if crisp_value is not None:
                    y = 0.
                    for key, term in self.fuzz_outputs[i].terms.items():
                        if key in cut_mfs:
                            y = max(
                                y,
                                interp_membership(self.fuzz_outputs[i].universe,
                                                  term.mf,
                                                  crisp_value))
                    if y < 0.1:
                        y = 1.

                    self.outvalues[i].setData([crisp_value] * 2, np.asarray([0, y]))
                    window.outtestlabels[i].setText(window.OutputList[i]['nombre'] +
                                            f': {np.around(crisp_value, 3)}')
                else:
                    crisp_value = 0
            else:
                try:
                    crisp_value = self.fuzz_outputs[i].output[self.Controlador]
                    if crisp_value is not None:
                        y = 0.
                        for key, term in self.fuzz_outputs[i].terms.items():
                            if key in cut_mfs:
                                y = max(
                                    y,
                                    interp_membership(self.fuzz_outputs[i].universe,
                                                    term.mf,
                                                    crisp_value))
                        if y < 0.1:
                            y = 1.

                        self.outvalues[i].setData([crisp_value] * 2, np.asarray([0, y]))
                        window.outtestlabels[i].setText(window.OutputList[i]['nombre'] +
                                                f': {np.around(crisp_value, 3)}')
                    else:
                        crisp_value = 0
                        window.outtestlabels[i].setText(window.OutputList[i]['nombre'] +
                                                    f': error, faltan reglas')
                except:
                    crisp_value = 0
                    window.outtestlabels[i].setText(window.OutputList[i]['nombre'] +
                                                    f': error, faltan reglas')

    def graficar_respuesta_2d(self, window, inrange, no):
        """
        Función para graficar la respuesta del controlador en caso de poseer una entrada
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param inrange: Rango de la variable de entrada
        :type inrange: list
        :param no: Numero de salidas
        :type no: int
        """
        entrada = np.linspace(*inrange, 500)

        entradas = []
        salidas = [[] for _ in range(no)]

        for value in entrada:
            self.Controlador.input[self.fuzz_inputs[0].label] = value
            try:
                self.Controlador.compute()
                entradas.append(value)
                for o in range(no):
                    salidas[o].append(self.Controlador.output[self.fuzz_outputs[o].label])
            except:
                pass

        # Se muestra una grafica por cada salida
        for o in range(no):
            window.respuesta2ds[o].canvas.axes.clear()
            window.respuesta2ds[o].canvas.axes.plot(entradas, salidas[o])
            window.respuesta2ds[o].canvas.axes.grid(color="lightgray")
            window.respuesta2ds[o].canvas.axes.set_xlabel(self.fuzz_inputs[0].label)
            window.respuesta2ds[o].canvas.axes.set_ylabel(self.fuzz_outputs[o].label)
            window.respuesta2ds[o].canvas.draw()
            window.respuesta2ds[o].toolbar.update()

    def graficar_respuesta_3d(self, window, inrange1, inrange2, no):
        """
        Función para graficar la superficie de respuesta del controlador en caso de poseer 2 entradas
        
        :param window: Objeto que contiene a la ventana principal
        :type window: object
        :param inrange1: Rango de la variable de entrada uno
        :type inrange1: list
        :param inrange2: Rango de la variable de entrada dos
        :type inrange2: list
        :param no: Numero de salidas
        :type no: int
        """

        n_puntos = 25
        entrada1 = np.linspace(*inrange1, n_puntos)
        entrada2 = np.linspace(*inrange2, n_puntos)
        entrada1, entrada2 = np.meshgrid(entrada1, entrada2)

        entrada11 = [np.zeros_like(entrada1) for _ in range(no)]
        entrada22 = [np.zeros_like(entrada2) for _ in range(no)]

        salidas = [np.zeros_like(entrada1) for _ in range(no)]

        for i in range(n_puntos):
            for j in range(n_puntos):
                self.Controlador.input[self.fuzz_inputs[0].label] = entrada1[i, j]
                self.Controlador.input[self.fuzz_inputs[1].label] = entrada2[i, j]

                # Se almacenan solo los valores validos
                try:
                    self.Controlador.compute()
                    for o in range(no):
                        entrada11[o][i, j] = entrada1[i, j]
                        entrada22[o][i, j] = entrada2[i, j]
                        salidas[o][i, j] = self.Controlador.output[
                            self.fuzz_outputs[o].label]
                except:
                    pass

        # Se grafica una superficie por cada salida
        for o in range(no):
            window.respuesta3ds[o].canvas.axes.clear()

            if window.respuesta3ds[o].colorbar != 0:
                window.respuesta3ds[o].colorbar.remove()

            surface = window.respuesta3ds[o].canvas.axes.plot_surface(entrada11[o], entrada22[o], salidas[o],
                                                            rstride=1, cstride=1, cmap='viridis', linewidth=0.4, antialiased=True)

            window.respuesta3ds[o].colorbar = window.respuesta3ds[o].canvas.figure.colorbar(surface)

            window.respuesta3ds[o].canvas.axes.view_init(30, 200)
            window.respuesta3ds[o].canvas.axes.set_xlabel(self.fuzz_inputs[0].label)
            window.respuesta3ds[o].canvas.axes.set_ylabel(self.fuzz_inputs[1].label)
            window.respuesta3ds[o].canvas.axes.set_zlabel(self.fuzz_outputs[o].label)
            window.respuesta3ds[o].canvas.draw()

    def calcular_valor(self, inputs, outputs):
        """
        Función para calcular las salidas del controlador dado sus entradas, esta función se utiliza en la funcionalidad de simulación de sistemas de control
        
        :param inputs: Lista con los valores de entrada
        :type inputs: list
        :param outputs: Lista vaciá del tamaño del numero de salidas
        :type outputs: list
        :return: Lista de valores de salida del controlador difuso
        :rtype: list
        """

        for i, value in enumerate(inputs):
            # Para asegurar los limites del universe de discurso
            value = np.clip(value, np.min(self.fuzz_inputs[i].universe), np.max(self.fuzz_inputs[i].universe))

            self.Controlador.input[self.fuzz_inputs[i].label] = value
        try:
            self.Controlador.compute()
        except:
            return [0]*len(outputs)

        for o in range(len(outputs)):
            outputs[o] = self.Controlador.output[self.fuzz_outputs[o].label]

        return outputs


class FISParser:
    """
    Clase para cargar y exportar archivos .fis, para cargar los archivos FIS las funciones get_system, get_vars,get_var y get_rules fueron tomadas de yapflm:
    
    Yet Another Python Fuzzy Logic Module: https://github.com/sputnick1124/yapflm
    
    Para obtener los datos necesarias del .fis, de allí, se aplica la función fis_to_json para completar el parsin. En el caso de la exportación, se realiza utilizando la función json_to_fis
    """

    def __init__(self, file, InputList=None, OutputList=None, RuleEtiquetas=None):
        """
        Constructor de la clase, inicializa las variables a utilizar y selecciona entre cargar el fis o exportarlo dependiendo de las variables con las que se cree el objeto
        
        :param file: Dirección del archivo a cargar o exportar
        :type file: str
        :param inputlist: Lista de variables de entrada, defaults to None
        :type inputlist: list, opcional
        :param OutputList: Lista de variables de entrada, defaults to None
        :type OutputList: list, opcional
        :param RuleEtiquetas: Lista con la información necesaria para crear las reglas, defaults to None
        :type RuleEtiquetas: list, opcional
        """

        # Cargar archivo .fis
        if InputList is None and OutputList is None and RuleEtiquetas is None:
            with open(file, 'r') as infis:
                self.rawlines = infis.readlines()
            self.systemList = 0
            self.InputList = []
            self.OutputList = []
            self.RuleList = []
            self.get_system()
            self.get_vars()
            self.get_rules()
        else:
            # Exportar archivo .fis
            self.file = file
            self.InputList = InputList
            self.OutputList = OutputList
            self.RuleEtiquetas = RuleEtiquetas
            self.json_to_fis()

    def get_system(self):
        """ Función tomada de yapflm (Yet Another Python Fuzzy Logic Module) """

        end_sysblock = self.rawlines.index('\n')
        systemblock = self.rawlines[1:end_sysblock]
        fisargs = map(lambda x: parse('{arg}={val}', x), systemblock)
        fissys = {f['arg'].lower(): f['val'].strip("'") for f in fisargs}
        self.numinputs = int(fissys['numinputs'])
        self.numoutputs = int(fissys['numoutputs'])
        self.numrules = int(fissys['numrules'])
        self.start_varblocks = end_sysblock + 1
        self.systemList = fissys

    def get_var(self, vartype, varnum, start_line, end_line):
        """ Función tomada de yapflm (Yet Another Python Fuzzy Logic Module) """

        varblock = self.rawlines[start_line:end_line]
        fisargs = map(lambda x: parse('{arg}={val}', x), varblock)
        fisvar = {f['arg'].lower(): f['val'].strip("'") for f in fisargs}

        if 'input' in vartype:
            self.InputList.append(fisvar)
        elif 'output' in vartype:
            self.OutputList.append(fisvar)

    def get_vars(self):
        """ Función tomada de yapflm (Yet Another Python Fuzzy Logic Module) """

        start_ruleblock = self.rawlines.index('[Rules]\n')
        var_lines = []
        var_types = []
        flag = 0
        for i, line in enumerate(self.rawlines[self.start_varblocks - 1:start_ruleblock]):
            if flag:
                flag = 0
                vt = parse('[{type}{num:d}]', line)
                var_types.append((vt['type'].lower(), vt['num']))
            if line == '\n':
                var_lines.append(i + self.start_varblocks - 1)
                flag = 1
        for i, l in enumerate(var_lines[:-1]):
            if 'input' in var_types[i][0]:
                self.get_var('input', var_types[i][1] - 1, l + 2, var_lines[i + 1])
            elif 'output' in var_types[i][0]:
                self.get_var('output', var_types[i][1] - 1, l + 2, var_lines[i + 1])

    def get_rules(self):
        """ Función tomada de yapflm (Yet Another Python Fuzzy Logic Module) """

        start_ruleblock = self.rawlines.index('[Rules]\n')
        ruleblock = self.rawlines[start_ruleblock + 1:]
        antecedents = (('{a%d:d} ' * self.numinputs) %
                       tuple(range(self.numinputs))).strip()
        consequents = ('{c%d:d} ' * self.numoutputs) % tuple(range(self.numoutputs))
        p = antecedents + ', ' + consequents + '({w:d}) : {c:d}'
        for rule in ruleblock:
            try:
                p = antecedents + ', ' + consequents + '({w:d}) : {c:d}'
                rp = parse(p, rule)
                r = []
                for inp in range(self.numinputs):
                    rpar = rp['a%d' % inp]
                    rval = rpar if rpar != 0 else None
                    r.append(rval)
                for outp in range(self.numoutputs):
                    rpar = rp['c%d' % outp]
                    rval = rpar if rpar != 0 else None
                    r.append(rval)
                r += [rp['w'], rp['c'] - 1]
                self.RuleList.append(r)
            except:
                p = antecedents + ', ' + consequents + '({w:f}) : {c:d}'
                rp = parse(p, rule)
                r = []
                for inp in range(self.numinputs):
                    rpar = rp['a%d' % inp]
                    rval = rpar if rpar != 0 else None
                    r.append(rval)
                for outp in range(self.numoutputs):
                    rpar = rp['c%d' % outp]
                    rval = rpar if rpar != 0 else None
                    r.append(rval)
                r += [rp['w'], rp['c'] - 1]
                self.RuleList.append(r)

    def fis_to_json(self):
        """ 
        Función para completar la creación del controlador a partir de un archivo .fis
        
        :return: Conjunto de entradas, salidas y reglas
        :rtype: tuple(list)
        """

        # Datos del controlador
        ni = int(self.systemList['numinputs'])
        no = int(self.systemList['numoutputs'])
        nr = int(self.systemList['numrules'])

        InputList = [0] * ni
        OutputList = [0] * no
        RuleEtiquetas = []

        # Creación de las variables de entrada
        for i in range(ni):
            InputList[i] = {
                "nombre":
                    self.InputList[i]['name'],
                "numeroE":
                    int(self.InputList[i]['nummfs']),
                "etiquetas": [0] * int(self.InputList[i]['nummfs']),
                "rango":
                    ast.literal_eval(
                        re.sub("\s+", ",", self.InputList[i]['range'].strip()))
            }
            
            for ne in range(int(self.InputList[i]['nummfs'])):
                temp_etiqueta = self.InputList[i]['mf' + str(ne + 1)].replace(
                    "'", '').split(':')
                temp2 = temp_etiqueta[1].split(',')
                InputList[i]['etiquetas'][ne] = {
                    "nombre": temp_etiqueta[0],
                    "mf": temp2[0],
                    "definicion": ast.literal_eval(re.sub("\s+", ",", temp2[1].strip()))
                }
        
        # Creación de las variables de salida
        for i in range(no):
            OutputList[i] = {
                "nombre":
                    self.OutputList[i]['name'],
                "numeroE":
                    int(self.OutputList[i]['nummfs']),
                "etiquetas": [0] * int(self.OutputList[i]['nummfs']),
                "rango":
                    ast.literal_eval(
                        re.sub("\s+", ",", self.OutputList[i]['range'].strip())),
                "metodo":
                    self.systemList['defuzzmethod']
            }

            for ne in range(int(self.OutputList[i]['nummfs'])):
                temp_etiqueta = self.OutputList[i]['mf' + str(ne + 1)].replace(
                    "'", '').split(':')
                temp2 = temp_etiqueta[1].split(',')
                OutputList[i]['etiquetas'][ne] = {
                    "nombre": temp_etiqueta[0],
                    "mf": temp2[0],
                    "definicion": ast.literal_eval(re.sub("\s+", ",", temp2[1].strip()))
                }

        # Creación de las reglas
        for numeror, i in enumerate(self.RuleList):
            ril = []
            rol = []

            for j in range(ni):
                if i[j] is not None:
                    nombre = InputList[j]['etiquetas'][abs(i[j]) - 1]['nombre']
                    numero = j
                    negacion = False if i[j] > 0 else True
                    ril.append([nombre, numero, negacion])

            for j in range(ni, no + ni):
                if i[j] is not None:
                    if i[j] < 0:
                        raise TypeError('No se permiten salidas negadas')
                    nombre = OutputList[j - ni]['etiquetas'][abs(i[j]) - 1]['nombre']
                    numero = j - ni
                    peso = float(i[no + ni])
                    rol.append([nombre, numero, peso])

            and_condition = True if i[ni + no + 1] == 0 else False
            RuleEtiquetas.append(copy.deepcopy([ril, rol, and_condition]))

        return copy.deepcopy(InputList), copy.deepcopy(OutputList), copy.deepcopy(RuleEtiquetas)

    def json_to_fis(self):
        """ Función para exportar el controlador en formato .fis """

        # Datos del controlador
        ni = len(self.InputList)
        no = len(self.OutputList)
        nr = len(self.RuleEtiquetas)

        with open(self.file, 'w') as f:

            # Información general del controlador
            f.write(f"[System]\n")
            f.write(f"Name='{self.file.split('/')[-1].split('.')[0]}'\n")
            f.write(f"Type='mamdani'\n")
            f.write(f"Version=2.0\n")
            f.write(f"NumInputs={ni}\n")
            f.write(f"NumOutputs={no}\n")
            f.write(f"NumRules={nr}\n")
            f.write(f"AndMethod='min'\n")
            f.write(f"OrMethod='max'\n")
            f.write(f"ImpMethod='min'\n")
            f.write(f"AggMethod='max'\n")
            f.write(f"DefuzzMethod='{self.OutputList[0]['metodo']}'\n")
            f.write(f"\n")

            # Parsin de las entradas del controlador
            for i in range(ni):
                f.write(f"[Input" + str(i + 1) + "]\n")
                f.write(f"Name='{self.InputList[i]['nombre']}'\n")
                string_temp = re.sub('\s+', '',
                                     str(self.InputList[i]['rango'])).replace(',', ' ')
                f.write(f"Range={string_temp}\n")
                f.write(f"NumMFs={self.InputList[i]['numeroE']}\n")

                for ne in range(self.InputList[i]['numeroE']):
                    string_temp = re.sub(
                        '\s+', '',
                        str(self.InputList[i]['etiquetas'][ne]['definicion'])).replace(
                            ',', ' ')
                    f.write(
                        f"MF{ne+1}='{self.InputList[i]['etiquetas'][ne]['nombre']}"
                        f"':'{self.InputList[i]['etiquetas'][ne]['mf']}',{string_temp}\n"
                    )

                f.write(f"\n")

            # Parsin de las salidas del controlador
            for i in range(no):
                f.write(f"[Output" + str(i + 1) + "]\n")
                f.write(f"Name='{self.OutputList[i]['nombre']}'\n")
                string_temp = re.sub('\s+', '',
                                     str(self.OutputList[i]['rango'])).replace(',', ' ')
                f.write(f"Range={string_temp}\n")
                f.write(f"NumMFs={self.OutputList[i]['numeroE']}\n")

                for ne in range(self.OutputList[i]['numeroE']):
                    string_temp = re.sub(
                        '\s+', '',
                        str(self.OutputList[i]['etiquetas'][ne]['definicion'])).replace(
                            ',', ' ')
                    f.write(
                        f"MF{ne+1}='{self.OutputList[i]['etiquetas'][ne]['nombre']}"
                        f"':'{self.OutputList[i]['etiquetas'][ne]['mf']}',{string_temp}\n"
                    )

                f.write(f"\n")

            # Parsin de las reglas del controlador
            rules_no_format = []
            for i, rule in enumerate(self.RuleEtiquetas):

                inner_rules = []

                # set de entradas
                for nir in range(ni):
                    for inputrule in rule[0]:
                        if nir == inputrule[1]:
                            if not inputrule[2]:
                                for ner, etiqueta in enumerate(self.InputList[nir]['etiquetas']):
                                    if etiqueta['nombre'] == inputrule[0]:
                                        inner_rules.append(ner + 1)
                                        break
                            else:
                                for ner, etiqueta in enumerate(self.InputList[nir]['etiquetas']):
                                    if etiqueta['nombre'] == inputrule[0]:
                                        inner_rules.append(-ner - 1)
                                        break

                            break
                        else:
                            continue
                    else:
                        inner_rules.append(0)
                        break

                # set de salidas
                for nor in range(no):
                    for outputtrule in rule[1]:
                        if nor == outputtrule[1]:
                            for ner, etiqueta in enumerate(self.OutputList[nor]['etiquetas']):
                                if etiqueta['nombre'] == outputtrule[0]:
                                    inner_rules.append(ner + 1)
                                    break
                            break
                        else:
                            continue
                    else:
                        inner_rules.append(0)

                inner_rules.append(rule[1][0][2])

                if rule[2]:
                    inner_rules.append(1)
                else:
                    inner_rules.append(2)

                rules_no_format.append(copy.deepcopy(inner_rules))

            f.write(f"[Rules]\n")

            # Escribiendo las reglas en el archivo
            for i in range(nr):
                rule_str = ""
                for j in range(ni):
                    if not j == ni - 1:
                        rule_str += str(rules_no_format[i][j]) + " "
                    else:
                        rule_str += str(rules_no_format[i][j])
                rule_str += ", "
                for j in range(ni, ni + no):
                    rule_str += str(rules_no_format[i][j]) + " "
                rule_str += f"({str(rules_no_format[i][ni+no])})" + " "
                rule_str += f": {str(rules_no_format[i][ni+no+1])}\n"
                f.write(rule_str)


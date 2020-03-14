""" 
Archivo para el manejo de la función de diseño de controladores difusos, sirve de intermediario entre la interfaz grafica y la clase creada para manejar el controlador difuso definida en rutinas_fuzzy.py 
"""


from handlers.modificadorMf import update_definicionmf, validacion_mf
from rutinas.rutinas_fuzzy import FuzzyController
from rutinas.rutinas_fuzzy import FISParser
from PySide2 import QtCore, QtGui, QtWidgets

import numpy as np

import copy
import json


def FuzzyHandler(self):
    """
    Función principal para el manejo de diseño de controladores difusos, se crean las señales a ejecutar cuando se interactuá con los widgets
    """

    self.EntradasTab = self.main.fuzzyTabWidget.widget(1)
    self.SalidasTab = self.main.fuzzyTabWidget.widget(2)
    self.ReglasTab = self.main.fuzzyTabWidget.widget(3)
    self.PruebaTab = self.main.fuzzyTabWidget.widget(4)
    self.RespuestaTab = self.main.fuzzyTabWidget.widget(5)

    self.main.guardarFuzzButton.setDisabled(True)
    self.main.guardarComoFuzzButton.setDisabled(True)
    self.main.exportarFuzzButton.setDisabled(True)

    # Ocultado de los tabs
    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    self.main.fuzzyTabWidget.removeTab(3)
    self.main.fuzzyTabWidget.removeTab(2)
    self.main.fuzzyTabWidget.removeTab(1)

    # Listas que definen al controlador difuso
    self.InputList = []
    self.OutputList = []
    self.RuleList = []
    self.RuleEtiquetas = []

    # Lista para para controlar un desplazamiento de ventana
    self.vector_rotacion = [-0.25, 0, 0.25, 0.5, 0.75, 1, 1.25]
    self.rotacion_windowIn = 2
    self.rotacion_windowOut = 2

    # Objeto de la clase FuzzyController
    self.fuzzInitController = FuzzyController

    # Objeto de la clase FISParser, para cargar y exportar .FIS
    self.parser = FISParser

    # Almacenado de widgets en listas para acceder a ellos por indices
    crear_vectores_de_widgets(self)

    # Ocultado de widgets
    for i_f, o_f, it_f, ot_f, f2d, f3d in zip(
        self.inframes,
        self.outframes,
        self.intestframes,
        self.outtestframes,
        self.respuesta2dframes,
        self.respuesta3dframes,
    ):
        i_f.hide()
        o_f.hide()
        it_f.hide()
        ot_f.hide()
        f2d.hide()
        f3d.hide()

    self.main.imagenEsquemas.setPixmap(
        QtGui.QPixmap(":/imagenes/imagenes/sinEsquema.png")
    )
    self.main.estrucNumberInputs.currentIndexChanged.connect(
        lambda: imagen_entradas(self)
    )
    self.main.estrucNumberOutputs.currentIndexChanged.connect(
        lambda: imagen_salidas(self)
    )
    self.main.fuzzyEsquemasCheck.clicked["bool"].connect(lambda: check_esquema_show(self))
    self.main.fuzzyEsquemas.currentIndexChanged.connect(lambda: show_esquema(self))
    self.main.generarFuzzyButton.clicked.connect(lambda: crear_tabs(self))
    self.main.guardarFuzzButton.clicked.connect(lambda: guardar_controlador(self))
    self.main.cargarFuzzButton.clicked.connect(lambda: cargar_controlador(self))
    self.main.guardarComoFuzzButton.clicked.connect(lambda: guardarcomo_controlador(self))
    self.main.exportarFuzzButton.clicked.connect(lambda: exportar_fis(self))

    self.main.inputNumber.currentIndexChanged.connect(lambda: seleccion_entrada(self))
    self.main.inputNombre.editingFinished.connect(lambda: nombre_entrada(self))
    self.main.inputNombre.focusIn.connect(lambda: cerrar_prueba(self))
    self.main.inputEtiquetasNum.editingFinished.connect(
        lambda: numero_de_etiquetas_in(self)
    )
    self.main.inputEtiquetasNum.focusIn.connect(lambda: cerrar_prueba(self))
    self.main.inputRange.editingFinished.connect(lambda: rango_in(self))
    self.main.inputRange.focusIn.connect(lambda: cerrar_prueba(self))

    self.main.etiquetaNumIn.currentIndexChanged.connect(
        lambda: seleccion_etiqueta_in(self)
    )
    self.main.etiquetaNombreIn.editingFinished.connect(lambda: nombre_etiqueta_in(self))
    self.main.etiquetaNombreIn.focusIn.connect(lambda: cerrar_prueba(self))
    self.main.etiquetaMfIn.currentIndexChanged.connect(lambda: seleccion_mf_in(self))
    self.main.etiquetaDefinicionIn.editingFinished.connect(lambda: definicion_in(self))
    self.main.etiquetaDefinicionIn.focusIn.connect(lambda: cerrar_prueba(self))

    self.main.outputNumber.currentIndexChanged.connect(lambda: seleccion_salida(self))
    self.main.outputNombre.editingFinished.connect(lambda: nombre_salida(self))
    self.main.outputNombre.focusIn.connect(lambda: cerrar_prueba(self))
    self.main.outputEtiquetasNum.editingFinished.connect(
        lambda: numero_de_etiquetas_out(self)
    )
    self.main.outputEtiquetasNum.focusIn.connect(lambda: cerrar_prueba(self))
    self.main.outputRange.editingFinished.connect(lambda: rango_out(self))
    self.main.outputRange.focusIn.connect(lambda: cerrar_prueba(self))
    self.main.defuzzMethodOut.currentIndexChanged.connect(lambda: defuzz_metodo(self))

    self.main.etiquetaNumOut.currentIndexChanged.connect(
        lambda: seleccion_etiqueta_out(self)
    )
    self.main.etiquetaNombreOut.editingFinished.connect(lambda: nombre_etiqueta_out(self))
    self.main.etiquetaNombreOut.focusIn.connect(lambda: cerrar_prueba(self))
    self.main.etiquetaMfOut.currentIndexChanged.connect(lambda: seleccion_mf_out(self))
    self.main.etiquetaDefinicionOut.editingFinished.connect(lambda: definicion_out(self))
    self.main.etiquetaDefinicionOut.focusIn.connect(lambda: cerrar_prueba(self))

    self.main.fuzzyTabWidget.currentChanged.connect(lambda: rule_list_visualizacion(self))
    self.main.rulelistWidget.currentRowChanged.connect(
        lambda: seleccionar_etiquetas(self)
    )
    self.main.ruleAgregarButton.clicked.connect(lambda: rule_list_agregar(self))
    self.main.ruleEliminarButton.clicked.connect(lambda: rule_list_eliminar(self))
    self.main.ruleCambiarButton.clicked.connect(lambda: rule_list_cambiar(self))
    self.main.ruleCrearButton.clicked.connect(lambda: crear_controlador(self))

    for slider in self.intestsliders:
        slider.valueChanged.connect(lambda: prueba_input(self))


def cerrar_prueba(self):
    """ Función para cerrar las pestañas de pruebas ante cambios en el controlador difuso """
    
    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)

def imagen_entradas(self):
    """ Función para establecer la imagen del numero de entradas """

    ni = self.main.estrucNumberInputs.currentIndex() + 1
    self.main.imagenInputs.setPixmap(
        QtGui.QPixmap(":/imagenes/imagenes/entrada" + str(ni) + ".png")
    )


def imagen_salidas(self):
    """ Función para establecer la imagen del numero de salidas """
    no = self.main.estrucNumberOutputs.currentIndex() + 1
    self.main.imagenOutputs.setPixmap(
        QtGui.QPixmap(":/imagenes/imagenes/salida" + str(no) + ".png")
    )


def check_esquema_show(self):
    """ Función para mediar entre entradas y salidas genéricas y esquemas de control """

    if not self.main.fuzzyEsquemasCheck.isChecked():
        self.main.imagenEsquemas.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/sinEsquema.png")
        )
        imagen_entradas(self)
        imagen_salidas(self)
    else:
        show_esquema(self)


def show_esquema(self):
    """ Función para establecer la imagen del esquema de control seleccionado """

    if self.main.fuzzyEsquemas.currentIndex() == 0:
        self.main.imagenEsquemas.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/pidDifuso.png")
        )
        self.main.imagenInputs.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/entrada3.png")
        )
        self.main.imagenOutputs.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/salida1.png")
        )
    elif self.main.fuzzyEsquemas.currentIndex() == 1:
        self.main.imagenEsquemas.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/piDifuso.png"))
        self.main.imagenInputs.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/entrada2.png")
        )
        self.main.imagenOutputs.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/salida1.png")
        )
    elif self.main.fuzzyEsquemas.currentIndex() == 2:
        self.main.imagenEsquemas.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/pdDifuso.png"))
        self.main.imagenInputs.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/entrada2.png")
        )
        self.main.imagenOutputs.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/salida1.png")
        )
    elif self.main.fuzzyEsquemas.currentIndex() == 3:
        self.main.imagenEsquemas.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/GainScheduler.png"))
        self.main.imagenInputs.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/entrada2.png")
        )
        self.main.imagenOutputs.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/salida3.png")
        )
    elif self.main.fuzzyEsquemas.currentIndex() == 4:
        self.main.imagenEsquemas.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/pidplusDifuso.png"))
        self.main.imagenInputs.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/entrada1.png")
        )
        self.main.imagenOutputs.setPixmap(
            QtGui.QPixmap(":/imagenes/imagenes/salida1.png")
        )


def crear_tabs(self):
    """ Función para iniciar el entorno de diseño para entradas y salidas genéricas """

    if not self.main.fuzzyEsquemasCheck.isChecked():
        self.setWindowTitle(
            "Laboratorio Virtual - Nuevo controlador sin guardar*"
        )

        self.main.inputNumber.blockSignals(True)
        self.main.outputNumber.blockSignals(True)
        self.main.inputNombre.setReadOnly(False)
        self.main.outputNombre.setReadOnly(False)

        # Vaciado de información previa
        self.current_file = ""
        self.InputList = []
        self.OutputList = []
        self.RuleList = []
        self.RuleEtiquetas = []

        # Habilitar guardado de archivos
        self.main.guardarFuzzButton.setEnabled(True)
        self.main.guardarComoFuzzButton.setEnabled(True)
        self.main.exportarFuzzButton.setEnabled(True)

        # Se ocultan todos los tabs y se muestran solo Entradas, Salidas y Reglas
        self.main.fuzzyTabWidget.removeTab(5)
        self.main.fuzzyTabWidget.removeTab(4)
        self.main.fuzzyTabWidget.removeTab(3)
        self.main.fuzzyTabWidget.removeTab(2)
        self.main.fuzzyTabWidget.removeTab(1)

        self.main.fuzzyTabWidget.addTab(self.EntradasTab, "Entradas")
        self.main.fuzzyTabWidget.addTab(self.SalidasTab, "Salidas")
        self.main.fuzzyTabWidget.addTab(self.ReglasTab, "Reglas")

        NumeroEntradas = int(self.main.estrucNumberInputs.currentText())
        NumeroSalidas = int(self.main.estrucNumberOutputs.currentText())

        self.main.inputNumber.clear()
        self.main.outputNumber.clear()

        # Creación de funciones de membresía genéricas
        for i in range(NumeroEntradas):
            self.main.inputNumber.insertItem(i, str(i + 1))
            temp_dic = inputDic_creator(self, i)
            self.InputList.append(temp_dic)
            ini_range_etiquetas = np.arange(-20, 21, 20 / 2).tolist()
            window = 0
            for j in range(self.InputList[i]["numeroE"]):
                self.InputList[i]["etiquetas"][j] = EtiquetasDic_creator(
                    self, j, ini_range_etiquetas[window:window + 3]
                )
                window += 1

        for i in range(NumeroSalidas):
            self.main.outputNumber.insertItem(i, str(i + 1))
            temp_dic = outputDic_creator(self, i)
            self.OutputList.append(temp_dic)
            ini_range_etiquetas = np.arange(-20, 21, 20 / 2).tolist()
            window = 0
            for j in range(self.OutputList[i]["numeroE"]):
                self.OutputList[i]["etiquetas"][j] = EtiquetasDic_creator(
                    self, j, ini_range_etiquetas[window:window + 3]
                )
                window += 1

        self.main.inputNumber.blockSignals(False)
        self.main.outputNumber.blockSignals(False)

        # Se inicializa el controlador con la información actual
        self.fuzzController = self.fuzzInitController(self.InputList, self.OutputList)

        seleccion_entrada(self)
        seleccion_salida(self)

        self.fuzzController.graficar_mf_in(self, 0)
        self.fuzzController.graficar_mf_out(self, 0)
    else:
        # En caso de que se seleccione un esquema y no entradas y salidas genéricas
        cargar_esquema(self)


def inputDic_creator(self, i):
    """
    Función para crear entradas genéricas
    
    :param i: Numero de entrada
    :type i: int
    """

    inputDic = {
        "nombre": "entrada" + str(i + 1),
        "numeroE": 3,
        "etiquetas": [0] * 3,
        "rango": [-10, 10],
    }
    return inputDic


def outputDic_creator(self, i):
    """
    Función para crear salidas genéricas
    
    :param i: Numero de salida
    :type i: int
    """

    outputDic = {
        "nombre": "salida" + str(i + 1),
        "numeroE": 3,
        "etiquetas": [0] * 3,
        "rango": [-10, 10],
        "metodo": "centroid",
    }
    return outputDic


def EtiquetasDic_creator(self, j, erange):
    """
    Función para crear etiquetas genéricas
    
    :param j: Numero de etiqueta
    :type j: int
    :param erange: Definición de la función de membresía
    :type erange: list
    """

    etiquetaDic = {
        "nombre": "etiqueta" + str(j + 1),
        "mf": "trimf",
        "definicion": round_list(erange),
    }
    return etiquetaDic


def cargar_esquema(self):
    """ Función para iniciar el entorno de diseño a partir de un esquema de control seleccionado """

    # Carga del archivo correspondiente al esquema seleccionado
    path = self.resource_path(
        "Esquemas/" + self.main.fuzzyEsquemas.currentText() + ".json"
    )
    with open(path, "r") as f:
        self.InputList, self.OutputList, self.RuleEtiquetas = json.load(f)

    self.main.inputNombre.setReadOnly(True)
    self.main.outputNombre.setReadOnly(True)
    self.current_file = ""

    # Habilitar guardado de archivos
    self.main.guardarFuzzButton.setEnabled(True)
    self.main.guardarComoFuzzButton.setEnabled(True)
    self.main.exportarFuzzButton.setEnabled(True)

    self.main.inputNumber.blockSignals(True)
    self.main.outputNumber.blockSignals(True)

    # Se ocultan todos los tabs y se muestran solo Entradas, Salidas y Reglas
    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    self.main.fuzzyTabWidget.removeTab(3)
    self.main.fuzzyTabWidget.removeTab(2)
    self.main.fuzzyTabWidget.removeTab(1)

    self.main.fuzzyTabWidget.addTab(self.EntradasTab, "Entradas")
    self.main.fuzzyTabWidget.addTab(self.SalidasTab, "Salidas")
    self.main.fuzzyTabWidget.addTab(self.ReglasTab, "Reglas")

    self.main.inputNumber.clear()
    self.main.outputNumber.clear()

    for i in range(len(self.InputList)):
        self.main.inputNumber.insertItem(i, str(i + 1))

    for i in range(len(self.OutputList)):
        self.main.outputNumber.insertItem(i, str(i + 1))

    self.main.inputNumber.blockSignals(False)
    self.main.outputNumber.blockSignals(False)

    # Se inicializa el controlador con la información actual
    self.fuzzController = self.fuzzInitController(self.InputList,
                                                  self.OutputList,
                                                  self.RuleEtiquetas)

    self.RuleList = copy.deepcopy(self.fuzzController.rulelist)

    seleccion_entrada(self)
    seleccion_salida(self)

    self.fuzzController.graficar_mf_in(self, 0)
    self.fuzzController.graficar_mf_out(self, 0)

    self.setWindowTitle(
        "Laboratorio Virtual - Nuevo controlador sin guardar*"
    )


def guardar_controlador(self):
    """ Función manejar el guardado del controlador diseñado """

    if len(self.current_file) > 0 and not '.fis' in self.current_file:
        with open(self.current_file, "w") as f:
            json.dump([self.InputList, self.OutputList, self.RuleEtiquetas], f, indent=4)
    else:
        guardarcomo_controlador(self)


def guardarcomo_controlador(self):
    """ Función manejar el guardado en un nuevo archivo del controlador diseñado """

    path_guardar = QtWidgets.QFileDialog.getSaveFileName(filter="JSON (*.json)")
    if len(path_guardar[0]) > 1:
        self.current_file = path_guardar[0]
        with open(path_guardar[0], "w") as f:
            json.dump([self.InputList, self.OutputList, self.RuleEtiquetas], f, indent=4)
            self.setWindowTitle(
                "Laboratorio Virtual - " + path_guardar[0].split("/")[-1]
            )


def exportar_fis(self):
    """ Función manejar el exportado del controlador diseñado a formato .FIS """

    path_guardar = QtWidgets.QFileDialog.getSaveFileName(filter="FIS (*.fis)")
    if len(path_guardar[0]) > 1:
        self.current_file = path_guardar[0]
        temp_parser = self.parser(self.current_file, self.InputList, self.OutputList, self.RuleEtiquetas)
        temp_parser.json_to_fis()
        self.setWindowTitle("Laboratorio Virtual - " +
                            path_guardar[0].split("/")[-1])


def cargar_controlador(self):
    """ Función manejar el cargado de controladores previamente diseñados, se aceptan formatos .JSON y .FIS """

    self.path_cargar = QtWidgets.QFileDialog.getOpenFileName(filter="JSON/FIS (*.json *.fis)")
    if len(self.path_cargar[0]) > 1:
        if '.json' in self.path_cargar[0]:
            with open(self.path_cargar[0], "r") as f:
                self.InputList, self.OutputList, self.RuleEtiquetas = json.load(f)
        else:
            temp_parser = self.parser(self.path_cargar[0])
            try:
                self.InputList, self.OutputList, self.RuleEtiquetas = temp_parser.fis_to_json()
            except TypeError:
                self.error_dialog.setInformativeText("No se permiten salidas negadas")
                self.error_dialog.exec_()
                return

        # Habilitar guardado de archivos
        self.main.guardarFuzzButton.setEnabled(True)
        self.main.guardarComoFuzzButton.setEnabled(True)
        self.main.exportarFuzzButton.setEnabled(True)
        self.main.inputNombre.setReadOnly(False)
        self.main.outputNombre.setReadOnly(False)

        self.current_file = copy.deepcopy(self.path_cargar[0])

        self.main.inputNumber.blockSignals(True)
        self.main.outputNumber.blockSignals(True)

        # Se ocultan todos los tabs y se muestran solo Entradas, Salidas y Reglas
        self.main.fuzzyTabWidget.removeTab(5)
        self.main.fuzzyTabWidget.removeTab(4)
        self.main.fuzzyTabWidget.removeTab(3)
        self.main.fuzzyTabWidget.removeTab(2)
        self.main.fuzzyTabWidget.removeTab(1)

        self.main.fuzzyTabWidget.addTab(self.EntradasTab, "Entradas")
        self.main.fuzzyTabWidget.addTab(self.SalidasTab, "Salidas")
        self.main.fuzzyTabWidget.addTab(self.ReglasTab, "Reglas")

        self.main.inputNumber.clear()
        self.main.outputNumber.clear()

        for i in range(len(self.InputList)):
            self.main.inputNumber.insertItem(i, str(i + 1))

        for i in range(len(self.OutputList)):
            self.main.outputNumber.insertItem(i, str(i + 1))

        self.main.inputNumber.blockSignals(False)
        self.main.outputNumber.blockSignals(False)

        # Se inicializa el controlador con la información actual
        self.fuzzController = self.fuzzInitController(self.InputList,
                                                      self.OutputList,
                                                      self.RuleEtiquetas)

        self.RuleList = copy.deepcopy(self.fuzzController.rulelist)

        seleccion_entrada(self)
        seleccion_salida(self)

        self.fuzzController.graficar_mf_in(self, 0)
        self.fuzzController.graficar_mf_out(self, 0)

        self.setWindowTitle(
            "Laboratorio Virtual - " + self.path_cargar[0].split("/")[-1]
        )


def seleccion_entrada(self):
    """ Función para desplegar la información de la entrada seleccionada """

    ni = self.main.inputNumber.currentIndex()
    self.main.inputNombre.setText(self.InputList[ni]["nombre"])
    self.main.inputEtiquetasNum.setText(str(self.InputList[ni]["numeroE"]))
    self.main.inputRange.setText(str(self.InputList[ni]["rango"]))
    self.main.etiquetaNumIn.clear()

    for j in range(self.InputList[ni]["numeroE"]):
        self.main.etiquetaNumIn.insertItem(j, str(j + 1))

    self.main.etiquetaNombreIn.setText(self.InputList[ni]["etiquetas"][0]["nombre"])
    self.main.etiquetaMfIn.setCurrentText(self.InputList[ni]["etiquetas"][0]["mf"])
    self.main.etiquetaDefinicionIn.setText(
        str(self.InputList[ni]["etiquetas"][0]["definicion"])
    )

    self.fuzzController.graficar_mf_in(self, ni)


def seleccion_salida(self):
    """ Función para desplegar la información de la salida seleccionada """

    no = self.main.outputNumber.currentIndex()
    self.main.outputNombre.setText(self.OutputList[no]["nombre"])
    self.main.outputEtiquetasNum.setText(str(self.OutputList[no]["numeroE"]))
    self.main.outputRange.setText(str(self.OutputList[no]["rango"]))
    self.main.defuzzMethodOut.setCurrentText(self.OutputList[no]["metodo"])
    self.main.etiquetaNumOut.clear()

    for j in range(self.OutputList[no]["numeroE"]):
        self.main.etiquetaNumOut.insertItem(j, str(j + 1))

    self.main.etiquetaNombreOut.setText(self.OutputList[no]["etiquetas"][0]["nombre"])
    self.main.etiquetaMfOut.setCurrentText(self.OutputList[no]["etiquetas"][0]["mf"])
    self.main.etiquetaDefinicionOut.setText(
        str(self.OutputList[no]["etiquetas"][0]["definicion"])
    )

    self.fuzzController.graficar_mf_out(self, no)


def nombre_entrada(self):
    """ Función para manejar el cambio de nombre de la entrada seleccionada """

    if self.main.inputNombre.text().strip() == '':
        self.error_dialog.setInformativeText(
            "El nombre no puede estar vació")
        self.error_dialog.exec_()
        self.main.inputNombre.setFocus()
        return

    ni = self.main.inputNumber.currentIndex()
    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    old_name = self.InputList[ni]["nombre"]
    flag = 0

    for i in self.InputList:
        if (
            i["nombre"] == self.main.inputNombre.text() and
            old_name != self.main.inputNombre.text()
        ):
            flag = 1

    # Chequeo en caso de nombre repetido, se concatena un "1" en caso positivo
    if not flag:
        self.InputList[ni]["nombre"] = self.main.inputNombre.text()
    else:
        self.InputList[ni]["nombre"] = self.main.inputNombre.text() + "1"
        self.main.inputNombre.setText(self.InputList[ni]["nombre"])

    self.fuzzController.cambiar_nombre_input(self, ni, self.InputList[ni]["nombre"])

    # Se actualizan la reglas con el nuevo nombre
    self.fuzzController.rulelist = []
    self.RuleList = self.fuzzController.crear_reglas(self.RuleEtiquetas)
    self.main.inputNombre.clearFocus()


def nombre_salida(self):
    """ Función para manejar el cambio de nombre de la salida seleccionada """

    if self.main.outputNombre.text().strip() == '':
        self.error_dialog.setInformativeText(
            "El nombre no puede estar vació")
        self.error_dialog.exec_()
        self.main.outputNombre.setFocus()
        return

    no = self.main.outputNumber.currentIndex()
    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    old_name = self.OutputList[no]["nombre"]
    flag = 0

    for o in self.OutputList:
        if (
            o["nombre"] == self.main.outputNombre.text() and
            old_name != self.main.outputNombre.text()
        ):
            flag = 1

    # Chequeo en caso de nombre repetido, se concatena un "1" en caso positivo
    if not flag:
        self.OutputList[no]["nombre"] = self.main.outputNombre.text()
    else:
        self.OutputList[no]["nombre"] = self.main.outputNombre.text() + "1"
        self.main.outputNombre.setText(self.OutputList[no]["nombre"])

    self.fuzzController.cambiar_nombre_output(self, no, self.OutputList[no]["nombre"])

    # Se actualizan la reglas con el nuevo nombre
    self.fuzzController.rulelist = []
    self.RuleList = self.fuzzController.crear_reglas(self.RuleEtiquetas)
    self.main.outputNombre.clearFocus()


def numero_de_etiquetas_in(self):
    """ Función para manejar el numero de etiquetas para la entrada seleccionada """

    try:
        _ = int(self.main.inputEtiquetasNum.text())
        if _ < 1:
            raise ValueError
    except ValueError:
        self.error_dialog.setInformativeText(
            "El numero de etiquetas debe ser un valor entero mayor o igual a 1")
        self.error_dialog.exec_()
        self.main.inputEtiquetasNum.setFocus()
        return

    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)

    ni = self.main.inputNumber.currentIndex()
    ne = int(self.main.inputEtiquetasNum.text())

    # En caso de que el nuevo numero de etiquetas sea menor que el actual se procede a eliminar un numero
    # de etiquetas igual a la diferencia entre el nuevo valor y el valor actual.
    if self.InputList[ni]["numeroE"] > ne:
        self.main.etiquetaNumIn.blockSignals(True)

        # Eliminación de las reglas que dependían de las etiquetas a eliminar
        for n in range(self.InputList[ni]["numeroE"] - 1, ne - 1, -1):
            new_list = []
            for i, sets in enumerate(copy.deepcopy(self.RuleEtiquetas)):
                for rule in sets[0]:
                    if (
                        rule[0] == self.InputList[ni]["etiquetas"][n]["nombre"] and
                        rule[1] == ni
                    ):
                        break
                    else:
                        new_list.append(self.RuleEtiquetas[i])
                        break

            self.RuleEtiquetas = copy.deepcopy(new_list)
            self.main.etiquetaNumIn.removeItem(n)

        # Eliminación de las etiquetas
        for _ in range(ne, self.InputList[ni]["numeroE"]):
            self.InputList[ni]["etiquetas"].pop()

        self.InputList[ni]["numeroE"] = ne
        self.RuleEtiquetas = copy.deepcopy(new_list)
        self.main.etiquetaNumIn.setCurrentIndex(ne - 1)
        self.main.etiquetaNombreIn.setText(
            self.InputList[ni]["etiquetas"][ne - 1]["nombre"]
        )
        self.main.etiquetaDefinicionIn.setText(
            str(self.InputList[ni]["etiquetas"][ne - 1]["definicion"])
        )
        self.main.etiquetaMfIn.setCurrentText(
            self.InputList[ni]["etiquetas"][ne - 1]["mf"]
        )

    # En caso de que el nuevo numero de etiquetas sea mayor que el actual se procede a agregar un numero
    # de etiquetas igual a la diferencia entre el nuevo valor y el valor actual.
    if self.InputList[ni]["numeroE"] < ne:
        self.main.etiquetaNumIn.blockSignals(True)
        rmin, rmax = self.InputList[ni]["rango"]

        # Creación de funciones de membresía trimf genéricas
        if (ne - self.InputList[ni]["numeroE"]) == 1:
            ini_range_etiquetas = [
                self.vector_rotacion[self.rotacion_windowIn] * (rmax-rmin) + rmin,
                self.vector_rotacion[self.rotacion_windowIn + 1] * (rmax-rmin) + rmin,
                self.vector_rotacion[self.rotacion_windowIn + 2] * (rmax-rmin) + rmin,
            ]

            self.rotacion_windowIn += 1
            if self.rotacion_windowIn > 4:
                self.rotacion_windowIn = 0
        else:
            step = (rmax-rmin) / ((ne - self.InputList[ni]["numeroE"]) - 1)
            ini_range_etiquetas = np.arange(rmin - step, rmax + step + 1, step).tolist()

        window = 0
        for j in range(self.InputList[ni]["numeroE"], ne):
            self.main.etiquetaNumIn.insertItem(j, str(j + 1))
            self.InputList[ni]["etiquetas"].append(
                EtiquetasDic_creator(self, j, ini_range_etiquetas[window:window + 3])
            )
            window += 1

        self.InputList[ni]["numeroE"] = ne

    # Se actualizan las etiquetas en el controlador
    self.fuzzController.cambio_etiquetas_input(self, self.InputList, ni)

    # Se actualizan la reglas con las nuevas etiquetas o la falta de ellas
    self.fuzzController.rulelist = []
    self.RuleList = self.fuzzController.crear_reglas(self.RuleEtiquetas)

    self.main.inputEtiquetasNum.clearFocus()
    self.main.etiquetaNumIn.blockSignals(False)


def numero_de_etiquetas_out(self):
    """ Función para manejar el numero de etiquetas para la salida seleccionada """

    try:
        _ = int(self.main.outputEtiquetasNum.text())
        if _ < 1:
            raise ValueError
    except ValueError:
        self.error_dialog.setInformativeText(
            "El numero de etiquetas debe ser un valor entero mayor o igual a 1")
        self.error_dialog.exec_()
        self.main.outputEtiquetasNum.setFocus()
        return

    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)

    no = self.main.outputNumber.currentIndex()
    ne = int(self.main.outputEtiquetasNum.text())

    # En caso de que el nuevo numero de etiquetas sea menor que el actual se procede a eliminar un numero
    # de etiquetas igual a la diferencia entre el nuevo valor y el valor actual.
    if self.OutputList[no]["numeroE"] > ne:
        self.main.etiquetaNumOut.blockSignals(True)

        # Eliminación de las reglas que dependían de las etiquetas a eliminar
        for n in range(self.OutputList[no]["numeroE"] - 1, ne - 1, -1):
            new_list = []
            for o, sets in enumerate(copy.deepcopy(self.RuleEtiquetas)):
                for rule in sets[1]:
                    if (
                        rule[0] == self.OutputList[no]["etiquetas"][n]["nombre"] and
                        rule[1] == no
                    ):
                        break
                    else:
                        new_list.append(self.RuleEtiquetas[o])
                        break

            self.RuleEtiquetas = copy.deepcopy(new_list)
            self.main.etiquetaNumOut.removeItem(n)

        # Eliminación de las etiquetas
        for _ in range(ne, self.OutputList[no]["numeroE"]):
            self.OutputList[no]["etiquetas"].pop()

        self.OutputList[no]["numeroE"] = ne
        self.RuleEtiquetas = copy.deepcopy(new_list)
        self.main.etiquetaNumOut.setCurrentIndex(ne - 1)
        self.main.etiquetaNombreOut.setText(
            self.OutputList[no]["etiquetas"][ne - 1]["nombre"]
        )
        self.main.etiquetaDefinicionOut.setText(
            str(self.OutputList[no]["etiquetas"][ne - 1]["definicion"])
        )
        self.main.etiquetaMfOut.setCurrentText(
            self.OutputList[no]["etiquetas"][ne - 1]["mf"]
        )

    # En caso de que el nuevo numero de etiquetas sea mayor que el actual se procede a agregar un numero
    # de etiquetas igual a la diferencia entre el nuevo valor y el valor actual.
    if self.OutputList[no]["numeroE"] < ne:
        self.main.etiquetaNumOut.blockSignals(True)
        rmin, rmax = self.OutputList[no]["rango"]

        # Creación de funciones de membresía trimf genéricas
        if (ne - self.OutputList[no]["numeroE"]) == 1:
            ini_range_etiquetas = [
                self.vector_rotacion[self.rotacion_windowOut] * (rmax-rmin) + rmin,
                self.vector_rotacion[self.rotacion_windowOut + 1] * (rmax-rmin) + rmin,
                self.vector_rotacion[self.rotacion_windowOut + 2] * (rmax-rmin) + rmin,
            ]

            self.rotacion_windowOut += 1
            if self.rotacion_windowOut > 4:
                self.rotacion_windowOut = 0
        else:
            step = (rmax-rmin) / ((ne - self.OutputList[no]["numeroE"]) - 1)
            ini_range_etiquetas = np.arange(rmin - step, rmax + step + 1, step).tolist()

        window = 0
        for j in range(self.OutputList[no]["numeroE"], ne):
            self.main.etiquetaNumOut.insertItem(j, str(j + 1))
            self.OutputList[no]["etiquetas"].append(
                EtiquetasDic_creator(self, j, ini_range_etiquetas[window:window + 3])
            )
            window += 1

        self.OutputList[no]["numeroE"] = ne

    # Se actualizan las etiquetas en el controlador
    self.fuzzController.cambio_etiquetas_output(self, self.OutputList, no)

    # Se actualizan la reglas con las nuevas etiquetas o la falta de ellas
    self.fuzzController.rulelist = []
    self.RuleList = self.fuzzController.crear_reglas(self.RuleEtiquetas)

    self.main.outputEtiquetasNum.clearFocus()
    self.main.etiquetaNumOut.blockSignals(False)


def rango_in(self):
    """ Función para manejar el rango para la entrada seleccionada """

    try:
        _ = json.loads(self.main.inputRange.text())
        if len(_) > 2 or len(_) < 2:
            raise ValueError
    except ValueError:
        self.error_dialog.setInformativeText(
            "Rango no valido, el rango debe estar entre corchetes y los valores separados por coma.\n i.g., [-10, 10]"
        )
        self.error_dialog.exec_()
        self.main.inputRange.setFocus()
        return

    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    ni = self.main.inputNumber.currentIndex()
    self.InputList[ni]["rango"] = json.loads(self.main.inputRange.text())

    # Se actualiza el rango y las etiquetas
    self.fuzzController.update_rango_input(self, self.InputList, ni)
    self.fuzzController.cambio_etiquetas_input(self, self.InputList, ni)
    self.main.inputRange.clearFocus()


def rango_out(self):
    """ Función para manejar el rango para la salida seleccionada """

    try:
        _ = json.loads(self.main.outputRange.text())
        if len(_) > 2 or len(_) < 2:
            raise ValueError
    except ValueError:
        self.error_dialog.setInformativeText(
            "Rango no valido, el rango debe estar entre corchetes y los valores separados por coma.\n i.g., [-10, 10]"
        )
        self.error_dialog.exec_()
        self.main.outputRange.setFocus()
        return

    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    no = self.main.outputNumber.currentIndex()
    self.OutputList[no]["rango"] = json.loads(self.main.outputRange.text())

    # Se actualiza el rango y las etiquetas
    self.fuzzController.update_rango_output(self, self.OutputList, no)
    self.fuzzController.cambio_etiquetas_output(self, self.OutputList, no)
    self.main.outputRange.clearFocus()


def defuzz_metodo(self):
    """ Función para manejar el metodo de defuzzificacion para la salida seleccionada """

    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    no = self.main.outputNumber.currentIndex()
    self.OutputList[no]["metodo"] = self.main.defuzzMethodOut.currentText()
    metodo = self.OutputList[no]["metodo"]

    # Se actualiza el metodo de defuzzificacion
    self.fuzzController.cambiar_metodo(self, no, metodo)


def seleccion_etiqueta_in(self):
    """ Función para desplegar la información de la etiqueta seleccionada de la entrada actual """

    ni = self.main.inputNumber.currentIndex()
    ne = self.main.etiquetaNumIn.currentIndex()

    self.main.etiquetaNombreIn.setText(self.InputList[ni]["etiquetas"][ne]["nombre"])
    self.main.etiquetaMfIn.blockSignals(True)
    self.main.etiquetaMfIn.setCurrentText(self.InputList[ni]["etiquetas"][ne]["mf"])
    self.main.etiquetaDefinicionIn.setText(
        str(self.InputList[ni]["etiquetas"][ne]["definicion"])
    )
    self.main.etiquetaMfIn.blockSignals(False)


def seleccion_etiqueta_out(self):
    """ Función para desplegar la información de la etiqueta seleccionada de la salida actual """

    no = self.main.outputNumber.currentIndex()
    ne = self.main.etiquetaNumOut.currentIndex()

    self.main.etiquetaNombreOut.setText(self.OutputList[no]["etiquetas"][ne]["nombre"])
    self.main.etiquetaMfOut.blockSignals(True)
    self.main.etiquetaMfOut.setCurrentText(self.OutputList[no]["etiquetas"][ne]["mf"])
    self.main.etiquetaDefinicionOut.setText(
        str(self.OutputList[no]["etiquetas"][ne]["definicion"])
    )
    self.main.etiquetaMfOut.blockSignals(False)

def nombre_etiqueta_in(self):
    """ Función para manejar el cambio de nombre de la etiqueta seleccionada de la entrada actual """

    if self.main.etiquetaNombreIn.text().strip() == '':
        self.error_dialog.setInformativeText(
            "El nombre no puede estar vació")
        self.error_dialog.exec_()
        self.main.etiquetaNombreIn.setFocus()
        return

    ni = self.main.inputNumber.currentIndex()
    ne = self.main.etiquetaNumIn.currentIndex()
    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    old_name = self.InputList[ni]["etiquetas"][ne]["nombre"]

    flag = 0

    for i in self.InputList[ni]["etiquetas"]:
        if (
            i["nombre"] == self.main.etiquetaNombreIn.text() and
            old_name != self.main.etiquetaNombreIn.text()
        ):
            flag = 1

    # Chequeo en caso de nombre repetido, se concatena un "1" en caso positivo
    if not flag:
        self.InputList[ni]["etiquetas"][ne]["nombre"] = self.main.etiquetaNombreIn.text()
    else:
        self.InputList[ni]["etiquetas"][ne]["nombre"] = (
            self.main.etiquetaNombreIn.text() + "1"
        )
        self.main.etiquetaNombreIn.setText(self.InputList[ni]["etiquetas"][ne]["nombre"])

    self.fuzzController.cambio_etinombre_input(self, self.InputList, ni, ne, old_name)

    # Se actualizan la reglas con el nuevo nombre de la etiqueta
    if len(self.RuleList) > 0:
        actualizar_RulesEtiquetas_in(self,
                                     ni,
                                     self.main.etiquetaNombreIn.text(),
                                     old_name)
        
    self.main.etiquetaNombreIn.clearFocus()


def actualizar_RulesEtiquetas_in(self, ni, new_name, old_name):
    """
    Función para actualizar el nombre en las reglas previamente creadas con el nuevo nombre de una etiqueta
    
    :param ni: Numero de entrada
    :type ni: int
    :param new_name: Nuevo nombre para la etiqueta a cambiar
    :type new_name: str
    :param old_name: Antiguo nombre de la etiqueta a cambiar
    :type old_name: str
    """

    for sets in self.RuleEtiquetas:
        for rule in sets[0]:
            if rule[0] == old_name and rule[1] == ni:
                rule[0] = new_name

    self.fuzzController.rulelist = []
    self.RuleList = self.fuzzController.crear_reglas(self.RuleEtiquetas)


def nombre_etiqueta_out(self):
    """ Función para manejar el cambio de nombre de la etiqueta seleccionada de la salida actual """

    if self.main.etiquetaNombreOut.text().strip() == '':
        self.error_dialog.setInformativeText(
            "El nombre no puede estar vació")
        self.error_dialog.exec_()
        self.main.etiquetaNombreOut.setFocus()
        return

    no = self.main.outputNumber.currentIndex()
    ne = self.main.etiquetaNumOut.currentIndex()
    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    old_name = self.OutputList[no]["etiquetas"][ne]["nombre"]

    flag = 0

    for i in self.OutputList[no]["etiquetas"]:
        if (
            i["nombre"] == self.main.etiquetaNombreOut.text() and
            old_name != self.main.etiquetaNombreOut.text()
        ):
            flag = 1

    # Chequeo en caso de nombre repetido, se concatena un "1" en caso positivo
    if not flag:
        self.OutputList[no]["etiquetas"][ne]["nombre"] = self.main.etiquetaNombreOut.text(
        )
    else:
        self.OutputList[no]["etiquetas"][ne]["nombre"] = (
            self.main.etiquetaNombreOut.text() + "1"
        )
        self.main.etiquetaNombreOut.setText(
            self.OutputList[no]["etiquetas"][ne]["nombre"]
        )

    self.fuzzController.cambio_etinombre_output(self, self.OutputList, no, ne, old_name)

    # Se actualizan la reglas con el nuevo nombre
    if len(self.RuleList) > 0:
        actualizar_RulesEtiquetas_out(
            self, no, self.main.etiquetaNombreOut.text(), old_name
        )
    
    self.main.etiquetaNombreOut.clearFocus()


def actualizar_RulesEtiquetas_out(self, no, new_name, old_name):
    """
    Función para actualizar el nombre en las reglas previamente creadas con el nuevo nombre de una etiqueta
    
    :param no: Numero de salida
    :type no: int
    :param new_name: Nuevo nombre para la etiqueta a cambiar
    :type new_name: str
    :param old_name: Antiguo nombre de la etiqueta a cambiar
    :type old_name: str
    """

    for sets in self.RuleEtiquetas:
        for rule in sets[1]:
            if rule[0] == old_name and rule[1] == no:
                rule[0] = new_name

    self.fuzzController.rulelist = []
    self.RuleList = self.fuzzController.crear_reglas(self.RuleEtiquetas)


def seleccion_mf_in(self):
    """ Función para manejar el cambio de función de membresía para la etiqueta seleccionada """

    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    ni = self.main.inputNumber.currentIndex()
    ne = self.main.etiquetaNumIn.currentIndex()

    # Se guarda el nombre de la función de membresía anterior
    old_mf = self.InputList[ni]["etiquetas"][ne]["mf"]

    definicion = self.InputList[ni]["etiquetas"][ne]["definicion"]
    self.InputList[ni]["etiquetas"][ne]["mf"] = self.main.etiquetaMfIn.currentText()

    # Se guarda el nombre de la función de membresía seleccionada
    new_mf = self.InputList[ni]["etiquetas"][ne]["mf"]

    # Se obtiene una definicion aproximada entre la antigua función de membresía y la seleccionada
    new_definicion, tooltip = update_definicionmf(self, old_mf, definicion, 'trimf')
    new_definicion, tooltip = update_definicionmf(self, 'trimf', new_definicion, self.main.etiquetaMfIn.currentText())
    new_definicion = round_list(new_definicion)

    self.main.etiquetaDefinicionIn.setText(str(new_definicion))
    self.main.etiquetaDefinicionIn.setToolTip(tooltip)

    # Se actualiza la nueva definicion a mostrar
    definicion_in(self)


def definicion_in(self):
    """ 
    Función para manejar el cambio de definicion de la función de membresía correspondiente a la etiqueta actual
    """

    try:
        deinificion_in_validator(self)
    except AssertionError:
        return

    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    ni = self.main.inputNumber.currentIndex()
    ne = self.main.etiquetaNumIn.currentIndex()
    self.InputList[ni]["etiquetas"][ne]["definicion"] = json.loads(
        self.main.etiquetaDefinicionIn.text())

    # Se actualiza la nueva definicion en el controlador
    self.fuzzController.update_definicion_input(self, self.InputList, ni, ne)
    self.main.etiquetaDefinicionIn.clearFocus()


def deinificion_in_validator(self):
    """ Función para validar las definiciones de las funciones de membresía """

    mf = self.main.etiquetaMfIn.currentText()
    try:
        _ = json.loads(self.main.etiquetaDefinicionIn.text())
        try:
            # Función externa para la validacion
            validacion_mf(self, _, mf)
        except AssertionError:
            self.main.etiquetaDefinicionIn.setFocus()
            raise AssertionError
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato de definicion invalido para la función de membresía: " + mf +
            "\nDebe estar entre corchetes con valores separados por comas")
        self.error_dialog.exec_()
        self.main.etiquetaDefinicionIn.setFocus()
        raise AssertionError


def seleccion_mf_out(self):
    """ Función para manejar el cambio de función de membresía para la etiqueta seleccionada """

    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    no = self.main.outputNumber.currentIndex()
    ne = self.main.etiquetaNumOut.currentIndex()
    # Se guarda el nombre de la función de membresía anterior
    old_mf = self.OutputList[no]["etiquetas"][ne]["mf"]

    definicion = self.OutputList[no]["etiquetas"][ne]["definicion"]
    self.OutputList[no]["etiquetas"][ne]["mf"] = self.main.etiquetaMfOut.currentText()

    # Se guarda el nombre de la función de membresía seleccionada
    new_mf = self.OutputList[no]["etiquetas"][ne]["mf"]

    # Se obtiene una definicion aproximada entre la antigua función de membresía y la seleccionada
    new_definicion, tooltip = update_definicionmf(self, old_mf, definicion, 'trimf')
    new_definicion, tooltip = update_definicionmf(self, 'trimf', new_definicion, self.main.etiquetaMfOut.currentText())

    new_definicion = round_list(new_definicion)
    self.main.etiquetaDefinicionOut.setText(str(new_definicion))
    self.main.etiquetaDefinicionOut.setToolTip(tooltip)

    # Se actualiza la nueva definicion a mostrar
    definicion_out(self)


def definicion_out(self):
    """ 
    Función para manejar el cambio de definicion de la función de membresía correspondiente a la etiqueta actual
    """

    try:
        deinificion_out_validator(self)
    except AssertionError:
        return

    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    no = self.main.outputNumber.currentIndex()
    ne = self.main.etiquetaNumOut.currentIndex()
    self.OutputList[no]["etiquetas"][ne]["definicion"] = json.loads(
        self.main.etiquetaDefinicionOut.text())

    # Se actualiza la nueva definicion en el controlador
    self.fuzzController.update_definicion_output(self, self.OutputList, no, ne)
    self.main.etiquetaDefinicionOut.clearFocus()


def deinificion_out_validator(self):
    """ Función para validar las definiciones de las funciones de membresía """

    mf = self.main.etiquetaMfOut.currentText()
    try:
        _ = json.loads(self.main.etiquetaDefinicionOut.text())
        try:
            # Función externa para la validacion
            validacion_mf(self, _, mf)
        except AssertionError:
            self.main.etiquetaDefinicionOut.setFocus()
            raise AssertionError
    except ValueError:
        self.error_dialog.setInformativeText(
            "Formato de definicion invalido para la función de membresía: " + mf +
            "\nDebe estar entre corchetes con valores separados por comas")
        self.error_dialog.exec_()
        self.main.etiquetaDefinicionOut.setFocus()
        raise AssertionError


def round_list(lista):
    """ Función para redondear los dígitos de una lista """
    return list(np.around(np.array(lista), 3))


def rule_list_visualizacion(self):
    """ Función para mostrar las reglas creadas para el controlador actual en un listWidget """

    if self.main.fuzzyTabWidget.currentIndex() == 3:

        self.main.rulelistWidget.blockSignals(True)

        self.main.rulelistWidget.clear()

        for regla in self.RuleList:
            self.main.rulelistWidget.addItem(str(regla))

        # Se ocultan los widgets necesarios en función del numero de entradas y salidas
        for i, o in zip(self.inframes, self.outframes):
            i.hide()
            o.hide()

        for i, o in zip(self.inlists, self.outlists):
            i.clear()
            o.clear()

        self.main.rulelistWidget.setCurrentRow(0)

        # Se muestran los widgets necesarios en función del numero de entradas
        for i, entrada in enumerate(self.InputList):
            self.inframes[i].show()
            self.inlabels[i].setText(entrada["nombre"])
            for etiqueta in entrada["etiquetas"]:
                self.inlists[i].addItem(etiqueta["nombre"])
            self.inlists[i].addItem("None")
            self.inlists[i].setCurrentRow(0)

        # Se muestran los widgets necesarios en función del numero de salidas
        for o, salida in enumerate(self.OutputList):
            self.outframes[o].show()
            self.outlabels[o].setText(salida["nombre"])
            for etiqueta in salida["etiquetas"]:
                self.outlists[o].addItem(etiqueta["nombre"])
            self.outlists[o].addItem("None")
            self.outlists[o].setCurrentRow(0)

        self.main.rulelistWidget.blockSignals(False)
        seleccionar_etiquetas(self)


def seleccionar_etiquetas(self):
    """ 
    Función para seleccionar las etiquetas correspondientes a cada entrada/salida de la regla seleccionada
    """

    if len(self.RuleEtiquetas) > 0:
        ni = len(self.InputList)
        no = len(self.OutputList)

        ruleindex = self.main.rulelistWidget.currentRow()
        Etiquetasin, Etiquetasout, logica = self.RuleEtiquetas[ruleindex]

        # Chequeo de AND o OR
        if logica:
            self.main.andradioButton.setChecked(True)
        else:
            self.main.orradioButton.setChecked(True)

        # Determinando que etiquetas corresponden a cada entrada
        for index in range(ni):
            for Etiquetasin2 in Etiquetasin:
                if Etiquetasin2[1] == index:
                    item = self.inlists[index].findItems(
                        Etiquetasin2[0], QtCore.Qt.MatchExactly
                    )
                    self.inlists[index].setCurrentItem(item[-1])
                    if Etiquetasin2[2]:
                        self.innots[index].setChecked(True)
                    else:
                        self.innots[index].setChecked(False)
                    break
            else:
                item = self.inlists[index].findItems("None", QtCore.Qt.MatchExactly)
                self.inlists[index].setCurrentItem(item[-1])
                self.innots[index].setChecked(False)

        # Determinando que etiquetas corresponden a cada salida
        for index in range(no):
            for Etiquetasout2 in Etiquetasout:
                if Etiquetasout2[1] == index:
                    item = self.outlists[index].findItems(
                        Etiquetasout2[0], QtCore.Qt.MatchExactly
                    )
                    self.outlists[index].setCurrentItem(item[-1])
                    self.outweights[index].setValue(Etiquetasout2[2])
                    break
            else:
                item = self.outlists[index].findItems("None", QtCore.Qt.MatchExactly)
                self.outlists[index].setCurrentItem(item[-1])


def rule_list_agregar(self):
    """ 
    Función para crear una nueva regla a partir de las etiquetas seleccionadas para cada entrada y salida
    """

    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    ni = len(self.InputList)
    no = len(self.OutputList)

    Etiquetasin = []
    Etiquetasout = []

    # Información de la entrada para la regla
    for i, entrada in enumerate(self.InputList):
        if self.inlists[i].currentItem().text() != "None":
            Etiquetasin.append(
                [self.inlists[i].currentItem().text(), i, self.innots[i].isChecked()]
            )

    # Información de la salida para la regla
    for o, salida in enumerate(self.OutputList):
        if self.outlists[o].currentItem().text() != "None":
            Etiquetasout.append(
                [self.outlists[o].currentItem().text(), o, self.outweights[o].value()]
            )

    # Si la regla es valida, se agrega al controlador y al listWidget
    if len(Etiquetasin) > 0 and len(Etiquetasout) > 0:
        self.RuleEtiquetas.append(
            copy.deepcopy(
                [Etiquetasin, Etiquetasout, self.main.andradioButton.isChecked()]))

        self.RuleList.append(
            self.fuzzController.agregar_regla(self,
                                              Etiquetasin,
                                              Etiquetasout,
                                              self.main.andradioButton.isChecked()))

        self.main.rulelistWidget.addItem(str(self.RuleList[-1]))
        self.main.rulelistWidget.setCurrentRow(len(self.RuleList) - 1)
    else:
        self.error_dialog.setInformativeText(
            "Regla no valida, debe contener al menos una entrada y una salida"
        )
        self.error_dialog.exec_()


def rule_list_eliminar(self):
    """ Función para eliminar una regla """

    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)

    if self.main.rulelistWidget.count():
        index_rule = self.main.rulelistWidget.currentRow()
        self.fuzzController.eliminar_regla(index_rule)
        self.main.rulelistWidget.takeItem(self.main.rulelistWidget.currentRow())
        del self.RuleList[index_rule]
        del self.RuleEtiquetas[index_rule]


def rule_list_cambiar(self):
    """ Función para modificar una regla """

    self.main.fuzzyTabWidget.removeTab(5)
    self.main.fuzzyTabWidget.removeTab(4)
    index_rule = self.main.rulelistWidget.currentRow()

    ni = len(self.InputList)
    no = len(self.OutputList)

    Etiquetasin = []
    Etiquetasout = []

    # Información de la entrada para la nueva regla
    for i, entrada in enumerate(self.InputList):
        if self.inlists[i].currentItem().text() != "None":
            Etiquetasin.append(
                [self.inlists[i].currentItem().text(), i, self.innots[i].isChecked()]
            )

    # Información de la salida para la nueva regla
    for o, salida in enumerate(self.OutputList):
        if self.outlists[o].currentItem().text() != "None":
            Etiquetasout.append(
                [self.outlists[o].currentItem().text(), o, self.outweights[o].value()]
            )

    # Si la nueva regla es valida, se elimina la anterior y se agrega al controlador y al listWidget
    if len(Etiquetasin) > 0 and len(Etiquetasout) > 0:
        del self.RuleEtiquetas[index_rule]
        self.RuleEtiquetas.insert(
            index_rule,
            copy.deepcopy(
                [Etiquetasin, Etiquetasout, self.main.andradioButton.isChecked()]
            ),
        )
        regla = self.fuzzController.cambiar_regla(self,
                                                  Etiquetasin,
                                                  Etiquetasout,
                                                  index_rule,
                                                  self.main.andradioButton.isChecked())
        
        self.main.rulelistWidget.takeItem(index_rule)
        self.main.rulelistWidget.insertItem(index_rule, str(regla))
        self.main.rulelistWidget.setCurrentRow(index_rule)
        del self.RuleList[index_rule]
        self.RuleList.insert(index_rule, regla)
    else:
        self.error_dialog.setInformativeText(
            "Regla no valida, debe contener al menos una entrada y una salida"
        )
        self.error_dialog.exec_()


def crear_controlador(self):
    """ 
    Función para crear el controlador a partir de toda la información recolectada, esta creación se realiza con el fin de realizar la prueba del controlador y observar la superficie de respuesta del controlador en caso de poseer una o dos entradas
    """

    if self.main.rulelistWidget.count():
        self.fuzzController = self.fuzzInitController(
            self.InputList, self.OutputList, self.RuleEtiquetas
        )
        self.RuleList = copy.deepcopy(self.fuzzController.rulelist)
        self.main.fuzzyTabWidget.addTab(self.PruebaTab, "Prueba")

        ni = len(self.InputList)
        no = len(self.OutputList)

        # Se ocultan los widgets necesarios en función del numero de entradas y salidas
        for it_f, ot_f, f2d, f3d in zip(
            self.intestframes,
            self.outtestframes,
            self.respuesta2dframes,
            self.respuesta3dframes,
        ):
            it_f.hide()
            ot_f.hide()
            f2d.hide()
            f3d.hide()

        # Se muestran los widgets necesarios en función del numero de entradas
        for i, salida in enumerate(self.InputList):
            self.intestframes[i].show()

        # Se muestran los widgets necesarios en función del numero de salidas
        for o, salida in enumerate(self.OutputList):
            self.outtestframes[o].show()

        # Ejecucion del código correspondiente a la prueba del controlador
        prueba_input(self)

        # Chequeo del numero de entradas
        if ni == 1:
            self.main.fuzzyTabWidget.addTab(self.RespuestaTab, "Respuesta")
            self.main.respuestastackedWidget.setCurrentIndex(0)
            for o, salida in enumerate(self.OutputList):
                self.respuesta2dframes[o].show()
            rimin, rimax = self.InputList[0]["rango"]
            self.fuzzController.graficar_respuesta_2d(self, [rimin, rimax], no)

        if ni == 2:
            self.main.fuzzyTabWidget.addTab(self.RespuestaTab, "Respuesta")
            self.main.respuestastackedWidget.setCurrentIndex(1)
            for o, salida in enumerate(self.OutputList):
                self.respuesta3dframes[o].show()
            rimin1, rimax1 = self.InputList[0]["rango"]
            rimin2, rimax2 = self.InputList[1]["rango"]
            self.fuzzController.graficar_respuesta_3d(
                self, [rimin1, rimax1], [rimin2, rimax2], no
            )


def prueba_input(self):
    """ Función para la ejecución del código correspondiente a la prueba del controlador """

    ni = len(self.InputList)
    no = len(self.OutputList)

    # Captura de los valores de entrada
    values = [i.value() for i in self.intestsliders[:ni]]

    for i, entrada in enumerate(self.InputList[:ni]):
        rmin, rmax = entrada["rango"]
        values[i] = values[i] * (rmax-rmin) / 1000 + rmin
        self.intestlabels[i].setText(entrada["nombre"] + f": {np.around(values[i], 3)}")

    self.fuzzController.prueba_de_controlador(self, values, ni, no)


def crear_vectores_de_widgets(self):
    """ Función para el almacenado de widgets en listas para acceder a ellos por indices """

    self.inframes = [
        self.main.inframe1,
        self.main.inframe2,
        self.main.inframe3,
        self.main.inframe4,
        self.main.inframe5,
        self.main.inframe6,
        self.main.inframe7,
        self.main.inframe8,
        self.main.inframe9,
        self.main.inframe10,
    ]

    self.outframes = [
        self.main.outframe1,
        self.main.outframe2,
        self.main.outframe3,
        self.main.outframe4,
        self.main.outframe5,
        self.main.outframe6,
        self.main.outframe7,
        self.main.outframe8,
        self.main.outframe9,
        self.main.outframe10,
    ]

    self.inlists = [
        self.main.inlist1,
        self.main.inlist2,
        self.main.inlist3,
        self.main.inlist4,
        self.main.inlist5,
        self.main.inlist6,
        self.main.inlist7,
        self.main.inlist8,
        self.main.inlist9,
        self.main.inlist10,
    ]

    self.outlists = [
        self.main.outlist1,
        self.main.outlist2,
        self.main.outlist3,
        self.main.outlist4,
        self.main.outlist5,
        self.main.outlist6,
        self.main.outlist7,
        self.main.outlist8,
        self.main.outlist9,
        self.main.outlist10,
    ]

    self.inlabels = [
        self.main.inlabel1,
        self.main.inlabel2,
        self.main.inlabel3,
        self.main.inlabel4,
        self.main.inlabel5,
        self.main.inlabel6,
        self.main.inlabel7,
        self.main.inlabel8,
        self.main.inlabel9,
        self.main.inlabel10,
    ]

    self.outlabels = [
        self.main.outlabel1,
        self.main.outlabel2,
        self.main.outlabel3,
        self.main.outlabel4,
        self.main.outlabel5,
        self.main.outlabel6,
        self.main.outlabel7,
        self.main.outlabel8,
        self.main.outlabel9,
        self.main.outlabel10,
    ]

    self.innots = [
        self.main.innot1,
        self.main.innot2,
        self.main.innot3,
        self.main.innot4,
        self.main.innot5,
        self.main.innot6,
        self.main.innot7,
        self.main.innot8,
        self.main.innot9,
        self.main.innot10,
    ]

    self.intestframes = [
        self.main.intestframe1,
        self.main.intestframe2,
        self.main.intestframe3,
        self.main.intestframe4,
        self.main.intestframe5,
        self.main.intestframe6,
        self.main.intestframe7,
        self.main.intestframe8,
        self.main.intestframe9,
        self.main.intestframe10,
    ]

    self.outtestframes = [
        self.main.outtestframe1,
        self.main.outtestframe2,
        self.main.outtestframe3,
        self.main.outtestframe4,
        self.main.outtestframe5,
        self.main.outtestframe6,
        self.main.outtestframe7,
        self.main.outtestframe8,
        self.main.outtestframe9,
        self.main.outtestframe10,
    ]

    self.intestsliders = [
        self.main.intestslider1,
        self.main.intestslider2,
        self.main.intestslider3,
        self.main.intestslider4,
        self.main.intestslider5,
        self.main.intestslider6,
        self.main.intestslider7,
        self.main.intestslider8,
        self.main.intestslider9,
        self.main.intestslider10,
    ]

    self.ingraphs = [
        self.main.ingraph1,
        self.main.ingraph2,
        self.main.ingraph3,
        self.main.ingraph4,
        self.main.ingraph5,
        self.main.ingraph6,
        self.main.ingraph7,
        self.main.ingraph8,
        self.main.ingraph9,
        self.main.ingraph10,
    ]

    self.outgraphs = [
        self.main.outgraph1,
        self.main.outgraph2,
        self.main.outgraph3,
        self.main.outgraph4,
        self.main.outgraph5,
        self.main.outgraph6,
        self.main.outgraph7,
        self.main.outgraph8,
        self.main.outgraph9,
        self.main.outgraph10,
    ]

    self.intestlabels = [
        self.main.intestlabel1,
        self.main.intestlabel2,
        self.main.intestlabel3,
        self.main.intestlabel4,
        self.main.intestlabel5,
        self.main.intestlabel6,
        self.main.intestlabel7,
        self.main.intestlabel8,
        self.main.intestlabel9,
        self.main.intestlabel10,
    ]

    self.outtestlabels = [
        self.main.outtestlabel1,
        self.main.outtestlabel2,
        self.main.outtestlabel3,
        self.main.outtestlabel4,
        self.main.outtestlabel5,
        self.main.outtestlabel6,
        self.main.outtestlabel7,
        self.main.outtestlabel8,
        self.main.outtestlabel9,
        self.main.outtestlabel10,
    ]

    self.respuesta3dframes = [
        self.main.respuesta3dframe1,
        self.main.respuesta3dframe2,
        self.main.respuesta3dframe3,
        self.main.respuesta3dframe4,
        self.main.respuesta3dframe5,
        self.main.respuesta3dframe6,
        self.main.respuesta3dframe7,
        self.main.respuesta3dframe8,
        self.main.respuesta3dframe9,
        self.main.respuesta3dframe10,
    ]

    self.respuesta2dframes = [
        self.main.respuesta2dframe1,
        self.main.respuesta2dframe2,
        self.main.respuesta2dframe3,
        self.main.respuesta2dframe4,
        self.main.respuesta2dframe5,
        self.main.respuesta2dframe6,
        self.main.respuesta2dframe7,
        self.main.respuesta2dframe8,
        self.main.respuesta2dframe9,
        self.main.respuesta2dframe10,
    ]

    self.respuesta3ds = [
        self.main.respuesta3d1,
        self.main.respuesta3d2,
        self.main.respuesta3d3,
        self.main.respuesta3d4,
        self.main.respuesta3d5,
        self.main.respuesta3d6,
        self.main.respuesta3d7,
        self.main.respuesta3d8,
        self.main.respuesta3d9,
        self.main.respuesta3d10,
    ]

    self.respuesta2ds = [
        self.main.respuesta2d1,
        self.main.respuesta2d2,
        self.main.respuesta2d3,
        self.main.respuesta2d4,
        self.main.respuesta2d5,
        self.main.respuesta2d6,
        self.main.respuesta2d7,
        self.main.respuesta2d8,
        self.main.respuesta2d9,
        self.main.respuesta2d10,
    ]

    self.outweights = [
        self.main.outweight1,
        self.main.outweight2,
        self.main.outweight3,
        self.main.outweight4,
        self.main.outweight5,
        self.main.outweight6,
        self.main.outweight7,
        self.main.outweight8,
        self.main.outweight9,
        self.main.outweight10,
    ]

La aplicación
-------------------------

Estructura del código
^^^^^^^^^^^^^^^^^^^^^^

El código fue realizado utilizando una combinación de programación estructurada y programación orientada a objetos. En la siguiente imagen se observa un esquema que representa la jerarquía del programa:

.. figure:: imagenes/estructuraMain.png
   :scale: 20 %
   :alt: Estructura
   :align: center

En la primera columna se encuentra el archivo main o principal, el cual se encarga de la creación de la ventana gráfica y del llamado de los archivos "handlers", los cuales se observan en la columna dos (Análisis, Entonación, Lógica difusa y Simulación), los archivos "handler" tienen la tarea de manejar la interfaz gráfica y hacer de enlace entre el usuario y las rutinas.

Los archivos de rutinas se observan en la tercera columna, su función es la de realizar los cálculos necesarios que solicite el usuario por medio de la interfaz gráfica.

Interfaz gráfica
^^^^^^^^^^^^^^^^

La interfaz gráfica fue realizada utilizando PySide2, las funciones de Laboratorio Virtual fueron separadas en pestañas. En las siguientes imágenes se señalan cada uno de los componentes que integran cada función.

Función de análisis
+++++++++++++++++++

.. figure:: imagenes/analisis.png
   :scale: 50 %
   :alt: analisis
   :align: center

.. figure:: imagenes/analisisSS.png
   :scale: 100 %
   :alt: analisisSS
   :align: center

1. Pestañas de funciones
2. Selector de representación
3. Coeficientes de la función de transferencia
4. Agregado de Delay
5. Discretización del proceso
6. Datos del análisis
7. Botón para realizar el análisis
8. Pestañas de gráficas
9. Gráfica con Matplotlib
10. Barra de herramientas de la gráfica
11. Matrices de estados

Función de entonación de controladores PID
+++++++++++++++++++++++++++++++++++++++++

.. figure:: imagenes/entonacionPID.png
   :scale: 50 %
   :alt: Estructura
   :align: center

.. figure:: imagenes/entonacionCSV.png
   :scale: 50 %
   :alt: Estructura
   :align: center

1. Función de entonación automática
2. Resolución de los sliders
3. Sliders de ganancias
4. Sliders de tiempo y coeficiente N
5. Gráfica con PyQtGraph
6. Carga del archivo CSV
7. Separador del archivo CSV
8. SPAN de la variable del proceso
9. SPAN de la entrada al proceso (EFC)
10. Slider para ajustar $t_1$
11. Gráfica de la variable del proceso
12. Gráfica de la entrada al proceso (EFC)

Función de diseño de controladores difusos
++++++++++++++++++++++++++++++++++++++++++

.. figure:: imagenes/fuzzyFront.png
   :scale: 50 %
   :alt: Estructura
   :align: center

1. Número de entradas y salidas
2. Selección de esquema de control
3. Botón para iniciar el diseño
4. Botón para cargar un diseño
5. Botones para salvar los diseños
6. Botón para exportar el diseño a FIS
7. Pestañas para el diseño
8. Información general
9. Estructura de entradas y salidas
10. Esquema de control

.. figure:: imagenes/fuzzyIO.png
   :scale: 50 %
   :alt: Estructura
   :align: center

1. Número de entrada/salida
2. Nombre de la entrada/salida
3. Número de etiquetas
4. Rango de la entrada/salida
5. Método de defuzzificacion
6. Número de etiqueta
7. Nombre de la etiqueta
8. Tipo de función de membresía
9. Definición de la función de membresía
10. Gráfica de las funciones de membresía

.. figure:: imagenes/fuzzyRules.png
   :scale: 50 %
   :alt: Estructura
   :align: center

1. Lista de reglas
2. Lógica de las premisas
3. Etiquetas de las entradas
4. Opción para negar la entrada
5. Etiquetas de las salidas
6. Peso de la salida
7. Botón para agregar una regla
8. Botón para cambiar una regla
9. Botón para eliminar una regla
10. Botón para crear el controlador y realizar pruebas

.. figure:: imagenes/fuzzyPrueba.png
   :scale: 70 %
   :alt: Estructura
   :align: center

.. figure:: imagenes/fuzzyRespuesta.png
   :scale: 70 %
   :alt: Estructura
   :align: center

1. Activación de reglas de forma gráfica para las entradas
2. Slider para asignar entrada
3. Valor de entrada
4. Activación de reglas de forma gráfica para las salidas
5. Valor de salida
6. Respuesta del controlador
7. Barra indicadora de altura (para dos entradas)

Función de simulación de sistemas de control
++++++++++++++++++++++++++++++++++++++++++++

.. figure:: imagenes/simulacionGeneral.png
   :scale: 56 %
   :alt: Estructura
   :align: center

.. figure:: imagenes/simulacionPlot.png
   :scale: 70 %
   :alt: Estructura
   :align: center

1. Pestañas de simulación
2. Esquema de control
3. Barras de configuración
4. Botón para simular
5. Gráfica de respuesta del sistema
6. Gráfica de la señal de control

.. figure:: imagenes/confGeneral.png
   :scale: 100 %
   :alt: confGeneral
   :align: center

.. figure:: imagenes/confAvz.png
   :scale: 100 %
   :alt: confAvz
   :align: center

.. figure:: imagenes/confBloq.png
   :scale: 100 %
   :alt: confBloq
   :align: center

.. figure:: imagenes/confControlador.png
   :scale: 100 %
   :alt: confControlador
   :align: center

1. Barra de configuración general
2. Selección del esquema de control
3. Tiempo de simulación
4. Valor del setpoint
5. Setpoint avanzado (variable)
6. Barra de configuración avanzada
7. Orden del atraso por PADE
8. Activación del filtro para la derivada
9. Selección del método de Runge-Kutta
10. Tolerancia relativa para el paso variable
11. Tolerancia absoluta para el paso variable
12. Máximo incremento del tamaño de paso
13. Mínimo decremento del tamaño de paso
14. Factor de seguridad para el paso variable
15. Botón para reiniciar la configuración
16. Barra de bloques adicionales
17. Activación del sensor
18. Numerador del sensor
19. Denominador del sensor
20. Activación del accionador
21. Numerador del accionador
22. Denominador del accionador
23. Activación del saturador
24. Límite inferior del saturador
25. Límite superior del saturador
26. Barra de configuración del controlador
27. Controlador difuso
28. Ganancia proporcional del PID
29. Ganancia integral del PID
30. Ganancia derivativa del PID
31. Coeficiente N
La aplicación
-------------------------

Estructura del código
^^^^^^^^^^^^^^^^^^^^^^

El código fue realizado utilizando una combinación de programación estructurada y programación orientada a objetos. En la siguiente imagen se observa un esquema que representa la jerarquía del programa:

.. figure:: imagenes/estructuraMain.png
   :scale: 20 %
   :alt: Estructura

En la primera columna se encuentra el archivo main o principal, el cual se encarga de la creación de la ventana gráfica y del llamado de los archivos "handlers", los cuales se observan en la columna dos (Análisis, Entonación, Lógica difusa y Simulación), los archivos "handler" tienen la tarea de manejar la interfaz gráfica y hacer de enlace entre el usuario y las rutinas.

Los archivos de rutinas se observan en la tercera columna, su función es la de realizar los cálculos necesarios que solicite el usuario por medio de la interfaz gráfica.

Interfaz gráfica
^^^^^^^^^^^^^^^^

La interfaz gráfica fue realizada utilizando PySide2, las funciones de Laboratorio Virtual fueron separadas en pestañas. En las siguientes imágenes se señalan cada uno de los componentes que integran cada función.

.. figure:: imagenes/analisis.png
   :scale: 50 %
   :alt: analisis

.. figure:: imagenes/analisisSS.png
   :scale: 100 %
   :alt: analisisSS

.. hlist::
   :columns: 2

   * hola
   * andate
   * pelotas

.. figure:: imagenes/entonacionPID.png
   :scale: 50 %
   :alt: Estructura

.. figure:: imagenes/entonacionCSV.png
   :scale: 50 %
   :alt: Estructura

.. figure:: imagenes/fuzzyFront.png
   :scale: 50 %
   :alt: Estructura

.. figure:: imagenes/fuzzyIO.png
   :scale: 50 %
   :alt: Estructura

.. figure:: imagenes/fuzzyRules.png
   :scale: 50 %
   :alt: Estructura

.. figure:: imagenes/fuzzyPrueba.png
   :scale: 70 %
   :alt: Estructura

.. figure:: imagenes/fuzzyRespuesta.png
   :scale: 70 %
   :alt: Estructura

.. figure:: imagenes/simulacionGeneral.png
   :scale: 56 %
   :alt: Estructura

.. figure:: imagenes/simulacionPlot.png
   :scale: 70 %
   :alt: Estructura





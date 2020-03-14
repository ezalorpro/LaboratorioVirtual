Como usar
-------------------------

Requisitos
^^^^^^^^^^^^
Como primer paso se debe descargar o clonar el repositorio de la aplicación alojado en github:

https://github.com/ezalorpro/LaboratorioVirtual

La aplicación fue programada en python y es necesario tener instalado una versión de python >= 3.7, adicionalmente, se necesitan los módulos listados a continuación::

    matplotlib>=3.1.1
    networkx==2.3
    numpy>=1.17.3
    parse==1.12.1
    PySide2==5.13.0
    scipy==1.3.1

Para instalar todos los módulos se puede utilizar el administrador de paquetes pip y el archivo requirements.txt ofrecido en el repositorio de la aplicación, el siguiente comando ejecuta la acción de instalación de los módulos::

    pip install requirements.txt

Ejecución
^^^^^^^^

La aplicación puede ser ejecutada al hacer un llamado de python sobre el archivo main.py, por lo cual se debe estar ubicado al mismo nivel que el archivo main.py::

    python main.py
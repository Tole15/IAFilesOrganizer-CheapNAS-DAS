# Manual de Uso de la Aplicación de Nomenclatura de Archivos

Este manual proporciona una guía detallada para utilizar la "Aplicación de Nomenclatura de Archivos", una herramienta desarrollada en Python utilizando la biblioteca tkinter. Esta aplicación te permite organizar y renombrar archivos de acuerdo con categorías personalizadas que definas.

## Requisitos Previos

Antes de utilizar la aplicación, asegúrate de tener instalado Python en tu sistema. Puedes descargarlo desde [el sitio web oficial de Python](https://www.python.org/downloads/).

## Instalación

No es necesario instalar nada adicional para utilizar esta aplicación. Simplemente descarga el código fuente y ejecuta el archivo Python.

## Ejecución de la Aplicación

Para ejecutar la aplicación, sigue estos pasos:

1. Abre una terminal o línea de comandos en tu sistema.
2. Navega hasta el directorio donde se encuentra el código fuente de la aplicación.
3. Ejecuta el archivo Python con el siguiente comando:

   ```
  python file_naming_app.py
   ```

   Asegúrate de reemplazar `nombre_del_archivo.py` con el nombre real del archivo de código fuente.

## Interfaz de Usuario

La aplicación presenta una interfaz de usuario simple y fácil de usar con las siguientes características:

### Paso 1: Seleccionar Directorio Base

- Haz clic en el botón "Seleccionar Directorio Base" para elegir la carpeta base donde se crearán las categorías y se organizarán los archivos.

### Paso 2: Configurar las Categorías Iniciales

- Haz clic en el botón "Añadir Categoría" para agregar nuevas categorías.
- Utiliza el botón "Borrar Categoría" para eliminar categorías existentes, opcionalmente también se pueden eliminar las carpetas correspondientes en el sistema de archivos.

### Paso 3: Seleccionar Archivos y Renombrar

- Haz clic en "Seleccionar Archivos y Renombrar" para seleccionar archivos y aplicarles un nuevo nombre basado en las categorías y subcarpetas.
- Puedes agregar un prefijo adicional opcional durante la selección y renombrado de archivos.

### Respaldar Categorías

- Utiliza el botón "Respaldar Categorías" para crear un archivo de respaldo en formato ZIP de todas las categorías y sus archivos.

### Restaurar desde Respaldo

- Con el botón "Restaurar desde Respaldo", puedes seleccionar un archivo de respaldo ZIP previamente creado y restaurar todas las categorías y sus archivos.

## Uso de la Aplicación

A continuación, se describe el proceso típico de uso de la aplicación:

1. Selecciona un "Directorio Base" donde se crearán las categorías y se organizarán los archivos.

2. Configura las "Categorías Iniciales" que se utilizarán para clasificar los archivos. Puedes agregar y eliminar categorías según sea necesario.

3. Selecciona archivos haciendo clic en "Seleccionar Archivos y Renombrar". La aplicación te pedirá que ingreses la categoría a la que pertenecen estos archivos y opcionalmente un prefijo adicional.

4. La aplicación renombrará y moverá los archivos a las carpetas correspondientes en función de la categoría seleccionada.

5. Si deseas hacer una copia de seguridad de tus categorías y archivos, puedes utilizar la función "Respaldar Categorías".

6. Si alguna vez necesitas restaurar tus categorías y archivos desde un respaldo, utiliza la función "Restaurar desde Respaldo".

## Solución de Problemas

Si encuentras algún problema al utilizar la aplicación, asegúrate de lo siguiente:

- Has seleccionado un "Directorio Base" válido antes de intentar seleccionar archivos.
- Las categorías que intentas utilizar existen en la lista de "Categorías Iniciales".
- Los nombres de archivo no contienen caracteres no permitidos o duplicados en el mismo directorio.

## Conclusión

La "Aplicación de Nomenclatura de Archivos" es una herramienta útil para organizar y renombrar archivos de manera eficiente. Con una interfaz de usuario sencilla, te permite gestionar categorías y mantener tus archivos organizados. ¡Disfruta de la organización y la gestión de tus archivos de una manera más eficiente!

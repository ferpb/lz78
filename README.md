# Compresor y descompresor LZ78


Fernando Peña Bes

*Universidad de Zaragoza, curso 2020-21*

Este programa fue desarrollado durante la asignatura Algoritmia para Problemas Difíciles en la Universidad de Zaragoza.

Es una implementación en Python sencilla del algoritmo de compresión LZ78 que permite comprimir y descomprimir cualquier tipo de fichero.

En el [informe](informe-lz78.pdf) se explica tanto el algoritmo de compresión como el de descompresión y se hace una comparativa de esta implementación con los programas `gzip` y `bzip2`.

```
Uso:
    lz78.py -{c, d} [opciones]

Opciones:
    -f fichero_entrada    Indicar el fichero de entrada
    -o fichero_salida     Indicar el fichero de salida
    -h                    Mostrar ayuda

La opción -c comprime un fichero. Si no se indica un fichero de salida, se
guarda en un nuevo fichero con el mismo nombre que el de entrada más la
extensión .lz.

La opción -d restaura un fichero comprimido a su estado inicial y lo renombra
eliminado la extensión .lz. Si el fichero de entrada no tiene la extensión
.lz, el programa termina con un error y sin realizar ningún cambio.

Si no se especifican ficheros o el nombre de los ficheros es -, la entrada
estándar se comprime o descomprime en la salida estándar.
```

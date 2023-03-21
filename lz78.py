#!/usr/bin/env python3

# Implementación básica del algoritmo de compresión LZ78
# Fernando Peña Bes
# Universidad de Zaragoza, diciembre de 2020

import sys
import getopt
import os
import math

from bitarray import bitarray

# Codifica mediante el algoritmo LZ78 todos los bytes que hay en <stream>
# y los escribe en <out>
def encode(stream, out):
    # La compresión consigue reemplazando ocurrencias repetidas
    # con referencias a un diccionario, que se construye conforme
    # se lee la entrada

    # Cada entrada del diccionario es de la forma
    #   dictionary[(index, byte)] = n
    # El valor 'n' es el índice de la entrada, 'index' es un índice a una
    # entrada previa del diccionario (index < n), y 'byte' es un byte que se
    # concatena el prefijo representado (recursivamente) por la entrada previa
    # para obtener la cadena correspondiente a la entrada actual.

    dictionary = dict()

    # El índice 0 indica el prefijo vacío
    last_matching_index = 0
    next_available_index = 1

    while True:
        # leer un byte
        byte = stream.read(1)

        # Si la entrada ha terminado, el algoritmo para
        if not byte:
            if last_matching_index != 0:
                # Si el último byte ha hecho match con una entrada
                # del diccionario, se deja el campo del byte vacío
                dictionary[(last_matching_index, None)] = next_available_index
            break

        # Para cada carácter que leemos, se busca un match en el dicionario de
        # la forma '(last matching index, byte)'
        if (last_matching_index, byte) in dictionary:
            # Si se encuentra un match, se asigna a 'last_matching_index' el índice de esa entrada
            last_matching_index = dictionary[(last_matching_index, byte)]
        else:
            # Si no, se crea una nueva entrada, se resetea 'last_matching_index'
            # e incrementa 'next_available_index'
            dictionary[(last_matching_index, byte)] = next_available_index
            last_matching_index = 0
            next_available_index += 1

    # Crear array de bits a partir del diccionario
    a = bitarray()

    # Se asume que el diccionario mantiene el orden de inserción
    for n_phrase, (i, s) in enumerate(dictionary.keys(), start=1):
        # Añadir número con el mínimo número de bits posible
        number_size = math.ceil(math.log(n_phrase, 2))
        num = bin(i)[2:].zfill(number_size)
        if n_phrase != 1:
            a.extend(num)
        # Añadir byte
        if s != None:
            a.frombytes(s)

    # Añadir padding de ceros para que la longitud del bitarray sea múltiplo de 8
    a.fill()

    # Escribir el bitarray en la salida
    a.tofile(out)


# Decodifica mediante el algoritmo LZ78 los bytes leídos de <stream>
# y los escribe en <out>
def decode(stream, out):
    # Leer entrada
    phrases = dict()
    a = bitarray()
    a.fromfile(stream)

    number_size = 1
    pointer = 0
    iteration = 1

    while pointer + number_size - 1 < len(a):
        if iteration == 1:
            i = 0
        else:
            # Leer número
            i = a[pointer:pointer + number_size].to01()
            i = int(i, 2)
            pointer += number_size

        # Intentar leer byte
        if i != 0 and pointer + 8 > len(a):
            # Caso en el que no hay byte en la última pareja
            out.write(phrases[i])
            break

        s = a[pointer:pointer+8].tobytes()
        pointer += 8

        if i != 0:
            # Buscar la frase en el diccionario
            p = phrases[i] + s
        else:
            p = s

        phrases[iteration] = p

        iteration += 1
        number_size = math.ceil(math.log(iteration, 2))

        out.write(p)


def print_help(full):
    if full:
        print("""Compresor/Descompresor Lempel-Ziv 78

    Fernando Peña Bes
    Universidad de Zaragoza, diciembre de 2020
""")

    print(
        """Uso:
    lz78 -{c, d} [opciones]

Opciones:
    -f fichero_entrada    Indicar el fichero de entrada
    -o fichero_salida     Indicar el fichero de salida
    -h                    Mostrar ayuda """)

    if full:
        print(
            """
La opción -c comprime un fichero. Si no se indica un fichero de salida, se
guarda en un nuevo fichero con el mismo nombre que el de entrada más la
extensión .lz.

La opción -d restaura un fichero comprimido a su estado inicial y lo renombra
eliminado la extensión .lz. Si el fichero de entrada no tiene la extensión
.lz, el programa termina con un error y sin realizar ningún cambio.

Si no se especifican ficheros o el nombre los ficheros es -, la entrada
estándar se comprime o descomprime en la salida estándar. """)


def main(argv):
    # Obtener argumentos

    input_file = ''
    output_file = ''

    operation = None

    try:
        opts, trail_args = getopt.getopt(
            argv, "hcdf:o:", ["help", "compress", "decompress", "file=", "out="])
    except getopt.GetoptError:
        print_help(False)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help(True)
            sys.exit(0)
        elif opt in ("-c", "--compress"):
            operation = encode
        elif opt in ("-d", "--decompress"):
            operation = decode
        elif opt in ("-f", "--file"):
            input_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg

    if not operation or trail_args:
        print_help(False)
        sys.exit(2)


    # Procesar ficheros de entrada y salida

    # Entrada
    try:
        if input_file == '' or input_file == '-':
            # Usar entrada estándar
            input_stream = os.fdopen(sys.stdin.fileno(), "rb", closefd=False)
        else:
            # Comprobar que la extensión al decodificar es .lz
            if operation == decode:
                extension = os.path.splitext(input_file)[1]
                if extension != ".lz":
                    print("El fichero de entrada no tiene extensión .lz")
                    sys.exit(1)
            input_stream = open(input_file, "rb")
    except IOError:
        print("No se ha podido abrir la entrada")
        sys.exit(1)

    # Salida
    try:
        if input_file != '' and input_file != '-' and output_file == '':
            if operation == encode:
                # Concatenar al fichero de entrada .lz
                output_stream = open(input_file + ".lz", "wb")
            elif operation == decode:
                # Eliminar la extensión .lz del fichero de entrada
                output_file = os.path.splitext(input_file)[0]
                output_stream = open(output_file, "wb")
        elif output_file != '' and output_file != '-':
            if operation == encode:
                # Si en el fichero a comprimir no se ha puesto la extensión .lz, se añade
                extension = os.path.splitext(output_file)[1]
                if extension != ".lz":
                    output_file += ".lz"
            output_stream = open(output_file, "wb")
        else:
            # Usar salida estándar
            output_stream = os.fdopen(sys.stdout.fileno(), "wb", closefd=False)
    except IOError:
        print("No se ha podido abrir la salida")
        sys.exit(1)

    # Ejecutar la operación
    try:
        operation(input_stream, output_stream)
    except Exception as e:
        if operation == encode:
            print("Ha habido un error durante la compresión")
        elif operation == decode:
            print("Ha habido un error durante la descompresión")

    input_stream.close()
    output_stream.close()

if __name__ == "__main__":
    main(sys.argv[1:])

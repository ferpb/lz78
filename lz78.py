#!/usr/local/bin/python3

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
    # La compresión se va a conseguir reemplazando ocurrencias
    # repetidas con referencias a un diccionario, construido en base a la entrada.

    # Cada entrada del diccionario es de la forma
    # dictionary[...] = {index, character}
    #   index es un índice a una entrada previa del diccionario, y characters se concatena
    #   a la candena representada por dictionary[index]

    dictionary = dict()
    compressed = []

    # El índice 0 indica el prefijo vacío
    last_matching_index = 0
    next_available_index = 1

    is_last_valid = True

    while True:
        # leer un byte
        byte = stream.read(1)

        # Si la entrada ha terminado, el algoritmo para
        if not byte:
            if last_matching_index != 0:
                # Si la porción de la entrada es igual que una de las frases que ya se han encontrado,
                # sólo interesa el <last_matching_index> a la hora de descomprimir.

                # Se marca que el último byte del fichero comprimido no será válido
                is_last_valid = False
                # Como último byte se escribe el byte nulo
                compressed.append((last_matching_index, b'\x00'))
            break

        # Para cada caracter, se busca un match en el dicionario
        # de la forma {last matching index, character}

        if (last_matching_index, byte) in dictionary:
            # Si se encuentra un match, last_matching_index se le asigna el índice de la entrada
            last_matching_index = dictionary[(last_matching_index, byte)]
        else:
            # Si no se encuentra un match, se crea una nueva entrada en el diccionario
            #   dictionary[next_available_index] = {last_matching_index, character}
            # y el algorimo imprime last_matching_index seguido por character,
            # resetea last_matching_index a 0 e incrementa next_available_index.
            dictionary[(last_matching_index, byte)] = next_available_index
            compressed.append((last_matching_index, byte))
            last_matching_index = 0
            next_available_index += 1

    # Crear array de bits
    a = bitarray()
    # El primer bit del fichero comprimido indica si el último byte es válido
    a.append(is_last_valid)

    # Escribir cada pareja (i, s) en el array de bits
    n_phrase = 1
    for (i, s) in compressed:
        number_size = math.ceil(math.log(n_phrase, 2))

        # No pasa nada por que log(1) sea cero en zfill
        num = bin(i)[2:].zfill(number_size)
        a.extend(num)
        a.frombytes(s)
        n_phrase += 1

    # Escribir el array de bits en la salida
    a.tofile(out)

    return compressed


# Decodificar mediante el algoritmo LZ78 todos los bytes que hay en <stream>
# y los escribe en <out>
def decode(stream, out):
    # Leer fichero

    phrases = dict()
    a = bitarray()
    a.fromfile(stream)

    num_frase = 1
    number_size = 1

    is_last_valid = a[0]

    pointer = 1

    iteration = 1

    while pointer + number_size + 8 < len(a):
        i = a[pointer:pointer + number_size].to01()

        i = int(i, 2)

        pointer += number_size

        s = a[pointer:pointer+8].tobytes()

        pointer += 8

        # No pasa nada por que log(1) sea cero en zfill
        # Pero aquí no se llega a invocar a log(1)
        num_frase += 1
        number_size = math.ceil(math.log(num_frase, 2))

        if i != 0:
            # buscar en el diccionario
            s2 = phrases[i]

            if pointer + 8 >= len(a) and not is_last_valid:
                # si estoy al final y no hay que escribir el último byte
                s = s2
            else:
                s = s2 + s

        phrases[iteration] = s
        out.write(s)
        iteration += 1


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
        # No se usan opciones largas
        opts, trail_args = getopt.getopt(
            argv, "hcdf:o:", ["help", "compress", "decompress", "file=", "out="])
        # opts, args = getopt.getopt(argv,"cxf:o:",[])
    except getopt.GetoptError:
        print_help(False)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help(True)
            sys.exit()
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

    # # print(opts, args)
    # print("input:", input_file)
    # print("output:", output_file)
    # print("operation:", operation)

    # Procesar ficheros de entrada y salida

    try:
        # Entrada
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

    try:
        # Salida
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
    except:
        if operation == encode:
            print("Ha habido un error durante la compresión")
        elif operation == decode:
            print("Ha habido un error durante la descompresión")


if __name__ == "__main__":
    main(sys.argv[1:])

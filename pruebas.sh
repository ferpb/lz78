#!/bin/bash

dirPruebas="pruebas"

# $1 = fichero
obtenerSize() {
    echo $(du -k $1 | cut -f1)
}

# $1 = Algoritmo
# $2 = tamaño antes de comprimir
# $3 = tamaño comprimido
imprimirCompresion() {
    echo "Compresor: $1"
    echo "    Tamaño comprimido: $3"
    # división decimal usando bc
    echo "    Factor compresión:" $(echo "scale=4; $3/$2" | bc)
}

tiempo() {
    TIMEFORMAT=%R
    echo -n "Tiempo: "
    time "$@"
}

for file in $dirPruebas/*
do
    echo "* Fichero: $file"

    sizeAntes=$(obtenerSize $file)
    echo "Tamaño sin comprimir: $sizeAntes"

    # lz78
    tiempo ./lz78.py -c -f $file
    sizeDespues=$(obtenerSize $file.lz)

    # Comprobar que el algoritmo implementado funciona bien
    if diff $file <(./lz78.py -d -f $file.lz -o -); then
        echo "LZ78 comprime bien"
    else
        echo "Error al comprimir con LZ78"
        exit
    fi

    rm $file.lz
    imprimirCompresion "LZ78" $sizeAntes $sizeDespues

    # gzip
    tiempo gzip $file
    sizeDespues=$(obtenerSize $file.gz)
    gunzip $file.gz
    imprimirCompresion "gzip" $sizeAntes $sizeDespues

    # bzip2
    tiempo bzip2 $file
    sizeDespues=$(obtenerSize $file.bz2)
    bunzip2 $file.bz2
    imprimirCompresion "bzip2" $sizeAntes $sizeDespues

    echo
done

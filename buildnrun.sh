#!/bin/bash

if [ ! -d "bin" ]; then
    mkdir bin
fi

echo "Compiling"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    gcc -shared -o bin/queens_logic.so src/queens_logic.c
else
    gcc -shared -o bin/queens_logic.so -fPIC src/queens_logic.c
fi

if [ $? -ne 0 ]; then
    echo "Error: C Compilation failed."
    exit 1
fi

cp src/*.py bin/
cp queen_asset.png bin/

cd bin
if command -v python3 &>/dev/null; then
    python3 queens_interface.py
else
    python queens_interface.py
fi
@echo off

if not exist "bin" mkdir bin

echo Compiling
gcc -shared -o bin\queens_logic.so src\queens_logic.c


copy src\*.py bin\ >nul
copy queen_asset.png bin\

cd bin
python queens_interface.py

pause
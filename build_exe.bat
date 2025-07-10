@echo off
echo Creando ejecutable para GestProdAdmin...
pyinstaller --name=GestProdAdmin --onedir --windowed --clean --noconfirm ^
--add-data="produccion.db;." ^
--add-data="produccio.db;." ^
--add-data="variablesCodProd.json;." ^
--add-data="version_info.txt;." ^
--add-data="config;config" ^
--add-data="database;database" ^
--add-data="security;security" ^
--add-data="services;services" ^
--add-data="ui;ui" ^
main.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo Ejecutable creado con exito en la carpeta 'dist\GestProdAdmin'
    echo.
    echo Para usar la aplicacion en otra PC, copie toda la carpeta 'dist\GestProdAdmin'
) else (
    echo Error al crear el ejecutable
)
pause

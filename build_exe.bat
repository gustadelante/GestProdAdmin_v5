@echo off
setlocal
call "%~dp0.venv\Scripts\activate.bat"
echo Creando ejecutable para GestProdAdmin...
python -m PyInstaller --name=GestProdAdmin --onefile --windowed --clean --noconfirm --collect-all PySide6 ^
--add-data "variablesCodProd.json;." ^
--add-data "version_info.txt;." ^
--add-data "config;config" ^
--add-data "database;database" ^
--add-data "security;security" ^
--add-data "services;services" ^
--add-data "ui;ui" ^
main.py

echo.
if %ERRORLEVEL% EQU 0 (
    if exist "%~dp0produccion.db" (
        copy /Y "%~dp0produccion.db" "%~dp0dist\GestProdAdmin\produccion.db" >nul
    )
    echo Ejecutable creado con exito en la carpeta 'dist\GestProdAdmin'
    echo.
    echo IMPORTANTE: La base de datos 'produccion.db' debe estar junto al ejecutable
    echo Para usar la aplicacion en otra PC:
    echo 1. Copie GestProdAdmin.exe a la carpeta deseada
    echo 2. Copie 'produccion.db' en la misma carpeta que el ejecutable
) else (
    echo Error al crear el ejecutable
)
pause

endlocal

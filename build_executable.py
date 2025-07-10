#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para crear el ejecutable de GestProdAdmin
"""

import os
import sys
import shutil
import subprocess

def main():
    """Función principal para crear el ejecutable"""
    print("Creando ejecutable para GestProdAdmin...")
    
    # Directorio base del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Archivos y carpetas a incluir
    data_files = [
        ('produccion.db', '.'),
        ('produccio.db', '.'),
        ('variablesCodProd.json', '.'),
        ('version_info.txt', '.'),
        ('config', 'config'),
        ('database', 'database'),
        ('security', 'security'),
        ('services', 'services'),
        ('ui', 'ui')
    ]
    
    # Construir la lista de argumentos para PyInstaller
    pyinstaller_args = [
        'pyinstaller',
        '--name=GestProdAdmin',
        '--onedir',
        '--windowed',
        '--clean',
        '--noconfirm',
        '--add-data=produccion.db;.',
        '--add-data=produccio.db;.',
        '--add-data=variablesCodProd.json;.',
        '--add-data=version_info.txt;.',
        '--add-data=config;config',
        '--add-data=database;database',
        '--add-data=security;security',
        '--add-data=services;services',
        '--add-data=ui;ui',
        'main.py'
    ]
    
    # Ejecutar PyInstaller
    try:
        subprocess.run(pyinstaller_args, check=True)
        print("\nEjecutable creado con éxito en la carpeta 'dist/GestProdAdmin'")
        print("\nPara usar la aplicación en otra PC, copie toda la carpeta 'dist/GestProdAdmin'")
    except subprocess.CalledProcessError as e:
        print(f"Error al crear el ejecutable: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

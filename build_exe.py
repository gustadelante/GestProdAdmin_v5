#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para crear el ejecutable de GestProdAdmin usando PyInstaller
Versión sin gestión de usuarios/permisos

Este script permite crear dos tipos de ejecutables:
1. Versión con base de datos externa (--external-db): La base de datos se mantiene fuera del ejecutable
   para facilitar actualizaciones. Ideal para uso diario.
2. Versión todo incluido (--all-in-one): Todo empaquetado en un solo archivo. Útil para distribución inicial.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

def create_executable(external_db=True, onefile=False):
    """Crear el ejecutable con las opciones especificadas
    
    Args:
        external_db (bool): Si es True, la base de datos se mantiene externa al ejecutable
        onefile (bool): Si es True, crea un único archivo ejecutable en lugar de un directorio
    """
    try:
        import PyInstaller.__main__
        
        # Nombre base para el ejecutable
        exe_name = "GestProdAdmin"
        if external_db:
            exe_name += "_ExternalDB"
        
        # Argumentos comunes para PyInstaller
        args = [
            'main.py',
            f'--name={exe_name}',
            '--windowed',
            '--clean',
            '--noconfirm',
            '--add-data=variablesCodProd.json;.',
            '--add-data=version_info.txt;.',
            '--add-data=config;config',
            '--add-data=database;database',
            '--add-data=security;security',
            '--add-data=services;services',
            '--add-data=ui;ui'
        ]
        
        # Configurar si es onefile o onedir
        if onefile:
            args.append('--onefile')
        else:
            args.append('--onedir')
        
        # Incluir o excluir la base de datos según la opción
        if not external_db:
            args.append('--add-data=produccion.db;.')
            if os.path.exists('produccio.db'):
                args.append('--add-data=produccio.db;.')
        
        # Ejecutar PyInstaller
        print(f"\nCreando ejecutable {exe_name} ({'onefile' if onefile else 'onedir'}) con base de datos {'externa' if external_db else 'incluida'}...")
        PyInstaller.__main__.run(args)
        
        # Si la base de datos es externa, copiarla a la carpeta dist para facilitar la distribución
        if external_db and not onefile:
            dist_dir = Path(f"dist/{exe_name}")
            if os.path.exists('produccion.db'):
                shutil.copy2('produccion.db', dist_dir / 'produccion.db')
                print(f"Base de datos copiada a {dist_dir / 'produccion.db'}")
            if os.path.exists('produccio.db'):
                shutil.copy2('produccio.db', dist_dir / 'produccio.db')
                print(f"Base de datos secundaria copiada a {dist_dir / 'produccio.db'}")
        
        print(f"\nEjecutable {exe_name} creado con éxito")
        if onefile:
            print(f"Archivo ejecutable: dist/{exe_name}.exe")
            if external_db:
                print("IMPORTANTE: Coloque el archivo produccion.db en el mismo directorio que el ejecutable")
        else:
            print(f"Carpeta del ejecutable: dist/{exe_name}/")
            print(f"Ejecutable principal: dist/{exe_name}/{exe_name}.exe")
        
        return True
    except ImportError:
        print("Error: No se pudo importar PyInstaller. Asegúrese de que está instalado.")
        print("Puede instalarlo con: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"Error al crear el ejecutable: {e}")
        return False

def main():
    """Función principal que procesa los argumentos y crea los ejecutables"""
    parser = argparse.ArgumentParser(description='Crear ejecutable para GestProdAdmin')
    parser.add_argument('--external-db', action='store_true', help='Crear versión con base de datos externa')
    parser.add_argument('--all-in-one', action='store_true', help='Crear versión con todo incluido')
    parser.add_argument('--onefile', action='store_true', help='Crear un único archivo ejecutable en lugar de un directorio')
    
    args = parser.parse_args()
    
    # Si no se especifica ninguna opción, mostrar ayuda
    if not (args.external_db or args.all_in_one):
        print("Creando ambas versiones del ejecutable por defecto...\n")
        success1 = create_executable(external_db=True, onefile=args.onefile)
        success2 = create_executable(external_db=False, onefile=args.onefile)
        return 0 if (success1 and success2) else 1
    
    # Crear las versiones solicitadas
    success = True
    if args.external_db:
        success = create_executable(external_db=True, onefile=args.onefile) and success
    if args.all_in_one:
        success = create_executable(external_db=False, onefile=args.onefile) and success
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

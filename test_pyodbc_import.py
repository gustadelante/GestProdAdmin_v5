#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script simple para verificar la disponibilidad de pyodbc
"""

import sys

print("=" * 60)
print("VERIFICACION DE PYODBC")
print("=" * 60)
print(f"\nPython executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    import pyodbc
    print(f"\n[OK] pyodbc importado exitosamente")
    print(f"Version: {pyodbc.version}")
    
    # Listar drivers disponibles
    drivers = pyodbc.drivers()
    print(f"\nDrivers ODBC disponibles ({len(drivers)}):")
    for driver in drivers:
        print(f"  - {driver}")
    
    if not drivers:
        print("\n[!] ADVERTENCIA: No hay drivers ODBC instalados")
        print("    Necesita instalar 'ODBC Driver 17 for SQL Server'")
    
except ImportError as e:
    print(f"\n[X] ERROR: No se pudo importar pyodbc")
    print(f"    {str(e)}")
    print(f"\nInstale con: pip install pyodbc")
    sys.exit(1)

print("\n" + "=" * 60)
print("[OK] pyodbc esta disponible y listo para usar")
print("=" * 60)

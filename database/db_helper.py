"""
Módulo de ayuda para la gestión de la base de datos
"""

import os
import sys
import logging

def get_db_path():
    """
    Obtiene la ruta de la base de datos, siguiendo este orden de prioridad:
    1. En el directorio del ejecutable (para la versión empaquetada)
    2. En el directorio raíz del proyecto (para desarrollo)
    
    Returns:
        str: Ruta completa al archivo de base de datos
    """
    # Nombre del archivo de base de datos
    db_filename = 'produccion.db'
    
    # Opción 1: Buscar en el directorio del ejecutable
    if getattr(sys, 'frozen', False):
        # Estamos ejecutando en modo compilado (PyInstaller)
        exe_dir = os.path.dirname(sys.executable)
        db_path = os.path.join(exe_dir, db_filename)
        if os.path.exists(db_path):
            return db_path
            
    # Opción 2: Buscar en el directorio raíz del proyecto
    # Obtenemos el directorio donde está este script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Subimos un nivel (al directorio raíz del proyecto)
    root_dir = os.path.dirname(current_dir)
    db_path = os.path.join(root_dir, db_filename)
    
    return db_path

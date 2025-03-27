#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de configuración de la aplicación

Contiene las configuraciones y ajustes de la aplicación.
"""

import os
import json
from pathlib import Path
from PySide6.QtCore import QSettings


class AppSettings:
    """Clase para gestionar las configuraciones de la aplicación"""
    
    def __init__(self):
        """Inicializa las configuraciones de la aplicación"""
        self.settings = QSettings()
        self.load_defaults()
        
        # Configuración de la base de datos
        self.db_config = {
            'user': 'root',
            'password': 'pepe01',
            'host': 'localhost',
            'port': 3306,
            'database': 'prod01'
        }
        
        # Configuración de la interfaz
        self.ui_config = {
            'theme': self.get_value('ui/theme', 'light'),
            'menu_visible': self.get_value('ui/menu_visible', True),
            'font_size': self.get_value('ui/font_size', 10)
        }
    
    def load_defaults(self):
        """Carga las configuraciones por defecto si no existen"""
        defaults = {
            'ui/theme': 'light',
            'ui/menu_visible': True,
            'ui/font_size': 10
        }
        
        for key, value in defaults.items():
            if not self.settings.contains(key):
                self.settings.setValue(key, value)
    
    def get_value(self, key, default=None):
        """Obtiene un valor de configuración"""
        value = self.settings.value(key, default)
        
        # Convertir valores de cadena a tipos apropiados
        if isinstance(default, bool):
            # Convertir a booleano si el valor predeterminado es booleano
            if isinstance(value, str):
                return value.lower() in ('true', 'yes', '1', 'on')
            return bool(value)
        elif isinstance(default, int):
            # Convertir a entero si el valor predeterminado es entero
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        
        return value
    
    def set_value(self, key, value):
        """Establece un valor de configuración"""
        self.settings.setValue(key, value)
        
        # Actualizar la configuración de la interfaz si es necesario
        if key.startswith('ui/'):
            ui_key = key.split('/')[-1]
            if ui_key in self.ui_config:
                self.ui_config[ui_key] = value
    
    def get_db_connection_string(self):
        """Retorna la cadena de conexión para SQLAlchemy"""
        return f"mariadb+pymysql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
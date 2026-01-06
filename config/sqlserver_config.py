#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de configuración de SQL Server

Contiene las configuraciones de conexión a SQL Server.
"""

from typing import Dict
from pathlib import Path
import json


class SQLServerConfig:
    """Clase para gestionar la configuración de SQL Server"""
    
    def __init__(self):
        """Inicializa la configuración de SQL Server"""
        self.config_file = Path(__file__).parent / 'sqlserver_credentials.json'
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, str]:
        """Carga la configuración desde el archivo JSON
        
        Returns:
            Diccionario con la configuración de SQL Server
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return config_data
            except Exception as e:
                import logging
                logging.error(f"Error al cargar configuración: {e}")
        
        return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, str]:
        """Retorna la configuración por defecto
        
        Returns:
            Diccionario con valores por defecto
        """
        return {
            'server': '10.12.34.70',
            'port': '1433',
            'database': 'nombre_base_datos',
            'username': 'usuario',
            'password': 'contraseña',
            'driver': 'ODBC Driver 17 for SQL Server',
            'timeout': '5'
        }
    
    def save_config(self, config: Dict[str, str]) -> bool:
        """Guarda la configuración en el archivo JSON
        
        Args:
            config: Diccionario con la configuración
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.config = config
            return True
        except Exception:
            return False
    
    def get_connection_string(self) -> str:
        """Genera la cadena de conexión para pyodbc
        
        Returns:
            Cadena de conexión
        """
        driver = self.config.get('driver', 'ODBC Driver 17 for SQL Server')
        server = self.config.get('server', '10.12.34.70')
        port = self.config.get('port', '1433')
        database = self.config.get('database', '')
        username = self.config.get('username', '')
        password = self.config.get('password', '')
        timeout = self.config.get('timeout', '5')
        
        # Si el servidor tiene una instancia nombrada (ej: server\instance), 
        # no incluir el puerto en la cadena de conexión
        if '\\' in server:
            server_part = f"SERVER={server};"
        else:
            server_part = f"SERVER={server},{port};"
        
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"{server_part}"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"Connection Timeout={timeout};"
        )
        
        return conn_str
    
    def get_server_address(self) -> str:
        """Retorna la dirección del servidor (solo IP, sin instancia)
        
        Returns:
            Dirección IP del servidor
        """
        server = self.config.get('server', '10.12.34.70')
        # Si tiene instancia nombrada (ej: 10.12.34.70\protheus), extraer solo la IP
        if '\\' in server:
            return server.split('\\')[0]
        return server
    
    def get_port(self) -> int:
        """Retorna el puerto del servidor
        
        Returns:
            Puerto del servidor
        """
        return int(self.config.get('port', '1433'))

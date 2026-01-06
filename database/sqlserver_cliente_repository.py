#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de repositorio de clientes para SQL Server

Contiene la lógica de acceso a datos para clientes en SQL Server.
"""

import logging
from typing import List, Tuple, Optional

logging.basicConfig(level=logging.DEBUG)

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    logging.warning("pyodbc no está instalado. Instale con: pip install pyodbc")


class SQLServerClienteRepository:
    """Clase para gestionar los datos de clientes desde SQL Server"""
    
    def __init__(self, connection_string: str):
        """
        Inicializa el repositorio de clientes
        
        Args:
            connection_string: Cadena de conexión ODBC para SQL Server
        """
        self.connection_string = connection_string
        self.connection: Optional[pyodbc.Connection] = None if PYODBC_AVAILABLE else None
        self.cursor: Optional[pyodbc.Cursor] = None if PYODBC_AVAILABLE else None
    
    def connect(self) -> bool:
        """
        Establece la conexión a SQL Server
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        if not PYODBC_AVAILABLE:
            logging.error("pyodbc no está instalado. Instale con: pip install pyodbc")
            return False
        
        try:
            self.connection = pyodbc.connect(self.connection_string)
            self.cursor = self.connection.cursor()
            logging.info("Conexión a SQL Server establecida exitosamente")
            return True
        except pyodbc.Error as e:
            logging.error(f"Error al conectar a SQL Server: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Error inesperado al conectar: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Cierra la conexión a SQL Server"""
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
            if self.connection:
                self.connection.close()
                self.connection = None
            logging.info("Conexión a SQL Server cerrada")
        except Exception as e:
            logging.error(f"Error al cerrar conexión: {str(e)}")
    
    def get_clientes(self, query: str) -> List[Tuple[str, str]]:
        """
        Ejecuta una consulta SQL para obtener clientes
        
        Args:
            query: Consulta SQL a ejecutar (debe retornar codigo, nombre)
            
        Returns:
            Lista de tuplas (codigo_cliente, nombre_cliente)
        """
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            clientes = []
            for row in results:
                codigo = str(row[0]).strip() if row[0] else ""
                nombre = str(row[1]).strip() if row[1] else ""
                
                # Asegurar que el código tenga 6 dígitos si es numérico
                if codigo.isdigit():
                    codigo = codigo.zfill(6)
                
                clientes.append((codigo, nombre))
            
            logging.info(f"Se obtuvieron {len(clientes)} clientes de SQL Server")
            return clientes
            
        except pyodbc.Error as e:
            logging.error(f"Error al ejecutar consulta SQL: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Error inesperado al obtener clientes: {str(e)}")
            return []
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Prueba la conexión a SQL Server
        
        Returns:
            Tupla (success, message)
        """
        try:
            if self.connect():
                self.cursor.execute("SELECT @@VERSION")
                version = self.cursor.fetchone()[0]
                self.disconnect()
                return True, f"Conexión exitosa. Versión: {version[:50]}..."
            else:
                return False, "No se pudo establecer la conexión"
        except Exception as e:
            return False, f"Error en prueba de conexión: {str(e)}"
    
    def __enter__(self):
        """Soporte para context manager"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Soporte para context manager"""
        self.disconnect()

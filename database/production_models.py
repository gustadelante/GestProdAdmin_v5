#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de modelos de producción

Contiene los modelos para la gestión de datos de producción.
"""

import sqlite3
import logging
from typing import List, Dict, Any, Optional, Tuple


class ProductionData:
    """Clase para gestionar los datos de producción desde la base de datos"""
    
    def __init__(self, db_path: str):
        """
        Inicializa el gestor de datos de producción
        
        Args:
            db_path (str): Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """
        Establece la conexión a la base de datos
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error al conectar a la base de datos: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Cierra la conexión a la base de datos"""
        if self.connection:
            self.connection.close()
    
    def get_table_names(self) -> List[str]:
        """
        Obtiene los nombres de las tablas en la base de datos
        
        Returns:
            List[str]: Lista de nombres de tablas
        """
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [table[0] for table in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error al obtener nombres de tablas: {str(e)}")
            return []
    
    def get_table_schema(self, table_name: str) -> List[Tuple]:
        """
        Obtiene el esquema de una tabla
        
        Args:
            table_name (str): Nombre de la tabla
            
        Returns:
            List[Tuple]: Lista de tuplas con información de las columnas
        """
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error al obtener esquema de tabla: {str(e)}")
            return []
    
    def get_production_data(self, table_name: str, filter_of: Optional[str] = None) -> Tuple[List[str], List[List]]:
        """
        Obtiene los datos de producción de la tabla especificada
        
        Args:
            table_name (str): Nombre de la tabla
            filter_of (Optional[str]): Filtro para la columna OF
            
        Returns:
            Tuple[List[str], List[List]]: Tupla con (nombres de columnas, filas de datos)
        """
        try:
            # Obtener nombres de columnas
            schema = self.get_table_schema(table_name)
            columns = [col[1] for col in schema]
            
            # Construir consulta SQL
            query = f"SELECT * FROM {table_name}"
            params = []
            
            # Aplicar filtro si se especifica
            if filter_of and 'OF' in columns:
                query += " WHERE OF LIKE ?"
                params.append(f"%{filter_of}%")
            
            # Ejecutar consulta
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            return columns, rows
        except sqlite3.Error as e:
            logging.error(f"Error al obtener datos de producción: {str(e)}")
            return [], []

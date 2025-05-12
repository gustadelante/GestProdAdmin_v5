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

    def insert_row(self, table_name: str, columns: list, row_data: list) -> bool:
        """
        Inserta una nueva fila en la tabla especificada.
        Args:
            table_name (str): Nombre de la tabla
            columns (list): Lista de nombres de columnas
            row_data (list): Valores a insertar
        Returns:
            bool: True si la inserción fue exitosa, False en caso contrario
        """
        try:
            placeholders = ','.join(['?'] * len(row_data))
            cols = ','.join(columns)
            query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
            self.cursor.execute(query, row_data)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error al insertar fila: {str(e)}")
            return False

    def update_row(self, table_name: str, columns: list, row_data: list, where_fields: list, where_values: list) -> bool:
        """
        Actualiza una fila existente en la tabla especificada usando múltiples claves.
        Args:
            table_name (str): Nombre de la tabla
            columns (list): Lista de nombres de columnas
            row_data (list): Nuevos valores
            where_fields (list): Lista de nombres de campos clave
            where_values (list): Lista de valores de los campos clave
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario
        """
        try:
            set_clause = ', '.join([f"{col} = ?" for col in columns])
            where_clause = ' AND '.join([f"{field} = ?" for field in where_fields])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            self.cursor.execute(query, row_data + where_values)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error al actualizar fila: {str(e)}")
            return False

    def delete_row(self, table_name: str, pk_name: str, pk_value) -> bool:
        """
        Elimina una fila de la tabla especificada.
        Args:
            table_name (str): Nombre de la tabla
            pk_name (str): Nombre de la columna clave primaria
            pk_value: Valor de la clave primaria
        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            query = f"DELETE FROM {table_name} WHERE {pk_name} = ?"
            self.cursor.execute(query, (pk_value,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error al eliminar fila: {str(e)}")
            return False

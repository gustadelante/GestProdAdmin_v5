#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de repositorio de clientes

Contiene la lógica de acceso a datos para clientes.
"""

import logging
import sqlite3
from typing import List, Tuple, Optional
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)


class ClienteRepository:
    """Clase para gestionar los datos de clientes desde la base de datos"""
    
    def __init__(self, db_path: str):
        """
        Inicializa el repositorio de clientes
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
    
    def connect(self) -> bool:
        """
        Establece la conexión a la base de datos
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
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
            self.connection = None
            self.cursor = None
    
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
                self.connect()
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            # Asegurar que los códigos sean strings de 6 dígitos
            clientes = []
            for row in results:
                codigo = str(row[0]).zfill(6) if row[0] else ""
                nombre = str(row[1]) if row[1] else ""
                clientes.append((codigo, nombre))
            
            return clientes
            
        except sqlite3.Error as e:
            logging.error(f"Error al obtener clientes: {str(e)}")
            return []
    
    def __enter__(self):
        """Soporte para context manager"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Soporte para context manager"""
        self.disconnect()

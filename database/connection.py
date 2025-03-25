#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de conexión a la base de datos

Gestiona la conexión a la base de datos y las sesiones de SQLAlchemy.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from database.models import Base

class DatabaseConnection:
    """Clase para gestionar la conexión a la base de datos"""
    
    def __init__(self, connection_string):
        """Inicializa la conexión a la base de datos
        
        Args:
            connection_string (str): Cadena de conexión para SQLAlchemy
        """
        self.connection_string = connection_string
        self.engine = None
        self.session_factory = None
        self.Session = None
    
    def connect(self):
        """Establece la conexión a la base de datos"""
        try:
            # Crear el motor de SQLAlchemy
            self.engine = create_engine(
                self.connection_string,
                pool_recycle=3600,
                echo=False  # Cambiar a True para ver las consultas SQL
            )
            
            # Crear la fábrica de sesiones
            self.session_factory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(self.session_factory)
            
            return True
        except SQLAlchemyError as e:
            logging.error(f"Error al conectar a la base de datos: {str(e)}")
            return False
    
    def create_tables(self):
        """Crea las tablas en la base de datos si no existen"""
        try:
            Base.metadata.create_all(self.engine)
            return True
        except SQLAlchemyError as e:
            logging.error(f"Error al crear las tablas: {str(e)}")
            return False
    
    def get_session(self):
        """Obtiene una sesión de la base de datos
        
        Returns:
            Session: Sesión de SQLAlchemy
        """
        if not self.Session:
            self.connect()
        return self.Session()
    
    def close_session(self, session):
        """Cierra una sesión de la base de datos
        
        Args:
            session (Session): Sesión de SQLAlchemy a cerrar
        """
        if session:
            session.close()
    
    def close_all_sessions(self):
        """Cierra todas las sesiones de la base de datos"""
        if self.Session:
            self.Session.remove()
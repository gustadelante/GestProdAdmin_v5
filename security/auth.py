#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de autenticación y seguridad

Gestiona la autenticación de usuarios, roles y permisos.
"""

import hashlib
import logging
from sqlalchemy.exc import SQLAlchemyError
from database.models import User, Role, Permission


class AuthManager:
    """Clase para gestionar la autenticación y autorización"""
    
    def __init__(self, db_connection):
        """Inicializa el gestor de autenticación
        
        Args:
            db_connection (DatabaseConnection): Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.current_user = None
    
    def hash_password(self, password):
        """Genera un hash seguro para la contraseña
        
        Args:
            password (str): Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña
        """
        # En una aplicación real, se debería usar bcrypt o similar
        # Esto es solo una implementación simple para el ejemplo
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """Autentica a un usuario con su nombre de usuario y contraseña
        
        Args:
            username (str): Nombre de usuario
            password (str): Contraseña
            
        Returns:
            bool: True si la autenticación es exitosa, False en caso contrario
        """
        session = self.db_connection.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            
            if user and user.password == self.hash_password(password) and user.is_active:
                self.current_user = user
                return True
            return False
        except SQLAlchemyError as e:
            logging.error(f"Error al autenticar usuario: {str(e)}")
            return False
        finally:
            self.db_connection.close_session(session)
    
    def logout(self):
        """Cierra la sesión del usuario actual"""
        self.current_user = None
    
    def get_current_user(self):
        """Obtiene el usuario actual
        
        Returns:
            User: Usuario actual o None si no hay sesión
        """
        return self.current_user
    
    def check_permission(self, permission_code):
        """Verifica si el usuario actual tiene un permiso específico
        
        Args:
            permission_code (str): Código del permiso a verificar
            
        Returns:
            bool: True si tiene el permiso, False en caso contrario
        """
        if not self.current_user:
            return False
        
        session = self.db_connection.get_session()
        try:
            # Obtener el rol del usuario con sus permisos
            role = session.query(Role).filter(Role.id == self.current_user.role_id).first()
            
            if not role:
                return False
            
            # Verificar si el rol tiene el permiso
            for permission in role.permissions:
                if permission.code == permission_code:
                    return True
            
            return False
        except SQLAlchemyError as e:
            logging.error(f"Error al verificar permisos: {str(e)}")
            return False
        finally:
            self.db_connection.close_session(session)
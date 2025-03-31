#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de inicialización de la base de datos

Crea usuarios, roles y permisos iniciales en la base de datos.
"""

import sys
import os
import logging

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import AppSettings
from database.connection import DatabaseConnection
from database.models import User, Role, Permission
from security.auth import AuthManager


def init_database():
    """Inicializa la base de datos con datos predeterminados"""
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Cargar configuraciones
    settings = AppSettings()
    
    # Crear conexión a la base de datos
    connection_string = settings.get_db_connection_string()
    db_connection = DatabaseConnection(connection_string)
    
    # Conectar a la base de datos
    if not db_connection.connect():
        logging.error("No se pudo conectar a la base de datos. Verifique la configuración.")
        return False
    
    # Crear las tablas si no existen
    if not db_connection.create_tables():
        logging.error("No se pudieron crear las tablas en la base de datos.")
        return False
    
    # Crear gestor de autenticación
    auth_manager = AuthManager(db_connection)
    
    # Obtener una sesión
    session = db_connection.get_session()
    
    try:
        # Crear permisos si no existen
        permissions = {
            'user_management': create_permission_if_not_exists(
                session, 'Gestión de Usuarios', 'Acceso al módulo de gestión de usuarios', 'USER_MANAGEMENT'
            ),
            'dashboard': create_permission_if_not_exists(
                session, 'Dashboard', 'Acceso al dashboard', 'DASHBOARD'
            ),
            'settings': create_permission_if_not_exists(
                session, 'Configuración', 'Acceso a la configuración', 'SETTINGS'
            ),
            # Nuevos permisos para el módulo de producción
            'production': create_permission_if_not_exists(
                session, 'Producción', 'Acceso al módulo de producción', 'PRODUCTION'
            ),
            'production_control': create_permission_if_not_exists(
                session, 'Control de Producción', 'Acceso al control de producción', 'PRODUCTION_CONTROL'
            ),
            'production_of_control': create_permission_if_not_exists(
                session, 'Control de Órdenes de Fabricación', 'Acceso al control de órdenes de fabricación', 'PRODUCTION_OF_CONTROL'
            )
        }
        
        # Crear rol de administrador si no existe
        admin_role = create_role_if_not_exists(
            session, 'admin', 'Administrador del sistema'
        )
        
        # Asignar todos los permisos al rol de administrador
        for permission in permissions.values():
            if permission not in admin_role.permissions:
                admin_role.permissions.append(permission)
        
        # Crear rol de operador si no existe
        operator_role = create_role_if_not_exists(
            session, 'operator', 'Operador del sistema'
        )
        
        # Asignar permisos al rol de operador
        operator_permissions = ['dashboard', 'production', 'production_control', 'production_of_control']
        for perm_key in operator_permissions:
            if permissions[perm_key] not in operator_role.permissions:
                operator_role.permissions.append(permissions[perm_key])
        
        session.commit()
        
        # Crear usuario administrador si no existe
        admin_user = create_user_if_not_exists(
            session, auth_manager,
            'admin', 'admin',
            'Administrador', 'admin@example.com',
            admin_role
        )
        
        # Crear usuario operador con rol de operador
        op_user = create_user_if_not_exists(
            session, auth_manager,
            'op', 'op',
            'Operador', 'op@example.com',
            operator_role
        )
        
        session.commit()
        logging.info("Base de datos inicializada correctamente.")
        return True
    
    except Exception as e:
        session.rollback()
        logging.error(f"Error al inicializar la base de datos: {str(e)}")
        return False
    
    finally:
        db_connection.close_session(session)
        db_connection.close_all_sessions()


def create_permission_if_not_exists(session, name, description, code):
    """Crea un permiso si no existe
    
    Args:
        session: Sesión de SQLAlchemy
        name (str): Nombre del permiso
        description (str): Descripción del permiso
        code (str): Código único del permiso
        
    Returns:
        Permission: Objeto de permiso creado o existente
    """
    permission = session.query(Permission).filter(Permission.code == code).first()
    
    if not permission:
        permission = Permission(name=name, description=description, code=code)
        session.add(permission)
        session.flush()
        logging.info(f"Permiso creado: {name} ({code})")
    
    return permission


def create_role_if_not_exists(session, name, description):
    """Crea un rol si no existe
    
    Args:
        session: Sesión de SQLAlchemy
        name (str): Nombre del rol
        description (str): Descripción del rol
        
    Returns:
        Role: Objeto de rol creado o existente
    """
    role = session.query(Role).filter(Role.name == name).first()
    
    if not role:
        role = Role(name=name, description=description)
        session.add(role)
        session.flush()
        logging.info(f"Rol creado: {name}")
    
    return role


def create_user_if_not_exists(session, auth_manager, username, password, full_name, email, role):
    """Crea un usuario si no existe
    
    Args:
        session: Sesión de SQLAlchemy
        auth_manager (AuthManager): Gestor de autenticación
        username (str): Nombre de usuario
        password (str): Contraseña
        full_name (str): Nombre completo
        email (str): Correo electrónico
        role (Role): Rol del usuario
        
    Returns:
        User: Objeto de usuario creado o existente
    """
    user = session.query(User).filter(User.username == username).first()
    
    if not user:
        # Crear nuevo usuario
        user = User(
            username=username,
            password=auth_manager.hash_password(password),
            full_name=full_name,
            email=email,
            is_active=True
        )
        
        # Asignar rol si se proporciona
        if role:
            user.role = role
        
        session.add(user)
        session.flush()
        logging.info(f"Usuario creado: {username}")
    else:
        # Actualizar usuario existente
        user.password = auth_manager.hash_password(password)
        user.full_name = full_name
        user.email = email
        user.is_active = True
        
        # Asignar rol si se proporciona
        if role:
            user.role = role
        elif user.role_id is not None:
            user.role_id = None
        
        session.flush()
        logging.info(f"Usuario actualizado: {username}")
    
    return user


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
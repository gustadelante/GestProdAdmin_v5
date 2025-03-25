#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de modelos de base de datos

Contiene los modelos de SQLAlchemy para la aplicación.
"""

import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Tabla de asociación entre roles y permisos (muchos a muchos)
role_permission = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)


class User(Base):
    """Modelo para la tabla de usuarios"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Almacenar hash, no contraseña en texto plano
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relación con el rol (muchos usuarios pueden tener un rol)
    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship('Role', back_populates='users')
    
    def set_password(self, password):
        """Establece la contraseña del usuario aplicando un hash
        
        Args:
            password (str): Contraseña en texto plano
        """
        import hashlib
        self.password = hashlib.sha256(password.encode()).hexdigest()
    
    def __repr__(self):
        return f"<User(username='{self.username}', full_name='{self.full_name}')>"


class Role(Base):
    """Modelo para la tabla de roles"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
    # Relación con usuarios (un rol puede tener muchos usuarios)
    users = relationship('User', back_populates='role')
    
    # Relación con permisos (muchos a muchos)
    permissions = relationship('Permission', secondary=role_permission, back_populates='roles')
    
    def __repr__(self):
        return f"<Role(name='{self.name}')>"


class Permission(Base):
    """Modelo para la tabla de permisos"""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    code = Column(String(50), unique=True, nullable=False)  # Código único para identificar el permiso en el código
    
    # Relación con roles (muchos a muchos)
    roles = relationship('Role', secondary=role_permission, back_populates='permissions')
    
    def __repr__(self):
        return f"<Permission(name='{self.name}', code='{self.code}')>"
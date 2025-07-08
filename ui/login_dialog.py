#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo del diálogo de inicio de sesión

Contiene la implementación del diálogo de inicio de sesión.
"""

import os
import sys
import logging
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)
from PySide6.QtGui import QIcon

# Añadir el directorio raíz al path para importar los módulos
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from database.connection import DatabaseConnection
from database.production_models import ProductionData
from security.auth import AuthManager


class LoginDialog(QDialog):
    """Diálogo de inicio de sesión"""
    
    def __init__(self, parent=None):
        """Inicializa el diálogo de inicio de sesión
        
        Args:
            parent (QWidget, optional): Widget padre
        """
        super().__init__(parent)
        
        # Configurar el diálogo
        self.setWindowTitle("Iniciar Sesión")
        self.setMinimumWidth(400)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setModal(True)
        
        # Centrar la ventana en la pantalla
        screen_geometry = self.screen().availableGeometry()
        size = self.sizeHint()
        x = (screen_geometry.width() - size.width()) // 2
        y = (screen_geometry.height() - size.height()) // 2
        self.move(x, y)
        
        # Obtener la configuración del padre si existe
        self.settings = parent.settings if parent else None
        
        # Inicializar la conexión a la base de datos y el gestor de autenticación
        self.init_database()
        
        # Inicializar la interfaz
        self.init_ui()
    
    def init_database(self):
        """Inicializa la conexión a la base de datos y el gestor de autenticación"""
        if self.settings:
            # Crear la conexión a la base de datos
            connection_string = self.settings.get_db_connection_string()
            self.db_connection = DatabaseConnection(connection_string)
            
            # Conectar a la base de datos
            if not self.db_connection.connect():
                QMessageBox.critical(
                    self,
                    "Error de Conexión",
                    "No se pudo conectar a la base de datos. Verifique la configuración."
                )
                return
            
            # Crear las tablas si no existen
            self.db_connection.create_tables()
            
            # Crear el gestor de autenticación
            self.auth_manager = AuthManager(self.db_connection)
    
    def init_ui(self):
        """Inicializa los componentes de la interfaz"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("GestProdAdmin")
        title_label.setObjectName("loginTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #3498db;")
        main_layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Iniciar Sesión")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 14pt; margin-bottom: 20px;")
        main_layout.addWidget(subtitle_label)
        
        # Formulario
        form_frame = QFrame()
        form_frame.setObjectName("loginForm")
        form_frame.setStyleSheet(
            "#loginForm { background-color: white; border-radius: 8px; padding: 20px; }"
            "QLabel { font-size: 11pt; }"
            "QLineEdit { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }"
        )
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(10)
        
        # Campo de usuario
        username_label = QLabel("Usuario:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingrese su nombre de usuario")
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        
        # Campo de contraseña
        password_label = QLabel("Contraseña:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        buttons_layout.setSpacing(10)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setObjectName("btnCancel")
        self.cancel_button.setStyleSheet(
            "#btnCancel { background-color: #e74c3c; color: white; padding: 8px 16px; "
            "border: none; border-radius: 4px; font-weight: bold; }"
            "#btnCancel:hover { background-color: #c0392b; }"
        )
        self.cancel_button.clicked.connect(self.reject)
        
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setObjectName("btnLogin")
        self.login_button.setStyleSheet(
            "#btnLogin { background-color: #3498db; color: white; padding: 8px 16px; "
            "border: none; border-radius: 4px; font-weight: bold; }"
            "#btnLogin:hover { background-color: #2980b9; }"
        )
        self.login_button.clicked.connect(self.login)
        
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.login_button)
        
        form_layout.addLayout(buttons_layout)
        main_layout.addWidget(form_frame)
        
        # Establecer el foco en el campo de usuario
        self.username_input.setFocus()
    
    def login(self):
        """Intenta iniciar sesión con las credenciales proporcionadas"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validar campos
        if not username or not password:
            QMessageBox.warning(
                self,
                "Campos Incompletos",
                "Por favor, complete todos los campos."
            )
            return
        
        # Intentar autenticar
        if self.auth_manager and self.auth_manager.authenticate(username, password):
            # Pasar el gestor de autenticación al padre si existe
            if self.parent():
                self.parent().set_auth_manager(self.auth_manager)
            
            # Actualizar campos vacíos según las reglas
            try:
                # Obtener la ruta de la base de datos de producción
                db_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                from database.db_helper import get_db_path
                db_path = get_db_path()
                
                logging.info(f"Intentando acceder a la base de datos en: {db_path}")
                
                # Verificar si el archivo existe
                if not os.path.exists(db_path):
                    logging.error(f"El archivo de base de datos no existe en: {db_path}")
                    # Intentar con mayúsculas (para Windows)
                    # No necesitamos buscar con mayúsculas ahora, el helper se encarga de la búsqueda
                    pass
                    if not os.path.exists(db_path):
                        logging.error(f"El archivo de base de datos tampoco existe en: {db_path}")
                        raise FileNotFoundError(f"No se encontró el archivo de base de datos en {db_path}")
                
                # Crear instancia de ProductionData
                self.production_data = ProductionData(db_path)
                
                # Conectar y actualizar campos vacíos
                if self.production_data.connect():
                    try:
                        # Actualizar campos vacíos
                        self.production_data.update_empty_bobinas_fields()
                        
                        # Si estamos en el widget de producción, forzar recarga de datos
                        if hasattr(self.parent(), 'production_widget'):
                            production_widget = self.parent().production_widget
                            if hasattr(production_widget, 'table_selector') and hasattr(production_widget, 'table_model'):
                                current_table = production_widget.table_selector.currentText()
                                if current_table:
                                    production_widget.table_model.load_data(current_table)
                    except Exception as e:
                        logging.error(f"Error al actualizar campos vacíos: {str(e)}", exc_info=True)
                    finally:
                        self.production_data.disconnect()
                else:
                    logging.error("No se pudo conectar a la base de datos")
            except Exception as e:
                logging.error(f"Error al actualizar campos vacíos después del inicio de sesión: {str(e)}", exc_info=True)
            
            # Cerrar el diálogo con éxito
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Error de Autenticación",
                "Usuario o contraseña incorrectos."
            )
    
    def keyPressEvent(self, event):
        """Maneja los eventos de teclado
        
        Args:
            event (QKeyEvent): Evento de teclado
        """
        # Si se presiona Enter, intentar iniciar sesión
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.login()
        else:
            # Pasar el evento al padre para manejo estándar
            super().keyPressEvent(event)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo del dashboard

Contiene la implementación del widget de dashboard principal.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPalette


class DashboardWidget(QWidget):
    """Widget del dashboard principal"""
    
    def __init__(self, parent=None):
        """Inicializa el widget del dashboard
        
        Args:
            parent (QWidget, optional): Widget padre
        """
        super().__init__(parent)
        
        # Inicializar la interfaz
        self.init_ui()
    
    def init_ui(self):
        """Inicializa los componentes de la interfaz"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título de bienvenida
        welcome_label = QLabel("Bienvenido al Sistema de Gestión de Producción")
        welcome_label.setObjectName("welcomeLabel")
        welcome_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(welcome_label)
        
        # Descripción
        description_label = QLabel(
            "Este sistema le permite gestionar la producción de la fábrica, "
            "administrar usuarios y configurar el sistema."
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 11pt; margin-bottom: 20px;")
        main_layout.addWidget(description_label)
        
        # Grid de tarjetas de información
        cards_grid = QGridLayout()
        cards_grid.setSpacing(15)
        
        # Tarjeta de usuarios
        users_card = self.create_info_card(
            "Usuarios",
            "Gestione los usuarios del sistema, asigne roles y permisos.",
            "#3498db"
        )
        cards_grid.addWidget(users_card, 0, 0)
        
        # Tarjeta de producción
        production_card = self.create_info_card(
            "Producción",
            "Supervise y gestione la producción de la fábrica.",
            "#2ecc71"
        )
        cards_grid.addWidget(production_card, 0, 1)
        
        # Tarjeta de informes
        reports_card = self.create_info_card(
            "Informes",
            "Genere informes y estadísticas de producción.",
            "#e74c3c"
        )
        cards_grid.addWidget(reports_card, 1, 0)
        
        # Tarjeta de configuración
        settings_card = self.create_info_card(
            "Configuración",
            "Configure los parámetros del sistema.",
            "#f39c12"
        )
        cards_grid.addWidget(settings_card, 1, 1)
        
        main_layout.addLayout(cards_grid)
        
        # Espaciador para empujar todo hacia arriba
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    
    def create_info_card(self, title, description, color):
        """Crea una tarjeta de información para el dashboard
        
        Args:
            title (str): Título de la tarjeta
            description (str): Descripción de la tarjeta
            color (str): Color de la tarjeta en formato hexadecimal
            
        Returns:
            QFrame: Frame configurado como tarjeta
        """
        card = QFrame()
        card.setObjectName("infoCard")
        # Usar concatenación de strings en lugar de f-strings para evitar problemas con las llaves
        card.setStyleSheet(
            "#infoCard {" +
            "\n    background-color: " + color + ";" +
            "\n    border-radius: 8px;" +
            "\n    padding: 15px;" +
            "\n}"
        )
        card.setMinimumHeight(150)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Layout de la tarjeta
        card_layout = QVBoxLayout(card)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: white;")
        card_layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 10pt; color: white;")
        card_layout.addWidget(desc_label)
        
        # Espaciador para empujar todo hacia arriba
        card_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        return card
    
    def set_auth_manager(self, auth_manager):
        """Establece el gestor de autenticación
        
        Args:
            auth_manager (AuthManager): Gestor de autenticación
        """
        self.auth_manager = auth_manager
        
        # Actualizar la interfaz con información del usuario si es necesario
        if auth_manager and auth_manager.get_current_user():
            user = auth_manager.get_current_user()
            # Aquí se podría personalizar el dashboard según el usuario
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de la ventana principal

Contiene la implementación de la ventana principal de la aplicación.
"""

import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame,
    QSizePolicy, QSpacerItem, QMessageBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, Signal, Slot, QTimer
from PySide6.QtGui import QIcon, QFont, QColor, QPalette

from ui.login_dialog import LoginDialog
from ui.dashboard import DashboardWidget
from ui.user_management import UserManagementWidget
from ui.production import ProductionControlWidget
from ui.production_of_detail import ProductionOFDetailWidget
from ui.styles import get_stylesheet, LIGHT_PALETTE, DARK_PALETTE


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self, settings):
        """Inicializa la ventana principal
        
        Args:
            settings (AppSettings): Configuración de la aplicación
        """
        super().__init__()
        self.settings = settings
        
        # Configurar la ventana
        self.setWindowTitle("ProdAdmin")
        self.setMinimumSize(1024, 768)
        
        # Aplicar tema
        self.apply_theme()
        
        # Inicializar la interfaz
        self.init_ui()
        
        # Asegurar que el menú siempre esté visible al iniciar
        self.settings.set_value('ui/menu_visible', True)
        
        # Conectar a la base de datos sin autenticación
        from database.connection import DatabaseConnection
        connection_string = self.settings.get_db_connection_string()
        self.db_connection = DatabaseConnection(connection_string)
        if self.db_connection.connect():
            # Mostrar la aplicación directamente sin autenticación
            self.showMaximized()
            # Acceso directo a Control de Producción
            self.change_page(1, "Control de Producción")
        else:
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos.")
    
    def init_ui(self):
        """Inicializa los componentes de la interfaz"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Contenedor del panel lateral
        self.side_container = QFrame()
        self.side_container.setObjectName("sideContainer")
        self.side_container.setMinimumWidth(50)
        self.side_container.setMaximumWidth(250)
        
        # Layout del contenedor lateral
        side_container_layout = QVBoxLayout(self.side_container)
        side_container_layout.setContentsMargins(0, 0, 0, 0)
        side_container_layout.setSpacing(0)
        
        # Panel lateral (menú)
        self.side_menu = QFrame()
        self.side_menu.setObjectName("sideMenu")
        self.side_menu.setMinimumWidth(250)
        
        # Layout del menú lateral
        side_menu_layout = QVBoxLayout(self.side_menu)
        side_menu_layout.setContentsMargins(0, 0, 0, 0)
        side_menu_layout.setSpacing(0)
        
        # Título del menú
        menu_title = QLabel("ProdAdmin")
        menu_title.setObjectName("menuTitle")
        menu_title.setAlignment(Qt.AlignCenter)
        menu_title.setMinimumHeight(60)
        side_menu_layout.addWidget(menu_title)
        
        # Botones del menú
        self.btn_dashboard = self.create_menu_button("Dashboard", "dashboard")
        self.btn_production_control = self.create_menu_button("Control de Producción", "production_control")
        self.btn_production_of = self.create_menu_button("Control de OF", "production_of")
        self.btn_settings = self.create_menu_button("Configuración", "settings")
        
        side_menu_layout.addWidget(self.btn_dashboard)
        side_menu_layout.addWidget(self.btn_production_control)
        side_menu_layout.addWidget(self.btn_production_of)
        side_menu_layout.addWidget(self.btn_settings)
        
        # Espaciador para empujar los botones hacia arriba
        side_menu_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Botón para cambiar tema
        self.btn_toggle_theme = QPushButton("Cambiar Tema")
        self.btn_toggle_theme.setObjectName("btnToggleTheme")
        self.btn_toggle_theme.clicked.connect(self.toggle_theme)
        side_menu_layout.addWidget(self.btn_toggle_theme)
        
        # Agregar el menú al contenedor lateral
        side_container_layout.addWidget(self.side_menu)
        
        # Panel de control (siempre visible)
        self.control_panel = QFrame()
        self.control_panel.setObjectName("controlPanel")
        self.control_panel.setMinimumHeight(100)
        self.control_panel.setMaximumHeight(100)
        
        # Layout del panel de control
        control_layout = QVBoxLayout(self.control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(5)
        
        # Botón para ocultar/mostrar menú
        self.btn_toggle_menu = QPushButton("<<")
        self.btn_toggle_menu.setObjectName("btnToggleMenu")
        self.btn_toggle_menu.clicked.connect(self.toggle_menu)
        control_layout.addWidget(self.btn_toggle_menu)
        
        # Agregar el panel de control al contenedor lateral
        side_container_layout.addWidget(self.control_panel)
        
        # Contenedor principal
        self.content_container = QFrame()
        self.content_container.setObjectName("contentContainer")
        
        # Layout del contenedor principal
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Barra superior
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setMinimumHeight(50)
        top_bar.setMaximumHeight(50)
        
        # Layout de la barra superior
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(10, 0, 10, 0)
        
        # Título de la página
        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("pageTitle")
        top_bar_layout.addWidget(self.page_title)
        
        # Espaciador para empujar el botón de cerrar sesión hacia la derecha
        top_bar_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        content_layout.addWidget(top_bar)
        
        # Contenido de la página
        self.pages = QStackedWidget()
        self.pages.setObjectName("pages")
        
        # Páginas
        self.dashboard_page = DashboardWidget()
        self.production_control_page = ProductionControlWidget()
        self.production_of_control_page = ProductionOFDetailWidget()
        self.settings_page = QWidget()  # Página de configuración (por implementar)
        
        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.production_control_page)
        self.pages.addWidget(self.production_of_control_page)
        self.pages.addWidget(self.settings_page)
        
        content_layout.addWidget(self.pages)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(self.side_container)
        main_layout.addWidget(self.content_container)
        
        # Conectar señales de los botones del menú
        self.btn_dashboard.clicked.connect(lambda: self.change_page(0, "Dashboard"))
        self.btn_production_control.clicked.connect(lambda: self.change_page(1, "Control de Producción"))
        self.btn_production_of.clicked.connect(lambda: self.change_page(2, "Control de Órdenes de Fabricación"))
        self.btn_settings.clicked.connect(lambda: self.change_page(3, "Configuración"))
    
    def create_menu_button(self, text, object_name):
        """Crea un botón para el menú lateral
        
        Args:
            text (str): Texto del botón
            object_name (str): Nombre del objeto para CSS
            
        Returns:
            QPushButton: Botón configurado
        """
        button = QPushButton(text)
        button.setObjectName(f"btn{object_name.capitalize()}")
        button.setMinimumHeight(50)
        button.setCheckable(True)
        return button
    
    def change_page(self, index, title):
        """Cambia la página actual
        
        Args:
            index (int): Índice de la página
            title (str): Título de la página
        """
        # Desmarcar todos los botones
        for btn in [self.btn_dashboard, self.btn_production_control, self.btn_production_of, self.btn_settings]:
            btn.setChecked(False)
        
        # Marcar el botón actual
        sender = self.sender()
        if sender:
            sender.setChecked(True)
        elif index == 0:
            self.btn_dashboard.setChecked(True)
        elif index == 1:
            self.btn_production_control.setChecked(True)
        elif index == 2:
            self.btn_production_of.setChecked(True)
        elif index == 3:
            self.btn_settings.setChecked(True)
        
        # Cargar datos si es la página de Control de Órdenes de Fabricación
        if index == 2 and hasattr(self.production_of_control_page, 'load_of_list'):
            self.production_of_control_page.load_of_list()
        
        # Cambiar la página y el título
        self.pages.setCurrentIndex(index)
        self.page_title.setText(title)
    
    def toggle_menu(self):
        """Oculta o muestra el menú lateral con animación"""
        width = self.side_menu.width()
        
        # Si el menú está expandido, contraerlo
        # Si está contraído, expandirlo a 250px
        if width > 50:
            target_width = 0
        else:
            target_width = 250
        
        # Crear animación para el menú
        self.animation = QPropertyAnimation(self.side_menu, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(width)
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        
        # También actualizar el maximumWidth para que coincida
        self.side_menu.setMaximumWidth(target_width)
        
        # Iniciar animación
        self.animation.start()
        
        # Cambiar el texto del botón
        if target_width <= 50:
            self.btn_toggle_menu.setText(">>")  
            self.settings.set_value('ui/menu_visible', False)
        else:
            self.btn_toggle_menu.setText("<<")
            self.settings.set_value('ui/menu_visible', True)
    
    def apply_theme(self):
        """Aplica el tema actual (claro u oscuro)"""
        theme = self.settings.ui_config['theme']
        
        # Aplicar paleta de colores
        if theme == 'dark':
            self.setPalette(DARK_PALETTE)
        else:
            self.setPalette(LIGHT_PALETTE)
        
        # Aplicar hoja de estilos
        self.setStyleSheet(get_stylesheet(theme))
    
    def toggle_theme(self):
        """Cambia entre tema claro y oscuro"""
        current_theme = self.settings.ui_config['theme']
        new_theme = 'dark' if current_theme == 'light' else 'light'
        
        # Actualizar configuración
        self.settings.set_value('ui/theme', new_theme)
        
        # Aplicar nuevo tema
        self.apply_theme()
    
    def show_login_dialog(self):
        """Método mantenido por compatibilidad pero sin funcionalidad"""
        # Mostrar la ventana principal directamente sin autenticación
        self.show()
    
    def set_auth_manager(self, auth_manager):
        """Método mantenido por compatibilidad pero sin funcionalidad"""
        pass
    
    def logout(self):
        """Método mantenido por compatibilidad pero sin funcionalidad"""
        pass
    
    def update_menu_visibility(self):
        """Actualiza la visibilidad de los menús (todos visibles sin restricciones)"""
        # Hacer visibles todos los botones sin verificar permisos
        if hasattr(self, 'btn_production_control'):
            self.btn_production_control.setVisible(True)
            
        if hasattr(self, 'btn_production_of'):
            self.btn_production_of.setVisible(True)
        
        if hasattr(self, 'btn_settings'):
            self.btn_settings.setVisible(True)
    
    # El método show_production_submenu ha sido eliminado ya que ahora tenemos botones directos
    # para Control de Producción y Control de Órdenes de Fabricación
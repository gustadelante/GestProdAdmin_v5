#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de estilos de la interfaz

Contiene las definiciones de estilos, paletas de colores y temas para la aplicación.
"""

from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

# Paleta de colores para tema claro
LIGHT_PALETTE = QPalette()
LIGHT_PALETTE.setColor(QPalette.Window, QColor(240, 245, 255))
LIGHT_PALETTE.setColor(QPalette.WindowText, QColor(30, 30, 30))
LIGHT_PALETTE.setColor(QPalette.Base, QColor(255, 255, 255))
LIGHT_PALETTE.setColor(QPalette.AlternateBase, QColor(230, 235, 245))
LIGHT_PALETTE.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
LIGHT_PALETTE.setColor(QPalette.ToolTipText, QColor(30, 30, 30))
LIGHT_PALETTE.setColor(QPalette.Text, QColor(30, 30, 30))
LIGHT_PALETTE.setColor(QPalette.Button, QColor(240, 245, 255))
LIGHT_PALETTE.setColor(QPalette.ButtonText, QColor(30, 30, 30))
LIGHT_PALETTE.setColor(QPalette.Link, QColor(42, 130, 218))
LIGHT_PALETTE.setColor(QPalette.Highlight, QColor(42, 130, 218))
LIGHT_PALETTE.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

# Paleta de colores para tema oscuro
DARK_PALETTE = QPalette()
DARK_PALETTE.setColor(QPalette.Window, QColor(45, 45, 60))
DARK_PALETTE.setColor(QPalette.WindowText, QColor(220, 220, 220))
DARK_PALETTE.setColor(QPalette.Base, QColor(30, 30, 45))
DARK_PALETTE.setColor(QPalette.AlternateBase, QColor(55, 55, 70))
DARK_PALETTE.setColor(QPalette.ToolTipBase, QColor(30, 30, 45))
DARK_PALETTE.setColor(QPalette.ToolTipText, QColor(220, 220, 220))
DARK_PALETTE.setColor(QPalette.Text, QColor(220, 220, 220))
DARK_PALETTE.setColor(QPalette.Button, QColor(45, 45, 60))
DARK_PALETTE.setColor(QPalette.ButtonText, QColor(220, 220, 220))
DARK_PALETTE.setColor(QPalette.Link, QColor(42, 130, 218))
DARK_PALETTE.setColor(QPalette.Highlight, QColor(42, 130, 218))
DARK_PALETTE.setColor(QPalette.HighlightedText, QColor(220, 220, 220))


def get_stylesheet(theme='light'):
    """Obtiene la hoja de estilos para el tema especificado
    
    Args:
        theme (str): Tema a aplicar ('light' o 'dark')
        
    Returns:
        str: Hoja de estilos CSS
    """
    # Colores base según el tema
    if theme == 'dark':
        primary_color = "#3498db"  # Azul
        secondary_color = "#2c3e50"  # Azul oscuro
        bg_color = "#2d2d3c"  # Fondo oscuro
        text_color = "#dcdcdc"  # Texto claro
        border_color = "#555555"  # Bordes
        hover_color = "#3e8ed0"  # Hover
    else:  # light
        primary_color = "#3498db"  # Azul
        secondary_color = "#2980b9"  # Azul más oscuro
        bg_color = "#f0f5ff"  # Fondo claro
        text_color = "#1a1a1a"  # Texto oscuro (más oscuro para mejor contraste)
        border_color = "#dddddd"  # Bordes
        hover_color = "#2980b9"  # Hover
    
    # Estilos comunes para ambos temas
    stylesheet = f'''
    /* Estilos específicos para títulos y descripciones */
    #welcomeLabel, #controlTitle, #ofControlTitle {{
        color: #0a0a0a;
        font-weight: bold;
    }}
    
    /* Estilos generales */
    QWidget {{
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 10pt;
    }}
    
    /* Menú lateral */
    #sideMenu {{
        background-color: {secondary_color};
        border: none;
    }}
    
    #menuTitle {{
        color: white;
        font-size: 18pt;
        font-weight: bold;
        padding: 10px;
    }}
    
    /* Botones del menú */
    #btnDashboard, #btnUsers, #btnProduction, #btnSettings {{
        background-color: transparent;
        border: none;
        color: white;
        text-align: left;
        padding-left: 20px;
        font-size: 11pt;
    }}
    
    #btnDashboard:hover, #btnUsers:hover, #btnProduction:hover, #btnSettings:hover {{
        background-color: {hover_color};
    }}
    
    #btnDashboard:checked, #btnUsers:checked, #btnProduction:checked, #btnSettings:checked {{
        background-color: {primary_color};
        border-left: 4px solid white;
    }}
    
    /* Submenu de producción */
    #productionSubmenu {{
        background-color: {secondary_color};
        border: 1px solid {border_color};
        border-radius: 4px;
        padding: 5px;
    }}
    
    #productionSubmenu::item {{
        padding: 8px 20px;
        color: white;
        border-radius: 3px;
    }}
    
    #productionSubmenu::item:selected, #productionSubmenu::item:hover {{
        background-color: {primary_color};
    }}
    
    /* Botones de acción */
    #btnToggleTheme, #btnToggleMenu, #btnLogout {{
        background-color: {primary_color};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    
    #btnToggleTheme:hover, #btnToggleMenu:hover, #btnLogout:hover {{
        background-color: {hover_color};
    }}
    
    /* Barra superior */
    #topBar {{
        background-color: {bg_color};
        border-bottom: 1px solid {border_color};
    }}
    
    #pageTitle {{
        font-size: 16pt;
        font-weight: bold;
        color: {text_color};
    }}
    
    /* Contenedor principal */
    #contentContainer {{
        background-color: {bg_color};
    }}
    
    /* Contenedor lateral y panel de control */
    #sideContainer {{
        background-color: {secondary_color};
        border: none;
    }}
    
    #controlPanel {{
        background-color: {secondary_color};
        border: none;
    }}
    
    /* Páginas */
    #pages {{
        background-color: {bg_color};
    }}
    
    /* Elementos de formulario */
    QLineEdit, QComboBox, QSpinBox, QTextEdit {{
        border: 1px solid {border_color};
        border-radius: 4px;
        padding: 8px;
        background-color: {bg_color};
        color: {text_color};
    }}
    
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {{
        border: 2px solid {primary_color};
    }}
    
    /* Tablas */
    QTableView {{
        border: 1px solid {border_color};
        background-color: {bg_color};
        alternate-background-color: rgba(0, 0, 0, 0.1);
        gridline-color: {border_color};
    }}
    
    QTableView::item {{
        color: {text_color};
    }}
    
    QTableView::item:selected {{
        background-color: {primary_color};
        color: white;
    }}
    
    QHeaderView::section {{
        background-color: {secondary_color};
        color: white;
        padding: 5px;
        border: 1px solid {border_color};
    }}
    
    /* Diálogos */
    QDialog {{
        background-color: {bg_color};
    }}
    
    /* Mensajes */
    QMessageBox {{
        background-color: {bg_color};
    }}
    
    /* Botones de iconos */
    #btnAddRow, #btnEditRow, #btnDeleteRow, #btnIconClear {{  /* Note the double braces for escaping */
        min-width: 40px;
        max-width: 40px;
        min-height: 40px;
        max-height: 40px;
        padding: 8px;
        border-radius: 20px;
        background-color: {primary_color};
        color: white; /* Color del icono */
        qproperty-iconSize: 24px;
    }}
    
    #btnAddRow:hover, #btnEditRow:hover, #btnDeleteRow:hover, #btnIconClear:hover {{
        background-color: {hover_color};
    }}
    
    /* Asegurar que los iconos SVG sean visibles */
    QPushButton QIcon {{
        color: white;
        fill: white;
    }}
    '''
    
    return stylesheet
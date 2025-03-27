#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GestProdAdmin - Aplicación de gestión de producción

Este es el punto de entrada principal de la aplicación.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QIcon

# Importar componentes de la aplicación
from ui.main_window import MainWindow
from config.settings import AppSettings


def setup_application():
    """Configuración inicial de la aplicación"""
    # Configurar información de la aplicación
    QCoreApplication.setOrganizationName("P")
    QCoreApplication.setApplicationName("GestProdAdmin")
    QCoreApplication.setApplicationVersion("1.0.0")
    
    # En versiones recientes de PySide6, el escalado de alto DPI está habilitado por defecto
    # No es necesario configurar atributos de alto DPI manualmente


def main():
    """Función principal que inicia la aplicación"""
    # Crear la aplicación
    app = QApplication(sys.argv)
    
    # Configurar la aplicación
    setup_application()
    
    # Cargar configuraciones
    settings = AppSettings()
    
    # Crear la ventana principal (pero no mostrarla todavía)
    window = MainWindow(settings)
    
    # Ejecutar el bucle de eventos
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
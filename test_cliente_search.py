#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar el sistema de búsqueda de clientes
"""

import sys
from PySide6.QtWidgets import QApplication
from ui.alistamiento import AlistamientoWidget
from config.sqlserver_config import SQLServerConfig

def main():
    """Función principal de prueba"""
    app = QApplication(sys.argv)
    
    # Crear widget de alistamiento
    widget = AlistamientoWidget()
    
    # Configurar SQL Server
    config = SQLServerConfig()
    cliente_query = """
        SELECT DISTINCT A1_COD AS CODCLIENTE,
                        A1_NOME AS NOMBRE 
        FROM SA1010
        WHERE A1_LOJA = '01'
    """
    widget.set_database_config(config, cliente_query)
    
    # Mostrar widget
    widget.setWindowTitle("Prueba de Búsqueda de Clientes")
    widget.resize(900, 400)
    widget.show()
    
    print("=" * 60)
    print("PRUEBA DE BUSQUEDA DE CLIENTES")
    print("=" * 60)
    print("\nInstrucciones:")
    print("1. Espere a que se carguen los clientes")
    print("2. Escriba parte del nombre de un cliente en el campo de busqueda")
    print("3. Seleccione un cliente de la lista desplegable")
    print("4. Verifique que se complete el codigo y nombre")
    print("\nEjemplos de busqueda:")
    print("- 'PAPELERA' -> deberia mostrar PAPELERA ENTRE RIOS SA")
    print("- 'ABERTURAS' -> deberia mostrar ABERTURAS VALENTINUZ S.A.")
    print("- '000001' -> deberia buscar por codigo")
    print("=" * 60)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

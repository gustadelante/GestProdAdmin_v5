#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Diálogo de búsqueda de BAJA

Ventana emergente para buscar y seleccionar registros de BAJA.
"""

from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot, QThread
from database.sqlserver_cliente_repository import SQLServerClienteRepository
from database.sqlserver_utils import check_server_online
from config.sqlserver_config import SQLServerConfig


class BajaSearchWorker(QThread):
    """Worker thread para buscar datos de BAJA"""
    
    baja_loaded = Signal(list)
    error_occurred = Signal(str)
    server_offline = Signal(str)
    
    def __init__(self, config: SQLServerConfig, lote: str = "", sublote: str = ""):
        """Inicializa el worker
        
        Args:
            config: Configuración de SQL Server
            lote: Filtro opcional por LOTE
            sublote: Filtro opcional por SUBLOTE
        """
        super().__init__()
        self.config = config
        self.lote = lote.strip()
        self.sublote = sublote.strip()
    
    def run(self) -> None:
        """Ejecuta la búsqueda de datos de BAJA"""
        try:
            # Verificar que pyodbc esté disponible
            try:
                import pyodbc
            except ImportError:
                self.error_occurred.emit(
                    "pyodbc no está instalado o no está disponible.\n\n"
                    "Instale con: pip install pyodbc"
                )
                return
            
            # Verificar conectividad del servidor
            server_address = self.config.get_server_address()
            port = self.config.get_port()
            
            is_online, message = check_server_online(server_address, port)
            
            if not is_online:
                self.server_offline.emit(message)
                return
            
            # Construir consulta SQL con filtros
            query = """
                SELECT B8_PRODUTO AS PRODUCTO,
                       B8_LOCAL AS DEPOSITO, 
                       B8_SALDO AS SALDO, 
                       B8_SALDO2 AS SALDO2,
                       B8_LOTECTL AS LOTE, 
                       B8_NUMLOTE AS SUBLOTE, 
                       B8_XFABRIC AS FECHAFAB, 
                       B8_DTVALID AS FECHAVENC 
                  FROM SB8010 
                 WHERE B8_SALDO > 0
                   AND B8_SALDO > B8_EMPENHO
            """
            
            # Agregar filtros opcionales
            if self.lote:
                query += f" AND B8_LOTECTL LIKE '%{self.lote}%'"
            if self.sublote:
                query += f" AND B8_NUMLOTE LIKE '%{self.sublote}%'"
            
            # Conectar y ejecutar consulta
            connection_string = self.config.get_connection_string()
            with SQLServerClienteRepository(connection_string) as repo:
                if not repo.connect():
                    self.error_occurred.emit("No se pudo conectar a SQL Server")
                    return
                
                cursor = repo.cursor
                cursor.execute(query)
                rows = cursor.fetchall()
                
                # Convertir a lista de diccionarios
                baja_data = []
                for row in rows:
                    baja_data.append({
                        'PRODUCTO': row.PRODUCTO if row.PRODUCTO else '',
                        'DEPOSITO': row.DEPOSITO if row.DEPOSITO else '',
                        'SALDO': row.SALDO if row.SALDO else 0,
                        'SALDO2': row.SALDO2 if row.SALDO2 else 0,
                        'LOTE': row.LOTE if row.LOTE else '',
                        'SUBLOTE': row.SUBLOTE if row.SUBLOTE else '',
                        'FECHAFAB': row.FECHAFAB if row.FECHAFAB else '',
                        'FECHAVENC': row.FECHAVENC if row.FECHAVENC else ''
                    })
                
                self.baja_loaded.emit(baja_data)
                
        except Exception as e:
            self.error_occurred.emit(str(e))


class BajaSearchDialog(QDialog):
    """Diálogo para buscar y seleccionar registros de BAJA"""
    
    def __init__(self, config: SQLServerConfig, parent=None):
        """Inicializa el diálogo
        
        Args:
            config: Configuración de SQL Server
            parent: Widget padre
        """
        super().__init__(parent)
        self.config = config
        self.baja_data: List[Dict[str, Any]] = []
        self.selected_items: List[Dict[str, Any]] = []
        
        self.setWindowTitle("Buscar BAJA")
        self.setMinimumSize(900, 500)
        self.init_ui()
    
    def init_ui(self) -> None:
        """Inicializa la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("Buscar Registros de BAJA")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Filtros de búsqueda
        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(15)
        
        # Filtro por LOTE
        lbl_lote = QLabel("LOTE:")
        filtros_layout.addWidget(lbl_lote)
        
        self.txt_lote = QLineEdit()
        self.txt_lote.setPlaceholderText("Filtrar por lote...")
        self.txt_lote.setMaximumWidth(150)
        self.txt_lote.returnPressed.connect(self.on_buscar)
        filtros_layout.addWidget(self.txt_lote)
        
        # Filtro por SUBLOTE
        lbl_sublote = QLabel("SUBLOTE:")
        filtros_layout.addWidget(lbl_sublote)
        
        self.txt_sublote = QLineEdit()
        self.txt_sublote.setPlaceholderText("Filtrar por sublote...")
        self.txt_sublote.setMaximumWidth(150)
        self.txt_sublote.returnPressed.connect(self.on_buscar)
        filtros_layout.addWidget(self.txt_sublote)
        
        # Botón Buscar
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setMaximumWidth(100)
        self.btn_buscar.clicked.connect(self.on_buscar)
        filtros_layout.addWidget(self.btn_buscar)
        
        filtros_layout.addStretch()
        layout.addLayout(filtros_layout)
        
        # Grilla de resultados
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(8)
        self.tabla_resultados.setHorizontalHeaderLabels([
            "PRODUCTO", "DEPOSITO", "SALDO", "SALDO2", 
            "LOTE", "SUBLOTE", "FECHA FAB", "FECHA VENC"
        ])
        self.tabla_resultados.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_resultados.setSelectionMode(QAbstractItemView.MultiSelection)
        self.tabla_resultados.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_resultados.horizontalHeader().setStretchLastSection(True)
        self.tabla_resultados.setAlternatingRowColors(True)
        layout.addWidget(self.tabla_resultados)
        
        # Botones del diálogo
        button_box = QDialogButtonBox()
        self.btn_agregar = button_box.addButton("Agregar Seleccionados", QDialogButtonBox.AcceptRole)
        btn_cancelar = button_box.addButton("Cancelar", QDialogButtonBox.RejectRole)
        
        # Desconectar el comportamiento por defecto y conectar manualmente
        # para evitar que Enter en los campos de búsqueda active el botón
        button_box.accepted.disconnect()
        self.btn_agregar.clicked.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        
        # Deshabilitar auto-default para que Enter no active el botón
        self.btn_agregar.setAutoDefault(False)
        self.btn_agregar.setDefault(False)
        
        layout.addWidget(button_box)
    
    @Slot()
    def on_buscar(self) -> None:
        """Maneja el clic en el botón Buscar"""
        lote = self.txt_lote.text().strip()
        sublote = self.txt_sublote.text().strip()
        
        # Crear y configurar el worker
        self.worker = BajaSearchWorker(self.config, lote, sublote)
        self.worker.baja_loaded.connect(self.on_baja_loaded)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.server_offline.connect(self.on_server_offline)
        
        # Deshabilitar botón mientras carga
        self.btn_buscar.setEnabled(False)
        self.btn_buscar.setText("Buscando...")
        
        # Iniciar búsqueda
        self.worker.start()
    
    @Slot(list)
    def on_baja_loaded(self, baja_data: List[Dict[str, Any]]) -> None:
        """Maneja la carga exitosa de datos
        
        Args:
            baja_data: Lista de diccionarios con datos de BAJA
        """
        self.baja_data = baja_data
        self.load_table(baja_data)
        
        # Habilitar botón
        self.btn_buscar.setEnabled(True)
        self.btn_buscar.setText("Buscar")
        
        if not baja_data:
            QMessageBox.information(
                self,
                "Sin Resultados",
                "No se encontraron registros con los filtros especificados."
            )
    
    @Slot(str)
    def on_error(self, error_msg: str) -> None:
        """Maneja errores en la búsqueda
        
        Args:
            error_msg: Mensaje de error
        """
        self.btn_buscar.setEnabled(True)
        self.btn_buscar.setText("Buscar")
        QMessageBox.critical(
            self,
            "Error al Cargar Datos",
            f"Ocurrió un error al cargar los datos:\n{error_msg}"
        )
    
    @Slot(str)
    def on_server_offline(self, message: str) -> None:
        """Maneja el caso cuando el servidor está offline
        
        Args:
            message: Mensaje descriptivo del problema
        """
        self.btn_buscar.setEnabled(True)
        self.btn_buscar.setText("Buscar")
        QMessageBox.warning(
            self,
            "Servidor No Disponible",
            f"No se pudo conectar al servidor SQL Server:\n{message}"
        )
    
    def load_table(self, baja_data: List[Dict[str, Any]]) -> None:
        """Carga los datos en la tabla
        
        Args:
            baja_data: Lista de diccionarios con datos de BAJA
        """
        self.tabla_resultados.setRowCount(0)
        
        for row_data in baja_data:
            row_position = self.tabla_resultados.rowCount()
            self.tabla_resultados.insertRow(row_position)
            
            # Agregar datos a las columnas
            self.tabla_resultados.setItem(row_position, 0, QTableWidgetItem(str(row_data['PRODUCTO'])))
            self.tabla_resultados.setItem(row_position, 1, QTableWidgetItem(str(row_data['DEPOSITO'])))
            self.tabla_resultados.setItem(row_position, 2, QTableWidgetItem(str(row_data['SALDO'])))
            self.tabla_resultados.setItem(row_position, 3, QTableWidgetItem(str(row_data['SALDO2'])))
            self.tabla_resultados.setItem(row_position, 4, QTableWidgetItem(str(row_data['LOTE'])))
            self.tabla_resultados.setItem(row_position, 5, QTableWidgetItem(str(row_data['SUBLOTE'])))
            self.tabla_resultados.setItem(row_position, 6, QTableWidgetItem(str(row_data['FECHAFAB'])))
            self.tabla_resultados.setItem(row_position, 7, QTableWidgetItem(str(row_data['FECHAVENC'])))
        
        # Ajustar columnas al contenido
        self.tabla_resultados.resizeColumnsToContents()
    
    @Slot()
    def on_accept(self) -> None:
        """Maneja la aceptación del diálogo"""
        selected_rows = self.tabla_resultados.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.information(
                self,
                "Sin Selección",
                "Por favor, seleccione al menos una fila."
            )
            return
        
        # Obtener los items seleccionados
        self.selected_items = []
        for index in selected_rows:
            row = index.row()
            if row < len(self.baja_data):
                self.selected_items.append(self.baja_data[row])
        
        self.accept()
    
    def get_selected_items(self) -> List[Dict[str, Any]]:
        """Obtiene los items seleccionados
        
        Returns:
            Lista de diccionarios con los items seleccionados
        """
        return self.selected_items

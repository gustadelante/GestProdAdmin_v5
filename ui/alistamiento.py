#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de Alistamiento

Contiene la implementación del formulario de alistamiento.
"""

from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QComboBox, QLineEdit, QGroupBox, QFormLayout, QMessageBox, QCompleter,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QAbstractItemView,
    QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QStringListModel, QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from database.sqlserver_cliente_repository import SQLServerClienteRepository
from database.sqlserver_utils import check_server_online
from config.sqlserver_config import SQLServerConfig
from ui.baja_search_dialog import BajaSearchDialog
from ui.producto_search_dialog import ProductoSearchDialog


class BajaLoaderWorker(QThread):
    """Worker thread para cargar datos de BAJA sin bloquear la UI"""
    
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
        """Ejecuta la carga de datos de BAJA en background"""
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


class ClienteLoaderWorker(QThread):
    """Worker thread para cargar clientes sin bloquear la UI"""
    
    clientes_loaded = Signal(list)
    error_occurred = Signal(str)
    server_offline = Signal(str)
    
    def __init__(self, config: SQLServerConfig, query: str):
        """Inicializa el worker
        
        Args:
            config: Configuración de SQL Server
            query: Consulta SQL para obtener clientes
        """
        super().__init__()
        self.config = config
        self.query = query
    
    def run(self) -> None:
        """Ejecuta la carga de clientes en background"""
        try:
            # Verificar que pyodbc esté disponible
            try:
                import pyodbc
            except ImportError:
                self.error_occurred.emit(
                    "pyodbc no está instalado o no está disponible.\n\n"
                    "Instale con: pip install pyodbc\n\n"
                    "Si ya está instalado, verifique que esté en el mismo entorno Python que la aplicación."
                )
                return
            
            # Verificar conectividad del servidor primero
            server_address = self.config.get_server_address()
            port = self.config.get_port()
            
            is_online, message = check_server_online(server_address, port)
            
            if not is_online:
                self.server_offline.emit(message)
                return
            
            # Si el servidor está online, intentar conectar y obtener clientes
            connection_string = self.config.get_connection_string()
            with SQLServerClienteRepository(connection_string) as repo:
                clientes = repo.get_clientes(self.query)
                self.clientes_loaded.emit(clientes)
                
        except ImportError as e:
            self.error_occurred.emit(f"Error de importación: {str(e)}")
        except Exception as e:
            self.error_occurred.emit(str(e))


class AlistamientoWidget(QWidget):
    """Widget para el formulario de alistamiento"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Inicializa el widget de alistamiento
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.clientes_data: List[Tuple[str, str]] = []
        self.sqlserver_config: Optional[SQLServerConfig] = None
        self.cliente_query: Optional[str] = None
        self.worker: Optional[ClienteLoaderWorker] = None
        self.init_ui()
    
    def init_ui(self) -> None:
        """Inicializa los componentes de la interfaz"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Sector 1: Título
        title = QLabel("Generación txt Alistamiento")
        title.setObjectName("alistamientoTitle")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Sector 2: Encabezado con recuadro "Alistamiento"
        header_group = QGroupBox("Alistamiento")
        header_group.setObjectName("alistamientoGroup")
        
        header_layout = QHBoxLayout(header_group)
        header_layout.setSpacing(15)
        header_layout.setContentsMargins(15, 15, 15, 15)
        
        # Label y ComboBox Tipo
        lbl_tipo = QLabel("Tipo:")
        header_layout.addWidget(lbl_tipo)
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.setObjectName("comboTipo")
        self.combo_tipo.addItem("504 - RBT", "504")
        self.combo_tipo.addItem("505 - ACH", "505")
        self.combo_tipo.setMinimumWidth(150)
        header_layout.addWidget(self.combo_tipo)
        
        # Espaciador
        header_layout.addSpacing(20)
        
        # Label Cliente
        lbl_cliente = QLabel("Cliente:")
        header_layout.addWidget(lbl_cliente)
        
        # Campo de Código de Cliente
        self.txt_codigo_cliente = QLineEdit()
        self.txt_codigo_cliente.setObjectName("txtCodigoCliente")
        self.txt_codigo_cliente.setPlaceholderText("Código")
        self.txt_codigo_cliente.setMaximumWidth(100)
        header_layout.addWidget(self.txt_codigo_cliente)
        
        # ComboBox de Nombre de Cliente (editable y filtrable)
        self.combo_nombre_cliente = QComboBox()
        self.combo_nombre_cliente.setObjectName("comboNombreCliente")
        self.combo_nombre_cliente.setEditable(True)
        self.combo_nombre_cliente.setInsertPolicy(QComboBox.NoInsert)
        self.combo_nombre_cliente.lineEdit().setPlaceholderText("Escriba para filtrar clientes...")
        self.combo_nombre_cliente.setMinimumWidth(400)
        header_layout.addWidget(self.combo_nombre_cliente)
        
        # Espaciador para empujar todo a la izquierda
        header_layout.addStretch()
        
        main_layout.addWidget(header_group)
        
        # Variables para datos de clientes
        self.cliente_codigo_map = {}  # {codigo: nombre}
        self.cliente_nombre_map = {}  # {nombre: codigo}
        
        # Conectar señales
        self.txt_codigo_cliente.textChanged.connect(self.on_codigo_changed)
        self.combo_nombre_cliente.currentTextChanged.connect(self.on_nombre_changed)
        
        # Sector 3: BAJA
        baja_group = QGroupBox("BAJA")
        baja_group.setObjectName("bajaGroup")
        baja_layout = QVBoxLayout(baja_group)
        baja_layout.setSpacing(10)
        baja_layout.setContentsMargins(15, 15, 15, 15)
        
        # Botón para abrir ventana de búsqueda
        btn_layout = QHBoxLayout()
        self.btn_buscar_baja = QPushButton("Buscar y Agregar Items")
        self.btn_buscar_baja.setObjectName("btnBuscarBaja")
        self.btn_buscar_baja.setMaximumWidth(200)
        self.btn_buscar_baja.clicked.connect(self.on_abrir_busqueda_baja)
        btn_layout.addWidget(self.btn_buscar_baja)
        
        self.btn_eliminar_baja = QPushButton("Eliminar Seleccionado")
        self.btn_eliminar_baja.setObjectName("btnEliminarBaja")
        self.btn_eliminar_baja.setMaximumWidth(150)
        self.btn_eliminar_baja.clicked.connect(self.on_eliminar_baja)
        btn_layout.addWidget(self.btn_eliminar_baja)
        
        btn_layout.addStretch()
        baja_layout.addLayout(btn_layout)
        
        # Grilla principal con items seleccionados
        self.tabla_baja = QTableWidget()
        self.tabla_baja.setObjectName("tablaBaja")
        self.tabla_baja.setColumnCount(8)
        self.tabla_baja.setHorizontalHeaderLabels([
            "PRODUCTO", "DEPOSITO", "SALDO", "SALDO2", 
            "LOTE", "SUBLOTE", "FECHA FAB", "FECHA VENC"
        ])
        self.tabla_baja.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_baja.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_baja.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_baja.horizontalHeader().setStretchLastSection(True)
        self.tabla_baja.setAlternatingRowColors(True)
        self.tabla_baja.setMinimumHeight(200)
        baja_layout.addWidget(self.tabla_baja)
        
        # Fila de totales
        totales_layout = QHBoxLayout()
        totales_layout.setSpacing(15)
        
        lbl_totales = QLabel("TOTALES:")
        lbl_totales.setStyleSheet("font-weight: bold;")
        totales_layout.addWidget(lbl_totales)
        
        lbl_saldo_label = QLabel("SALDO:")
        totales_layout.addWidget(lbl_saldo_label)
        
        self.lbl_total_saldo = QLabel("0")
        self.lbl_total_saldo.setObjectName("lblTotalSaldo")
        self.lbl_total_saldo.setStyleSheet("font-weight: bold; min-width: 80px;")
        totales_layout.addWidget(self.lbl_total_saldo)
        
        totales_layout.addSpacing(20)
        
        lbl_saldo2_label = QLabel("SALDO2:")
        totales_layout.addWidget(lbl_saldo2_label)
        
        self.lbl_total_saldo2 = QLabel("0")
        self.lbl_total_saldo2.setObjectName("lblTotalSaldo2")
        self.lbl_total_saldo2.setStyleSheet("font-weight: bold; min-width: 80px;")
        totales_layout.addWidget(self.lbl_total_saldo2)
        
        totales_layout.addStretch()
        baja_layout.addLayout(totales_layout)
        
        # Configurar política de tamaño para que se expanda verticalmente
        from PySide6.QtWidgets import QSizePolicy
        baja_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        main_layout.addWidget(baja_group)
        
        # Variables para datos de BAJA
        self.baja_seleccionados: List[Dict[str, Any]] = []
        
        # Sector 4: ALTA
        alta_group = QGroupBox("ALTA")
        alta_group.setObjectName("altaGroup")
        alta_layout = QVBoxLayout(alta_group)
        alta_layout.setSpacing(10)
        alta_layout.setContentsMargins(15, 15, 15, 15)
        
        # Botones para agregar/eliminar filas
        btn_alta_layout = QHBoxLayout()
        self.btn_agregar_fila_alta = QPushButton("Agregar Fila")
        self.btn_agregar_fila_alta.setObjectName("btnAgregarFilaAlta")
        self.btn_agregar_fila_alta.setMaximumWidth(120)
        self.btn_agregar_fila_alta.clicked.connect(self.on_agregar_fila_alta)
        btn_alta_layout.addWidget(self.btn_agregar_fila_alta)
        
        self.btn_eliminar_fila_alta = QPushButton("Eliminar Fila")
        self.btn_eliminar_fila_alta.setObjectName("btnEliminarFilaAlta")
        self.btn_eliminar_fila_alta.setMaximumWidth(120)
        self.btn_eliminar_fila_alta.clicked.connect(self.on_eliminar_fila_alta)
        btn_alta_layout.addWidget(self.btn_eliminar_fila_alta)
        
        btn_alta_layout.addStretch()
        alta_layout.addLayout(btn_alta_layout)
        
        # Grilla ALTA con 8 columnas
        self.tabla_alta = QTableWidget()
        self.tabla_alta.setObjectName("tablaAlta")
        self.tabla_alta.setColumnCount(8)
        self.tabla_alta.setHorizontalHeaderLabels([
            "PRODUCTO", "KILOS", "LOTE", "BOBINA", 
            "SUBLOTE", "NRO. OT", "FECHA FAB", "PROD"
        ])
        
        # Configurar anchos de columnas
        self.tabla_alta.setColumnWidth(0, 150)  # PRODUCTO - 20 caracteres
        self.tabla_alta.setColumnWidth(1, 80)   # KILOS - 6,2 caracteres
        self.tabla_alta.setColumnWidth(2, 100)  # LOTE - 10 caracteres
        self.tabla_alta.setColumnWidth(3, 70)   # BOBINA - 6 caracteres
        self.tabla_alta.setColumnWidth(4, 70)   # SUBLOTE - 6 caracteres
        self.tabla_alta.setColumnWidth(5, 80)   # NUMERO OT - 6 caracteres
        self.tabla_alta.setColumnWidth(6, 100)  # FECHA FAB
        self.tabla_alta.setColumnWidth(7, 60)   # PROD - 2 caracteres
        
        self.tabla_alta.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_alta.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_alta.setAlternatingRowColors(True)
        self.tabla_alta.setMinimumHeight(200)
        
        # Configurar altura de filas para que el texto sea completamente visible
        self.tabla_alta.verticalHeader().setDefaultSectionSize(40)
        
        # Instalar event filter para navegación con Enter
        self.tabla_alta.installEventFilter(self)
        
        # Conectar señales para manejo de la grilla
        self.tabla_alta.cellClicked.connect(self.on_celda_alta_clicked)
        self.tabla_alta.itemChanged.connect(self.on_item_alta_changed)
        self.tabla_alta.currentCellChanged.connect(self.on_current_cell_changed)
        
        alta_layout.addWidget(self.tabla_alta)
        
        # Configurar política de tamaño para que se expanda verticalmente
        alta_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        main_layout.addWidget(alta_group)
        
        # Variables para datos de ALTA
        self.alta_data: List[Dict[str, Any]] = []
        self._updating_alta = False  # Flag para evitar recursión en itemChanged
    
    @Slot(str)
    def on_codigo_changed(self, codigo: str) -> None:
        """Maneja el cambio en el campo de código
        
        Args:
            codigo: Código ingresado
        """
        codigo = codigo.strip()
        if codigo in self.cliente_codigo_map:
            # Bloquear señales para evitar recursividad
            self.combo_nombre_cliente.blockSignals(True)
            nombre = self.cliente_codigo_map[codigo]
            index = self.combo_nombre_cliente.findText(nombre)
            if index >= 0:
                self.combo_nombre_cliente.setCurrentIndex(index)
            self.combo_nombre_cliente.blockSignals(False)
    
    @Slot(str)
    def on_nombre_changed(self, nombre: str) -> None:
        """Maneja el cambio en el combo de nombre
        
        Args:
            nombre: Nombre seleccionado o escrito
        """
        nombre = nombre.strip()
        if nombre in self.cliente_nombre_map:
            # Bloquear señales para evitar recursividad
            self.txt_codigo_cliente.blockSignals(True)
            codigo = self.cliente_nombre_map[nombre]
            self.txt_codigo_cliente.setText(codigo)
            self.txt_codigo_cliente.blockSignals(False)
    
    def load_clientes(self, clientes: List[Tuple[str, str]]) -> None:
        """Carga la lista de clientes en el ComboBox
        
        Args:
            clientes: Lista de tuplas (codigo_cliente, nombre_cliente)
        """
        self.clientes_data = clientes
        
        # Limpiar mapas y combo
        self.cliente_codigo_map.clear()
        self.cliente_nombre_map.clear()
        self.combo_nombre_cliente.clear()
        
        # Agregar ítem vacío al inicio
        self.combo_nombre_cliente.addItem("", "")
        
        # Llenar mapas y combo
        for codigo, nombre in clientes:
            self.cliente_codigo_map[codigo] = nombre
            self.cliente_nombre_map[nombre] = codigo
            self.combo_nombre_cliente.addItem(nombre, codigo)
        
        # Configurar filtrado del ComboBox
        completer = QCompleter(self.combo_nombre_cliente.model(), self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.combo_nombre_cliente.setCompleter(completer)
        
        # Habilitar campos
        self.txt_codigo_cliente.setEnabled(True)
        self.combo_nombre_cliente.setEnabled(True)
        self.combo_nombre_cliente.lineEdit().setPlaceholderText(f"Buscar entre {len(clientes)} clientes...")
    
    def get_tipo_selected(self) -> str:
        """Obtiene el tipo seleccionado (504 o 505)
        
        Returns:
            Código del tipo seleccionado
        """
        return self.combo_tipo.currentData()
    
    def get_cliente_selected(self) -> Optional[str]:
        """Obtiene el código del cliente seleccionado
        
        Returns:
            Código del cliente o None si no hay selección
        """
        codigo = self.txt_codigo_cliente.text().strip()
        return codigo if codigo else None
    
    def get_cliente_nombre(self) -> Optional[str]:
        """Obtiene el nombre del cliente seleccionado
        
        Returns:
            Nombre del cliente o None si no hay selección
        """
        nombre = self.combo_nombre_cliente.currentText().strip()
        return nombre if nombre else None
    
    def set_database_config(self, config: SQLServerConfig, cliente_query: str) -> None:
        """Configura la conexión a SQL Server y la consulta SQL
        
        Args:
            config: Configuración de SQL Server
            cliente_query: Consulta SQL para obtener clientes (debe retornar codigo, nombre)
        """
        self.sqlserver_config = config
        self.cliente_query = cliente_query
    
    def load_clientes_from_db(self) -> None:
        """Carga los clientes desde SQL Server usando un worker thread"""
        if not self.sqlserver_config or not self.cliente_query:
            QMessageBox.warning(
                self,
                "Configuración Incompleta",
                "No se ha configurado la conexión a SQL Server o la consulta SQL."
            )
            return
        
        # Crear y configurar el worker
        self.worker = ClienteLoaderWorker(self.sqlserver_config, self.cliente_query)
        self.worker.clientes_loaded.connect(self.on_clientes_loaded)
        self.worker.error_occurred.connect(self.on_load_error)
        self.worker.server_offline.connect(self.on_server_offline)
        
        # Deshabilitar campos de cliente mientras carga
        self.txt_codigo_cliente.setEnabled(False)
        self.combo_nombre_cliente.setEnabled(False)
        self.combo_nombre_cliente.lineEdit().setPlaceholderText("Verificando servidor...")
        self.txt_codigo_cliente.clear()
        self.combo_nombre_cliente.clear()
        
        # Iniciar carga
        self.worker.start()
    
    @Slot(list)
    def on_clientes_loaded(self, clientes: List[Tuple[str, str]]) -> None:
        """Maneja la carga exitosa de clientes
        
        Args:
            clientes: Lista de tuplas (codigo, nombre)
        """
        self.load_clientes(clientes)
        
        if not clientes:
            QMessageBox.information(
                self,
                "Sin Datos",
                "No se encontraron clientes en la base de datos."
            )
    
    @Slot(str)
    def on_load_error(self, error_msg: str) -> None:
        """Maneja errores en la carga de clientes
        
        Args:
            error_msg: Mensaje de error
        """
        self.txt_codigo_cliente.setEnabled(True)
        self.combo_nombre_cliente.setEnabled(True)
        self.combo_nombre_cliente.lineEdit().setPlaceholderText("Escriba para buscar cliente...")
        QMessageBox.critical(
            self,
            "Error al Cargar Clientes",
            f"Ocurrió un error al cargar los clientes:\n{error_msg}"
        )
    
    @Slot(str)
    def on_server_offline(self, message: str) -> None:
        """Maneja el caso cuando el servidor SQL Server está offline
        
        Args:
            message: Mensaje descriptivo del problema
        """
        self.txt_codigo_cliente.setEnabled(True)
        self.combo_nombre_cliente.setEnabled(True)
        self.combo_nombre_cliente.lineEdit().setPlaceholderText("Escriba para buscar cliente...")
        QMessageBox.warning(
            self,
            "Servidor No Disponible",
            f"No se pudo conectar al servidor SQL Server:\n{message}\n\nVerifique la conectividad de red."
        )
    
    @Slot()
    def on_abrir_busqueda_baja(self) -> None:
        """Abre el diálogo de búsqueda de BAJA"""
        if not self.sqlserver_config:
            QMessageBox.warning(
                self,
                "Configuración Faltante",
                "No se ha configurado la conexión a SQL Server."
            )
            return
        
        # Crear y mostrar el diálogo de búsqueda
        dialog = BajaSearchDialog(self.sqlserver_config, self)
        
        if dialog.exec() == QDialog.Accepted:
            # Obtener los items seleccionados
            selected_items = dialog.get_selected_items()
            
            if selected_items:
                # Agregar los items a la lista de seleccionados
                for item in selected_items:
                    # Verificar que no esté duplicado (por LOTE y SUBLOTE)
                    is_duplicate = any(
                        existing['LOTE'] == item['LOTE'] and 
                        existing['SUBLOTE'] == item['SUBLOTE']
                        for existing in self.baja_seleccionados
                    )
                    
                    if not is_duplicate:
                        self.baja_seleccionados.append(item)
                
                # Actualizar la grilla principal
                self.actualizar_tabla_baja()
                
                QMessageBox.information(
                    self,
                    "Items Agregados",
                    f"Se agregaron {len(selected_items)} item(s) a la lista."
                )
    
    def actualizar_tabla_baja(self) -> None:
        """Actualiza la grilla principal con los items seleccionados"""
        self.tabla_baja.setRowCount(0)
        
        # Variables para acumular totales
        total_saldo = 0
        total_saldo2 = 0
        
        for row_data in self.baja_seleccionados:
            row_position = self.tabla_baja.rowCount()
            self.tabla_baja.insertRow(row_position)
            
            # Agregar datos a las columnas
            self.tabla_baja.setItem(row_position, 0, QTableWidgetItem(str(row_data['PRODUCTO'])))
            self.tabla_baja.setItem(row_position, 1, QTableWidgetItem(str(row_data['DEPOSITO'])))
            self.tabla_baja.setItem(row_position, 2, QTableWidgetItem(str(row_data['SALDO'])))
            self.tabla_baja.setItem(row_position, 3, QTableWidgetItem(str(row_data['SALDO2'])))
            self.tabla_baja.setItem(row_position, 4, QTableWidgetItem(str(row_data['LOTE'])))
            self.tabla_baja.setItem(row_position, 5, QTableWidgetItem(str(row_data['SUBLOTE'])))
            self.tabla_baja.setItem(row_position, 6, QTableWidgetItem(str(row_data['FECHAFAB'])))
            self.tabla_baja.setItem(row_position, 7, QTableWidgetItem(str(row_data['FECHAVENC'])))
            
            # Acumular totales
            try:
                total_saldo += float(row_data['SALDO'])
            except (ValueError, TypeError):
                pass
            
            try:
                total_saldo2 += float(row_data['SALDO2'])
            except (ValueError, TypeError):
                pass
        
        # Ajustar columnas al contenido
        self.tabla_baja.resizeColumnsToContents()
        
        # Actualizar labels de totales
        self.lbl_total_saldo.setText(f"{total_saldo:,.2f}")
        self.lbl_total_saldo2.setText(f"{total_saldo2:,.2f}")
    
    @Slot()
    def on_eliminar_baja(self) -> None:
        """Elimina el item seleccionado de la grilla"""
        current_row = self.tabla_baja.currentRow()
        
        if current_row < 0:
            QMessageBox.information(
                self,
                "Sin Selección",
                "Por favor, seleccione una fila para eliminar."
            )
            return
        
        # Eliminar de la lista
        if current_row < len(self.baja_seleccionados):
            item = self.baja_seleccionados[current_row]
            self.baja_seleccionados.pop(current_row)
            
            # Actualizar la grilla
            self.actualizar_tabla_baja()
            
            QMessageBox.information(
                self,
                "Eliminado",
                f"Se eliminó el item:\nProducto: {item['PRODUCTO']}\nLote: {item['LOTE']}"
            )
    
    @Slot()
    def on_agregar_fila_alta(self) -> None:
        """Agrega una nueva fila vacía a la grilla ALTA"""
        row_position = self.tabla_alta.rowCount()
        self.tabla_alta.insertRow(row_position)
        
        # Crear items para cada columna
        for col in range(8):
            item = QTableWidgetItem("")
            
            # La primera columna (PRODUCTO) no es editable directamente
            # Se selecciona desde el diálogo
            if col == 0:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setBackground(Qt.lightGray)
            
            self.tabla_alta.setItem(row_position, col, item)
    
    @Slot()
    def on_eliminar_fila_alta(self) -> None:
        """Elimina la fila seleccionada de la grilla ALTA"""
        current_row = self.tabla_alta.currentRow()
        
        if current_row < 0:
            QMessageBox.information(
                self,
                "Sin Selección",
                "Por favor, seleccione una fila para eliminar."
            )
            return
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de eliminar esta fila?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.tabla_alta.removeRow(current_row)
    
    @Slot(int, int)
    def on_celda_alta_clicked(self, row: int, col: int) -> None:
        """Maneja el clic en una celda de la grilla ALTA
        
        Args:
            row: Fila clickeada
            col: Columna clickeada
        """
        # Solo abrir diálogo si es la columna PRODUCTO (columna 0)
        if col == 0:
            self.abrir_dialogo_producto(row)
    
    def abrir_dialogo_producto(self, row: int) -> None:
        """Abre el diálogo de búsqueda de productos
        
        Args:
            row: Fila donde se colocará el producto seleccionado
        """
        if not self.sqlserver_config:
            QMessageBox.warning(
                self,
                "Configuración Faltante",
                "No se ha configurado la conexión a SQL Server."
            )
            return
        
        # Crear y mostrar el diálogo de búsqueda de productos
        dialog = ProductoSearchDialog(self.sqlserver_config, self)
        
        if dialog.exec() == QDialog.Accepted:
            producto = dialog.get_selected_producto()
            
            if producto:
                # Bloquear señales temporalmente
                self._updating_alta = True
                
                # Colocar el código del producto en la celda
                item = self.tabla_alta.item(row, 0)
                if item:
                    item.setText(producto['CODIGO'])
                else:
                    new_item = QTableWidgetItem(producto['CODIGO'])
                    new_item.setFlags(new_item.flags() & ~Qt.ItemIsEditable)
                    new_item.setBackground(Qt.lightGray)
                    self.tabla_alta.setItem(row, 0, new_item)
                
                # Autocompletar columna PROD con caracteres 3-4 del código de producto
                codigo = producto['CODIGO']
                if len(codigo) >= 4:
                    prod_value = codigo[2:4]  # Caracteres 3 y 4 (índices 2 y 3)
                    prod_item = self.tabla_alta.item(row, 7)
                    if prod_item:
                        prod_item.setText(prod_value)
                    else:
                        self.tabla_alta.setItem(row, 7, QTableWidgetItem(prod_value))
                
                self._updating_alta = False
    
    @Slot(QTableWidgetItem)
    def on_item_alta_changed(self, item: QTableWidgetItem) -> None:
        """Maneja cambios en items de la grilla ALTA
        
        Args:
            item: Item que cambió
        """
        if self._updating_alta:
            return
        
        row = item.row()
        col = item.column()
        
        # Si cambió la columna BOBINA (col 3), copiar a SUBLOTE (col 4)
        if col == 3:
            self._updating_alta = True
            bobina_value = item.text()
            sublote_item = self.tabla_alta.item(row, 4)
            if sublote_item:
                sublote_item.setText(bobina_value)
            else:
                self.tabla_alta.setItem(row, 4, QTableWidgetItem(bobina_value))
            self._updating_alta = False
    
    @Slot(int, int, int, int)
    def on_current_cell_changed(self, current_row: int, current_col: int, 
                                previous_row: int, previous_col: int) -> None:
        """Maneja el cambio de celda actual en la grilla ALTA
        
        Args:
            current_row: Fila actual
            current_col: Columna actual
            previous_row: Fila anterior
            previous_col: Columna anterior
        """
        # Si el foco entra en la columna FECHA FAB (col 6) y está vacía, poner fecha actual
        if current_row >= 0 and current_col == 6:
            fecha_item = self.tabla_alta.item(current_row, current_col)
            if not fecha_item or not fecha_item.text().strip():
                from datetime import datetime
                fecha_actual = datetime.now().strftime("%d/%m/%Y")
                
                self._updating_alta = True
                if fecha_item:
                    fecha_item.setText(fecha_actual)
                else:
                    self.tabla_alta.setItem(current_row, current_col, QTableWidgetItem(fecha_actual))
                self._updating_alta = False
    
    def eventFilter(self, obj, event) -> bool:
        """Filtro de eventos para manejar navegación con Enter en la grilla ALTA
        
        Args:
            obj: Objeto que generó el evento
            event: Evento a filtrar
            
        Returns:
            True si el evento fue manejado, False en caso contrario
        """
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QKeyEvent
        
        if obj == self.tabla_alta and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Return or key_event.key() == Qt.Key_Enter:
                current_row = self.tabla_alta.currentRow()
                current_col = self.tabla_alta.currentColumn()
                
                if current_row >= 0 and current_col >= 0:
                    # Mover a la siguiente columna editable
                    next_col = current_col + 1
                    
                    # Si es la columna PRODUCTO (0), saltar a la siguiente editable (1)
                    if next_col == 0:
                        next_col = 1
                    
                    # Si llegamos al final de las columnas, ir a la siguiente fila
                    if next_col >= 8:
                        next_col = 1  # Saltar columna PRODUCTO
                        current_row += 1
                        
                        # Si no hay más filas, no hacer nada
                        if current_row >= self.tabla_alta.rowCount():
                            return True
                    
                    # Mover a la siguiente celda
                    self.tabla_alta.setCurrentCell(current_row, next_col)
                    self.tabla_alta.editItem(self.tabla_alta.item(current_row, next_col))
                    return True
        
        return super().eventFilter(obj, event)
    
    def showEvent(self, event) -> None:
        """Se ejecuta cuando el widget se muestra
        
        Args:
            event: Evento de mostrar
        """
        super().showEvent(event)
        # Cargar clientes si están configurados y no hay datos cargados
        if self.sqlserver_config and self.cliente_query and not self.clientes_data:
            self.load_clientes_from_db()

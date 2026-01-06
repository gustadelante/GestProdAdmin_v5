#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Diálogo de búsqueda de Productos

Ventana emergente para buscar y seleccionar productos de SB1010.
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


class ReverseCompare:
    """Clase auxiliar para invertir el orden de comparación en ordenamientos"""
    
    def __init__(self, value):
        self.value = value
    
    def __lt__(self, other):
        return self.value > other.value
    
    def __gt__(self, other):
        return self.value < other.value
    
    def __eq__(self, other):
        return self.value == other.value
    
    def __le__(self, other):
        return self.value >= other.value
    
    def __ge__(self, other):
        return self.value <= other.value
    
    def __ne__(self, other):
        return self.value != other.value


class ProductoSearchWorker(QThread):
    """Worker thread para buscar productos"""
    
    productos_loaded = Signal(list)
    error_occurred = Signal(str)
    server_offline = Signal(str)
    
    def __init__(self, config: SQLServerConfig, codigo: str = ""):
        """Inicializa el worker
        
        Args:
            config: Configuración de SQL Server
            codigo: Filtro opcional por CODIGO
        """
        super().__init__()
        self.config = config
        self.codigo = codigo.strip()
    
    def run(self) -> None:
        """Ejecuta la búsqueda de productos"""
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
            
            # Construir consulta SQL con filtro
            query = """
                SELECT B1_COD AS CODIGO, 
                       B1_DESC AS DESCRIPCION, 
                       B1_XGRAMAJ AS GRAMAJE, 
                       B1_XDIALAR AS DIAMETRO, 
                       B1_XANBOTO AS ANCHO, 
                       B1_XALISTA AS ALIS, 
                       B1_XPRODUC AS PRODUCTO 
                  FROM SB1010
                 WHERE B1_TIPO = 'PE'
            """
            
            # Agregar filtro opcional por código
            if self.codigo:
                query += f" AND B1_COD LIKE '%{self.codigo}%'"
            
            query += " ORDER BY 3, 6, 4, 5"
            
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
                productos_data = []
                for row in rows:
                    productos_data.append({
                        'CODIGO': row.CODIGO if row.CODIGO else '',
                        'DESCRIPCION': row.DESCRIPCION if row.DESCRIPCION else '',
                        'GRAMAJE': row.GRAMAJE if row.GRAMAJE else '',
                        'DIAMETRO': row.DIAMETRO if row.DIAMETRO else '',
                        'ANCHO': row.ANCHO if row.ANCHO else '',
                        'ALIS': row.ALIS if row.ALIS else '',
                        'PRODUCTO': row.PRODUCTO if row.PRODUCTO else ''
                    })
                
                self.productos_loaded.emit(productos_data)
                
        except Exception as e:
            self.error_occurred.emit(str(e))


class ProductoSearchDialog(QDialog):
    """Diálogo para buscar y seleccionar productos"""
    
    def __init__(self, config: SQLServerConfig, parent=None):
        """Inicializa el diálogo
        
        Args:
            config: Configuración de SQL Server
            parent: Widget padre
        """
        super().__init__(parent)
        self.config = config
        self.productos_data: List[Dict[str, Any]] = []
        self.selected_producto: Optional[Dict[str, Any]] = None
        self.sort_columns: List[tuple] = []  # Lista de (columna, orden) para ordenamiento multi-columna
        
        self.setWindowTitle("Buscar Producto")
        self.setMinimumSize(1100, 500)
        self.resize(1200, 600)
        self.init_ui()
    
    def init_ui(self) -> None:
        """Inicializa la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("Buscar Productos")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Filtro de búsqueda
        filtro_layout = QHBoxLayout()
        filtro_layout.setSpacing(15)
        
        # Filtro por CODIGO
        lbl_codigo = QLabel("CÓDIGO:")
        filtro_layout.addWidget(lbl_codigo)
        
        self.txt_codigo = QLineEdit()
        self.txt_codigo.setPlaceholderText("Filtrar por código...")
        self.txt_codigo.setMaximumWidth(200)
        self.txt_codigo.returnPressed.connect(self.on_buscar)
        filtro_layout.addWidget(self.txt_codigo)
        
        # Botón Buscar
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setMaximumWidth(100)
        self.btn_buscar.clicked.connect(self.on_buscar)
        filtro_layout.addWidget(self.btn_buscar)
        
        filtro_layout.addStretch()
        layout.addLayout(filtro_layout)
        
        # Grilla de resultados
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(7)
        self.tabla_resultados.setHorizontalHeaderLabels([
            "CÓDIGO", "DESCRIPCIÓN", "GRAMAJE", "DIAMETRO", "ANCHO", "ALIS", "PRODUCTO"
        ])
        self.tabla_resultados.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_resultados.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_resultados.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_resultados.horizontalHeader().setStretchLastSection(True)
        self.tabla_resultados.setAlternatingRowColors(True)
        self.tabla_resultados.setSortingEnabled(False)  # Deshabilitamos el ordenamiento automático
        self.tabla_resultados.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        self.tabla_resultados.doubleClicked.connect(self.on_double_click)
        layout.addWidget(self.tabla_resultados)
        
        # Botones del diálogo
        button_box = QDialogButtonBox()
        self.btn_seleccionar = button_box.addButton("Seleccionar", QDialogButtonBox.AcceptRole)
        btn_cancelar = button_box.addButton("Cancelar", QDialogButtonBox.RejectRole)
        
        # Desconectar el comportamiento por defecto
        button_box.accepted.disconnect()
        self.btn_seleccionar.clicked.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        
        # Deshabilitar auto-default
        self.btn_seleccionar.setAutoDefault(False)
        self.btn_seleccionar.setDefault(False)
        
        layout.addWidget(button_box)
        
        # Cargar todos los productos al inicio
        self.on_buscar()
    
    @Slot()
    def on_buscar(self) -> None:
        """Maneja el clic en el botón Buscar"""
        codigo = self.txt_codigo.text().strip()
        
        # Crear y configurar el worker
        self.worker = ProductoSearchWorker(self.config, codigo)
        self.worker.productos_loaded.connect(self.on_productos_loaded)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.server_offline.connect(self.on_server_offline)
        
        # Deshabilitar botón mientras carga
        self.btn_buscar.setEnabled(False)
        self.btn_buscar.setText("Buscando...")
        
        # Iniciar búsqueda
        self.worker.start()
    
    @Slot(list)
    def on_productos_loaded(self, productos_data: List[Dict[str, Any]]) -> None:
        """Maneja la carga exitosa de datos
        
        Args:
            productos_data: Lista de diccionarios con datos de productos
        """
        self.productos_data = productos_data
        self.load_table(productos_data)
        
        # Habilitar botón
        self.btn_buscar.setEnabled(True)
        self.btn_buscar.setText("Buscar")
        
        if not productos_data:
            QMessageBox.information(
                self,
                "Sin Resultados",
                "No se encontraron productos con el filtro especificado."
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
    
    @Slot(int)
    def on_header_clicked(self, logical_index: int) -> None:
        """Maneja el clic en el encabezado de una columna para ordenamiento multi-columna
        
        Args:
            logical_index: Índice de la columna clickeada
        """
        # Mapeo de índices de columna a nombres de campos
        column_names = ['CODIGO', 'DESCRIPCION', 'GRAMAJE', 'DIAMETRO', 'ANCHO', 'ALIS', 'PRODUCTO']
        
        if logical_index >= len(column_names):
            return
        
        column_name = column_names[logical_index]
        
        # Verificar si la columna ya está en la lista de ordenamiento
        existing_index = None
        for i, (col, order) in enumerate(self.sort_columns):
            if col == column_name:
                existing_index = i
                break
        
        if existing_index is not None:
            # Si ya existe, cambiar el orden (asc <-> desc)
            current_order = self.sort_columns[existing_index][1]
            new_order = Qt.DescendingOrder if current_order == Qt.AscendingOrder else Qt.AscendingOrder
            self.sort_columns[existing_index] = (column_name, new_order)
        else:
            # Si no existe, agregar al final con orden ascendente
            self.sort_columns.append((column_name, Qt.AscendingOrder))
        
        # Aplicar el ordenamiento multi-columna
        self.apply_multi_column_sort()
    
    def apply_multi_column_sort(self) -> None:
        """Aplica el ordenamiento multi-columna a los datos"""
        if not self.productos_data or not self.sort_columns:
            return
        
        # Crear una copia de los datos para ordenar
        sorted_data = self.productos_data.copy()
        
        # Crear una función de clave que ordena por todas las columnas simultáneamente
        # Similar a SQL: ORDER BY col1, col2, col3
        def sort_key(item):
            key_tuple = []
            for column_name, order in self.sort_columns:
                value = str(item.get(column_name, ''))
                # Si es descendente, negar el valor para invertir el orden
                # Usamos una clase personalizada que invierte la comparación
                if order == Qt.DescendingOrder:
                    # Crear un wrapper que invierte las comparaciones
                    key_tuple.append(ReverseCompare(value))
                else:
                    key_tuple.append(value)
            return tuple(key_tuple)
        
        # Ordenar usando la clave compuesta
        sorted_data.sort(key=sort_key)
        
        # Recargar la tabla con los datos ordenados
        self.load_table(sorted_data)
        
        # Actualizar indicadores visuales en los encabezados
        self.update_header_indicators()
    
    def update_header_indicators(self) -> None:
        """Actualiza los indicadores visuales en los encabezados de columna"""
        column_names = ['CODIGO', 'DESCRIPCION', 'GRAMAJE', 'DIAMETRO', 'ANCHO', 'ALIS', 'PRODUCTO']
        base_labels = ["CÓDIGO", "DESCRIPCIÓN", "GRAMAJE", "DIAMETRO", "ANCHO", "ALIS", "PRODUCTO"]
        
        # Resetear todos los encabezados
        for i, label in enumerate(base_labels):
            self.tabla_resultados.horizontalHeaderItem(i).setText(label)
        
        # Agregar indicadores para columnas ordenadas
        for priority, (column_name, order) in enumerate(self.sort_columns, 1):
            col_index = column_names.index(column_name)
            arrow = "↑" if order == Qt.AscendingOrder else "↓"
            priority_text = f" ({priority})" if len(self.sort_columns) > 1 else ""
            new_label = f"{base_labels[col_index]} {arrow}{priority_text}"
            self.tabla_resultados.horizontalHeaderItem(col_index).setText(new_label)
    
    def load_table(self, productos_data: List[Dict[str, Any]]) -> None:
        """Carga los datos en la tabla
        
        Args:
            productos_data: Lista de diccionarios con datos de productos
        """
        self.tabla_resultados.setRowCount(0)
        
        for row_data in productos_data:
            row_position = self.tabla_resultados.rowCount()
            self.tabla_resultados.insertRow(row_position)
            
            # Agregar datos a las columnas
            self.tabla_resultados.setItem(row_position, 0, QTableWidgetItem(str(row_data['CODIGO'])))
            self.tabla_resultados.setItem(row_position, 1, QTableWidgetItem(str(row_data['DESCRIPCION'])))
            self.tabla_resultados.setItem(row_position, 2, QTableWidgetItem(str(row_data['GRAMAJE'])))
            self.tabla_resultados.setItem(row_position, 3, QTableWidgetItem(str(row_data['DIAMETRO'])))
            self.tabla_resultados.setItem(row_position, 4, QTableWidgetItem(str(row_data['ANCHO'])))
            self.tabla_resultados.setItem(row_position, 5, QTableWidgetItem(str(row_data['ALIS'])))
            self.tabla_resultados.setItem(row_position, 6, QTableWidgetItem(str(row_data['PRODUCTO'])))
        
        # Ajustar columnas al contenido
        self.tabla_resultados.resizeColumnsToContents()
    
    @Slot()
    def on_double_click(self) -> None:
        """Maneja el doble clic en una fila"""
        self.on_accept()
    
    @Slot()
    def on_accept(self) -> None:
        """Maneja la aceptación del diálogo"""
        current_row = self.tabla_resultados.currentRow()
        
        if current_row < 0:
            QMessageBox.information(
                self,
                "Sin Selección",
                "Por favor, seleccione un producto."
            )
            return
        
        # Obtener el producto seleccionado
        if current_row < len(self.productos_data):
            self.selected_producto = self.productos_data[current_row]
            self.accept()
    
    def get_selected_producto(self) -> Optional[Dict[str, Any]]:
        """Obtiene el producto seleccionado
        
        Returns:
            Diccionario con el producto seleccionado o None
        """
        return self.selected_producto

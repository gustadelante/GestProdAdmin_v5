#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de detalle de órdenes de fabricación

Contiene la implementación de la vista detallada de órdenes de fabricación.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QSpacerItem, QPushButton, QMessageBox, QGridLayout,
    QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import os
from typing import Dict, List, Set, Tuple
from database.production_models import ProductionData


class ProductionOFDetailWidget(QWidget):
    """Widget para el detalle de órdenes de fabricación"""
    
    def __init__(self, parent=None):
        """
        Inicializa el widget de detalle de órdenes de fabricación
        
        Args:
            parent (QWidget, optional): Widget padre
        """
        super().__init__(parent)
        from database.db_helper import get_db_path
        self.db_path = get_db_path()
        self.production_data = ProductionData(self.db_path)
        self.current_of = ""
        self.of_list = []
        self.init_ui()
        self.load_of_list()
    
    def init_ui(self):
        """Inicializa los componentes de la interfaz"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Cabecera con selector de OF
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        
        # Etiqueta y selector de OF
        header_layout.addWidget(QLabel("Orden de Fabricación:"))
        self.of_selector = QComboBox()
        self.of_selector.setMinimumWidth(200)
        self.of_selector.currentIndexChanged.connect(self.load_of_data)
        header_layout.addWidget(self.of_selector)
        
        # Botones de navegación
        self.btn_prev = QPushButton("Anterior")
        self.btn_prev.clicked.connect(self.go_to_prev_of)
        header_layout.addWidget(self.btn_prev)
        
        self.btn_next = QPushButton("Siguiente")
        self.btn_next.clicked.connect(self.go_to_next_of)
        header_layout.addWidget(self.btn_next)
        
        # Botón de exportación
        self.btn_export = QPushButton("Exportar datos")
        self.btn_export.setToolTip("Exportar datos de la OF seleccionada a un archivo TXT")
        self.btn_export.clicked.connect(self.export_data)
        self.btn_export.setEnabled(False)  # Deshabilitado hasta que se seleccione una OF
        header_layout.addWidget(self.btn_export)
        
        # Espaciador para empujar todo a la izquierda
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        main_layout.addWidget(header_frame)
        
        # Contenido principal
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_layout = QVBoxLayout(self.content_frame)
        
        # Placeholder para el contenido dinámico (se llenará al seleccionar una OF)
        self.placeholder_label = QLabel("Seleccione una Orden de Fabricación para ver su detalle")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("font-size: 14pt; color: gray;")
        self.content_layout.addWidget(self.placeholder_label)
        
        main_layout.addWidget(self.content_frame)
        
        # Espaciador para empujar todo hacia arriba
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    
    def load_of_list(self):
        """Carga la lista de órdenes de fabricación disponibles"""
        try:
            if not self.production_data.connect():
                QMessageBox.critical(
                    self, 
                    "Error de conexión", 
                    "No se pudo conectar a la base de datos de producción."
                )
                return
            
            # Obtener las tablas disponibles
            tables = self.production_data.get_table_names()
            
            # Buscar la tabla 'bobina' o usar la primera disponible
            table_name = "bobina" if "bobina" in tables else tables[0] if tables else ""
            
            if not table_name:
                QMessageBox.warning(
                    self, 
                    "Sin tablas", 
                    "No se encontraron tablas en la base de datos de producción."
                )
                self.production_data.disconnect()
                return
            
            # Obtener el esquema de la tabla para verificar si tiene columna OF
            schema = self.production_data.get_table_schema(table_name)
            columns = [col[1].lower() for col in schema]  # Convertir a minúsculas para comparación
            
            if "of" not in columns:
                QMessageBox.warning(
                    self, 
                    "Columna no encontrada", 
                    f"La tabla {table_name} no tiene una columna 'OF'."
                )
                self.production_data.disconnect()
                return
            
            # Consultar las OF únicas
            self.cursor = self.production_data.connection.cursor()
            self.cursor.execute(f"SELECT DISTINCT OF FROM {table_name} ORDER BY OF")
            of_values = [row[0] for row in self.cursor.fetchall()]
            
            # Actualizar la lista de OF
            self.of_list = of_values
            self.of_selector.clear()
            
            if of_values:
                # Ordenar numéricamente las OF
                # Crear una lista de tuplas (of_original, of_numeric) para ordenar
                numeric_of_values = []
                for of_val in of_values:
                    # Intentar convertir a número para ordenamiento
                    try:
                        # Extraer solo dígitos si hay caracteres no numéricos
                        numeric_val = ''.join(c for c in str(of_val) if c.isdigit())
                        if numeric_val:
                            numeric_of_values.append((of_val, int(numeric_val)))
                        else:
                            # Si no hay dígitos, mantener el valor original al final
                            numeric_of_values.append((of_val, float('inf')))
                    except (ValueError, TypeError):
                        # Si no se puede convertir, mantener el valor original al final
                        numeric_of_values.append((of_val, float('inf')))
                
                # Ordenar por el valor numérico (segundo elemento de la tupla)
                numeric_of_values.sort(key=lambda x: x[1])
                
                # Extraer solo los valores originales ordenados
                sorted_of_values = [item[0] for item in numeric_of_values]
                
                # Agregar al selector
                self.of_selector.addItems([str(of) for of in sorted_of_values])
            else:
                QMessageBox.information(
                    self, 
                    "Sin datos", 
                    f"No se encontraron órdenes de fabricación en la tabla {table_name}."
                )
            
            self.production_data.disconnect()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al cargar las órdenes de fabricación: {str(e)}"
            )
            if self.production_data.connection:
                self.production_data.disconnect()
    
    def load_of_data(self, index=0):
        """Carga los datos de la OF seleccionada"""
        if index < 0 or self.of_selector.count() == 0:
            return
        
        # Obtener la OF seleccionada
        self.current_of = self.of_selector.currentText()
        
        try:
            if not self.production_data.connect():
                QMessageBox.critical(
                    self, 
                    "Error de conexión", 
                    "No se pudo conectar a la base de datos de producción."
                )
                return
            
            # Obtener las tablas disponibles
            tables = self.production_data.get_table_names()
            
            # Buscar la tabla 'bobina' o usar la primera disponible
            table_name = "bobina" if "bobina" in tables else tables[0] if tables else ""
            
            if not table_name:
                self.production_data.disconnect()
                return
            
            # Consultar los datos de la OF seleccionada
            self.cursor = self.production_data.connection.cursor()
            query = f"SELECT * FROM {table_name} WHERE OF = ? ORDER BY sec, bobina_num"
            self.cursor.execute(query, (self.current_of,))
            rows = self.cursor.fetchall()
            
            # Obtener los nombres de las columnas
            schema = self.production_data.get_table_schema(table_name)
            columns = [col[1] for col in schema]
            
            # Crear un diccionario para mapear nombres de columnas a índices
            column_indices = {col.lower(): idx for idx, col in enumerate(columns)}  # Convertir claves a minúsculas
            
            # Verificar si existen las columnas necesarias
            required_columns = ["OF", "bobina_num", "sec", "ancho", "peso"]
            missing_columns = [col for col in required_columns if col.lower() not in column_indices]  # Comparar en minúsculas
            
            if missing_columns:
                QMessageBox.warning(
                    self, 
                    "Columnas no encontradas", 
                    f"Faltan las siguientes columnas en la tabla {table_name}: {', '.join(missing_columns)}"
                )
                self.production_data.disconnect()
                return
            
            # Limpiar el contenido actual
            self.clear_content()
            
            # Si no hay datos, mostrar un mensaje
            if not rows:
                self.placeholder_label.setText(f"No hay datos para la OF {self.current_of}")
                self.placeholder_label.setVisible(True)
                self.production_data.disconnect()
                return
            
            # Ocultar el placeholder
            self.placeholder_label.setVisible(False)
            
            # Organizar los datos por sec
            sec_data = {}
            sec_values = set()
            
            for row in rows:
                sec = row[column_indices["sec".lower()]]
                sec_values.add(sec)
                
                if sec not in sec_data:
                    sec_data[sec] = []
                
                sec_data[sec].append({
                    "bobina_num": row[column_indices["bobina_num".lower()]],
                    "ancho": row[column_indices["ancho".lower()]],
                    "peso": row[column_indices["peso".lower()]]
                })
            
            # Crear un grid layout para los grupos de columnas
            grid_layout = QGridLayout()
            grid_layout.setSpacing(20)
            
            # Crear un grupo de columnas para cada sec
            col_index = 0
            for sec in sorted(sec_values):
                if sec not in sec_data:
                    continue
                
                # Crear un frame para este grupo
                group_frame = QFrame()
                group_frame.setObjectName(f"secGroup_{sec}")
                group_frame.setFrameShape(QFrame.StyledPanel)
                group_layout = QVBoxLayout(group_frame)
                
                # Título del grupo
                sec_title = QLabel(f"OF {self.current_of} / {sec}")
                sec_title.setAlignment(Qt.AlignCenter)
                sec_title.setStyleSheet("font-weight: bold; font-size: 12pt;")
                group_layout.addWidget(sec_title)
                
                # Tabla para este grupo
                table = QTableWidget()
                table.setColumnCount(3)  # ancho, bobina_num/sec, peso
                table.setHorizontalHeaderLabels(["Ancho", f"Bobina/Sec {sec}", "Peso"])
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                table.setEditTriggers(QTableWidget.NoEditTriggers)
                
                # Llenar la tabla con los datos
                table.setRowCount(len(sec_data[sec]))
                
                total_peso = 0
                
                for i, item in enumerate(sec_data[sec]):
                    # Ancho
                    ancho_item = QTableWidgetItem(str(item["ancho"]))
                    ancho_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(i, 0, ancho_item)
                    
                    # Bobina/Sec
                    bobina_item = QTableWidgetItem(f"{item['bobina_num']}/{sec}")
                    bobina_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(i, 1, bobina_item)
                    
                    # Peso
                    peso = item["peso"]
                    peso_item = QTableWidgetItem(str(peso))
                    peso_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(i, 2, peso_item)
                    
                    # Acumular el peso total
                    try:
                        total_peso += float(peso) if peso else 0
                    except (ValueError, TypeError):
                        pass
                
                group_layout.addWidget(table)
                
                # Mostrar el total de peso
                total_label = QLabel(f"Total Peso: {total_peso:.2f}")
                total_label.setAlignment(Qt.AlignRight)
                total_label.setStyleSheet("font-weight: bold;")
                group_layout.addWidget(total_label)
                
                # Agregar este grupo al grid layout
                grid_layout.addWidget(group_frame, 0, col_index)
                col_index += 1
            
            # Agregar el grid layout al contenido
            self.content_layout.addLayout(grid_layout)
            
            # Actualizar los botones de navegación
            self.update_navigation_buttons()
            
            self.production_data.disconnect()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al cargar los datos de la OF {self.current_of}: {str(e)}"
            )
            if self.production_data.connection:
                self.production_data.disconnect()
    
    def clear_content(self):
        """Limpia el contenido actual"""
        # Eliminar todos los widgets del layout excepto el placeholder
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Eliminar todos los widgets del sublayout
                while item.layout().count():
                    subitem = item.layout().takeAt(0)
                    if subitem.widget():
                        subitem.widget().deleteLater()
    
    def go_to_prev_of(self):
        """Navega a la OF anterior"""
        current_index = self.of_selector.currentIndex()
        if current_index > 0:
            self.of_selector.setCurrentIndex(current_index - 1)
    
    def go_to_next_of(self):
        """Navega a la OF siguiente"""
        current_index = self.of_selector.currentIndex()
        if current_index < self.of_selector.count() - 1:
            self.of_selector.setCurrentIndex(current_index + 1)
    
    def update_navigation_buttons(self):
        """Actualiza el estado de los botones de navegación"""
        current_index = self.of_selector.currentIndex()
        self.btn_prev.setEnabled(current_index > 0)
        self.btn_export.setEnabled(self.of_selector.count() > 0 and current_index >= 0)
        self.btn_next.setEnabled(current_index < self.of_selector.count() - 1)
    
    def export_data(self):
        """Exporta los datos de la OF seleccionada a un archivo de texto"""
        if not self.current_of:
            QMessageBox.warning(
                self, 
                "Exportación", 
                "Seleccione una Orden de Fabricación para exportar"
            )
            return
        
        try:
            # Conectar a la base de datos
            if not self.production_data.connect():
                QMessageBox.critical(
                    self, 
                    "Error de conexión", 
                    "No se pudo conectar a la base de datos de producción."
                )
                return
            
            # Obtener las tablas disponibles
            tables = self.production_data.get_table_names()
            
            # Buscar la tabla 'bobina' o usar la primera disponible
            table_name = "bobina" if "bobina" in tables else tables[0] if tables else ""
            
            if not table_name:
                self.production_data.disconnect()
                return
            
            # Consultar los datos de la OF seleccionada
            self.cursor = self.production_data.connection.cursor()
            query = f"SELECT * FROM {table_name} WHERE OF = ? ORDER BY sec, bobina_num"
            self.cursor.execute(query, (self.current_of,))
            rows = self.cursor.fetchall()
            
            # Obtener los nombres de las columnas
            schema = self.production_data.get_table_schema(table_name)
            columns = [col[1] for col in schema]
            
            # Convertir las filas a una lista de diccionarios para facilitar el manejo
            data = []
            for row in rows:
                record = {}
                for i, col in enumerate(columns):
                    record[col.lower()] = row[i]  # Usar claves en minúsculas
                data.append(record)
            
            # Llamar al exportador para guardar los datos
            from services.export_manager import ProductionExporter
            ProductionExporter.export_to_txt(self, self.current_of, data, self.production_data.connection)
            
            self.production_data.disconnect()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al exportar los datos: {str(e)}"
            )
            if self.production_data.connection:
                self.production_data.disconnect()
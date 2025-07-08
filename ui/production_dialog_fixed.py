#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de diálogos para producción

Contiene los diálogos utilizados en las operaciones CRUD de producción.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDialogButtonBox, QLabel, QComboBox, QDateEdit,
    QSpinBox, QDoubleSpinBox, QMessageBox, QDateTimeEdit,
    QWidget
)
from PySide6.QtCore import Qt, QDate, QDateTime
import json
import os
import logging


class ProductionRecordDialog(QDialog):
    """Diálogo para agregar o editar registros de producción"""
    
    def __init__(self, column_names, row_data=None, parent=None, is_copy_mode=False):
        """
        Inicializa el diálogo para agregar o editar registros de producción
        
        Args:
            column_names (list): Lista de nombres de columnas
            row_data (list, optional): Datos de la fila para edición. Si es None, se trata de un nuevo registro.
            parent (QWidget, optional): Widget padre
            is_copy_mode (bool, optional): Si es True, se está realizando una copia de un registro existente
        """
        super().__init__(parent)
        
        # Guardar el modo de copia
        self.is_copy_mode = is_copy_mode
        
        # Cargar datos de combos desde variablesCodProd.json
        self.combo_data = {
            "Productos": [],
            "Alistamiento": [],
            "Calidad": [],
            "Observaciones": []
        }
        self.codprod_to_nombre = {}  # Diccionario para mapear códigos a nombres de productos
        
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'variablesCodProd.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key in self.combo_data:
                    self.combo_data[key] = data.get(key, [])
                    
                # Poblar el diccionario de códigos a nombres para productos
                if 'Productos' in data:
                    for item in data['Productos']:
                        if 'codigo' in item and 'nombre' in item:
                            self.codprod_to_nombre[item['codigo']] = item['nombre']
                            
        except Exception as e:
            print(f"Error cargando variablesCodProd.json: {e}")
        
        # Configurar el diálogo
        if self.is_copy_mode:
            self.setWindowTitle("Copiar Registro")
        else:
            self.setWindowTitle("Editar Registro" if row_data else "Agregar Registro")
        
        # Configuración básica
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        
        # Guardar referencias
        self.column_names = column_names
        self.is_edit_mode = row_data is not None and not is_copy_mode
        self.field_widgets = {}  # Diccionario para mantener referencias a los widgets
        
        # Inicializar la interfaz
        self.init_ui(row_data)
    
    def init_ui(self, row_data):
        """
        Inicializa los componentes de la interfaz
        
        Args:
            row_data (list): Datos de la fila para edición
        """
        print(f"[DEBUG] init_ui - row_data: {row_data}")
        print(f"[DEBUG] init_ui - column_names: {self.column_names}")
        
        # Layout principal - diseño lo más básico posible
        main_layout = QVBoxLayout(self)
        
        # Formulario simple 
        form_layout = QFormLayout()
        main_layout.addLayout(form_layout)
        
        # Crear widgets para cada campo
        for col_idx, col_name in enumerate(self.column_names):
            col_name_lower = col_name.lower()
            widget = None
            
            if col_name_lower == "codprod":
                # Combo para Productos
                widget = QComboBox()
                widget.setEditable(True)
                widget.setInsertPolicy(QComboBox.NoInsert)
                for item in self.combo_data['Productos']:
                    widget.addItem(f"{item['codigo']} - {item['nombre']}", item['codigo'])
                if row_data and col_idx < len(row_data):
                    print(f"[DEBUG] Buscando código de producto: {row_data[col_idx]} (tipo: {type(row_data[col_idx])})")
                    idx = widget.findData(row_data[col_idx])
                    print(f"[DEBUG] Índice encontrado: {idx}")
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
                        print(f"[DEBUG] Índice establecido: {widget.currentIndex()}")
                    else:
                        print("[DEBUG] No se encontró el código de producto en la lista")
                self.codprod_combo = widget
                # Conectar la señal de cambio de selección para actualizar el peso
                widget.currentIndexChanged.connect(self.update_peso_from_codprod)
                
            elif col_name_lower == "descprod":
                widget = QLineEdit()
                self.descprod_widget = widget
                if row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")
            
            elif col_name_lower == "alistamiento":
                widget = QComboBox()
                widget.setEditable(True)
                widget.setInsertPolicy(QComboBox.NoInsert)
                for item in self.combo_data['Alistamiento']:
                    widget.addItem(f"{item['codigo']} - {item['nombre']}", item['codigo'])
                if row_data and col_idx < len(row_data):
                    idx = widget.findData(row_data[col_idx])
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
            
            elif col_name_lower == "calidad":
                widget = QComboBox()
                widget.setEditable(True)
                widget.setInsertPolicy(QComboBox.NoInsert)
                for item in self.combo_data['Calidad']:
                    widget.addItem(f"{item['codigo']} - {item['nombre']}", item['codigo'])
                if row_data and col_idx < len(row_data):
                    idx = widget.findData(row_data[col_idx])
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
            
            elif col_name_lower == "obs":
                widget = QComboBox()
                widget.setEditable(True)
                widget.setInsertPolicy(QComboBox.NoInsert)
                for item in self.combo_data['Observaciones']:
                    widget.addItem(f"{item['codigo']} - {item['nombre']}", item['codigo'])
                if row_data and col_idx < len(row_data):
                    idx = widget.findData(row_data[col_idx])
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
            
            elif col_name_lower == "observaciones":
                widget = QLineEdit()
                if row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")
            
            elif col_name_lower == "fecha":
                widget = QDateTimeEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd/MM/yyyy HH:mm")
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    print(f"[DEBUG] Procesando campo fecha: {row_data[col_idx]}")
                    try:
                        date_str = str(row_data[col_idx])
                        if ' ' in date_str and ':' in date_str:
                            date = QDateTime.fromString(date_str, "yyyy-MM-dd HH:mm")
                        else:
                            date = QDateTime.fromString(date_str, "yyyy-MM-dd")
                        
                        if date.isValid():
                            widget.setDateTime(date)
                            print(f"[DEBUG] Fecha establecida: {date.toString('dd/MM/yyyy HH:mm')}")
                        else:
                            widget.setDateTime(QDateTime.currentDateTime())
                    except Exception as e:
                        print(f"[DEBUG] Error al analizar la fecha {row_data[col_idx]}: {e}")
                        widget.setDateTime(QDateTime.currentDateTime())
                else:
                    widget.setDateTime(QDateTime.currentDateTime())
            
            elif "fecha" in col_name_lower and col_name_lower != "fecha":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd/MM/yyyy")
                
                # Solo establecer fecha si estamos editando un registro existente
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    try:
                        date_str = str(row_data[col_idx])
                        # Intentar diferentes formatos de fecha
                        for fmt in ["yyyy-MM-dd", "dd/MM/yyyy", "yyyy/MM/dd", "dd-MM-yyyy"]:
                            date = QDate.fromString(date_str, fmt)
                            if date.isValid():
                                widget.setDate(date)
                                break
                        else:
                            # Si no se pudo analizar, dejar en blanco
                            widget.setDate(QDate())
                    except Exception as e:
                        print(f"Error al analizar la fecha {date_str}: {e}")
                        widget.setDate(QDate())  # Fecha inválida = campo vacío
                else:
                    # Para nuevos registros, dejar el campo vacío
                    widget.setDate(QDate())  # Fecha inválida = campo vacío
            
            elif col_name_lower == "cantidadenprimeraudm":
                widget = QLineEdit()
                widget.setReadOnly(True)  # Hacer el campo de solo lectura
                if row_data and col_idx < len(row_data) and row_data[col_idx] is not None:
                    try:
                        # Formatear el valor a 2 decimales con coma como separador decimal
                        valor = float(row_data[col_idx])
                        widget.setText(f"{valor:.2f}".replace('.', ','))
                    except (ValueError, TypeError):
                        widget.setText("0,00")
                else:
                    widget.setText("0,00")
                self.cantidad_primera_udm_widget = widget
                
            elif col_name_lower in ["peso", "gramaje", "diametro", "ancho"]:
                widget = QDoubleSpinBox()
                widget.setRange(0, 9999.99)
                widget.setDecimals(2)
                widget.setSingleStep(0.1)
                widget.setSpecialValueText("0.00")
                if row_data and col_idx < len(row_data) and row_data[col_idx] is not None:
                    try:
                        widget.setValue(float(row_data[col_idx]))
                    except:
                        widget.setValue(0.0)
                else:
                    widget.setValue(0.0)
            
            elif col_name_lower == "turno":
                widget = QComboBox()
                widget.setEditable(True)
                widget.addItems(["A", "B", "C", "D"])
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    index = widget.findText(row_data[col_idx])
                    if index >= 0:
                        widget.setCurrentIndex(index)
            
            elif col_name_lower in ["of", "bobina_num", "sec"]:
                widget = QSpinBox()
                widget.setRange(0, 999999)
                widget.setSpecialValueText("0")
                widget.setValue(0)
                if row_data and col_idx < len(row_data) and row_data[col_idx] is not None:
                    try:
                        widget.setValue(int(row_data[col_idx]))
                    except:
                        pass
            
            elif col_name_lower == "producto":
                widget = QLineEdit()
                if row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")
            
            else:
                # Para todos los demás campos, usar QLineEdit como fallback
                widget = QLineEdit()
                if row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")
            
            # Guardar referencia al widget
            self.field_widgets[col_idx] = widget
            
            # Agregar al layout
            if widget:
                form_layout.addRow(f"{col_name}:", widget)
                print(f"[DEBUG] Campo agregado al formulario: {col_name}")
        
        # Agregar botones
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def validate_and_accept(self):
        """
        Valida los datos del formulario antes de aceptar
        """
        # Validaciones básicas si son necesarias
        self.accept()
    
    def update_peso_from_codprod(self, index):
        """
        Actualiza el campo CantidadEnPrimeraUdM con el peso del producto seleccionado
        Siempre actualiza el campo, incluso si ya tiene un valor
        """
        if not hasattr(self, 'cantidad_primera_udm_widget') or not hasattr(self, 'codprod_combo'):
            return
            
        # Obtener el código de producto seleccionado
        codigo = self.codprod_combo.currentData()
        if not codigo:
            # Si no hay código seleccionado, establecer valor por defecto
            self.cantidad_primera_udm_widget.setText("0,00")
            return
            
        # Buscar el producto en la lista
        for producto in self.combo_data['Productos']:
            if producto.get('codigo') == codigo:
                # Obtener el peso del producto (asumiendo que está en el campo 'peso')
                peso = producto.get('peso', 0)
                try:
                    # Convertir a float para manejar diferentes formatos de entrada
                    peso_float = float(peso)
                    # Formatear a 2 decimales con coma como separador decimal
                    peso_formateado = f"{peso_float:.2f}".replace('.', ',')
                    # Actualizar el campo CantidadEnPrimeraUdM
                    self.cantidad_primera_udm_widget.setText(peso_formateado)
                except (ValueError, TypeError):
                    # En caso de error, establecer valor por defecto
                    self.cantidad_primera_udm_widget.setText("0,00")
                return
        
        # Si no se encontró el producto, establecer valor por defecto
        self.cantidad_primera_udm_widget.setText("0,00")
    
    def get_row_data(self):
        """
        Obtiene los datos del formulario
        
        Returns:
            list: Lista con los valores de los campos
        """
        row_data = []
        
        for col_idx, col_name in enumerate(self.column_names):
            widget = self.field_widgets.get(col_idx)
            col_name_lower = col_name.lower()
            
            if not widget:
                row_data.append(None)
                continue
            
            # Obtener el valor según el tipo de widget
            if col_name_lower == "codprod" and hasattr(self, 'codprod_combo'):
                value = self.codprod_combo.currentData()
            elif col_name_lower == "descprod" and hasattr(self, 'descprod_widget'):
                codigo = self.codprod_combo.currentData() if hasattr(self, 'codprod_combo') else ""
                nombre = self.codprod_to_nombre.get(codigo, "")
                value = nombre.upper()
            elif isinstance(widget, QDateTimeEdit):
                value = widget.dateTime().toString("yyyy-MM-dd HH:mm")
            elif isinstance(widget, QDateEdit):
                value = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QDoubleSpinBox):
                value = widget.value()
            elif isinstance(widget, QSpinBox):
                value = widget.value()
            elif isinstance(widget, QComboBox):
                if widget.currentData():
                    value = widget.currentData()
                else:
                    text = widget.currentText()
                    if " - " in text:
                        value = text.split(" - ")[0].strip()
                    else:
                        value = text
            else:  # QLineEdit
                value = widget.text()
            
            row_data.append(value)
        
        return row_data

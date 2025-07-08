#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de diálogos para producción

Contiene los diálogos utilizados en las operaciones CRUD de producción.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDialogButtonBox, QLabel, QComboBox, QDateEdit,
    QSpinBox, QDoubleSpinBox, QMessageBox, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, QDate
import json
import os


class ProductionRecordDialog(QDialog):
    """Diálogo para agregar o editar registros de producción"""
    
    def __init__(self, column_names, row_data=None, parent=None):
        """
        Inicializa el diálogo para agregar o editar registros de producción
        
        Args:
            column_names (list): Lista de nombres de columnas
            row_data (list, optional): Datos de la fila para edición. Si es None, se trata de un nuevo registro.
            parent (QWidget, optional): Widget padre
        """
        super().__init__(parent)
        
        # Cargar datos de combos desde variablesCodProd.json
        self.combo_data = {
            "Productos": [],
            "Alistamiento": [],
            "Calidad": [],
            "Observaciones": []
        }
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'variablesCodProd.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key in self.combo_data:
                    self.combo_data[key] = data.get(key, [])
        except Exception as e:
            print(f"Error cargando variablesCodProd.json: {e}")
        
        # Configurar el diálogo
        self.setWindowTitle("Editar Registro" if row_data else "Agregar Registro")
        self.setMinimumWidth(450)
        
        # Guardar referencias
        self.column_names = column_names
        self.is_edit_mode = row_data is not None
        
        # Inicializar la interfaz
        self.init_ui(row_data)
    
    def init_ui(self, row_data):
        """
        Inicializa los componentes de la interfaz
        
        Args:
            row_data (list): Datos de la fila para edición
        """
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Agregar nota sobre persistencia
        note_label = QLabel(
            "<i>Nota: Los cambios se guardan en la base de datos.</i>"
        )
        note_label.setStyleSheet("color: #666;")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        # Crear scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Contenedor para el formulario
        scroll_content = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Crear campos de entrada para cada columna
        self.field_widgets = {}
        
        # Para autocompletar descripción del producto
        self.codprod_combo = None
        self.descprod_widget = None
        self.codprod_to_nombre = {item['codigo']: item['nombre'] for item in self.combo_data['Productos']}
        
        # Campos que deben ser de solo lectura (en minúsculas para comparación)
        read_only_fields = [
            'primeraunidaddemedida', 'lote', 'fechavalidezlote',
            'fechaelaboracion', 'nroot', 'codclie',
            'cuentacontable', 'metros'
        ]
        
        for col_idx, col_name in enumerate(self.column_names):
            col_name_lower = col_name.lower()
            is_read_only = col_name_lower in read_only_fields
            
            if col_name_lower == "codprod":
                # Combo para Productos
                widget = QComboBox()
                widget.setEditable(False)
                for item in self.combo_data['Productos']:
                    widget.addItem(f"{item['codigo']} - {item['nombre']}", item['codigo'])
                if row_data and col_idx < len(row_data):
                    idx = widget.findData(row_data[col_idx])
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
                self.codprod_combo = widget
            elif col_name_lower == "descprod":
                widget = QLineEdit()
                widget.setReadOnly(True)
                self.descprod_widget = widget
                if row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")
            elif col_name_lower == "alistamiento":
                widget = QComboBox()
                widget.setEditable(False)
                for item in self.combo_data['Alistamiento']:
                    widget.addItem(f"{item['codigo']} - {item['nombre']}", item['codigo'])
                if row_data and col_idx < len(row_data):
                    idx = widget.findData(row_data[col_idx])
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
            elif col_name_lower == "calidad":
                widget = QComboBox()
                widget.setEditable(False)
                for item in self.combo_data['Calidad']:
                    widget.addItem(f"{item['codigo']} - {item['nombre']}", item['codigo'])
                if row_data and col_idx < len(row_data):
                    idx = widget.findData(row_data[col_idx])
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
            elif col_name_lower == "observaciones":
                widget = QComboBox()
                widget.setEditable(False)
                for item in self.combo_data['Observaciones']:
                    widget.addItem(f"{item['codigo']} - {item['nombre']}", item['codigo'])
                if row_data and col_idx < len(row_data):
                    idx = widget.findData(row_data[col_idx])
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
            elif "fecha" in col_name_lower:
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                
                # Obtener fecha actual
                current_date = QDate.currentDate()
                
                # Establecer valor por defecto según el campo
                if "fechavalidezlote" in col_name_lower:
                    # Para fechaValidezLote: fecha actual + 5 años
                    default_date = current_date.addYears(5)
                    widget.setDate(default_date)
                    widget.setDisplayFormat("dd/MM/yyyy")
                else:
                    # Para otros campos de fecha (fechaElaboración, etc.): fecha actual
                    widget.setDate(current_date)
                    widget.setDisplayFormat("dd/MM/yyyy")
                
                # Si hay un valor existente, usarlo (útil en modo edición o copia)
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    try:
                        # Intentar parsear la fecha en formato YYYY-MM-DD
                        date_str = str(row_data[col_idx])
                        if date_str:
                            if "-" in date_str:
                                date_parts = date_str.split("-")
                                if len(date_parts) == 3:
                                    widget.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
                            elif "/" in date_str:
                                # Si el formato no es válido, intentar con formato DD/MM/YYYY
                                date_parts = date_str.split("/")
                                if len(date_parts) == 3:
                                    widget.setDate(QDate(int(date_parts[2]), int(date_parts[1]), int(date_parts[0])))
                    except Exception as e:
                        logging.warning(f"Error al analizar la fecha {row_data[col_idx]}: {e}")
                        # Mantener el valor por defecto si hay un error
            elif ("peso" in col_name_lower or "gramaje" in col_name_lower or 
                  "diametro" in col_name_lower or "ancho" in col_name_lower):
                widget = QDoubleSpinBox()
                widget.setRange(0, 9999.99)
                widget.setDecimals(2)
                widget.setSingleStep(0.1)
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    try:
                        widget.setValue(float(row_data[col_idx]))
                    except:
                        pass
            elif "turno" in col_name_lower:
                widget = QComboBox()
                widget.setEditable(False)
                widget.addItems(["A", "B", "C", "D"])
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    index = widget.findText(row_data[col_idx])
                    if index >= 0:
                        widget.setCurrentIndex(index)
            elif col_name_lower in ["of", "bobina_num", "sec"]:
                widget = QSpinBox()
                widget.setRange(0, 999999)
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    try:
                        widget.setValue(int(row_data[col_idx]))
                    except:
                        pass
            else:
                widget = QLineEdit()
                if row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")
            
            # Hacer el campo de solo lectura si corresponde
            if is_read_only and hasattr(widget, 'setEnabled'):
                widget.setEnabled(False)
                widget.setStyleSheet("background-color: #f0f0f0;")
            
            # Agregar el campo al formulario
            form_layout.addRow(f"{col_name}:", widget)
            self.field_widgets[col_name] = widget
        
        # Conectar autocompletado de descprod si corresponde
        if self.codprod_combo and self.descprod_widget:
            def update_descprod(idx):
                codigo = self.codprod_combo.itemData(idx)
                nombre = self.codprod_to_nombre.get(codigo, "")
                self.descprod_widget.setText(nombre)
            self.codprod_combo.currentIndexChanged.connect(update_descprod)
            # Inicializar descprod si hay valor seleccionado
            idx = self.codprod_combo.currentIndex()
            if idx >= 0:
                update_descprod(idx)
        
        # Agregar el formulario al contenedor del scroll
        scroll_content_layout.addLayout(form_layout)
        
        # Configurar el scroll area
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area, 1)  # El 1 hace que el scroll area tome todo el espacio disponible
        
        # Botones de aceptar/cancelar (fuera del scroll area)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def validate_and_accept(self):
        """
        Valida los datos del formulario antes de aceptar
        """
        # Validar campos obligatorios
        # Por ejemplo, asegurarse de que OF no esté vacío
        of_field = self.field_widgets.get("OF") or self.field_widgets.get("of")
        if of_field and isinstance(of_field, QSpinBox) and of_field.value() == 0:
            QMessageBox.warning(
                self,
                "Validación",
                "El campo OF es obligatorio y debe ser mayor que cero."
            )
            return
        
        # Si todo está bien, aceptar el diálogo
        self.accept()
    
    def get_row_data(self):
        """
        Obtiene los datos del formulario
        
        Returns:
            list: Lista con los valores de los campos
        """
        row_data = []
        
        for col_name in self.column_names:
            widget = self.field_widgets[col_name]
            col_name_lower = col_name.lower()
            
            # Obtener el valor según el tipo de widget
            if col_name_lower == "codprod" and isinstance(widget, QComboBox):
                # Para codprod, guardar solo el código (no el texto completo)
                value = widget.currentData()
            elif col_name_lower == "descprod" and self.descprod_widget:
                # Para descprod, guardar el nombre del producto en mayúsculas
                codigo = self.codprod_combo.currentData() if self.codprod_combo else ""
                nombre = self.codprod_to_nombre.get(codigo, "")
                value = nombre.upper()
            elif isinstance(widget, QDateEdit):
                value = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QDoubleSpinBox):
                value = str(widget.value())
            elif isinstance(widget, QSpinBox):
                value = str(widget.value())
            elif isinstance(widget, QComboBox):
                # Para otros combos, extraer solo el código (primeros caracteres antes del guion)
                text = widget.currentText()
                if " - " in text:
                    value = text.split(" - ")[0].strip()
                else:
                    value = text
            else:  # QLineEdit
                value = widget.text()
            
            row_data.append(value)
        
        return row_data

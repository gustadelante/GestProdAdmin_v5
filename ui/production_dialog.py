#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de diálogos para producción

Contiene los diálogos utilizados en las operaciones CRUD de producción.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDialogButtonBox, QLabel, QComboBox, QDateEdit,
    QSpinBox, QDoubleSpinBox, QMessageBox
)
from PySide6.QtCore import Qt, QDate


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
            "<i>Nota: Los cambios solo se mantienen en memoria y no se guardan en la base de datos.</i>"
        )
        note_label.setStyleSheet("color: #666;")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Crear campos de entrada para cada columna
        self.field_widgets = {}
        
        for col_idx, col_name in enumerate(self.column_names):
            # Determinar el tipo de campo según el nombre de la columna
            if "fecha" in col_name.lower():
                # Campo de fecha
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDate(QDate.currentDate())
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    try:
                        # Intentar convertir el texto a fecha
                        date_parts = row_data[col_idx].split("-")
                        if len(date_parts) == 3:
                            widget.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
                    except:
                        pass
            elif "peso" in col_name.lower() or "gramaje" in col_name.lower() or "diametro" in col_name.lower() or "ancho" in col_name.lower():
                # Campo numérico con decimales
                widget = QDoubleSpinBox()
                widget.setRange(0, 9999.99)
                widget.setDecimals(2)
                widget.setSingleStep(0.1)
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    try:
                        widget.setValue(float(row_data[col_idx]))
                    except:
                        pass
            elif "turno" in col_name.lower():
                # Selector de turno
                widget = QComboBox()
                widget.addItems(["Mañana", "Tarde", "Noche"])
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    index = widget.findText(row_data[col_idx])
                    if index >= 0:
                        widget.setCurrentIndex(index)
            elif "of" == col_name.lower() or "bobina_num" == col_name.lower() or "sec" == col_name.lower():
                # Campo numérico entero
                widget = QSpinBox()
                widget.setRange(0, 999999)
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    try:
                        widget.setValue(int(row_data[col_idx]))
                    except:
                        pass
            else:
                # Campo de texto por defecto
                widget = QLineEdit()
                if row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")
            
            form_layout.addRow(f"{col_name}:", widget)
            self.field_widgets[col_name] = widget
        
        layout.addLayout(form_layout)
        
        # Botones de aceptar/cancelar
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
            
            # Obtener el valor según el tipo de widget
            if isinstance(widget, QDateEdit):
                value = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QDoubleSpinBox):
                value = str(widget.value())
            elif isinstance(widget, QSpinBox):
                value = str(widget.value())
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
            else:  # QLineEdit
                value = widget.text()
            
            row_data.append(value)
        
        return row_data

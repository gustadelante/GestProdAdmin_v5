"""
Production Record Dialog Module.

This module contains the ProductionRecordDialog class for managing production records.
"""
import json
import os
import logging

class ProductionRecordDialog(QDialog):
    """Dialog for managing production records.
    
    Args:
        parent (QWidget, optional): Parent widget
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {
            "Productos": [],
            "Alistamiento": [],
            "Calidad": [],
            "Observaciones": []
        }
        
        try:
            with open('data.json', 'r') as f:
                self.data = json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content)
        
        form_layout = QFormLayout()
        
        widget = QComboBox()
        widget.setEditable(False)
        widget.addItem(f"{item['codigo']} - {item['nombre']}", item['codigo'])
        widget = QDateEdit()
        widget.setCalendarPopup(True)
        widget.setDisplayFormat("dd/MM/yyyy")

        # Obtener fecha actual
        current_date = QDate.currentDate()

        # Establecer valor por defecto según el campo
        if "fechavalidezlote" in col_name_lower:
            # Para fechaValidezLote: fecha actual + 5 años
            default_date = current_date.addYears(5)
            widget.setDate(default_date)
        else:
            # Para otros campos de fecha (fechaElaboración, etc.): fecha actual
            widget.setDate(current_date)

        # Si hay un valor existente y no está vacío, intentar usarlo
        if row_data and col_idx < len(row_data):
            date_value = str(row_data[col_idx]).strip()
            if date_value:
                parsed = False
                # Intentar formato YYYY-MM-DD
                if '-' in date_value:
                    date_parts = date_value.split("-")
                    if len(date_parts) == 3:
                        try:
                            year, month, day = map(int, date_parts)
                            widget.setDate(QDate(year, month, day))
                            parsed = True
                        except Exception as e:
                            logging.warning(f"Error al analizar la fecha (YYYY-MM-DD) {date_value}: {e}")
                # Intentar formato DD/MM/YYYY solo si no se parseó antes
                if not parsed and '/' in date_value:
                    date_parts = date_value.split("/")
                    if len(date_parts) == 3:
                        try:
                            day, month, year = map(int, date_parts)
                            widget.setDate(QDate(year, month, day))
                            parsed = True
                        except Exception as e:
                            logging.warning(f"Error al analizar la fecha (DD/MM/YYYY) {date_value}: {e}")
                # Si no se pudo parsear, mantener el valor por defecto


        # SOLO para widgets numéricos, no para QDateEdit
        # (esto debe ir en el bloque donde se crea el widget numérico, no aquí)

                
        # Configurar combo box para calificaciones
        widget = QComboBox()
        widget.setEditable(False)
        widget.addItems(["A", "B", "C", "D"])
        form_layout.addRow(f"{col_name}:", widget)
        
        
        scroll_content_layout.addLayout(form_layout)
        
        scroll_area.setWidget(scroll_content)
        
        layout.addWidget(button_box)
        
        # Initialize row_data as an empty list
        row_data = []
        
        # Get the value based on widget type
        if isinstance(widget, QComboBox):
            if widget.isEditable():
                value = widget.currentText()
                if " - " in value:
                    value = value.split(" - ")[0].strip()
            else:
                value = widget.currentData() or widget.currentText()
        elif isinstance(widget, QDateEdit):
            value = widget.date().toString("yyyy-MM-dd")
        elif hasattr(widget, 'value'):  # For QSpinBox, QDoubleSpinBox, etc.
            value = str(widget.value())
        else:  # Default to text for QLineEdit and others
            value = widget.text()
        
        # Convert to uppercase if it's a name field
        if col_name_lower in ['nombre', 'descripcion']:
            value = value.upper()
            
        row_data.append(value)
        
        return row_data

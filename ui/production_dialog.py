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
    QWidget, QScrollArea
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
        # Índices de columnas relevantes
        try:
            lower_names = [n.lower() for n in self.column_names]
        except Exception:
            lower_names = []
        self.idx_codprod = next((i for i, n in enumerate(lower_names) if n == 'codprod'), None)
        self.idx_producto = next((i for i, n in enumerate(lower_names) if n == 'producto'), None)
        self.idx_codigoDeProducto = next((i for i, n in enumerate(lower_names) if n == 'codigodeproducto'), None)
        
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
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Crear un área de desplazamiento
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget para contener el formulario
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        # Crear widgets para cada campo
        self.peso_widget = None
        self.cant1_widget = None  # CantidadEnPrimeraUdM
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
            
            elif col_name_lower == "fecha_validez_lote":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd/MM/yyyy")
                
                # Set default date to current date + 5 years for expiration date
                default_date = QDate.currentDate().addYears(5)
                widget.setDate(default_date)
                
                # If editing existing record, try to parse the date
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    date_value = str(row_data[col_idx]).strip()
                    if date_value:
                        parsed = False
                        # Try YYYY-MM-DD format
                        if '-' in date_value:
                            date_parts = date_value.split("-")
                            if len(date_parts) == 3:
                                try:
                                    year, month, day = map(int, date_parts)
                                    widget.setDate(QDate(year, month, day))
                                    parsed = True
                                except Exception:
                                    pass
                        # Try DD/MM/YYYY format if first attempt failed
                        if not parsed and '/' in date_value:
                            date_parts = date_value.split("/")
                            if len(date_parts) == 3:
                                try:
                                    day, month, year = map(int, date_parts)
                                    widget.setDate(QDate(year, month, day))
                                except Exception:
                                    pass
                
                self.field_widgets[col_idx] = widget
                form_layout.addRow(QLabel(col_name), widget)
                continue
            
            elif col_name_lower in ["fecha", "created_at"]:
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd/MM/yyyy")
                
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    try:
                        date_str = str(row_data[col_idx]).strip()
                        if not date_str:
                            widget.setDate(QDate.currentDate())
                            continue
                            
                        # Si la fecha ya está en formato dd/MM/yyyy, usarla directamente
                        if len(date_str) == 10 and date_str[2] == '/' and date_str[5] == '/':
                            day, month, year = map(int, date_str.split('/'))
                            widget.setDate(QDate(year, month, day))
                            continue
                            
                        # Intentar diferentes formatos de fecha
                        for fmt in ["yyyy-MM-dd HH:mm:ss", "yyyy-MM-dd", "dd/MM/yyyy"]:
                            date = QDate.fromString(date_str, fmt)
                            if date.isValid():
                                widget.setDate(date)
                                break
                        else:
                            # Si no se pudo parsear, usar fecha actual
                            widget.setDate(QDate.currentDate())
                    except Exception as e:
                        print(f"[DEBUG] Error al analizar la fecha {row_data[col_idx]}: {e}")
                        widget.setDate(QDate.currentDate())
                else:
                    # Si no hay valor, usar la fecha actual
                    widget.setDate(QDate.currentDate())
                
                # Asegurarse de que el widget se muestre correctamente
                widget.setStyleSheet("""
                    QDateEdit {
                        padding: 5px;
                        min-width: 100px;
                    }
                """)
            
            elif "fecha" in col_name_lower and col_name_lower not in ["fecha", "created_at"]:
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd/MM/yyyy")
                
                if row_data and col_idx < len(row_data) and row_data[col_idx]:
                    try:
                        date_str = str(row_data[col_idx]).strip()
                        if not date_str:
                            widget.setDate(QDate.currentDate())
                            continue
                            
                        # Intentar diferentes formatos de fecha
                        for fmt in ["yyyy-MM-dd HH:mm:ss", "yyyy-MM-dd", "dd/MM/yyyy"]:
                            date = QDate.fromString(date_str, fmt)
                            if date.isValid():
                                widget.setDate(date)
                                break
                        else:
                            # Si no se pudo parsear, usar fecha actual
                            widget.setDate(QDate.currentDate())
                    except Exception as e:
                        print(f"[DEBUG] Error al analizar la fecha {row_data[col_idx]}: {e}")
                        widget.setDate(QDate.currentDate())
                else:
                    widget.setDate(QDate.currentDate())
            
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
                if col_name_lower == "peso":
                    self.peso_widget = widget

            # --- Campos por requerimiento de alta ---
            elif col_name_lower == "tipo_mov":
                widget = QLineEdit()
                # Prefill solo en alta (no en edición ni copia)
                if not self.is_edit_mode and not self.is_copy_mode:
                    widget.setText("ALTA")
                elif row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")

            elif col_name_lower == "tipomovimiento":
                widget = QLineEdit()
                if not self.is_edit_mode and not self.is_copy_mode:
                    widget.setText("006")
                elif row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")

            elif col_name_lower == "deposito":
                widget = QLineEdit()
                if not self.is_edit_mode and not self.is_copy_mode:
                    widget.setText("01")
                elif row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")

            elif col_name_lower == "primeraundemedida":
                widget = QLineEdit()
                if not self.is_edit_mode and not self.is_copy_mode:
                    widget.setText("KG")
                elif row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")

            elif col_name_lower == "cantidadenprimeraudm":
                widget = QDoubleSpinBox()
                widget.setRange(0, 999999.99)
                widget.setDecimals(2)
                widget.setSingleStep(0.1)
                widget.setSpecialValueText("0.00")
                # Prefill con peso si es alta
                if not self.is_edit_mode and not self.is_copy_mode and self.peso_widget is not None:
                    widget.setValue(float(self.peso_widget.value()))
                elif row_data and col_idx < len(row_data) and row_data[col_idx] is not None:
                    try:
                        widget.setValue(float(row_data[col_idx]))
                    except:
                        widget.setValue(0.0)
                else:
                    widget.setValue(0.0)
                self.cant1_widget = widget

            elif col_name_lower == "codclie":
                widget = QLineEdit()
                if not self.is_edit_mode and not self.is_copy_mode:
                    widget.setText("000011")
                elif row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")

            elif col_name_lower == "cuentacontable":
                widget = QLineEdit()
                if not self.is_edit_mode and not self.is_copy_mode:
                    widget.setText("1401010000")
                elif row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")

            elif col_name_lower == "segundaundemedida":
                widget = QLineEdit()
                if not self.is_edit_mode and not self.is_copy_mode:
                    widget.setText("UN")
                elif row_data and col_idx < len(row_data):
                    widget.setText(str(row_data[col_idx]) if row_data[col_idx] is not None else "")

            elif col_name_lower == "cantidadensegunda":
                widget = QSpinBox()
                widget.setRange(0, 999999)
                if not self.is_edit_mode and not self.is_copy_mode:
                    widget.setValue(1)
                elif row_data and col_idx < len(row_data) and row_data[col_idx] is not None:
                    try:
                        widget.setValue(int(row_data[col_idx]))
                    except:
                        widget.setValue(0)
            
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

            # Conectar señales para blanquear codigoDeProducto y actualizar producto
            try:
                if col_name_lower in ["ancho", "gramaje", "diametro"] and hasattr(widget, 'valueChanged'):
                    widget.valueChanged.connect(self._on_trigger_field_changed)
                elif col_name_lower in ["codprod", "alistamiento", "calidad", "obs"] and isinstance(widget, QComboBox):
                    widget.currentIndexChanged.connect(self._on_trigger_field_changed)
                    if widget.isEditable():
                        widget.editTextChanged.connect(self._on_trigger_field_changed)
            except Exception as e:
                logging.error(f"Error conectando señales para {col_name}: {e}")
        
        # Configurar el scroll area con el formulario
        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area, 1)  # El 1 hace que el scroll area tome todo el espacio disponible
        
        # Agregar botones al final (fuera del scroll area)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        # Sincronizar CantidadEnPrimeraUdM con Peso si ambos widgets existen
        try:
            if self.peso_widget is not None and self.cant1_widget is not None:
                def _sync_cantidad_desde_peso(val):
                    try:
                        self.cant1_widget.setValue(float(val))
                    except Exception:
                        pass
                self.peso_widget.valueChanged.connect(_sync_cantidad_desde_peso)
        except Exception as e:
            logging.error(f"Error configurando sincronización peso -> CantidadEnPrimeraUdM: {e}")

    def _on_trigger_field_changed(self, *args, **kwargs):
        """Se dispara cuando cambian campos que obligan a blanquear codigoDeProducto y recalcular producto."""
        try:
            # Blanquear codigoDeProducto si existe
            if self.idx_codigoDeProducto is not None and self.idx_codigoDeProducto in self.field_widgets:
                w = self.field_widgets[self.idx_codigoDeProducto]
                if isinstance(w, QLineEdit):
                    w.setText("")
                elif isinstance(w, QComboBox):
                    # Por si en alguna tabla es combo
                    if w.isEditable():
                        w.clearEditText()
                    w.setCurrentIndex(-1)

            # Actualizar 'producto' con el segundo carácter de 'codprod'
            if self.idx_producto is not None and self.idx_producto in self.field_widgets:
                producto_char = ""
                # Obtener código desde el combo de codprod si está disponible
                codigo = ""
                if hasattr(self, 'codprod_combo') and isinstance(self.codprod_combo, QComboBox):
                    codigo = self.codprod_combo.currentData() or ""
                    if not codigo:
                        text = self.codprod_combo.currentText() or ""
                        codigo = text.split(" - ")[0].strip() if text else ""
                elif self.idx_codprod is not None and self.idx_codprod in self.field_widgets:
                    wcod = self.field_widgets[self.idx_codprod]
                    if isinstance(wcod, QLineEdit):
                        codigo = (wcod.text() or "").strip()
                if len(codigo) >= 2:
                    producto_char = codigo[1]
                # Establecer en el widget de producto (asumido QLineEdit)
                wprod = self.field_widgets[self.idx_producto]
                if isinstance(wprod, QLineEdit):
                    wprod.setText(producto_char)
        except Exception as e:
            logging.error(f"Error en _on_trigger_field_changed: {e}")
    
    def validate_and_accept(self):
        """
        Valida los datos del formulario antes de aceptar
        """
        # Validaciones básicas si son necesarias
        self.accept()
    
    def get_row_data(self):
        """
        Obtiene los datos del formulario
        
        Returns:
            list: Lista con los valores de los campos en el orden de las columnas
        """
        # Inicializar con None para todas las columnas
        row_data = [None] * len(self.column_names)
        
        for col_idx, col_name in enumerate(self.column_names):
            widget = self.field_widgets.get(col_idx)
            if not widget:
                continue
                
            col_name_lower = col_name.lower()
            value = None
            
            # Obtener el valor según el tipo de widget
            if col_name_lower == "codprod" and hasattr(self, 'codprod_combo'):
                value = self.codprod_combo.currentData()
            elif col_name_lower == "descprod" and hasattr(self, 'descprod_widget'):
                codigo = self.codprod_combo.currentData() if hasattr(self, 'codprod_combo') else ""
                nombre = self.codprod_to_nombre.get(codigo, "")
                value = nombre.upper()
            elif isinstance(widget, QDateEdit):
                # Para todos los campos de fecha (incluyendo fecha, created_at, etc.)
                # Usar el formato dd/MM/yyyy para guardar
                value = widget.date().toString("dd/MM/yyyy")
            elif isinstance(widget, QDateTimeEdit):
                # Por si acaso hay algún campo de fecha/hora que necesite manejarse de otra manera
                value = widget.dateTime().toString("dd/MM/yyyy HH:mm")
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
            
            # Asignar el valor en la posición correcta
            if col_idx < len(row_data):
                row_data[col_idx] = value
        
        return row_data

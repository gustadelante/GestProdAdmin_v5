#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de producción

Contiene la implementación de las vistas relacionadas con la producción.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QTableView, QFrame, QSizePolicy, QSpacerItem,
    QLineEdit, QComboBox, QHeaderView, QMessageBox, QDialog, QStyle
)
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon

import os
from ui.production_models import ProductionTableModel, ProductionSortFilterProxyModel
from ui.icons import ADD_ICON, EDIT_ICON, DELETE_ICON, CLEAR_ICON, COPY_ICON, svg_to_icon


class ProductionControlWidget(QWidget):
    """Widget para el control de producción"""

    # ...

    def delete_selected_rows(self):
        """Elimina las filas seleccionadas"""
        selected_rows = self.production_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(
                self,
                "Sin Selección",
                "Por favor, seleccione al menos un registro para eliminar."
            )
            return
        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar {len(selected_rows)} registro(s)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            # Convertir índices del modelo proxy al modelo fuente y ordenarlos en orden descendente
            source_indices = [self.proxy_model.mapToSource(index).row() for index in selected_rows]
            source_indices.sort(reverse=True)
            # Eliminar filas
            for row_index in source_indices:
                self.table_model.delete_row(row_index)
            # Refrescar la grilla
            self.table_model.load_data(self.table_model.table_name)
            QMessageBox.information(
                self,
                "Registros Eliminados",
                f"{len(selected_rows)} registro(s) han sido eliminados correctamente de la base de datos."
            )
            self.btn_edit_row.setEnabled(False)
            self.btn_delete_row.setEnabled(False)

    """Widget para el control de producción"""

    # ...

    def show_edit_row_dialog(self):
        """Muestra el diálogo para editar una fila seleccionada"""
        # Obtener la fila seleccionada
        selected_rows = self.production_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(
                self,
                "Sin Selección",
                "Por favor, seleccione un registro para editar."
            )
            return
        # Solo permitir editar una fila a la vez
        if len(selected_rows) > 1:
            QMessageBox.warning(
                self,
                "Múltiples Selecciones",
                "Por favor, seleccione solo un registro para editar a la vez."
            )
            return
        # Obtener el índice de la fila seleccionada
        proxy_index = selected_rows[0]
        row_index = self.proxy_model.mapToSource(proxy_index).row()
        row_data = self.table_model.data_rows[row_index]
        # Importar aquí para evitar dependencias circulares
        from ui.production_dialog import ProductionRecordDialog
        # Crear diálogo de edición
        dialog = ProductionRecordDialog(self.table_model.column_names, row_data.copy(), self)
        # Mostrar diálogo
        if dialog.exec() == QDialog.Accepted:
            # Obtener datos del formulario
            new_row_data = dialog.get_row_data()
            # Actualizar fila en el modelo y base de datos
            updated = self.table_model.update_row(row_index, new_row_data)
            if updated:
                # Refrescar datos de la grilla (reload)
                self.table_model.load_data(self.table_model.table_name)
                QMessageBox.information(
                    self,
                    "Registro Actualizado",
                    "El registro ha sido actualizado correctamente en la base de datos."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "No se pudo actualizar el registro."
                )

    """Widget para el control de producción"""
    
    def __init__(self, parent=None):
        """
        Inicializa el widget de control de producción
        
        Args:
            parent (QWidget, optional): Widget padre
        """
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Inicializa los componentes de la interfaz"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título
        """ title_label = QLabel("Control de Producción")
        title_label.setObjectName("controlTitle")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label) """
        
        # Descripción
        """ description_label = QLabel(
            "Esta sección le permite gestionar y monitorear el control de producción."
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 11pt; margin-bottom: 20px;")
        main_layout.addWidget(description_label)
         """
        # Contenido principal
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        
        # Controles de filtrado
        filter_layout = QHBoxLayout()
        
        # Selector de tabla (oculto, pero mantenido para funcionalidad)
        self.table_selector = QComboBox()
        self.table_selector.setMinimumWidth(200)
        self.table_selector.currentIndexChanged.connect(self.load_table_data)
        self.table_selector.setVisible(False)  # Ocultar el selector
        
        # No agregamos el label ni el selector al layout
        # filter_layout.addWidget(QLabel("Tabla:"))
        # filter_layout.addWidget(self.table_selector)
        
        # filter_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum))
        
        # Filtro por OF (exclusivamente)
        filter_layout.addWidget(QLabel("Filtrar por OF (Orden de Fabricación):"))
        self.of_filter = QLineEdit()
        self.of_filter.setPlaceholderText("Ingrese número de OF para filtrar...")
        self.of_filter.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.of_filter)
        
        # Botón para limpiar filtro con icono estándar de PySide6
        self.btn_clear_filter = QPushButton()
        self.btn_clear_filter.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        self.btn_clear_filter.setToolTip("Limpiar filtro")
        self.btn_clear_filter.setObjectName("btnIconClear")
        self.btn_clear_filter.clicked.connect(self.clear_filter)
        filter_layout.addWidget(self.btn_clear_filter)
        
        # Agregar espacio flexible
        filter_layout.addStretch()
        
        # Botones CRUD para la tabla
        crud_layout = QHBoxLayout()
        
        # Botón para agregar fila con icono estándar de PySide6
        self.btn_add_row = QPushButton()
        self.btn_add_row.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        self.btn_add_row.setToolTip("Agregar registro")
        self.btn_add_row.setObjectName("btnAddRow")
        self.btn_add_row.clicked.connect(self.show_add_row_dialog)
        crud_layout.addWidget(self.btn_add_row)
        
        # Botón para copiar fila con icono SVG personalizado
        self.btn_copy_row = QPushButton()
        #self.btn_copy_row.setIcon(svg_to_icon(COPY_ICON))
        self.btn_copy_row.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.btn_copy_row.setToolTip("Copiar registro seleccionado")
        self.btn_copy_row.setObjectName("btnCopyRow")
        self.btn_copy_row.clicked.connect(self.show_copy_row_dialog)
        crud_layout.addWidget(self.btn_copy_row)
        
        # Botón para editar fila con icono estándar de PySide6
        self.btn_edit_row = QPushButton()
        self.btn_edit_row.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.btn_edit_row.setToolTip("Editar registro seleccionado")
        self.btn_edit_row.setObjectName("btnEditRow")
        self.btn_edit_row.clicked.connect(self.show_edit_row_dialog)
        crud_layout.addWidget(self.btn_edit_row)
        
        # Botón para eliminar fila con icono estándar de PySide6
        self.btn_delete_row = QPushButton()
        self.btn_delete_row.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.btn_delete_row.setToolTip("Eliminar registros seleccionados")
        self.btn_delete_row.setObjectName("btnDeleteRow")
        self.btn_delete_row.clicked.connect(self.delete_selected_rows)
        crud_layout.addWidget(self.btn_delete_row)

        filter_layout.addLayout(crud_layout)
        
        content_layout.addLayout(filter_layout)

        # --- ComboBox de Calidad y Observaciones y botón Procesar ---
        from ui.production_combo_data import load_combo_data
        combo_data = load_combo_data()

        calidad_obs_layout = QHBoxLayout()
        calidad_obs_layout.setSpacing(10)
        calidad_obs_layout.setContentsMargins(0, 0, 0, 0)

        # Espacio flexible para empujar calidad y su combo a la derecha
        calidad_obs_layout.addStretch(1)
        label_calidad = QLabel("Calidad:")
        label_calidad.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        calidad_obs_layout.addWidget(label_calidad)
        self.combo_calidad = QComboBox()
        self.combo_calidad.setObjectName("comboCalidad")
        self.combo_calidad.setEditable(True)
        self.combo_calidad.setInsertPolicy(QComboBox.NoInsert)
        max_calidad_width = 0
        for item in combo_data["Calidad"]:
            text = f"{item['codigo']} - {item['nombre']}"
            self.combo_calidad.addItem(text, item['codigo'])
            width = self.combo_calidad.fontMetrics().boundingRect(text).width()
            if width > max_calidad_width:
                max_calidad_width = width
        exact_calidad_width = max_calidad_width + 15
        self.combo_calidad.setMinimumWidth(exact_calidad_width)
        self.combo_calidad.setMaximumWidth(exact_calidad_width)
        self.combo_calidad.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        calidad_obs_layout.addWidget(self.combo_calidad)

        # Espacio pequeño entre combos
        calidad_obs_layout.addSpacing(15)

        label_obs = QLabel("Obs:")
        label_obs.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        calidad_obs_layout.addWidget(label_obs)

        self.combo_obs = QComboBox()
        self.combo_obs.setObjectName("comboObs")
        self.combo_obs.setEditable(True)
        self.combo_obs.setInsertPolicy(QComboBox.NoInsert)
        max_obs_width = 0
        for item in combo_data["Observaciones"]:
            text = f"{item['codigo']} - {item['nombre']}"
            self.combo_obs.addItem(text, item['codigo'])
            width = self.combo_obs.fontMetrics().boundingRect(text).width()
            if width > max_obs_width:
                max_obs_width = width
        exact_obs_width = max_obs_width + 15
        self.combo_obs.setMinimumWidth(exact_obs_width)
        self.combo_obs.setMaximumWidth(exact_obs_width)
        self.combo_obs.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        calidad_obs_layout.addWidget(self.combo_obs)

        # El botón Procesar será proporcional al combo más ancho
        btn_width = max(exact_calidad_width, exact_obs_width)
        self.btn_procesar = QPushButton("Cambiar")
        self.btn_procesar.setObjectName("btnProcesar")
        self.btn_procesar.setToolTip("Cambia calidad y obs para todos los registros que se visualizan en la grilla")
        self.btn_procesar.setMinimumWidth(btn_width)
        self.btn_procesar.setMaximumWidth(btn_width)
        self.btn_procesar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # Slot a definir por el usuario
        self.btn_procesar.clicked.connect(self.cambiar_calidad_obs)
        calidad_obs_layout.addWidget(self.btn_procesar)

        # --- FIN combos y botón ---

        content_layout.addLayout(calidad_obs_layout)
        
        # Tabla de datos de producción
        self.production_table = QTableView()
        self.production_table.setObjectName("productionTable")
        self.production_table.setAlternatingRowColors(False)
        self.production_table.setSelectionBehavior(QTableView.SelectRows)
        self.production_table.setSelectionMode(QTableView.MultiSelection)  # Permitir selección múltiple
        self.production_table.setSortingEnabled(True)
        self.production_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.production_table.horizontalHeader().setStretchLastSection(True)
        
        # Ocultar los números de fila (vertical header)
        self.production_table.verticalHeader().setVisible(False)
        
        # Modelo de datos
        self.table_model = ProductionTableModel(self)
        
        # Modelo proxy para ordenamiento y filtrado
        self.proxy_model = ProductionSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.table_model)
        self.production_table.setModel(self.proxy_model)
        
        # Conectar señal de clic para manejar la selección de filas
        self.production_table.clicked.connect(self.handle_table_click)
        
        content_layout.addWidget(self.production_table)
        
        main_layout.addWidget(content_frame)
        
        # Cargar tablas disponibles
        self.load_available_tables()
    
    def cambiar_calidad_obs(self):
        """
        Cambia calidad y obs para todos los registros visualizados y actualiza codigoDeProducto.
        """
        # Obtener valores seleccionados
        calidad_text = self.combo_calidad.currentText().strip()
        obs_text = self.combo_obs.currentText().strip()
        calidad_val = calidad_text.split(' ')[0] if calidad_text else ''
        obs_val = obs_text.split(' ')[0] if obs_text else ''

        # Indices de columnas
        try:
            col_calidad = self.table_model.column_names.index('calidad')
        except ValueError:
            QMessageBox.warning(self, 'Error', 'No se encontró la columna "calidad".')
            return
        try:
            col_obs = self.table_model.column_names.index('obs')
        except ValueError:
            QMessageBox.warning(self, 'Error', 'No se encontró la columna "obs".')
            return
        try:
            col_codprod = self.table_model.column_names.index('codigoDeProducto')
        except ValueError:
            QMessageBox.warning(self, 'Error', 'No se encontró la columna "codigoDeProducto".')
            return

        # Recorrer solo los registros visualizados (filtrados)
        for proxy_row in range(self.proxy_model.rowCount()):
            src_row = self.proxy_model.mapToSource(self.proxy_model.index(proxy_row, 0)).row()
            row_data = self.table_model.data_rows[src_row]
            # Cambiar calidad y obs
            row_data[col_calidad] = calidad_val
            row_data[col_obs] = obs_val
            # Modificar codigoDeProducto
            codprod = row_data[col_codprod]
            if isinstance(codprod, str) and len(codprod) >= 8 and len(calidad_val) == 2 and len(obs_val) == 2:
                codprod_new = (
                    codprod[:4] + calidad_val + obs_val + codprod[8:]
                )
                row_data[col_codprod] = codprod_new
            # Actualizar el modelo
            ok = self.table_model.update_row(src_row, row_data)
            if not ok:
                bobina = row_data[self.table_model.column_names.index('bobina_num')] if 'bobina_num' in self.table_model.column_names else '?'
                sec = row_data[self.table_model.column_names.index('sec')] if 'sec' in self.table_model.column_names else '?'
                QMessageBox.critical(self, 'Error al guardar', f'No se pudo actualizar la fila Bobina: {bobina} / Sec: {sec}.\nRevise la base de datos o los permisos.')

        self.table_model.layoutChanged.emit()
        self.production_table.viewport().update()
        QMessageBox.information(self, 'Cambios aplicados', 'Se cambiaron calidad y obs para todos los registros visualizados.')

    def load_available_tables(self):
        """Carga las tablas disponibles en la base de datos"""
        try:
            # Crear una instancia temporal para obtener las tablas
            from database.production_models import ProductionData
            import os
            
            from database.db_helper import get_db_path
            db_path = get_db_path()
            prod_data = ProductionData(db_path)
            
            if prod_data.connect():
                tables = prod_data.get_table_names()
                prod_data.disconnect()
                
                # Actualizar el selector de tablas
                self.table_selector.clear()
                if tables:
                    self.table_selector.addItems(tables)
                    
                    # Buscar la tabla 'bobina' y seleccionarla automáticamente
                    bobina_index = self.table_selector.findText("bobina")
                    if bobina_index >= 0:
                        self.table_selector.setCurrentIndex(bobina_index)
                    # Si no existe la tabla bobina, cargar la primera tabla disponible
                    else:
                        self.load_table_data()
                else:
                    QMessageBox.warning(
                        self, 
                        "Sin tablas", 
                        "No se encontraron tablas en la base de datos de producción."
                    )
            else:
                QMessageBox.critical(
                    self, 
                    "Error de conexión", 
                    "No se pudo conectar a la base de datos de producción."
                )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al cargar las tablas disponibles: {str(e)}"
            )
    
    def load_table_data(self, index=0):
        """Carga los datos de la tabla seleccionada"""
        if self.table_selector.count() > 0:
            table_name = self.table_selector.currentText()
            filter_text = self.of_filter.text()
            
            # Cargar datos en el modelo
            success = self.table_model.load_data(table_name, filter_text if filter_text else None)
            
            if success:
                # No es necesario ocultar la columna ID ya que no hay columna de selección
                # La columna 0 ahora es la columna OF
                pass
            else:
                QMessageBox.warning(
                    self, 
                    "Error de carga", 
                    f"No se pudieron cargar los datos de la tabla {table_name}."
                )
    
    def apply_filter(self):
        """Aplica el filtro por OF"""
        filter_text = self.of_filter.text()
        self.proxy_model.set_of_filter(filter_text)
    
    def clear_filter(self):
        """Limpia el filtro por OF"""
        self.of_filter.clear()
        self.proxy_model.set_of_filter("")
    
    def handle_table_click(self, index):
        """Maneja el clic en la tabla para la selección de filas
        
        Args:
            index (QModelIndex): Índice del modelo donde se hizo clic
        """
        # La selección ahora se maneja automáticamente por el QTableView
        # ya que está configurado con QTableView.SelectRows y QTableView.MultiSelection
        # Habilitar/deshabilitar botones según la selección
        selected_rows = self.production_table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        single_selection = len(selected_rows) == 1
        
        self.btn_edit_row.setEnabled(has_selection and single_selection)
        self.btn_copy_row.setEnabled(has_selection and single_selection)
        self.btn_delete_row.setEnabled(has_selection)
    
    def show_copy_row_dialog(self):
        """Muestra el diálogo para copiar un registro existente"""
        # Obtener la fila seleccionada
        selected_rows = self.production_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(
                self,
                "Sin Selección",
                "Por favor, seleccione un registro para copiar."
            )
            return
        # Solo permitir copiar una fila a la vez
        if len(selected_rows) > 1:
            QMessageBox.warning(
                self,
                "Múltiples Selecciones",
                "Por favor, seleccione solo un registro para copiar a la vez."
            )
            return
            
        # Obtener los datos del registro seleccionado
        proxy_index = selected_rows[0]
        row_index = self.proxy_model.mapToSource(proxy_index).row()
        row_data = self.table_model.data_rows[row_index]
        
        # Crear diálogo con los datos del registro seleccionado
        from ui.production_dialog import ProductionRecordDialog
        dialog = ProductionRecordDialog(self.table_model.column_names, row_data.copy(), self, is_copy_mode=True)
        
        # Mostrar diálogo
        if dialog.exec() == QDialog.Accepted:
            # Obtener datos del formulario
            new_row_data = dialog.get_row_data()
            
            # Obtener índices de las columnas
            column_names = [name.lower() for name in self.table_model.column_names]
            try:
                bobina_idx = column_names.index('bobina_num')
                sec_idx = column_names.index('sec')
                
                # Obtener valores originales
                original_bobina = str(row_data[bobina_idx]) if len(row_data) > bobina_idx else ''
                original_sec = str(row_data[sec_idx]) if len(row_data) > sec_idx else ''
                
                # Obtener nuevos valores
                new_bobina = str(new_row_data[bobina_idx]) if len(new_row_data) > bobina_idx else ''
                new_sec = str(new_row_data[sec_idx]) if len(new_row_data) > sec_idx else ''
            except ValueError:
                # Si no se encuentran las columnas, continuar sin validación
                original_bobina = ''
                original_sec = ''
                new_bobina = ''
                new_sec = ''
            
            if original_bobina == new_bobina and original_sec == new_sec:
                QMessageBox.warning(
                    self,
                    "Datos Inválidos",
                    "Debe modificar al menos el número de bobina o la secuencia para crear una copia."
                )
                return
                
            # Verificar si ya existe un registro con el mismo bobina_num y sec
            if self._check_duplicate_bobina(new_row_data):
                QMessageBox.warning(
                    self,
                    "Registro Duplicado",
                    "Ya existe un registro con el mismo número de bobina y secuencia."
                )
                return
            
            # Agregar fila al modelo
            source_model = self.proxy_model.sourceModel()
            row_index = source_model.add_row(new_row_data)
            
            # Recargar los datos en la tabla
            current_table = self.table_selector.currentText()
            if current_table:
                self.table_model.load_data(current_table)
            
            # Informar al usuario
            QMessageBox.information(
                self,
                "Registro Copiado",
                "El registro ha sido copiado correctamente en la base de datos."
            )
    
    def _check_duplicate_bobina(self, row_data):
        """Verifica si ya existe un registro con el mismo bobina_num y sec"""
        try:
            # Obtener índices de las columnas
            column_names = [name.lower() for name in self.table_model.column_names]
            try:
                bobina_idx = column_names.index('bobina_num')
                sec_idx = column_names.index('sec')
                
                # Obtener valores del nuevo registro
                bobina_num = str(row_data[bobina_idx]) if len(row_data) > bobina_idx else None
                sec = str(row_data[sec_idx]) if len(row_data) > sec_idx else None
                
                if bobina_num is None or sec is None:
                    return False
                    
                # Buscar en los datos existentes
                for row in self.table_model.data_rows:
                    row_bobina = str(row[bobina_idx]) if len(row) > bobina_idx else ''
                    row_sec = str(row[sec_idx]) if len(row) > sec_idx else ''
                    
                    if row_bobina == str(bobina_num) and row_sec == str(sec):
                        return True
                return False
            except ValueError:
                # Si no se encuentran las columnas, no hay duplicados
                return False
        except Exception as e:
            print(f"Error verificando duplicados: {e}")
            return False
    
    def show_add_row_dialog(self):
        """Muestra el diálogo para agregar una nueva fila"""
        from ui.production_dialog import ProductionRecordDialog
        
        # Crear diálogo con campos apropiados para cada tipo de dato
        dialog = ProductionRecordDialog(self.table_model.column_names, None, self, is_copy_mode=False)
        
        # Mostrar diálogo
        if dialog.exec() == QDialog.Accepted:
            # Obtener datos del formulario
            row_data = dialog.get_row_data()
            
            # Agregar fila al modelo
            source_model = self.proxy_model.sourceModel()
            row_index = source_model.add_row(row_data)
            
            # Actualizar campos vacíos según las reglas
            if source_model.production_data.connect():
                try:
                    # Actualizar campos vacíos
                    source_model.production_data.update_empty_bobinas_fields()
                    
                    # Forzar una recarga completa de los datos
                    current_table = self.table_selector.currentText()
                    if current_table:
                        # Guardar la posición de desplazamiento actual
                        scroll_pos = self.production_table.verticalScrollBar().value()
                        
                        # Recargar los datos
                        self.table_model.load_data(current_table)
                        
                        # Restaurar la posición de desplazamiento
                        QTimer.singleShot(0, lambda: self.production_table.verticalScrollBar().setValue(scroll_pos))
                        
                except Exception as e:
                    logging.error(f"Error al actualizar campos vacíos: {str(e)}", exc_info=True)
                finally:
                    source_model.production_data.disconnect()
            
            # Informar al usuario
            QMessageBox.information(
                self,
                "Registro Agregado",
                "El registro ha sido agregado correctamente en la base de datos."
            )


class ProductionOFControlWidget(QWidget):
    """Widget para el control de órdenes de fabricación"""
    
    def __init__(self, parent=None):
        """
        Inicializa el widget de control de órdenes de fabricación
        
        Args:
            parent (QWidget, optional): Widget padre
        """
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Inicializa los componentes de la interfaz"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título
        """ title_label = QLabel("Control de Órdenes de Fabricación")
        title_label.setObjectName("ofControlTitle")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
         """
        # Descripción
        """ description_label = QLabel(
            "Esta sección le permite gestionar y monitorear las órdenes de fabricación."
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 11pt; margin-bottom: 20px;")
        main_layout.addWidget(description_label) """
        
        # Contenido principal (a implementar según requerimientos específicos)
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        
        # Placeholder para contenido futuro
        placeholder_label = QLabel("Contenido del Control de Órdenes de Fabricación (a implementar)")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("font-size: 14pt; color: gray;")
        content_layout.addWidget(placeholder_label)
        
        main_layout.addWidget(content_frame)
        
        # Espaciador para empujar todo hacia arriba
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
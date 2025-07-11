#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de modelos de UI para producción

Contiene los modelos de datos para las vistas de producción.
"""

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication
from typing import List, Any, Optional
import os

from database.production_models import ProductionData


class ProductionTableModel(QAbstractTableModel):
    """Modelo de tabla para datos de producción"""
    
    def __init__(self, parent=None):
        """
        Inicializa el modelo de tabla para datos de producción
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.column_names = []
        self.data_rows = []
        from database.db_helper import get_db_path
        self.db_path = get_db_path()
        self.production_data = ProductionData(self.db_path)
        self.table_name = ""
        self.checked_rows = set()  # Conjunto para almacenar las filas seleccionadas
        self.default_row = []  # Valores por defecto para una nueva fila
        
    def load_data(self, table_name: str, filter_of: Optional[str] = None) -> bool:
        """
        Carga los datos de producción desde la base de datos
        
        Args:
            table_name (str): Nombre de la tabla
            filter_of (Optional[str]): Filtro para la columna OF
            
        Returns:
            bool: True si la carga fue exitosa, False en caso contrario
        """
        try:
            # Conectar a la base de datos
            if not self.production_data.connect():
                return False
            
            # Verificar si la tabla existe y obtener su nombre real (case-insensitive)
            self.production_data.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND LOWER(name) = LOWER(?)",[table_name])
            table_info = self.production_data.cursor.fetchone()
            
            if not table_info:
                # Si no se encuentra la tabla, intentar con 'bobina' o 'bobinas'
                self.production_data.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (LOWER(name) = 'bobina' OR LOWER(name) = 'bobinas')")
                table_info = self.production_data.cursor.fetchone()
                
            if not table_info:
                # Listar todas las tablas disponibles para diagnóstico
                self.production_data.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [t[0] for t in self.production_data.cursor.fetchall()]
                import logging
                logging.error(f"No se encontró la tabla '{table_name}' ni 'bobina'/'bobinas' en la base de datos. Tablas disponibles: {', '.join(tables)}")
                self.production_data.disconnect()
                return False
                
            # Usar el nombre real de la tabla
            self.table_name = table_info[0]
            import logging
            logging.info(f"Usando tabla: {self.table_name}")
            
            # Obtener datos
            columns, rows = self.production_data.get_production_data(self.table_name, filter_of)
            
            # Actualizar modelo
            self.beginResetModel()
            
            # Definir el orden exacto de las columnas
            # Obs debe ir antes de observaciones
            desired_order = ["of", "bobina_num", "sec", "ancho", "peso", "gramaje", "diametro", 
                          "fecha", "turno", "codprod", "descprod", "alistamiento", "calidad", "obs", "observaciones", "created_at"]
            
            # Crear un diccionario para mapear columnas a sus índices originales
            column_indices = {col: idx for idx, col in enumerate(columns)}
            
            # Reordenar las columnas según el orden deseado
            ordered_columns = []
            ordered_indices = []
            
            # Primero verificar si existe la columna 'id' y excluirla
            id_column_index = None
            for col_name in columns:
                if col_name.lower() == 'id':
                    id_column_index = column_indices[col_name]
                    # No la agregamos a ordered_columns para ocultarla
            
            # Asegurar que OF sea la primera columna si existe
            of_found = False
            if "OF" in column_indices:
                ordered_columns.append("OF")
                ordered_indices.append(column_indices["OF"])
                of_found = True
            
            # Luego agregar las columnas en el orden deseado si existen (excepto OF que ya se agregó)
            for col_name in desired_order:
                if col_name != "OF" and col_name in column_indices:
                    ordered_columns.append(col_name)
                    ordered_indices.append(column_indices[col_name])
            
            # Finalmente agregar cualquier columna restante que no esté en el orden deseado (excepto id)
            for col_name in columns:
                if col_name not in desired_order and col_name != "OF" and col_name.lower() != 'id':
                    ordered_columns.append(col_name)
                    ordered_indices.append(column_indices[col_name])
            
            # Reordenar las filas de datos según los nuevos índices de columnas
            reordered_rows = []
            for row in rows:
                new_row = [row[i] for i in ordered_indices]
                reordered_rows.append(new_row)
            
            # Establecer los nombres de columnas en el orden deseado
            self.column_names = ordered_columns.copy()
            # Agregar columna de observaciones al final
            #self.column_names.append("Obs")
            # Agregar columna vacía para Obs al final
            self.data_rows = [list(row) + [""] for row in reordered_rows]
            # Crear una fila por defecto con valores vacíos para cada columna
            self.default_row = [""] * len(self.column_names)
            # Limpiar selecciones previas
            self.checked_rows.clear()
            self.endResetModel()
            
            # Desconectar de la base de datos
            self.production_data.disconnect()
            
            return True
        except Exception as e:
            print(f"Error al cargar datos: {str(e)}")
            return False
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """
        Devuelve el número de filas en el modelo
        
        Args:
            parent: Índice del modelo padre
            
        Returns:
            int: Número de filas
        """
        return len(self.data_rows)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """
        Devuelve el número de columnas en el modelo
        
        Args:
            parent: Índice del modelo padre
            
        Returns:
            int: Número de columnas
        """
        return len(self.column_names)
    
    def data(self, index, role=Qt.DisplayRole) -> Any:
        """
        Devuelve los datos para el rol especificado
        
        Args:
            index: Índice del modelo
            role: Rol de los datos
            
        Returns:
            Any: Datos para el rol especificado
        """
        if not index.isValid():
            return None
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if 0 <= index.column() < len(self.column_names) and 0 <= index.row() < len(self.data_rows):
                value = self.data_rows[index.row()][index.column()]
                
                # Verificar si la columna es una fecha
                col_name = self.column_names[index.column()].lower()
                if value and ('fecha' in col_name or col_name in ['created_at', 'fechaelaboracion']):
                    from datetime import datetime
                    try:
                        # Si el valor es None o está vacío, devolver cadena vacía
                        if not value:
                            return ""
                        
                        # Si ya es un objeto date o datetime, formatearlo directamente
                        if hasattr(value, 'strftime'):
                            return value.strftime("%d/%m/%Y")
                            
                        # Convertir a string y limpiar espacios
                        date_str = str(value).strip()
                        
                        # Si ya está en el formato dd/MM/yyyy o empieza con ese formato, devolver solo la fecha
                        if len(date_str) >= 10 and date_str[2] == '/' and date_str[5] == '/':
                            # Si hay una hora después, recortar solo la fecha
                            return date_str[:10]
                        
                        # Intentar diferentes formatos de fecha
                        formats_to_try = [
                            "%Y-%m-%d %H:%M:%S",  # Formato ISO con hora
                            "%Y-%m-%d",           # Formato ISO sin hora
                            "%d/%m/%Y %H:%M:%S",  # Formato español con hora
                            "%d/%m/%Y",           # Formato español sin hora
                            "%d-%m-%Y %H:%M:%S",  # Formato con guiones
                            "%d-%m-%Y",           # Formato con guiones sin hora
                            "%Y%m%d"               # Formato compacto (AAAAMMDD)
                        ]
                        
                        for fmt in formats_to_try:
                            try:
                                # Intentar parsear la fecha
                                clean_date_str = date_str.split('.')[0]  # Eliminar milisegundos si existen
                                date_obj = datetime.strptime(clean_date_str, fmt)
                                return date_obj.strftime("%d/%m/%Y")
                            except (ValueError, IndexError):
                                continue
                        
                        # Si no se pudo formatear, devolver el valor original
                        return date_str
                        
                    except Exception as e:
                        print(f"Error al formatear fecha en columna {col_name} (valor: '{value}'): {e}")
                        return str(value) if value else ""
                
                # Para otros valores, devolverlos tal cual
                return value
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole) -> Any:
        """
        Devuelve los datos de cabecera para el rol especificado
        
        Args:
            section: Sección (fila o columna)
            orientation: Orientación (horizontal o vertical)
            role: Rol de los datos
            
        Returns:
            Any: Datos de cabecera para el rol especificado
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal and section < len(self.column_names):
                return self.column_names[section]
            elif orientation == Qt.Vertical:
                return section + 1
        
        return None
    
    def flags(self, index) -> Qt.ItemFlags:
        """
        Devuelve las banderas para el índice especificado
        
        Args:
            index: Índice del modelo
            
        Returns:
            Qt.ItemFlags: Banderas para el índice
        """
        flags = super().flags(index)
        
        # Todas las columnas son editables ahora para soportar CRUD
        flags |= Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        
        return flags
    
    def setData(self, index, value, role=Qt.EditRole) -> bool:
        """
        Establece los datos para el índice y rol especificados y actualiza la base de datos.
        Args:
            index: Índice del modelo
            value: Valor a establecer
            role: Rol de los datos
        Returns:
            bool: True si se establecieron los datos correctamente, False en caso contrario
        """
        print(f"setData llamado: index=({index.row()}, {index.column()}), value={value}, role={role}")
        if not index.isValid():
            print("setData: índice inválido")
            return False
        if role == Qt.EditRole:
            row_index = index.row()
            col_index = index.column()
            print(f"setData: editando fila {row_index}, columna {col_index}")
            self.data_rows[row_index][col_index] = value
            # Persistir el cambio en la base de datos usando bobina y sec
            self.production_data.connect()
            db_columns = [col for col in self.column_names if col.lower() != 'obs']
            db_row_data = self.data_rows[row_index][:len(db_columns)]
            # Imprimir nombres de columnas reales
            print(f"setData: column_names reales: {self.column_names}")
            # Buscar 'bobina_num' y 'sec' ignorando mayúsculas/minúsculas y espacios
            def normalize(col):
                return col.strip().replace(' ', '').lower()
            try:
                idx_bobina = [normalize(c) for c in self.column_names].index('bobina_num')
                idx_sec = [normalize(c) for c in self.column_names].index('sec')
            except ValueError:
                print("setData: No se encontraron columnas 'bobina_num' y/o 'sec' (buscando flexiblemente)")
                self.production_data.disconnect()
                return False
            bobina_value = self.data_rows[row_index][idx_bobina]
            sec_value = self.data_rows[row_index][idx_sec]
            print(f"setData: update_row con bobina_num={bobina_value}, sec={sec_value}, datos={db_row_data}")
            res = self.production_data.update_row(
                self.table_name, db_columns, db_row_data,
                ['bobina_num', 'sec'], [bobina_value, sec_value]
            )
            print(f"setData: resultado update_row = {res}")
            self.production_data.disconnect()
            self.dataChanged.emit(index, index, [role])
            return True
        print("setData: role no es EditRole")
        return False


    def add_row(self, row_data=None):
        """
        Agrega una nueva fila al modelo y la persiste en la base de datos.
        Args:
            row_data (list, optional): Datos para la nueva fila. Si es None, se usa la fila por defecto.
        Returns:
            int: Índice de la nueva fila
        """
        if row_data is None:
            row_data = self.default_row.copy()
            
        # Crear una copia de los datos para no modificar el original
        row_data = list(row_data)
        
        # Persistir en la base de datos
        self.production_data.connect()
        
        # Excluir columnas calculadas/no persistentes
        db_columns = [col for col in self.column_names if col.lower() != 'obs']
        
        # Crear un diccionario temporal para mapear nombres de columna a sus valores
        row_dict = dict(zip([col.lower() for col in self.column_names], row_data))
        
        # Crear la lista de datos para la base de datos usando solo las columnas que se van a guardar
        db_row_data = []
        for col in db_columns:
            col_lower = col.lower()
            if col_lower in row_dict:
                db_row_data.append(row_dict[col_lower])
            else:
                # Si la columna no está en los datos, usar None
                db_row_data.append(None)
        
        # Insertar en la base de datos
        success = self.production_data.insert_row(self.table_name, db_columns, db_row_data)
        self.production_data.disconnect()
        
        if not success:
            # Si hubo un error al insertar, devolver -1
            return -1
            
        # Insertar la nueva fila en memoria
        row_index = len(self.data_rows)
        self.beginInsertRows(QModelIndex(), row_index, row_index)
        self.data_rows.append(row_data)
        self.endInsertRows()
        
        return row_index

    def update_row(self, row_index, row_data):
        """
        Actualiza SOLO los campos calidad, obs y codigoDeProducto en la tabla bobina, usando bobina_num y sec como claves exactas.
        Garantiza persistencia real en la base.
        """
        import logging
        logging.info(f"=== INICIANDO UPDATE_ROW PARA FILA {row_index} ===")
        if 0 <= row_index < len(self.data_rows):
            self.production_data.connect()
            current_data = self.data_rows[row_index].copy()
            # Buscar índices exactos
            def idx(col):
                return self.column_names.index(col) if col in self.column_names else -1
            
            try:
                # Verificar que existan las columnas necesarias
                idx_bobina = idx('bobina_num')
                if idx_bobina == -1:
                    logging.error("No se encontró la columna 'bobina_num' en el modelo")
                    self.production_data.disconnect()
                    return False
                
                idx_sec = idx('sec')
                if idx_sec == -1:
                    logging.error("No se encontró la columna 'sec' en el modelo")
                    self.production_data.disconnect()
                    return False
                
                idx_calidad = idx('calidad')
                if idx_calidad == -1:
                    logging.error("No se encontró la columna 'calidad' en el modelo")
                    self.production_data.disconnect()
                    return False
                
                idx_obs = idx('obs')
                if idx_obs == -1:
                    logging.error("No se encontró la columna 'obs' en el modelo")
                    self.production_data.disconnect()
                    return False
                
                # Buscar la columna de código de producto (codigoDeProducto o codprod)
                idx_codprod = None
                codprod_column_name = None
                if 'codigoDeProducto' in self.column_names:
                    idx_codprod = idx('codigoDeProducto')
                    codprod_column_name = 'codigoDeProducto'
                    logging.info("Usando columna 'codigoDeProducto' para actualizar")
                elif 'codprod' in self.column_names:
                    idx_codprod = idx('codprod')
                    codprod_column_name = 'codprod'
                    logging.info("Usando columna 'codprod' para actualizar")
                else:
                    logging.warning("No se encontró ninguna columna de código de producto en el modelo")
                
                # Valores clave
                bobina_value = current_data[idx_bobina]
                sec_value = current_data[idx_sec]
                
                logging.info(f"Valores clave: bobina_num={bobina_value}, sec={sec_value}")
                
                # Valores actuales
                old_calidad = current_data[idx_calidad]
                old_obs = current_data[idx_obs]
                old_codprod = current_data[idx_codprod] if idx_codprod is not None else None
                
                # Nuevos valores
                calidad = row_data[idx_calidad]
                obs = row_data[idx_obs]
                codprod = row_data[idx_codprod] if idx_codprod is not None else None
                
                logging.info(f"Valores a actualizar: calidad: '{old_calidad}' -> '{calidad}', obs: '{old_obs}' -> '{obs}'")
                if idx_codprod is not None:
                    logging.info(f"Código de producto: '{old_codprod}' -> '{codprod}'")
                
                # Construir columnas/campos a actualizar
                columns = ['calidad', 'obs']
                values = [calidad, obs]
                
                # Agregar código de producto si existe
                if idx_codprod is not None and codprod is not None:
                    columns.append(codprod_column_name)  # Usar el nombre correcto de la columna
                    values.append(codprod)
                    logging.info(f"Agregando columna {codprod_column_name} con valor {codprod} a la actualización")
                
                # Verificar si la tabla existe y obtener su nombre real (case-insensitive)
                self.production_data.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND LOWER(name) IN ('bobina', 'bobinas')")
                table_info = self.production_data.cursor.fetchone()
                
                if not table_info:
                    # Listar todas las tablas disponibles para diagnóstico
                    self.production_data.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [t[0] for t in self.production_data.cursor.fetchall()]
                    logging.error(f"No se encontró la tabla 'bobina' o 'bobinas' en la base de datos. Tablas disponibles: {', '.join(tables)}")
                    self.production_data.disconnect()
                    return False
                    
                table_name = table_info[0]  # Usar el nombre real de la tabla
                logging.info(f"Usando tabla: {table_name}")
                
                # Verificar las columnas en la tabla de la base de datos
                db_columns = self.production_data.get_table_columns(table_name)
                logging.info(f"Columnas en tabla {table_name}: {db_columns}")
                
                # Filtrar columnas que realmente existen en la base de datos
                valid_columns = []
                valid_values = []
                for col, val in zip(columns, values):
                    if col.lower() in [c.lower() for c in db_columns]:
                        valid_columns.append(col)
                        valid_values.append(val)
                    else:
                        logging.warning(f"Columna '{col}' no existe en la tabla {table_name} de la base de datos")
                
                if not valid_columns:
                    logging.error("No hay columnas válidas para actualizar")
                    self.production_data.disconnect()
                    return False
                
                # Asegurar que las columnas de clave también existan en la base de datos
                if 'bobina_num' not in db_columns and 'bobina_num'.lower() not in [c.lower() for c in db_columns]:
                    logging.error(f"La columna 'bobina_num' no existe en la tabla {table_name}")
                    self.production_data.disconnect()
                    return False
                if 'sec' not in db_columns and 'sec'.lower() not in [c.lower() for c in db_columns]:
                    logging.error(f"La columna 'sec' no existe en la tabla {table_name}")
                    self.production_data.disconnect()
                    return False
                
                # Ejecutar update directo con el nombre correcto de la tabla
                logging.info(f"Ejecutando UPDATE {table_name} SET {', '.join([f'{c}=?' for c in valid_columns])} WHERE bobina_num=? AND sec=?")
                logging.info(f"Valores SET: {valid_values}, Valores WHERE: [{bobina_value}, {sec_value}]")
                
                result = self.production_data.update_row(
                    table_name,
                    valid_columns,
                    valid_values,
                    ['bobina_num', 'sec'],
                    [bobina_value, sec_value]
                )
                
                # Forzar commit explícito
                if result:
                    try:
                        self.production_data.connection.commit()
                        logging.info("Commit explícito realizado en update_row")
                    except Exception as e:
                        logging.error(f"Error al hacer commit: {str(e)}")
                    
                self.production_data.disconnect()
                
                if result:
                    # Actualizar datos en memoria
                    self.data_rows[row_index][idx_calidad] = calidad
                    self.data_rows[row_index][idx_obs] = obs
                    if idx_codprod is not None:
                        self.data_rows[row_index][idx_codprod] = codprod
                    
                    # Notificar cambios en la interfaz
                    top_left = self.index(row_index, 0)
                    bottom_right = self.index(row_index, len(self.column_names) - 1)
                    self.dataChanged.emit(top_left, bottom_right)
                    logging.info("Datos actualizados en memoria y notificación enviada")
                    return True
                else:
                    logging.error(f"No se pudo actualizar la fila bobina_num={bobina_value}, sec={sec_value}")
                    return False
            except Exception as e:
                logging.error(f"Error en update_row: {str(e)}", exc_info=True)
                if self.production_data.connection:
                    self.production_data.disconnect()
                return False
        else:
            logging.error(f"Índice de fila fuera de rango: {row_index} (total filas: {len(self.data_rows)})")
        return False


    def delete_row(self, row_index):
        """
        Elimina una fila del modelo y de la base de datos usando bobina_num y sec como claves.
        Args:
            row_index (int): Índice de la fila a eliminar
        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario
        """
        if 0 <= row_index < len(self.data_rows):
            try:
                # Obtener índices de las columnas necesarias
                col_names = [col.lower() for col in self.column_names]
                
                # Verificar que existan las columnas necesarias
                if 'bobina_num' not in col_names or 'sec' not in col_names:
                    print("Error: No se encontraron las columnas 'bobina_num' y/o 'sec'")
                    return False
                
                # Obtener los valores de bobina_num y sec
                bobina_num_index = col_names.index('bobina_num')
                sec_index = col_names.index('sec')
                
                bobina_num = self.data_rows[row_index][bobina_num_index]
                sec = self.data_rows[row_index][sec_index]
                
                if not bobina_num or not sec:
                    print("Error: Los campos 'bobina_num' y 'sec' no pueden estar vacíos")
                    return False
                
                # Eliminar de la base de datos usando bobina_num y sec
                self.production_data.connect()
                success = self.production_data.delete_row(
                    self.table_name, 
                    None,  # No usamos pk_name
                    None,  # No usamos pk_value
                    str(bobina_num),  # bobina
                    str(sec)          # sec
                )
                self.production_data.disconnect()
                
                if not success:
                    print("Error al eliminar la fila de la base de datos")
                    return False
                
                # Eliminar en memoria
                self.beginRemoveRows(QModelIndex(), row_index, row_index)
                del self.data_rows[row_index]
                self.endRemoveRows()
                return True
                
            except Exception as e:
                print(f"Error al eliminar la fila: {str(e)}")
                if self.production_data.connection:
                    self.production_data.disconnect()
                return False
        return False


class ProductionSortFilterProxyModel(QSortFilterProxyModel):
    """Modelo proxy para ordenar y filtrar datos de producción"""
    
    def __init__(self, parent=None):
        """
        Inicializa el modelo proxy para ordenar y filtrar datos de producción
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.of_filter = ""
        # Asegurar que el proxy pase correctamente los flags y datos
        self.setDynamicSortFilter(True)
    
    def set_of_filter(self, filter_text: str) -> None:
        """
        Establece el filtro para la columna OF
        
        Args:
            filter_text (str): Texto de filtro
        """
        self.of_filter = filter_text
        self.invalidateFilter()
        
    def flags(self, index):
        """Asegura que los flags se pasen correctamente al modelo fuente"""
        source_index = self.mapToSource(index)
        return self.sourceModel().flags(source_index)
        
    def setData(self, index, value, role=Qt.EditRole):
        """Asegura que los cambios de datos se pasen correctamente al modelo fuente"""
        source_index = self.mapToSource(index)
        return self.sourceModel().setData(source_index, value, role)
    
    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        """
        Determina si una fila debe ser aceptada por el filtro
        
        Args:
            source_row: Fila en el modelo fuente
            source_parent: Índice del padre en el modelo fuente
            
        Returns:
            bool: True si la fila debe ser aceptada, False en caso contrario
        """
        # Si no hay filtro, aceptar todas las filas
        if not self.of_filter:
            return True
        
        # Buscar la columna OF (puede estar como "OF", "of", "Orden de Fabricación", etc.)
        source_model = self.sourceModel()
        of_column = -1
        
        for i in range(source_model.columnCount()):
            header = str(source_model.headerData(i, Qt.Horizontal) or "").upper()
            if "OF" in header or "ORDEN" in header or "FABRICACION" in header or "FABRICACIÓN" in header:
                of_column = i
                break
        
        # Si no se encuentra la columna OF, buscar en la primera columna como fallback
        # ya que normalmente la OF es la primera columna en tablas de producción
        if of_column == -1 and source_model.columnCount() > 0:
            of_column = 0
        
        # Obtener el valor de la columna OF
        of_value = source_model.data(source_model.index(source_row, of_column))
        
        # Verificar si el valor coincide con el filtro
        if of_value is not None and self.of_filter.lower() in str(of_value).lower():
            return True
        
        return False
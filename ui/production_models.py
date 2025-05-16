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
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'produccion.db')
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
            
            # Obtener datos
            self.table_name = table_name
            columns, rows = self.production_data.get_production_data(table_name, filter_of)
            
            # Actualizar modelo
            self.beginResetModel()
            
            # Definir el orden exacto de las columnas
            desired_order = ["of", "bobina_num", "sec", "ancho", "peso", "gramaje", "diametro", 
                            "fecha", "turno", "codprod", "descprod", "alistamiento", "calidad", "observaciones", "created_at", "obs"]
            
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
                return self.data_rows[index.row()][index.column()]
        
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
        # Persistir en la base de datos
        self.production_data.connect()
        # Excluir columnas calculadas/no persistentes
        db_columns = [col for col in self.column_names if col.lower() != 'obs']
        # Obtener codprod y descprod desde row_data según el índice de las columnas
        if 'codprod' in [c.lower() for c in db_columns] and 'descprod' in [c.lower() for c in db_columns]:
            idx_codprod = [c.lower() for c in self.column_names].index('codprod')
            idx_descprod = [c.lower() for c in self.column_names].index('descprod')
            codprod = row_data[idx_codprod]
            descprod = row_data[idx_descprod]
            db_row_data = row_data[:len(db_columns)]
            db_row_data[idx_codprod] = codprod
            db_row_data[idx_descprod] = descprod
        self.production_data.insert_row(self.table_name, db_columns, db_row_data)
        self.production_data.disconnect()
        # Insertar la nueva fila en memoria
        row_index = len(self.data_rows)
        self.beginInsertRows(QModelIndex(), row_index, row_index)
        self.data_rows.append(row_data)
        return row_index

    def update_row(self, row_index, row_data):
        """
        Actualiza una fila existente y la persiste en la base de datos usando bobina y sec como clave.
        Args:
            row_index (int): Índice de la fila a actualizar
            row_data (list): Nuevos datos para la fila
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario
        """
        if 0 <= row_index < len(self.data_rows):
            # Actualizar en la base de datos
            self.production_data.connect()
            db_columns = [col for col in self.column_names if col.lower() != 'obs']
            db_row_data = row_data[:len(db_columns)]
            
            # Buscar 'bobina_num' y 'sec' como clave para la actualización
            try:
                # Normalizar nombres de columnas para búsqueda flexible
                def normalize(col):
                    return col.strip().replace(' ', '').lower()
                
                idx_bobina = [normalize(c) for c in self.column_names].index('bobina_num')
                idx_sec = [normalize(c) for c in self.column_names].index('sec')
                
                bobina_value = self.data_rows[row_index][idx_bobina]
                sec_value = self.data_rows[row_index][idx_sec]
                
                # Actualizar en la base de datos
                result = self.production_data.update_row(
                    self.table_name, db_columns, db_row_data,
                    ['bobina_num', 'sec'], [bobina_value, sec_value]
                )
                self.production_data.disconnect()
                
                if result:
                    # Actualizar en memoria
                    self.data_rows[row_index] = row_data
                    top_left = self.index(row_index, 0)
                    bottom_right = self.index(row_index, len(self.column_names) - 1)
                    self.dataChanged.emit(top_left, bottom_right)
                    return True
                return False
            except ValueError:
                print("Error: No se encontraron columnas 'bobina_num' y/o 'sec'")
                self.production_data.disconnect()
                return False
        return False

    def delete_row(self, row_index):
        """
        Elimina una fila del modelo y de la base de datos.
        Args:
            row_index (int): Índice de la fila a eliminar
        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario
        """
        if 0 <= row_index < len(self.data_rows):
            # Eliminar de la base de datos
            self.production_data.connect()
            db_columns = [col for col in self.column_names if col.lower() != 'obs']
            pk_name = 'id' if 'id' in [c.lower() for c in db_columns] else db_columns[0]
            pk_index = [c.lower() for c in self.column_names].index(pk_name)
            pk_value = self.data_rows[row_index][pk_index]
            self.production_data.delete_row(self.table_name, pk_name, pk_value)
            self.production_data.disconnect()
            # Eliminar en memoria
            self.beginRemoveRows(QModelIndex(), row_index, row_index)
            del self.data_rows[row_index]
            self.endRemoveRows()
            return True
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
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de modelos de producción

Contiene los modelos para la gestión de datos de producción.
"""

import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

logging.basicConfig(level=logging.DEBUG)

class ProductionData:
    """Clase para gestionar los datos de producción desde la base de datos"""
    
    def __init__(self, db_path: str):
        """
        Inicializa el gestor de datos de producción
        
        Args:
            db_path (str): Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """
        Establece la conexión a la base de datos
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error al conectar a la base de datos: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Cierra la conexión a la base de datos"""
        if self.connection:
            self.connection.close()
    
    def get_table_names(self) -> List[str]:
        """
        Obtiene los nombres de las tablas en la base de datos
        
        Returns:
            List[str]: Lista de nombres de tablas
        """
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [table[0] for table in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error al obtener nombres de tablas: {str(e)}")
            return []
    
    def get_table_schema(self, table_name: str) -> List[Tuple]:
        """
        Obtiene el esquema de una tabla
        
        Args:
            table_name (str): Nombre de la tabla
            
        Returns:
            List[Tuple]: Lista de tuplas con información de las columnas
        """
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error al obtener esquema de tabla: {str(e)}")
            return []
    
    def get_production_data(self, table_name: str, filter_of: Optional[str] = None) -> Tuple[List[str], List[List]]:
        """
        Obtiene los datos de producción de la tabla especificada
        
        Args:
            table_name (str): Nombre de la tabla
            filter_of (Optional[str]): Filtro para la columna OF
            
        Returns:
            Tuple[List[str], List[List]]: Tupla con (nombres de columnas, filas de datos)
        """
        try:
            # Actualizar campos vacíos en la tabla bobina (incluyendo CantidadEnPrimeraUdM)
            self.update_empty_bobinas_fields()
            
            # Actualizar campos de calidad y obs
            if hasattr(self, 'update_quality_fields'):
                self.update_quality_fields()
                
            # Obtener nombres de columnas
            schema = self.get_table_schema(table_name)
            columns = [col[1] for col in schema]
            
            # Construir consulta SQL
            query = f"SELECT * FROM {table_name}"
            params = []
            
            # Aplicar filtro si se especifica
            if filter_of and 'OF' in columns:
                query += " WHERE OF LIKE ?"
                params.append(f"%{filter_of}%")
            
            # Ejecutar consulta
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            return columns, rows
        except sqlite3.Error as e:
            logging.error(f"Error al obtener datos de producción: {str(e)}")
            return [], []

    def insert_row(self, table_name: str, columns: list, row_data: list) -> bool:
        """
        Inserta una nueva fila en la tabla especificada.
        
        Args:
            table_name (str): Nombre de la tabla
            columns (list): Lista de nombres de columnas
            row_data (list): Valores a insertar
            
        Returns:
            bool: True si la inserción fue exitosa, False en caso contrario
        """
        try:
            # Obtener el esquema de la tabla para identificar los tipos de columna
            schema = self.get_table_schema(table_name)
            column_types = {col[1]: col[2].upper() for col in schema}
            
            # Formatear fechas
            formatted_data = []
            for i, (col_name, value) in enumerate(zip(columns, row_data)):
                if value is not None and ('DATE' in column_types.get(col_name, '') or 
                                        col_name.lower() in ['fechavalidezlote', 'fechaelaboracion']):
                    formatted_data.append(self._format_date(value, col_name))
                else:
                    formatted_data.append(value)
            
            placeholders = ','.join(['?'] * len(formatted_data))
            cols = ','.join(columns)
            query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
            self.cursor.execute(query, formatted_data)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error al insertar fila: {str(e)}")
            return False

    def update_row(self, table_name: str, columns: list, row_data: list, where_fields: list, where_values: list) -> bool:
        """
        Actualiza una fila existente en la tabla especificada usando múltiples claves.
        
        Args:
            table_name (str): Nombre de la tabla
            columns (list): Lista de nombres de columnas
            row_data (list): Nuevos valores
            where_fields (list): Lista de nombres de campos clave
            where_values (list): Lista de valores de los campos clave
            
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario
        """
        try:
            # Obtener el esquema de la tabla para identificar los tipos de columna
            schema = self.get_table_schema(table_name)
            column_types = {col[1]: col[2].upper() for col in schema}
            
            # Formatear fechas en row_data
            formatted_row_data = []
            for i, (col_name, value) in enumerate(zip(columns, row_data)):
                if value is not None and ('DATE' in column_types.get(col_name, '') or 
                                        col_name.lower() in ['fechavalidezlote', 'fechaelaboracion']):
                    formatted_row_data.append(self._format_date(value, col_name))
                else:
                    formatted_row_data.append(value)
            
            # Formatear fechas en where_values
            formatted_where_values = []
            for i, (field, value) in enumerate(zip(where_fields, where_values)):
                if value is not None and ('DATE' in column_types.get(field, '') or 
                                        field.lower() in ['fechavalidezlote', 'fechaelaboracion']):
                    formatted_where_values.append(self._format_date(value, field))
                else:
                    formatted_where_values.append(value)
            
            set_clause = ', '.join([f"{col} = ?" for col in columns])
            where_clause = ' AND '.join([f"{field} = ?" for field in where_fields])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            
            self.cursor.execute(query, formatted_row_data + formatted_where_values)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error al actualizar fila: {str(e)}")
            return False

    def delete_row(self, table_name: str, pk_name: str, pk_value, bobina: str = None, sec: str = None) -> bool:
        """
        Elimina una fila de la tabla especificada usando la clave primaria o la combinación de bobina y sec.
        
        Args:
            table_name (str): Nombre de la tabla
            pk_name (str): Nombre de la columna clave primaria (opcional si se usan bobina y sec)
            pk_value: Valor de la clave primaria (opcional si se usan bobina y sec)
            bobina (str, optional): Valor del campo bobina para la condición WHERE
            sec (str, optional): Valor del campo sec para la condición WHERE
            
        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            if bobina is not None and sec is not None:
                # Usar bobina_num y sec como condiciones de búsqueda
                query = f"DELETE FROM {table_name} WHERE bobina_num = ? AND sec = ?"
                params = (bobina, sec)
                logging.info(f"Ejecutando consulta: {query} con parámetros: {params}")
            else:
                # Usar la clave primaria como condición de búsqueda (comportamiento anterior)
                query = f"DELETE FROM {table_name} WHERE {pk_name} = ?"
                params = (pk_value,)
                logging.info(f"Ejecutando consulta: {query} con parámetros: {params}")
                
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error al eliminar fila: {str(e)}")
            return False
            
    def _format_gramaje(self, gramaje):
        """Formatea el gramaje tomando solo la parte entera"""
        if gramaje is None:
            return "000"
        try:
            # Tomar solo la parte entera
            entero = str(int(float(gramaje)))
            # Rellenar con ceros a la izquierda hasta 4 dígitos
            return entero.zfill(3)
        except (ValueError, TypeError):
            return "0000"
    
    def _format_diametro(self, diametro):
        """Formatea el diámetro como se especifica"""
        if diametro is None:
            return "0000"
        try:
            # Convertir a entero multiplicando por 10 (para mover la coma)
            # y luego formatear a 4 dígitos con ceros a la izquierda
            valor = int(float(diametro) * 10)
            return f"{valor:04d}"
        except (ValueError, TypeError):
            return "0000"
    
    def _format_date(self, date_value, field_name=None):
        """
        Formatea una fecha al formato dd/mm/yyyy.
        
        Args:
            date_value: Valor de fecha (puede ser datetime, date o string)
            field_name: Nombre del campo de fecha (opcional, para manejar campos específicos)
            
        Returns:
            str: Fecha formateada como dd/mm/yyyy o None si no se puede formatear
        """
        if not date_value:
            return None
            
        try:
            # Si es un string, intentar convertirlo a datetime
            if isinstance(date_value, str):
                # Eliminar espacios en blanco
                date_str = date_value.strip()
                
                # Si el string ya está en formato dd/mm/yyyy, devolverlo tal cual
                if re.match(r'^\d{2}/\d{2}/\d{4}$', date_str):
                    return date_str
                    
                # Si el string incluye hora, extraer solo la parte de la fecha
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                
                # Intentar diferentes formatos de fecha
                for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y'):
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime('%d/%m/%Y')
                    except ValueError:
                        continue
                return date_str  # Si no coincide con ningún formato, devolver el valor original
            
            # Si es un objeto date o datetime, formatearlo
            if hasattr(date_value, 'strftime'):
                return date_value.strftime('%d/%m/%Y')
                
            return str(date_value)
        except Exception as e:
            logging.warning(f"No se pudo formatear la fecha {date_value} para el campo {field_name}: {str(e)}")
            return date_value
            
    def _format_ancho(self, ancho):
        """
        Formatea el ancho con 3 dígitos enteros y 2 decimales.
        - Los enteros se rellenan con ceros a la izquierda si son menos de 3 dígitos
        - Los decimales se rellenan con ceros a la derecha si hay menos de 2 dígitos
        - Total: 5 dígitos (3 enteros + 2 decimales)
        """
        if ancho is None:
            return "00000"
            
        try:
            # Convertir a float y manejar el signo negativo si existe
            valor = float(ancho)
            es_negativo = valor < 0
            valor = abs(valor)
            
            # Separar parte entera y decimal
            parte_entera = int(valor)
            parte_decimal = valor - parte_entera
            
            # Formatear parte entera (3 dígitos con ceros a la izquierda)
            str_entero = f"{parte_entera:03d}"[-3:]  # Tomar solo 3 dígitos
            
            # Formatear parte decimal (2 dígitos con ceros a la derecha)
            decimal_redondeado = round(parte_decimal * 100)  # Mover a centésimas
            str_decimal = f"{decimal_redondeado:02d}"[:2]  # Tomar solo 2 dígitos
            
            # Combinar las partes
            resultado = f"{str_entero}{str_decimal}"
            
            # Agregar signo negativo si es necesario
            if es_negativo:
                resultado = "-" + resultado
                
            # Asegurar que siempre tengamos 5 dígitos
            return resultado[:5].ljust(5, '0')
            
        except (ValueError, TypeError):
            return "00000"
    
    def update_empty_bobinas_fields(self) -> bool:
        """
        Actualiza los campos vacíos en la tabla bobina según las reglas especificadas.
        - Actualiza el campo codigodeproducto con la concatenación de varios campos
        - Actualiza el campo lote con el formato 'of/sec' si está vacío
        - Actualiza el campo nroOT con el valor de 'of' si está vacío
        """
        try:
            # Verificar si la tabla bobina existe
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='bobina' OR name='bobinas')")
            table_info = self.cursor.fetchone()
            
            if not table_info:
                logging.warning("No se encontró la tabla 'bobina' ni 'bobinas' en la base de datos")
                return False
                
            table_name = table_info[0]  # Usar el nombre real de la tabla
            
            # Verificar las columnas existentes en la tabla
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columnas = [col[1] for col in self.cursor.fetchall()]
            
            # Verificar si existen las columnas necesarias
            required_columns = ['of', 'sec', 'lote', 'nroOT', 'peso', 'CantidadEnPrimeraUdM']
            missing_columns = [col for col in required_columns if col not in columnas]
            
            if missing_columns:
                logging.warning(f"Faltan columnas requeridas en la tabla {table_name}")
                logging.warning(f"Columnas faltantes: {missing_columns}")
                logging.warning(f"Columnas encontradas: {columnas}")
                return False
            
            # Obtener todos los registros de la tabla bobina que necesitan actualización
            # Incluimos peso en la consulta para actualizar CantidadEnPrimeraUdM
            query = f"""
                SELECT rowid, alistamiento, codprod, calidad, obs, gramaje, diametro, ancho, of, sec, lote, nroOT, peso
                FROM {table_name}
                WHERE lote IS NULL OR lote = '' OR nroOT IS NULL OR nroOT = '' 
                   OR codigodeproducto IS NULL OR codigodeproducto = ''
                   OR peso IS NOT NULL
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            if not rows:
                logging.info(f"No se encontraron registros que necesiten actualización en {table_name}")
                return True
                
            updated_count = 0
            
            for row in rows:
                try:
                    # Asegurarse de que la tupla tenga la longitud esperada
                    if len(row) < 13:  # Verificar que tenemos todos los campos esperados
                        logging.warning(f"Fila con formato inesperado: {row}")
                        continue
                        
                    rowid = row[0]
                    alistamiento = row[1]
                    codprod = row[2]
                    calidad = row[3]
                    obs = row[4]
                    gramaje = row[5]
                    diametro = row[6]
                    ancho = row[7]
                    of = row[8]
                    sec = row[9]
                    lote_actual = row[10]
                    nro_ot_actual = row[11]
                    peso = row[12]
                    
                    # Convertir a string y limpiar los valores
                    alistamiento = str(alistamiento or '').strip()
                    codprod = str(codprod or '').strip()
                    calidad = str(calidad or '').strip()
                    obs = str(obs or '').strip()
                    
                    # Formatear los valores numéricos
                    gramaje_fmt = self._format_gramaje(gramaje)
                    diametro_fmt = self._format_diametro(diametro)
                    ancho_fmt = self._format_ancho(ancho)
                    
                    # Construir el código de producto
                    nuevo_codigo = (
                        f"{alistamiento}{codprod}{calidad}{obs}"
                        f"{gramaje_fmt}{diametro_fmt}{ancho_fmt}"
                    )
                    
                    # Inicializar listas para la construcción dinámica de la consulta
                    updates = ["codigodeproducto = ?"]
                    params = [nuevo_codigo]
                    
                    # Actualizar CantidadEnPrimeraUdM con el valor de peso formateado a 2 decimales
                    if peso is not None:
                        try:
                            # Convertir a float y formatear a 2 decimales con coma como separador decimal
                            peso_float = float(peso)
                            peso_formateado = f"{peso_float:.2f}".replace('.', ',')
                            updates.append("CantidadEnPrimeraUdM = ?")
                            params.append(peso_formateado)
                        except (ValueError, TypeError):
                            # En caso de error, establecer valor por defecto
                            updates.append("CantidadEnPrimeraUdM = ?")
                            params.append("0,00")
                    
                    # Función auxiliar para verificar si un valor está vacío o es None
                    def is_empty(value):
                        return value is None or (isinstance(value, str) and value.strip() == '')
                    
                    # Actualizar el lote si está vacío o es NULL y tenemos of y sec
                    if is_empty(lote_actual) and of is not None and sec is not None:
                        nuevo_lote = f"{of}/{sec}"
                        updates.append("lote = ?")
                        params.append(nuevo_lote)
                    
                    # Actualizar nroOT si está vacío o es NULL y tenemos of
                    if is_empty(nro_ot_actual) and of is not None:
                        nro_ot_valor = str(of)
                        updates.append("nroOT = ?")
                        params.append(nro_ot_valor)
                    
                    # Si solo hay el código de producto para actualizar, verificar si es necesario
                    if len(updates) > 1 or is_empty(nuevo_codigo):
                        # Construir y ejecutar la consulta de actualización
                        update_query = f"UPDATE {table_name} SET {', '.join(updates)} WHERE rowid = ?"
                        params.append(rowid)
                        self.cursor.execute(update_query, params)
                        updated_count += 1
                        
                        # Hacer commit después de cada actualización para asegurar
                        self.connection.commit()
                        
                except Exception as e:
                    logging.error(f"Error al procesar el registro {rowid}: {str(e)}")
                    self.connection.rollback()
            
            logging.info(f"Se actualizaron {updated_count} registros en la tabla {table_name}")
            return True
            
        except sqlite3.Error as e:
            logging.error(f"Error al actualizar campos vacíos: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
                
    def check_quality_fields_status(self) -> dict:
        """
        Verifica el estado de los campos de calidad en la base de datos.
        
        Returns:
            dict: Diccionario con estadísticas sobre los campos de calidad
        """
        if not self.connection:
            if not self.connect():
                logging.error("No se pudo establecer conexión a la base de datos")
                return {}
                
        try:
            # Verificar si la tabla bobina existe (case-insensitive)
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND LOWER(name) = 'bobina'")
            table_info = self.cursor.fetchone()
            
            if not table_info:
                # Listar todas las tablas disponibles para diagnóstico
                self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [t[0] for t in self.cursor.fetchall()]
                logging.error(f"No se encontró la tabla 'bobina' en la base de datos. Tablas disponibles: {', '.join(tables)}")
                return {}
                
            table_name = table_info[0]  # Usar el nombre real de la tabla
            logging.info(f"Verificando campos de calidad en tabla: {table_name}")
            
            # Obtener estadísticas
            stats = {}
            
            # Contar registros totales
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            stats['total_records'] = self.cursor.fetchone()[0]
            
            # Contar registros con calidad NULL o vacía
            self.cursor.execute(f"""
                SELECT COUNT(*) 
                FROM {table_name} 
                WHERE calidad IS NULL OR TRIM(COALESCE(calidad, '')) = ''
            """)
            stats['empty_calidad'] = self.cursor.fetchone()[0]
            
            # Contar registros con obs NULL o vacía
            self.cursor.execute(f"""
                SELECT COUNT(*) 
                FROM {table_name} 
                WHERE obs IS NULL OR TRIM(COALESCE(obs, '')) = ''
            """)
            stats['empty_obs'] = self.cursor.fetchone()[0]
            
            # Contar registros con codprod válido (1 o 2)
            self.cursor.execute(f"""
                SELECT COUNT(*) 
                FROM {table_name} 
                WHERE TRIM(COALESCE(codprod, '')) IN ('1', '2', '3', '4', '5', '6', '7')
            """)
            stats['valid_codprod'] = self.cursor.fetchone()[0]
            
            # Verificar algunos registros de ejemplo
            self.cursor.execute(f"""
                SELECT rowid, codprod, calidad, obs 
                FROM {table_name} 
                WHERE (calidad IS NULL OR TRIM(COALESCE(calidad, '')) = '')
                   OR (obs IS NULL OR TRIM(COALESCE(obs, '')) = '')
                LIMIT 5
            """)
            stats['sample_records'] = [dict(zip(['rowid', 'codprod', 'calidad', 'obs'], row)) 
                                    for row in self.cursor.fetchall()]
            
            # Verificar la consulta de actualización
            if stats['empty_calidad'] > 0 or stats['empty_obs'] > 0:
                logging.info(f"Se encontraron {stats['empty_calidad']} registros con 'calidad' vacía y {stats['empty_obs']} con 'obs' vacía")
            else:
                logging.info("No se encontraron registros con campos de calidad vacíos")
            
            return stats
            
        except Exception as e:
            logging.error(f"Error al verificar el estado de los campos de calidad: {str(e)}", exc_info=True)
            return {}
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """
        Obtiene la lista de columnas de una tabla
        
        Args:
            table_name (str): Nombre de la tabla
            
        Returns:
            List[str]: Lista de nombres de columnas
        """
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            return [col[1] for col in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error al obtener columnas de la tabla {table_name}: {str(e)}")
            return []
            
    def update_quality_fields(self) -> bool:
        """
        Actualiza los campos de calidad y observaciones según las reglas especificadas.
        Actualiza los campos 'calidad' y 'obs' basado en el valor de 'codprod'.
        
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario
        """
        if not self.connection:
            if not self.connect():
                logging.error("No se pudo establecer conexión a la base de datos")
                return False
                
        try:
            # Verificar si la tabla bobina existe (case-insensitive)
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND LOWER(name) = 'bobina'")
            table_info = self.cursor.fetchone()
            
            if not table_info:
                # Listar todas las tablas disponibles para diagnóstico
                self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [t[0] for t in self.cursor.fetchall()]
                logging.error(f"No se encontró la tabla 'bobina' en la base de datos. Tablas disponibles: {', '.join(tables)}")
                return False
                
            table_name = table_info[0]  # Usar el nombre real de la tabla
            logging.info(f"Usando tabla: {table_name}")
            
            # Obtener la estructura de la tabla
            columns = self.get_table_columns(table_name)
            logging.info(f"Columnas de la tabla {table_name}: {', '.join(columns)}")
            
            # Verificar que las columnas necesarias existan
            required_columns = {'codprod', 'calidad', 'obs', 'producto'}
            optional_columns = {'fecha', 'fechaElaboracion', 'fechaValidezLote'}
            
            # Verificar columnas requeridas
            missing_required = required_columns - set(columns)
            if missing_required:
                logging.error(f"Faltan columnas requeridas en la tabla: {', '.join(missing_required)}")
                return False
                
            # Verificar columnas opcionales
            missing_optional = optional_columns - set(columns)
            if missing_optional:
                logging.warning(f"Columnas opcionales no encontradas: {', '.join(missing_optional)}")
                
            # Determinar qué columnas opcionales están presentes
            has_fecha = 'fecha' in columns
            has_fecha_elab = 'fechaElaboracion' in columns
            has_fecha_validez = 'fechaValidezLote' in columns
                
            # Obtener todos los registros
            self.cursor.execute(f"SELECT rowid, * FROM {table_name}")
            rows = self.cursor.fetchall()
            
            # Obtener índices de las columnas
            rowid_idx = 0  # rowid siempre es el primer elemento
            codprod_idx = columns.index('codprod') + 1  # +1 porque rowid es el primer elemento
            calidad_idx = columns.index('calidad') + 1
            obs_idx = columns.index('obs') + 1
            producto_idx = columns.index('producto') + 1
            
            # Inicializar índices de columnas opcionales
            fecha_idx = -1
            fecha_elab_idx = -1
            fecha_validez_idx = -1
            
            if has_fecha:
                fecha_idx = columns.index('fecha') + 1
            if has_fecha_elab:
                fecha_elab_idx = columns.index('fechaElaboracion') + 1
            if has_fecha_validez:
                fecha_validez_idx = columns.index('fechaValidezLote') + 1
            
            # Obtener fechas actuales (solo si se necesitan)
            hoy = datetime.now().date()
            fecha_elab = hoy.strftime('%d/%m/%Y')
            fecha_validez = (hoy + timedelta(days=5*365)).strftime('%d/%m/%Y')  # 5 años después
            
            updated_count = 0
            total_processed = 0
            
            logging.info(f"Iniciando actualización de {len(rows)} registros...")
            
            # Procesar cada registro
            for row in rows:
                total_processed += 1
                try:
                    # Obtener valores usando los índices correctos
                    rowid = row[rowid_idx]
                    codprod = row[codprod_idx] if codprod_idx < len(row) else None
                    producto = row[producto_idx] if producto_idx < len(row) else None
                    
                    # Inicializar variables para fechas
                    fecha_actual = None
                    fecha_elab_actual = None
                    fecha_validez_actual = None
                    
                    # Obtener valores de fechas solo si las columnas existen
                    if has_fecha and fecha_idx < len(row):
                        fecha_actual = row[fecha_idx]
                    if has_fecha_elab and fecha_elab_idx < len(row):
                        fecha_elab_actual = row[fecha_elab_idx]
                    if has_fecha_validez and fecha_validez_idx < len(row):
                        fecha_validez_actual = row[fecha_validez_idx]
                    
                    # Convertir a string y limpiar espacios
                    codprod_str = str(codprod).strip() if codprod is not None else ''
                    producto_str = str(producto).strip() if producto is not None else ''
                    fecha_elab_str = str(fecha_elab_actual).strip() if fecha_elab_actual is not None else ''
                    fecha_validez_str = str(fecha_validez_actual).strip() if fecha_validez_actual is not None else ''
                    
                    # Normalizar codprod quitando ceros a la izquierda
                    codprod_normalized = codprod_str.lstrip('0')
                    if not codprod_normalized:  # Si queda vacío después de quitar ceros
                        codprod_normalized = '0'
                    
                    # Inicializar listas para la actualización
                    updates = []
                    params = []
                    
                    # Determinar los nuevos valores basados en codprod_normalized
                    if codprod_normalized == '03':
                        new_calidad = '05'
                        new_obs = '02'
                    elif codprod_normalized == '01':
                        new_calidad = '01'
                        new_obs = '00'
                    elif codprod_normalized == '02':
                        new_calidad = '01'
                        new_obs = '01'
                    elif codprod_normalized == '04':
                        new_calidad = '01'
                        new_obs = '01'
                    elif codprod_normalized == '05':
                        new_calidad = '05'
                        new_obs = '05'
                    elif codprod_normalized == '06':
                        new_calidad = '01'
                        new_obs = '01'
                    elif codprod_normalized == '07':
                        new_calidad = '01'
                        new_obs = '00'
                    else:
                        # Si no coincide con ningún caso, usar valores por defecto
                        new_calidad = '01'
                        new_obs = '00'
                    
                    # Actualizar calidad y obs
                    updates.append("calidad = ?")
                    params.append(new_calidad)
                    updates.append("obs = ?")
                    params.append(new_obs)
                    
                    # Actualizar el campo producto si está vacío y codprod tiene al menos 2 dígitos
                    if not producto_str and len(codprod_str) >= 2:
                        # Tomar el segundo dígito de codprod (índice 1) como producto
                        new_producto = codprod_str[1] if len(codprod_str) > 1 else '0'
                        updates.append("producto = ?")
                        params.append(new_producto)
                        logging.debug(f"Actualizando producto: '{producto_str}' -> '{new_producto}' (segundo dígito de codprod='{codprod_str}')")
                    
                    # Establecer valores por defecto para fechas si están vacías
                    hoy = datetime.now().date()
                    
                    # Para el campo 'fecha' (fecha actual)
                    if has_fecha:
                        fecha_str = str(fecha_actual).strip() if fecha_actual is not None else ''
                        if not fecha_str:
                            fecha_default = hoy.strftime('%d/%m/%Y')
                            updates.append("fecha = ?")
                            params.append(fecha_default)
                            logging.debug(f"Estableciendo fecha por defecto: '{fecha_str}' -> '{fecha_default}'")
                    
                    # Para el campo 'fechaElaboracion' (usar el valor del campo fecha)
                    if has_fecha_elab and fecha_actual is not None:
                        try:
                            # Convertir la fecha a objeto datetime si es necesario
                            if isinstance(fecha_actual, str):
                                # Intentar diferentes formatos de fecha
                                for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y'):
                                    try:
                                        fecha_dt = datetime.strptime(fecha_actual, fmt)
                                        break
                                    except ValueError:
                                        continue
                                else:
                                    # Si no se pudo parsear, usar la fecha actual
                                    fecha_dt = hoy
                            else:
                                # Si ya es un objeto fecha
                                fecha_dt = fecha_actual
                            
                            # Formatear la fecha a dd/mm/yyyy
                            fecha_formateada = fecha_dt.strftime('%d/%m/%Y')
                            updates.append("fechaElaboracion = ?")
                            params.append(fecha_formateada)
                            logging.debug(f"Actualizando fechaElaboracion: '{fecha_elab_actual}' -> '{fecha_formateada}'")
                            
                            # Actualizar fechaValidezLote (fecha + 5 años)
                            if has_fecha_validez:
                                fecha_validez = (fecha_dt + timedelta(days=5*365)).strftime('%d/%m/%Y')
                                updates.append("fechaValidezLote = ?")
                                params.append(fecha_validez)
                                logging.debug(f"Actualizando fechaValidezLote: '{fecha_validez_actual}' -> '{fecha_validez}'")
                                
                        except Exception as e:
                            logging.error(f"Error al procesar fechas: {str(e)}", exc_info=True)
                    
                    logging.debug(f"Actualizando registro {rowid}: codprod='{codprod_str}' (normalizado='{codprod_normalized}') -> calidad='{new_calidad}', obs='{new_obs}'")
                    
                    # Ejecutar el UPDATE
                    update_query = f"UPDATE {table_name} SET " + ", ".join(updates) + " WHERE rowid = ?"
                    params.append(rowid)
                    self.cursor.execute(update_query, params)
                    updated_count += 1
                    
                    # Hacer commit periódicamente
                    if updated_count % 100 == 0:
                        self.connection.commit()
                        logging.debug(f"Commit parcial: {updated_count} registros actualizados")
                
                except Exception as e:
                    logging.error(f"Error al procesar el registro con rowid {rowid}: {str(e)}", exc_info=True)
                    continue
            
            # Hacer commit final
            self.connection.commit()
            logging.info(f"Proceso completado. Registros procesados: {total_processed}, actualizados: {updated_count}")
            return True
            
        except sqlite3.Error as e:
            logging.error(f"Error en la base de datos al actualizar campos de calidad: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
        except Exception as e:
            logging.error(f"Error inesperado en update_quality_fields: {str(e)}", exc_info=True)
            if self.connection:
                self.connection.rollback()
            return False

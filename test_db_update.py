#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para probar la actualización de campos de calidad y observaciones en la base de datos.
Este script verifica que los cambios se persistan correctamente en la base de datos SQLite.
"""

import os
import sys
import logging
import sqlite3
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class DbTester:
    """Clase para probar la actualización de la base de datos"""
    
    def __init__(self, db_path):
        """Inicializar con la ruta a la base de datos"""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Conectar a la base de datos"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            logging.info(f"Conectado a la base de datos: {self.db_path}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error al conectar a la base de datos: {str(e)}")
            return False
    
    def disconnect(self):
        """Cerrar la conexión a la base de datos"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            logging.info("Conexión cerrada")
    
    def get_table_info(self):
        """Obtener información sobre las tablas en la base de datos"""
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            logging.info(f"Tablas en la base de datos: {[t[0] for t in tables]}")
            
            # Buscar tabla bobina o bobinas
            bobina_table = None
            for table in tables:
                if table[0].lower() in ['bobina', 'bobinas']:
                    bobina_table = table[0]
                    break
            
            if not bobina_table:
                logging.error("No se encontró la tabla bobina o bobinas")
                return False
            
            # Obtener estructura de la tabla
            self.cursor.execute(f"PRAGMA table_info({bobina_table})")
            columns = self.cursor.fetchall()
            logging.info(f"Columnas en {bobina_table}: {[c[1] for c in columns]}")
            
            # Verificar si existen las columnas necesarias
            column_names = [c[1].lower() for c in columns]
            required_columns = ['bobina_num', 'sec', 'calidad', 'obs']
            
            for col in required_columns:
                if col not in column_names:
                    logging.error(f"Falta la columna requerida: {col}")
                    return False
            
            # Verificar columna de código de producto
            if 'codprod' in column_names:
                self.codprod_column = 'codprod'
                logging.info("Usando columna 'codprod' para código de producto")
            elif 'codigodeproducto' in column_names:
                self.codprod_column = 'codigoDeProducto'
                logging.info("Usando columna 'codigoDeProducto' para código de producto")
            else:
                logging.error("No se encontró columna para código de producto (codprod o codigoDeProducto)")
                return False
            
            self.table_name = bobina_table
            return True
        except sqlite3.Error as e:
            logging.error(f"Error al obtener información de la tabla: {str(e)}")
            return False
    
    def test_update(self):
        """Probar la actualización de calidad y observaciones"""
        try:
            # Obtener un registro de ejemplo
            self.cursor.execute(f"SELECT bobina_num, sec, calidad, obs, {self.codprod_column} FROM {self.table_name} LIMIT 1")
            row = self.cursor.fetchone()
            
            if not row:
                logging.error(f"No se encontraron registros en la tabla {self.table_name}")
                return False
            
            bobina_num, sec, calidad_orig, obs_orig, codprod_orig = row
            logging.info(f"Registro original: bobina_num={bobina_num}, sec={sec}, calidad={calidad_orig}, obs={obs_orig}, {self.codprod_column}={codprod_orig}")
            
            # Nuevos valores para probar
            calidad_new = "XX" if calidad_orig != "XX" else "YY"
            obs_new = "ZZ" if obs_orig != "ZZ" else "WW"
            
            # Modificar código de producto si es posible
            codprod_new = None
            if codprod_orig and isinstance(codprod_orig, str) and len(codprod_orig) >= 8:
                codprod_new = codprod_orig[:4] + calidad_new + obs_new + codprod_orig[8:]
                logging.info(f"Nuevo código de producto: {codprod_new}")
            
            # Ejecutar actualización
            set_clause = "calidad = ?, obs = ?"
            params = [calidad_new, obs_new]
            
            if codprod_new:
                set_clause += f", {self.codprod_column} = ?"
                params.append(codprod_new)
            
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE bobina_num = ? AND sec = ?"
            params.extend([bobina_num, sec])
            
            logging.info(f"Ejecutando: {query}")
            logging.info(f"Parámetros: {params}")
            
            self.cursor.execute(query, params)
            self.connection.commit()
            
            affected = self.cursor.rowcount
            logging.info(f"Filas afectadas: {affected}")
            
            if affected == 0:
                logging.error("No se actualizó ningún registro")
                return False
            
            # Verificar que los cambios se hayan guardado
            self.cursor.execute(f"SELECT bobina_num, sec, calidad, obs, {self.codprod_column} FROM {self.table_name} WHERE bobina_num = ? AND sec = ?", [bobina_num, sec])
            updated_row = self.cursor.fetchone()
            
            if not updated_row:
                logging.error("No se pudo recuperar el registro actualizado")
                return False
            
            _, _, calidad_updated, obs_updated, codprod_updated = updated_row
            logging.info(f"Registro actualizado: calidad={calidad_updated}, obs={obs_updated}, {self.codprod_column}={codprod_updated}")
            
            # Verificar que los valores se hayan actualizado correctamente
            if calidad_updated != calidad_new or obs_updated != obs_new:
                logging.error(f"Los valores no se actualizaron correctamente. Esperado: calidad={calidad_new}, obs={obs_new}, Actual: calidad={calidad_updated}, obs={obs_updated}")
                return False
            
            if codprod_new and codprod_updated != codprod_new:
                logging.error(f"El código de producto no se actualizó correctamente. Esperado: {codprod_new}, Actual: {codprod_updated}")
                return False
            
            # Restaurar valores originales
            self.cursor.execute(f"UPDATE {self.table_name} SET calidad = ?, obs = ?, {self.codprod_column} = ? WHERE bobina_num = ? AND sec = ?", 
                              [calidad_orig, obs_orig, codprod_orig, bobina_num, sec])
            self.connection.commit()
            logging.info("Valores originales restaurados")
            
            return True
        except sqlite3.Error as e:
            logging.error(f"Error durante la prueba de actualización: {str(e)}")
            return False

def main():
    """Función principal"""
    # Buscar la base de datos
    db_path = "produccion.db"
    if not os.path.exists(db_path):
        logging.error(f"No se encontró la base de datos en {db_path}")
        return 1
    
    # Crear y ejecutar el tester
    tester = DbTester(db_path)
    
    try:
        if not tester.connect():
            return 1
        
        if not tester.get_table_info():
            return 1
        
        if tester.test_update():
            logging.info("¡PRUEBA EXITOSA! La actualización de calidad y observaciones funciona correctamente.")
            return 0
        else:
            logging.error("La prueba de actualización falló.")
            return 1
    finally:
        tester.disconnect()

if __name__ == "__main__":
    sys.exit(main())

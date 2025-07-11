#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para depurar el problema de actualización de calidad y obs
"""

import logging
import os
import sqlite3
from database.production_models import ProductionData

logging.basicConfig(level=logging.DEBUG)

def test_update():
    """
    Prueba la actualización de calidad y obs directamente en la base de datos.
    """
    from database.db_helper import get_db_path
    db_path = get_db_path()
    logging.info(f"Usando base de datos: {db_path}")
    
    # Crear instancia de ProductionData
    prod_data = ProductionData(db_path)
    if not prod_data.connect():
        logging.error("Error al conectar a la base de datos")
        return
    
    # Verificar la estructura de la base de datos
    # 1. Encontrar el nombre real de la tabla 'bobina'
    prod_data.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND LOWER(name) IN ('bobina', 'bobinas')")
    table_info = prod_data.cursor.fetchone()
    
    if not table_info:
        # Mostrar tablas disponibles
        prod_data.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in prod_data.cursor.fetchall()]
        logging.error(f"No se encontró la tabla 'bobina' o 'bobinas'. Tablas disponibles: {', '.join(tables)}")
        prod_data.disconnect()
        return
    
    table_name = table_info[0]
    logging.info(f"Nombre real de la tabla: {table_name}")
    
    # 2. Verificar las columnas de la tabla
    columns = prod_data.get_table_columns(table_name)
    logging.info(f"Columnas de la tabla {table_name}: {columns}")
    
    # 3. Verificar que existan las columnas necesarias
    required_cols = ['bobina_num', 'sec', 'calidad', 'obs']
    for col in required_cols:
        if col not in columns:
            logging.error(f"Columna requerida '{col}' no existe en la tabla")
            prod_data.disconnect()
            return
    
    # 4. Mostrar primeros registros para referencia
    prod_data.cursor.execute(f"SELECT rowid, bobina_num, sec, calidad, obs FROM {table_name} LIMIT 5")
    rows = prod_data.cursor.fetchall()
    logging.info(f"Muestra de registros en tabla {table_name}:")
    for row in rows:
        logging.info(f"  rowid={row[0]}, bobina_num={row[1]}, sec={row[2]}, calidad={row[3]}, obs={row[4]}")
    
    if not rows:
        logging.warning("No hay registros en la tabla")
        prod_data.disconnect()
        return
    
    # 5. Intentar actualizar el primer registro
    first_record = rows[0]
    bobina_num = first_record[1]
    sec = first_record[2]
    current_calidad = first_record[3]
    current_obs = first_record[4]
    
    new_calidad = '05' if current_calidad != '05' else '01'
    new_obs = '02' if current_obs != '02' else '00'
    
    logging.info(f"Intentando actualizar registro con bobina_num={bobina_num}, sec={sec}")
    logging.info(f"Valores actuales: calidad={current_calidad}, obs={current_obs}")
    logging.info(f"Nuevos valores: calidad={new_calidad}, obs={new_obs}")
    
    # Probar actualización con update_row
    result = prod_data.update_row(
        table_name,
        ['calidad', 'obs'],
        [new_calidad, new_obs],
        ['bobina_num', 'sec'],
        [bobina_num, sec]
    )
    
    # Verificar resultado
    if result:
        logging.info("Actualización exitosa con update_row")
        
        # Verificar que los cambios se hayan guardado
        prod_data.cursor.execute(f"SELECT calidad, obs FROM {table_name} WHERE bobina_num = ? AND sec = ?", [bobina_num, sec])
        updated = prod_data.cursor.fetchone()
        
        if updated:
            logging.info(f"Valores después de la actualización: calidad={updated[0]}, obs={updated[1]}")
            if updated[0] == new_calidad and updated[1] == new_obs:
                logging.info("¡Verificación exitosa! Los valores se actualizaron correctamente.")
            else:
                logging.error("Los valores en la base de datos no coinciden con los esperados.")
        else:
            logging.error("No se pudo verificar la actualización (no se encontró el registro).")
    else:
        logging.error("La actualización con update_row falló.")
    
    # Probar actualización directa con SQL para comparar
    try:
        prod_data.cursor.execute(
            f"UPDATE {table_name} SET calidad = ?, obs = ? WHERE bobina_num = ? AND sec = ?",
            [new_calidad, new_obs, bobina_num, sec]
        )
        prod_data.connection.commit()
        affected = prod_data.cursor.rowcount
        
        logging.info(f"Actualización directa con SQL: {affected} filas afectadas")
        
        # Verificar que los cambios se hayan guardado
        prod_data.cursor.execute(f"SELECT calidad, obs FROM {table_name} WHERE bobina_num = ? AND sec = ?", [bobina_num, sec])
        updated = prod_data.cursor.fetchone()
        
        if updated:
            logging.info(f"Valores después de la actualización directa: calidad={updated[0]}, obs={updated[1]}")
    except sqlite3.Error as e:
        logging.error(f"Error en actualización directa con SQL: {str(e)}")
    
    prod_data.disconnect()

if __name__ == "__main__":
    test_update()

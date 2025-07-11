#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar las actualizaciones de calidad y observación
en la base de datos de producción.
"""

import os
import sys
import logging
import sqlite3
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Agregar la ruta del proyecto al path
script_path = Path(__file__).resolve().parent
sys.path.insert(0, str(script_path))

# Importar las clases necesarias
from database.production_models import ProductionData

def main():
    """Prueba de actualización directa de la base de datos"""
    db_path = os.path.join(script_path, 'produccion.db')
    
    # Verificar que la base de datos existe
    if not os.path.exists(db_path):
        logging.error(f"Base de datos no encontrada en {db_path}")
        return
    
    logging.info(f"Usando base de datos: {db_path}")
    
    # Crear instancia de ProductionData
    prod_data = ProductionData(db_path)
    prod_data.connect()
    
    try:
        # Verificar las tablas disponibles
        tables = prod_data.get_table_names()
        logging.info(f"Tablas disponibles: {tables}")
        
        # Encontrar la tabla de bobinas
        bobina_table = None
        for table in tables:
            if table.lower() in ['bobina', 'bobinas']:
                bobina_table = table
                break
        
        if not bobina_table:
            logging.error("No se encontró la tabla de bobinas")
            return
            
        logging.info(f"Usando tabla: {bobina_table}")
        
        # Obtener las columnas de la tabla
        columns = prod_data.get_table_columns(bobina_table)
        logging.info(f"Columnas en la tabla {bobina_table}: {columns}")
        
        # Verificar que existen las columnas necesarias
        required_cols = ['bobina_num', 'sec', 'calidad', 'obs']
        missing = [col for col in required_cols if col not in columns]
        if missing:
            logging.error(f"Faltan las siguientes columnas: {missing}")
            return
        
        # Obtener el primer registro para prueba
        prod_data.cursor.execute(f"SELECT bobina_num, sec, calidad, obs FROM {bobina_table} LIMIT 1")
        row = prod_data.cursor.fetchone()
        if not row:
            logging.error("No se encontraron registros en la tabla")
            return
            
        bobina_num, sec, calidad_orig, obs_orig = row
        logging.info(f"Registro de prueba: bobina_num={bobina_num}, sec={sec}, calidad={calidad_orig}, obs={obs_orig}")
        
        # Valores de prueba
        new_calidad = "9" if calidad_orig != "9" else "8"
        new_obs = "7" if obs_orig != "7" else "6"
        
        logging.info(f"Valores a actualizar: calidad={new_calidad}, obs={new_obs}")
        
        # Ejecutar la actualización
        result = prod_data.update_row(
            bobina_table,
            ['calidad', 'obs'],
            [new_calidad, new_obs],
            ['bobina_num', 'sec'],
            [bobina_num, sec]
        )
        
        # Verificar el resultado
        if result:
            logging.info("Actualización realizada correctamente")
            
            # Verificar que los cambios se guardaron
            prod_data.cursor.execute(f"SELECT calidad, obs FROM {bobina_table} WHERE bobina_num=? AND sec=?", 
                                   [bobina_num, sec])
            updated = prod_data.cursor.fetchone()
            
            if updated:
                logging.info(f"Valores después de actualizar: calidad={updated[0]}, obs={updated[1]}")
                
                if updated[0] == new_calidad and updated[1] == new_obs:
                    logging.info("¡Actualización verificada! Los valores coinciden.")
                else:
                    logging.error("La actualización no fue efectiva o no se guardaron los cambios correctamente.")
            else:
                logging.error("No se pudo encontrar el registro después de actualizarlo")
        else:
            logging.error("La actualización falló")
    
    except Exception as e:
        logging.error(f"Error en la prueba: {str(e)}", exc_info=True)
    finally:
        prod_data.disconnect()

if __name__ == "__main__":
    main()

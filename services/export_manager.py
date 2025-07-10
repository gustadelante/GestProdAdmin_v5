#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para la exportación de datos

Contiene funcionalidades para exportar datos a diferentes formatos.
"""

import os
import datetime
from typing import List, Dict, Any
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget


class ProductionExporter:
    """Clase para exportar datos de producción a diferentes formatos"""
    
    @staticmethod
    def export_to_txt(parent: QWidget, of: str, data: List[Dict[str, Any]], db_connection) -> bool:
        """
        Exporta datos de producción a un archivo de texto

        Args:
            parent (QWidget): Widget padre para los diálogos
            of (str): Orden de fabricación seleccionada
            data (List[Dict]): Datos a exportar
            db_connection: Conexión a la base de datos

        Returns:
            bool: True si la exportación fue exitosa, False en caso contrario
        """
        try:
            # Solicitar al usuario la ubicación del archivo
            default_filename = f"produccion_OF_{of}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath, _ = QFileDialog.getSaveFileName(
                parent,
                "Guardar archivo de exportación",
                os.path.join("c:/temp/", default_filename),
                "Archivos de texto (*.txt)"
            )
            
            if not filepath:
                return False  # Usuario canceló la operación
            
            # Abrir el archivo para escribir
            with open(filepath, 'w', encoding='utf-8') as f:
                # Para cada registro, escribir una línea con los campos requeridos
                for record in data:
                    # Extraer los campos directamente del registro
                    bobina_num = record.get('bobina_num', '')
                    sec = record.get('sec', '')
                    
                    # Campos requeridos para la exportación usando los nombres reales de la tabla
                    # Los campos en el orden requerido son:
                    # tipo_mov;tipomovimiento;01;codigodeproducto;primeraundemedida;cantidadenprimeraudm;
                    # segundaundemedida;cantidadensegunda;;;lote;fechavalidezlote;fechaelaboracion;;;;
                    # nroot;;cuentacontable;bobina_num"/"sec;turno;producto
                    
                    # Obtener valores de los campos o usar valores por defecto - usando nombres en minúsculas ya que así se guardan
                    tipo_mov = record.get('tipo_mov', 'S')  # Usar valor real o 'S' por defecto
                    tipo_movimiento = record.get('tipomovimiento', 'PRODUCCION')
                    codigo_operacion = "P1"  # Valor fijo
                    codigo_producto = record.get('codigodeproducto', '') or ''  # Clave en minúsculas y evitar None
                    primera_udm = record.get('primeraundemedida', 'KG') or 'KG'  # Clave en minúsculas y evitar None
                    # Formatear cantidad_primera con 2 decimales y coma como separador decimal (formato 9,99)
                    try:
                        # Obtener el valor numérico (intentar con cantidadenprimeramudm y si no existe usar peso)
                        valor_numerico = float(record.get('cantidadenprimeramudm', record.get('peso', 0)) or 0)
                        # Formatear con 2 decimales y reemplazar el punto por coma
                        cantidad_primera = f"{valor_numerico:.2f}".replace('.', ',')
                    except (ValueError, TypeError):
                        # Si hay error de conversión, usar 0,00 como valor por defecto
                        cantidad_primera = "0,00"
                    segunda_udm = record.get('segundaundemedida', '') or ''  # Clave en minúsculas y evitar None
                    cantidad_segunda = str(record.get('cantidadensegunda', '1') or '')  # Clave en minúsculas y evitar None
                    lote = record.get('lote', f"{of}_{bobina_num}") or f"{of}_{bobina_num}"  # Evitar None
                    fecha_validez_lote = record.get('fechavalidezlote', '') or ''  # Clave en minúsculas y evitar None
                    fecha_elaboracion = record.get('fechaelaboracion', record.get('fecha', datetime.datetime.now().strftime('%d/%m/%Y'))) or ''  # Evitar None
                    nroot = record.get('nroot', of) or of  # Usando 'nroot' en minúsculas y evitar None
                    cuenta_contable = record.get('cuentacontable', '') or ''
                    bobina_sec = f"{bobina_num}/{sec}"
                    turno = record.get('turno', '') or ''
                    producto = record.get('producto', codigo_producto) or codigo_producto or ''  # Usar producto o codigoDeProducto y evitar None
                    
                    # Construir la línea con los campos separados por punto y coma
                    line = f"{tipo_mov};{tipo_movimiento};{codigo_operacion};{codigo_producto};{primera_udm};"
                    line += f"{cantidad_primera};{segunda_udm};{cantidad_segunda};;;"
                    line += f"{lote};{fecha_validez_lote};{fecha_elaboracion};;;;"
                    line += f"{nroot};;{cuenta_contable};{bobina_sec};{turno};;{producto}"  # Agregado un campo vacío adicional entre turno y producto
                    
                    # Escribir la línea en el archivo
                    f.write(line + '\n')
            
            QMessageBox.information(
                parent,
                "Exportación Completada",
                f"Los datos de la OF {of} se han exportado correctamente a:\n{filepath}"
            )
            return True
            
        except Exception as e:
            QMessageBox.critical(
                parent,
                "Error de Exportación",
                f"Error al exportar los datos: {str(e)}"
            )
            return False

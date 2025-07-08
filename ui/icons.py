#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de iconos

Contiene definiciones de iconos SVG para la interfaz de usuario.
"""

# Iconos Material Design en formato SVG

# Icono de agregar (plus)
ADD_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24">
    <path d="M0 0h24v24H0z" fill="none"/>
    <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
</svg>
"""

# Icono de editar (edit)
EDIT_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24">
    <path d="M0 0h24v24H0z" fill="none"/>
    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
</svg>
"""

# Icono de eliminar (delete)
DELETE_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24">
    <path d="M0 0h24v24H0z" fill="none"/>
    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
</svg>
"""

# Icono de limpiar (clear)
CLEAR_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24">
    <path d="M0 0h24v24H0z" fill="none"/>
    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
</svg>
"""

# Icono de copiar (copy)
COPY_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24">
    <circle cx="12" cy="12" r="12" fill="#2196F3"/>
    <path d="M0 0h24v24H0z" fill="none"/>
    <path d="M16 8h-4v8h6v-6l-2-2zm-1 0v2h2v-2h-2z" fill="white"/>
    <path d="M12 6H8v8h2v-6h2V6z" fill="white"/>
    <path d="M10 9h2v1h-2z" fill="white"/>
    <path d="M10 11h2v1h-2z" fill="white"/>
    <path d="M13 11h2v1h-2z" fill="white"/>
    <path d="M13 13h2v1h-2z" fill="white"/>
</svg>
"""




from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtCore import QByteArray, Qt

def svg_to_icon(svg_content, color="white", size=24):
    """
    Convierte un SVG a un formato que puede ser utilizado como icono en PySide6.
    Args:
        svg_content (str): Contenido SVG
        color (str): Color opcional para reemplazar el color base del SVG
        size (int): Tamaño del icono en píxeles
    Returns:
        QIcon: Icono generado a partir del SVG
    """
    # Reemplazar el color si es necesario
    if color and color != "white":
        svg_content = svg_content.replace("#fff", color).replace("#ffffff", color)
    svg_bytes = QByteArray(svg_content.encode("utf-8"))
    renderer = QSvgRenderer(svg_bytes)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

def svg_to_icon_with_color(svg_content, color):
    # Reemplazar el color de relleno en todos los paths excepto los que tienen fill="none"
    svg_with_color = svg_content.replace('<path d="M0 0h24v24H0z" fill="none"/>', 
                                        '<path d="M0 0h24v24H0z" fill="none"/>')
    
    # Buscar todos los paths que no tienen un atributo fill y agregarles el color
    svg_with_color = svg_with_color.replace('<path d="', f'<path fill="{color}" d="')
    
    return svg_with_color

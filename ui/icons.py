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

def svg_to_icon(svg_content, color="white"):
    """
    Convierte un SVG a un formato que puede ser utilizado como icono en PySide6
    
    Args:
        svg_content (str): Contenido SVG
        color (str): Color del icono (por defecto blanco para mejor contraste en botones)
        
    Returns:
        str: SVG modificado para usar como icono
    """
    # Reemplazar el color de relleno en todos los paths excepto los que tienen fill="none"
    svg_with_color = svg_content.replace('<path d="M0 0h24v24H0z" fill="none"/>', 
                                        '<path d="M0 0h24v24H0z" fill="none"/>')
    
    # Buscar todos los paths que no tienen un atributo fill y agregarles el color
    svg_with_color = svg_with_color.replace('<path d="', f'<path fill="{color}" d="')
    
    return svg_with_color

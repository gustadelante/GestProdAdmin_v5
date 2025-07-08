import re

# Ruta al archivo a modificar
file_path = r'd:\desarrollo\GestProdAdmin_v4\ui\production_dialog.py'

# Leer el contenido actual
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Hacer que los combos sean editables
content = content.replace("widget.setEditable(False)", "widget.setEditable(True)")

# 2. Eliminar la lógica de solo lectura basada en is_read_only
content = re.sub(r'\s*is_read_only\s*=\s*self\.is_edit_mode\s*and\s*row_data\s*and\s*col_idx\s*<\s*len\(row_data\)\s*and\s*row_data\[col_idx\]\s*is not None\s*\n', '', content)

# 3. Asegurar que los combos tengan la propiedad de autocompletado
content = content.replace("widget = QComboBox()", "widget = QComboBox()\n                widget.setEditable(True)\n                widget.setInsertPolicy(QComboBox.NoInsert)")

# 4. Añadir el import necesario para QComboBox si no existe
if "from PySide6.QtWidgets import" in content and "QComboBox" not in content:
    content = content.replace(
        "from PySide6.QtWidgets import (",
        "from PySide6.QtWidgets import (QComboBox, "
    )

# Escribir el archivo modificado
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Archivo modificado exitosamente. Todos los campos ahora son editables.")

import re

# Ruta al archivo a modificar
file_path = r'd:\desarrollo\GestProdAdmin_v4\ui\production_dialog.py'

# Leer el contenido actual
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Patrón para encontrar y modificar el campo descprod
pattern = r'(elif\s+col_name_lower\s*==\s*["\']descprod["\']:.*?widget\s*=\s*QLineEdit\(\)\s*)\n\s*widget\.setReadOnly\(True\)(\s*\n\s*self\.descprod_widget\s*=\s*widget)'
replacement = r'\1\2'

# Realizar el reemplazo
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Escribir el archivo modificado
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Archivo modificado exitosamente.")

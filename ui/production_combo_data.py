import os
import json

def load_combo_data():
    """
    Carga los datos de combos desde variablesCodProd.json
    Returns:
        dict: Diccionario con claves 'Calidad' y 'Observaciones'
    """
    combo_data = {"Calidad": [], "Observaciones": []}
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'variablesCodProd.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            combo_data["Calidad"] = data.get("Calidad", [])
            combo_data["Observaciones"] = data.get("Observaciones", [])
    except Exception as e:
        print(f"[ERROR] No se pudo cargar variablesCodProd.json: {e}")
    return combo_data

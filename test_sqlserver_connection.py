#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de prueba para validar la conexión a SQL Server

Verifica:
1. Conectividad del servidor (socket)
2. Conexión a SQL Server con pyodbc
3. Ejecución de la consulta de clientes
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from config.sqlserver_config import SQLServerConfig
from database.sqlserver_utils import check_server_online
from database.sqlserver_cliente_repository import SQLServerClienteRepository


def main():
    """Función principal de prueba"""
    print("=" * 60)
    print("PRUEBA DE CONEXIÓN A SQL SERVER")
    print("=" * 60)
    
    # Cargar configuración
    config = SQLServerConfig()
    server = config.get_server_address()
    port = config.get_port()
    
    print(f"\n1. Configuracion cargada:")
    print(f"   - Archivo config: {config.config_file}")
    print(f"   - Archivo existe: {config.config_file.exists()}")
    print(f"   - Servidor: {server}")
    print(f"   - Puerto: {port}")
    print(f"   - Base de datos: {config.config.get('database')}")
    print(f"   - Usuario: {config.config.get('username')}")
    
    # Verificar conectividad del servidor
    print(f"\n2. Verificando conectividad del servidor {server}:{port}...")
    is_online, message = check_server_online(server, port, timeout=5)
    
    if not is_online:
        print(f"   [X] ERROR: {message}")
        print("\n   Posibles causas:")
        print("   - La VPN está activa?")
        print("   - Hay un firewall bloqueando el puerto 1433")
        print("   - La direccion IP es incorrecta")
        return 1
    
    print(f"   [OK] {message}")
    
    # Intentar conectar a SQL Server
    print(f"\n3. Conectando a SQL Server...")
    connection_string = config.get_connection_string()
    
    try:
        repo = SQLServerClienteRepository(connection_string)
        success, msg = repo.test_connection()
        
        if not success:
            print(f"   [X] ERROR: {msg}")
            print("\n   Posibles causas:")
            print("   - Credenciales incorrectas")
            print("   - Base de datos no existe")
            print("   - Usuario no tiene permisos")
            print("   - Driver ODBC no instalado")
            return 1
        
        print(f"   [OK] Conexion exitosa")
        print(f"   {msg}")
        
    except ImportError as e:
        print(f"   [X] ERROR: pyodbc no esta instalado")
        print(f"   Instale con: pip install pyodbc")
        return 1
    except Exception as e:
        print(f"   [X] ERROR: {str(e)}")
        return 1
    
    # Ejecutar consulta de clientes
    print(f"\n4. Ejecutando consulta de clientes...")
    cliente_query = """
        SELECT DISTINCT A1_COD AS CODCLIENTE,
                        A1_NOME AS NOMBRE 
        FROM SA1010
        WHERE A1_LOJA = '01'
    """
    
    try:
        with SQLServerClienteRepository(connection_string) as repo:
            clientes = repo.get_clientes(cliente_query)
            
            if not clientes:
                print(f"   [!] ADVERTENCIA: La consulta no retorno resultados")
                print(f"   Verifique que la tabla SA1010 existe y tiene datos")
                return 1
            
            print(f"   [OK] Consulta exitosa")
            print(f"   Se obtuvieron {len(clientes)} clientes")
            
            # Mostrar los primeros 5 clientes
            print(f"\n5. Primeros clientes encontrados:")
            for i, (codigo, nombre) in enumerate(clientes[:5], 1):
                print(f"   {i}. {codigo} - {nombre}")
            
            if len(clientes) > 5:
                print(f"   ... y {len(clientes) - 5} más")
    
    except Exception as e:
        print(f"   [X] ERROR al ejecutar consulta: {str(e)}")
        return 1
    
    print("\n" + "=" * 60)
    print("[OK] TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    print("=" * 60)
    print("\nLa aplicacion esta lista para cargar clientes desde SQL Server")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

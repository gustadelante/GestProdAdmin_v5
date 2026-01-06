#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de utilidades para SQL Server

Contiene funciones de utilidad para trabajar con SQL Server.
"""

import socket
import logging
from typing import Tuple

logging.basicConfig(level=logging.DEBUG)


def check_server_online(server_address: str, port: int = 1433, timeout: int = 3) -> Tuple[bool, str]:
    """
    Verifica si el servidor SQL Server está online
    
    Args:
        server_address: Dirección IP o nombre del servidor
        port: Puerto del servidor (por defecto 1433)
        timeout: Tiempo de espera en segundos
        
    Returns:
        Tupla (is_online, message) donde is_online es True si el servidor responde
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((server_address, port))
        sock.close()
        
        if result == 0:
            logging.info(f"Servidor {server_address}:{port} está online")
            return True, f"Servidor {server_address} está online"
        else:
            logging.warning(f"Servidor {server_address}:{port} no responde")
            return False, f"Servidor {server_address} no responde en el puerto {port}"
            
    except socket.gaierror:
        msg = f"No se pudo resolver la dirección {server_address}"
        logging.error(msg)
        return False, msg
    except socket.timeout:
        msg = f"Tiempo de espera agotado al conectar a {server_address}:{port}"
        logging.error(msg)
        return False, msg
    except Exception as e:
        msg = f"Error al verificar conectividad: {str(e)}"
        logging.error(msg)
        return False, msg

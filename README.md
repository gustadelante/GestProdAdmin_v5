# GestProdAdmin

Aplicación de gestión de producción para entornos de red LAN con interfaz moderna desarrollada en Python.

## Características

- **Interfaz Moderna**: Diseño basado en Material Design con PySide6
- **Temas Claro y Oscuro**: Cambia entre temas con un solo clic
- **Menú Lateral Ocultable**: Interfaz adaptable con animaciones fluidas
- **Gestión de Usuarios**: Administración completa de usuarios, roles y permisos
- **Dashboard Informativo**: Panel principal con información relevante
- **Base de Datos MariaDB**: Almacenamiento robusto y confiable
- **Arquitectura Modular**: Código organizado en capas para fácil mantenimiento

## Requisitos

- Python 3.8 o superior
- MariaDB 10.5 o superior
- Paquetes Python (ver requirements.txt)

## Estructura del Proyecto

```
GestProdAdmin_v3/
├── config/             # Configuración de la aplicación
├── database/           # Modelos y conexión a la base de datos
├── security/           # Autenticación y autorización
├── ui/                 # Componentes de la interfaz de usuario
├── main.py             # Punto de entrada de la aplicación
└── README.md           # Este archivo
```

## Configuración

### Base de Datos

1. Instalar MariaDB
2. Crear una base de datos llamada `prod01`
3. Configurar usuario `root` con contraseña `pepe01` o modificar los datos de conexión en `config/settings.py`

### Entorno Python

1. Crear un entorno virtual:
   ```
   python -m venv .venv
   ```

2. Activar el entorno virtual:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

3. Instalar dependencias:
   ```
   pip install PySide6 SQLAlchemy pymysql cryptography
   ```

## Ejecución

```
python main.py
```

## Módulos Principales

### Seguridad

El módulo de seguridad gestiona la autenticación de usuarios, roles y permisos. Permite controlar el acceso a diferentes partes de la aplicación según los permisos asignados a cada rol.

### Base de Datos

Utiliza SQLAlchemy como ORM para interactuar con MariaDB. Los modelos incluyen:
- Usuarios
- Roles
- Permisos

### Interfaz de Usuario

Desarrollada con PySide6, incluye:
- Ventana principal con menú lateral
- Dashboard informativo
- Gestión de usuarios, roles y permisos
- Temas claro y oscuro

## Desarrollo

Para contribuir al proyecto:

1. Clonar el repositorio
2. Crear un entorno virtual y configurar dependencias
3. Realizar cambios siguiendo la arquitectura modular
4. Probar los cambios antes de enviar

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

# GestProdAdmin v5

Aplicación de gestión de producción con interfaz moderna desarrollada en Python. Versión simplificada sin autenticación de usuarios.

## Características

- **Interfaz Moderna**: Diseño basado en Material Design con PySide6
- **Temas Claro y Oscuro**: Cambia entre temas con un solo clic
- **Menú Lateral Ocultable**: Interfaz adaptable con animaciones fluidas
- **Dashboard Informativo**: Panel principal con información relevante
- **Base de Datos SQLite**: Almacenamiento local sin necesidad de servidor
- **Arquitectura Modular**: Código organizado en capas para fácil mantenimiento
- **Sin Autenticación**: Acceso directo a todas las funciones sin inicio de sesión

## Requisitos

- Para desarrollo:
  - Python 3.8 o superior
  - Paquetes Python (ver requirements.txt)
- Para uso del ejecutable:
  - Windows 10/11

## Estructura del Proyecto

```
GestProdAdmin_v5/
├── config/             # Configuración de la aplicación
├── database/           # Modelos y conexión a la base de datos
├── security/           # Componentes de seguridad (deshabilitados)
├── services/           # Servicios de la aplicación
├── ui/                 # Componentes de la interfaz de usuario
├── build_exe.py        # Script para crear el ejecutable
├── main.py             # Punto de entrada de la aplicación
├── produccion.db       # Base de datos SQLite
└── README.md           # Este archivo
```

## Configuración para Desarrollo

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
   pip install -r requirements.txt
   ```

4. Ejecutar la aplicación:
   ```
   python main.py
   ```

## Construcción del Ejecutable

El script `build_exe.py` permite crear dos versiones del ejecutable:

1. **Versión con base de datos externa** (recomendada para uso diario):
   - La base de datos se mantiene fuera del ejecutable para facilitar actualizaciones
   - Comando: `python build_exe.py --external-db`

2. **Versión todo incluido**:
   - Todo empaquetado en un solo directorio
   - Comando: `python build_exe.py --all-in-one`

3. **Opciones adicionales**:
   - Para crear un único archivo ejecutable: `python build_exe.py --onefile`
   - Para crear ambas versiones: `python build_exe.py` (sin argumentos)

### Ubicación de los Ejecutables

Los ejecutables se crean en la carpeta `dist/`:
- Versión con base de datos externa: `dist/GestProdAdmin_ExternalDB/`
- Versión todo incluido: `dist/GestProdAdmin/`

## Implementación y Uso

### Versión con Base de Datos Externa

1. Copie la carpeta `dist/GestProdAdmin_ExternalDB/` a la ubicación deseada
2. Asegúrese de que el archivo `produccion.db` esté en la misma carpeta que el ejecutable
3. Para actualizar la base de datos, simplemente reemplace el archivo `produccion.db`

### Versión Todo Incluido

1. Copie la carpeta `dist/GestProdAdmin/` a la ubicación deseada
2. La base de datos está incluida dentro del ejecutable
3. Para actualizaciones, deberá reemplazar todo el ejecutable

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

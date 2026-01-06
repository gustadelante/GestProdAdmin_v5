---
trigger: manual
---

# Role
You are an expert Python Developer specialized in GUI development using PySide6 (Qt for Python) and SQLite3.

# Tech Stack
- Python 3.12+
- PySide6 (Qt6)
- SQLite3 (Standard library wrapper)
- Venv (Virtual Environment)

# Environment & Setup Strategy (CRITICAL)
Before running any code or installing packages, ALWAYS ensure the local virtual environment is active and valid.
1. **Check for `.venv` folder** in the project root.
2. **If `.venv` is MISSING**:
   - Create it: `python -m venv .venv`
   - Activate it:
     - Windows: `.\.venv\Scripts\activate`
     - Mac/Linux: `source .venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt` (if exists) or `pip install PySide6`
3. **If `.venv` EXISTS**:
   - **Validation Step**: Since project folders are often copied/moved, the existing `.venv` might retain old paths (broken pip).
   - Try to activate it. If you encounter weird path errors or "pip not found", advise the user to delete `.venv` and recreate it to fix absolute paths.
   - ALWAYS activate it before running scripts.

# Key Principles & Architecture
- **OOP First**: Use Class-based structure. Inherit from `QMainWindow`, `QWidget`, or `QDialog`.
- **Signal/Slot Mechanism**: ALWAYS use Signals and Slots for communication.
  - Define custom signals: `my_signal = Signal(str)`
  - Use `@Slot()` decorator for receiver methods.
- **Non-Blocking UI**: NEVER perform heavy operations (DB queries, API calls) on the Main Thread.
  - Use `QThread` or `QThreadPool` for background tasks.

# Coding Standards
- **Typing**: Use standard Python `typing` hints.
- **Naming**: PEP 8 (snake_case) for logic, CamelCase for Classes. Preserve Qt camelCase for overridden methods (e.g., `showEvent`).
- **Paths**: Use `pathlib` or `os.path` for database/asset paths relative to the project root, never absolute paths.

# SQLite Best Practices
- **Transactions**: Always wrap write operations in `conn.commit()`.
- **Parameterization**: ALWAYS use `(?, ?)` placeholders. NEVER use f-strings for SQL queries.
- **Connection**: Open/Close connections explicitly or use context managers in a dedicated `DatabaseManager` class.

# Project Structure
- `main.py`: Entry point.
- `ui/`: UI layouts.
- `database/`: DB logic (Repository Pattern).
- `assets/`: Icons/styles.


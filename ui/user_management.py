#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de gestión de usuarios

Contiene la implementación del widget de gestión de usuarios, roles y permisos.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QTabWidget, QFormLayout, QLineEdit, QComboBox,
    QMessageBox, QDialog, QDialogButtonBox, QCheckBox, QListWidget,
    QGroupBox, QScrollArea, QFrame, QSplitter, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, Slot, QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem

from sqlalchemy.exc import SQLAlchemyError
from database.models import User, Role, Permission


class UserManagementWidget(QWidget):
    """Widget para la gestión de usuarios, roles y permisos"""
    
    def __init__(self, parent=None):
        """Inicializa el widget de gestión de usuarios
        
        Args:
            parent (QWidget, optional): Widget padre
        """
        super().__init__(parent)
        self.auth_manager = None
        self.db_connection = None
        
        # Inicializar la interfaz
        self.init_ui()
    
    def init_ui(self):
        """Inicializa los componentes de la interfaz"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Pestañas para usuarios, roles y permisos
        self.tabs = QTabWidget()
        self.tabs.setObjectName("userManagementTabs")
        
        # Pestaña de usuarios
        self.users_tab = QWidget()
        self.setup_users_tab()
        self.tabs.addTab(self.users_tab, "Usuarios")
        
        # Pestaña de roles
        self.roles_tab = QWidget()
        self.setup_roles_tab()
        self.tabs.addTab(self.roles_tab, "Roles")
        
        # Pestaña de permisos
        self.permissions_tab = QWidget()
        self.setup_permissions_tab()
        self.tabs.addTab(self.permissions_tab, "Permisos")
        
        # Pestaña de asignación de permisos a roles
        self.role_permissions_tab = QWidget()
        self.setup_role_permissions_tab()
        self.tabs.addTab(self.role_permissions_tab, "Asignación de Permisos")
        
        main_layout.addWidget(self.tabs)
    
    def setup_users_tab(self):
        """Configura la pestaña de gestión de usuarios"""
        layout = QVBoxLayout(self.users_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.btn_add_user = QPushButton("Agregar Usuario")
        self.btn_add_user.setObjectName("btnAddUser")
        self.btn_add_user.clicked.connect(self.show_add_user_dialog)
        
        self.btn_edit_user = QPushButton("Editar Usuario")
        self.btn_edit_user.setObjectName("btnEditUser")
        self.btn_edit_user.clicked.connect(self.show_edit_user_dialog)
        
        self.btn_delete_user = QPushButton("Eliminar Usuario")
        self.btn_delete_user.setObjectName("btnDeleteUser")
        self.btn_delete_user.clicked.connect(self.delete_user)
        
        buttons_layout.addWidget(self.btn_add_user)
        buttons_layout.addWidget(self.btn_edit_user)
        buttons_layout.addWidget(self.btn_delete_user)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Tabla de usuarios
        self.users_table = QTableView()
        self.users_table.setObjectName("usersTable")
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSelectionBehavior(QTableView.SelectRows)
        self.users_table.setSelectionMode(QTableView.SingleSelection)
        self.users_table.setEditTriggers(QTableView.NoEditTriggers)
        
        # Modelo para la tabla de usuarios
        self.users_model = QStandardItemModel(0, 5, self)
        self.users_model.setHorizontalHeaderLabels(["ID", "Usuario", "Nombre Completo", "Email", "Rol"])
        
        # Filtro para búsqueda
        self.users_proxy_model = QSortFilterProxyModel(self)
        self.users_proxy_model.setSourceModel(self.users_model)
        self.users_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.users_proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas
        
        self.users_table.setModel(self.users_proxy_model)
        
        layout.addWidget(self.users_table)
    
    def setup_roles_tab(self):
        """Configura la pestaña de gestión de roles"""
        layout = QVBoxLayout(self.roles_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.btn_add_role = QPushButton("Agregar Rol")
        self.btn_add_role.setObjectName("btnAddRole")
        self.btn_add_role.clicked.connect(self.show_add_role_dialog)
        
        self.btn_edit_role = QPushButton("Editar Rol")
        self.btn_edit_role.setObjectName("btnEditRole")
        self.btn_edit_role.clicked.connect(self.show_edit_role_dialog)
        
        self.btn_delete_role = QPushButton("Eliminar Rol")
        self.btn_delete_role.setObjectName("btnDeleteRole")
        self.btn_delete_role.clicked.connect(self.delete_role)
        
        buttons_layout.addWidget(self.btn_add_role)
        buttons_layout.addWidget(self.btn_edit_role)
        buttons_layout.addWidget(self.btn_delete_role)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Tabla de roles
        self.roles_table = QTableView()
        self.roles_table.setObjectName("rolesTable")
        self.roles_table.setAlternatingRowColors(True)
        self.roles_table.setSelectionBehavior(QTableView.SelectRows)
        self.roles_table.setSelectionMode(QTableView.SingleSelection)
        self.roles_table.setEditTriggers(QTableView.NoEditTriggers)
        
        # Modelo para la tabla de roles
        self.roles_model = QStandardItemModel(0, 3, self)
        self.roles_model.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción"])
        
        # Filtro para búsqueda
        self.roles_proxy_model = QSortFilterProxyModel(self)
        self.roles_proxy_model.setSourceModel(self.roles_model)
        self.roles_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.roles_proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas
        
        self.roles_table.setModel(self.roles_proxy_model)
        
        layout.addWidget(self.roles_table)
    
    def setup_permissions_tab(self):
        """Configura la pestaña de gestión de permisos"""
        layout = QVBoxLayout(self.permissions_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.btn_add_permission = QPushButton("Agregar Permiso")
        self.btn_add_permission.setObjectName("btnAddPermission")
        self.btn_add_permission.clicked.connect(self.show_add_permission_dialog)
        
        self.btn_edit_permission = QPushButton("Editar Permiso")
        self.btn_edit_permission.setObjectName("btnEditPermission")
        self.btn_edit_permission.clicked.connect(self.show_edit_permission_dialog)
        
        self.btn_delete_permission = QPushButton("Eliminar Permiso")
        self.btn_delete_permission.setObjectName("btnDeletePermission")
        self.btn_delete_permission.clicked.connect(self.delete_permission)
        
        buttons_layout.addWidget(self.btn_add_permission)
        buttons_layout.addWidget(self.btn_edit_permission)
        buttons_layout.addWidget(self.btn_delete_permission)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Tabla de permisos
        self.permissions_table = QTableView()
        self.permissions_table.setObjectName("permissionsTable")
        self.permissions_table.setAlternatingRowColors(True)
        self.permissions_table.setSelectionBehavior(QTableView.SelectRows)
        self.permissions_table.setSelectionMode(QTableView.SingleSelection)
        self.permissions_table.setEditTriggers(QTableView.NoEditTriggers)
        
        # Modelo para la tabla de permisos
        self.permissions_model = QStandardItemModel(0, 4, self)
        self.permissions_model.setHorizontalHeaderLabels(["ID", "Nombre", "Código", "Descripción"])
        
        # Filtro para búsqueda
        self.permissions_proxy_model = QSortFilterProxyModel(self)
        self.permissions_proxy_model.setSourceModel(self.permissions_model)
        self.permissions_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.permissions_proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas
        
        self.permissions_table.setModel(self.permissions_proxy_model)
        
        layout.addWidget(self.permissions_table)
    
    def setup_role_permissions_tab(self):
        """Configura la pestaña de asignación de permisos a roles"""
        layout = QVBoxLayout(self.role_permissions_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Crear un splitter para dividir la pantalla
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo: Lista de roles
        roles_panel = QWidget()
        roles_layout = QVBoxLayout(roles_panel)
        roles_layout.setContentsMargins(0, 0, 0, 0)
        
        roles_label = QLabel("Roles")
        roles_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        roles_layout.addWidget(roles_label)
        
        self.roles_list = QListWidget()
        self.roles_list.setAlternatingRowColors(True)
        self.roles_list.currentRowChanged.connect(self.on_role_selected)
        roles_layout.addWidget(self.roles_list)
        
        # Panel derecho: Permisos del rol seleccionado
        permissions_panel = QWidget()
        permissions_layout = QVBoxLayout(permissions_panel)
        permissions_layout.setContentsMargins(0, 0, 0, 0)
        
        permissions_label = QLabel("Permisos")
        permissions_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        permissions_layout.addWidget(permissions_label)
        
        # Área de desplazamiento para los permisos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.permissions_container = QWidget()
        self.permissions_layout = QVBoxLayout(self.permissions_container)
        self.permissions_layout.setContentsMargins(0, 0, 0, 0)
        self.permissions_layout.setSpacing(5)
        self.permissions_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(self.permissions_container)
        permissions_layout.addWidget(scroll_area)
        
        # Botón para guardar cambios
        self.btn_save_permissions = QPushButton("Guardar Cambios")
        self.btn_save_permissions.setObjectName("btnSavePermissions")
        self.btn_save_permissions.clicked.connect(self.save_role_permissions)
        permissions_layout.addWidget(self.btn_save_permissions)
        
        # Agregar paneles al splitter
        splitter.addWidget(roles_panel)
        splitter.addWidget(permissions_panel)
        splitter.setSizes([200, 400])  # Tamaños iniciales
        
        layout.addWidget(splitter)
    
    def set_auth_manager(self, auth_manager):
        """Establece el gestor de autenticación y carga los datos
        
        Args:
            auth_manager (AuthManager): Gestor de autenticación
        """
        self.auth_manager = auth_manager
        self.db_connection = auth_manager.db_connection
        
        # Cargar datos iniciales
        self.load_users()
        self.load_roles()
        self.load_permissions()
        self.load_role_permissions()
    
    def load_users(self):
        """Carga los usuarios desde la base de datos"""
        if not self.db_connection:
            return
        
        # Limpiar modelo
        self.users_model.removeRows(0, self.users_model.rowCount())
        
        session = self.db_connection.get_session()
        try:
            users = session.query(User).all()
            
            for user in users:
                row = [
                    QStandardItem(str(user.id)),
                    QStandardItem(user.username),
                    QStandardItem(user.full_name),
                    QStandardItem(user.email),
                    QStandardItem(user.role.name if user.role else "Sin rol")
                ]
                self.users_model.appendRow(row)
                
            # Ajustar columnas
            self.users_table.resizeColumnsToContents()
        except SQLAlchemyError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar usuarios: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)
    
    def load_roles(self):
        """Carga los roles desde la base de datos"""
        if not self.db_connection:
            return
        
        # Limpiar modelo
        self.roles_model.removeRows(0, self.roles_model.rowCount())
        
        session = self.db_connection.get_session()
        try:
            roles = session.query(Role).all()
            
            for role in roles:
                row = [
                    QStandardItem(str(role.id)),
                    QStandardItem(role.name),
                    QStandardItem(role.description or "")
                ]
                self.roles_model.appendRow(row)
                
            # Ajustar columnas
            self.roles_table.resizeColumnsToContents()
        except SQLAlchemyError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar roles: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)
    
    def load_permissions(self):
        """Carga los permisos desde la base de datos"""
        if not self.db_connection:
            return
        
        # Limpiar modelo
        self.permissions_model.removeRows(0, self.permissions_model.rowCount())
        
        session = self.db_connection.get_session()
        try:
            permissions = session.query(Permission).all()
            
            for permission in permissions:
                row = [
                    QStandardItem(str(permission.id)),
                    QStandardItem(permission.name),
                    QStandardItem(permission.code),
                    QStandardItem(permission.description or "")
                ]
                self.permissions_model.appendRow(row)
                
            # Ajustar columnas
            self.permissions_table.resizeColumnsToContents()
        except SQLAlchemyError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar permisos: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)
    
    def load_role_permissions(self):
        """Carga los roles para la pestaña de asignación de permisos"""
        if not self.db_connection:
            return
        
        # Limpiar lista de roles
        self.roles_list.clear()
        
        session = self.db_connection.get_session()
        try:
            roles = session.query(Role).all()
            
            for role in roles:
                self.roles_list.addItem(role.name)
                # Almacenar el ID del rol como dato del item
                item = self.roles_list.item(self.roles_list.count() - 1)
                item.setData(Qt.UserRole, role.id)
            
            # Seleccionar el primer rol si existe
            if self.roles_list.count() > 0:
                self.roles_list.setCurrentRow(0)
        
        except SQLAlchemyError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar roles: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)
    
    def on_role_selected(self, row):
        """Maneja la selección de un rol en la lista
        
        Args:
            row (int): Índice de la fila seleccionada
        """
        if row < 0 or not self.db_connection:
            return
        
        # Limpiar los checkboxes de permisos
        self.clear_permissions_layout()
        
        # Obtener el ID del rol seleccionado
        role_id = self.roles_list.item(row).data(Qt.UserRole)
        
        session = self.db_connection.get_session()
        try:
            # Obtener el rol con sus permisos
            role = session.query(Role).filter(Role.id == role_id).first()
            if not role:
                return
            
            # Obtener todos los permisos disponibles
            all_permissions = session.query(Permission).all()
            
            # Crear un grupo para los permisos
            permissions_group = QGroupBox(f"Permisos para el rol: {role.name}")
            permissions_group_layout = QVBoxLayout(permissions_group)
            
            # Crear checkboxes para cada permiso
            for permission in all_permissions:
                checkbox = QCheckBox(f"{permission.name} ({permission.code})")
                checkbox.setToolTip(permission.description or "")
                
                # Marcar el checkbox si el rol tiene este permiso
                checkbox.setChecked(permission in role.permissions)
                
                # Almacenar el ID del permiso como dato del checkbox
                checkbox.setProperty("permission_id", permission.id)
                
                permissions_group_layout.addWidget(checkbox)
            
            # Agregar el grupo al layout de permisos
            self.permissions_layout.addWidget(permissions_group)
            
        except SQLAlchemyError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar permisos del rol: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)
    
    def clear_permissions_layout(self):
        """Limpia el layout de permisos"""
        # Eliminar todos los widgets del layout
        while self.permissions_layout.count():
            item = self.permissions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def save_role_permissions(self):
        """Guarda los permisos asignados al rol seleccionado"""
        if not self.db_connection:
            return
        
        # Obtener el rol seleccionado
        selected_row = self.roles_list.currentRow()
        if selected_row < 0:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor, seleccione un rol para asignar permisos."
            )
            return
        
        role_id = self.roles_list.item(selected_row).data(Qt.UserRole)
        
        # Obtener los permisos seleccionados
        selected_permissions = []
        
        # Buscar el grupo de permisos (debe ser el primer widget en el layout)
        if self.permissions_layout.count() > 0:
            group = self.permissions_layout.itemAt(0).widget()
            if isinstance(group, QGroupBox):
                group_layout = group.layout()
                
                # Recorrer todos los checkboxes
                for i in range(group_layout.count()):
                    widget = group_layout.itemAt(i).widget()
                    if isinstance(widget, QCheckBox) and widget.isChecked():
                        permission_id = widget.property("permission_id")
                        if permission_id:
                            selected_permissions.append(permission_id)
        
        # Guardar los cambios en la base de datos
        session = self.db_connection.get_session()
        try:
            # Obtener el rol
            role = session.query(Role).filter(Role.id == role_id).first()
            if not role:
                return
            
            # Obtener los permisos seleccionados
            permissions = session.query(Permission).filter(Permission.id.in_(selected_permissions)).all()
            
            # Actualizar los permisos del rol
            role.permissions = permissions
            
            session.commit()
            
            QMessageBox.information(
                self,
                "Permisos Actualizados",
                f"Los permisos para el rol '{role.name}' han sido actualizados correctamente."
            )
            
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar permisos: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)
    
    # Métodos para gestionar usuarios
    def show_add_user_dialog(self):
        """Muestra el diálogo para agregar un nuevo usuario"""
        dialog = UserDialog(self, self.db_connection)
        if dialog.exec():
            self.load_users()
    
    def show_edit_user_dialog(self):
        """Muestra el diálogo para editar un usuario existente"""
        # Obtener el usuario seleccionado
        selected = self.users_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor, seleccione un usuario para editar."
            )
            return
        
        # Obtener el ID del usuario
        index = self.users_proxy_model.mapToSource(selected[0])
        user_id = int(self.users_model.item(index.row(), 0).text())
        
        # Mostrar diálogo de edición
        dialog = UserDialog(self, self.db_connection, user_id)
        if dialog.exec():
            self.load_users()
    
    def delete_user(self):
        """Elimina un usuario seleccionado"""
        # Obtener el usuario seleccionado
        selected = self.users_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor, seleccione un usuario para eliminar."
            )
            return
        
        # Confirmar eliminación
        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar este usuario?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Obtener el ID del usuario
        index = self.users_proxy_model.mapToSource(selected[0])
        user_id = int(self.users_model.item(index.row(), 0).text())
        
        # Eliminar usuario
        session = self.db_connection.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                self.load_users()
                QMessageBox.information(
                    self,
                    "Usuario Eliminado",
                    "El usuario ha sido eliminado correctamente."
                )
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(
                self,
                "Error",
                f"Error al eliminar usuario: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)
    
    # Métodos para gestionar roles
    def show_add_role_dialog(self):
        """Muestra el diálogo para agregar un nuevo rol"""
        dialog = RoleDialog(self, self.db_connection)
        if dialog.exec():
            self.load_roles()
    
    def show_edit_role_dialog(self):
        """Muestra el diálogo para editar un rol existente"""
        # Obtener el rol seleccionado
        selected = self.roles_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor, seleccione un rol para editar."
            )
            return
        
        # Obtener el ID del rol
        index = self.roles_proxy_model.mapToSource(selected[0])
        role_id = int(self.roles_model.item(index.row(), 0).text())
        
        # Mostrar diálogo de edición
        dialog = RoleDialog(self, self.db_connection, role_id)
        if dialog.exec():
            self.load_roles()
            self.load_users()  # Actualizar usuarios por si cambiaron los roles
    
    def delete_role(self):
        """Elimina un rol seleccionado"""
        # Obtener el rol seleccionado
        selected = self.roles_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor, seleccione un rol para eliminar."
            )
            return
        
        # Confirmar eliminación
        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar este rol? Los usuarios asociados quedarán sin rol.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Obtener el ID del rol
        index = self.roles_proxy_model.mapToSource(selected[0])
        role_id = int(self.roles_model.item(index.row(), 0).text())
        
        # Eliminar rol
        session = self.db_connection.get_session()
        try:
            role = session.query(Role).filter(Role.id == role_id).first()
            if role:
                session.delete(role)
                session.commit()
                self.load_roles()
                self.load_users()  # Actualizar usuarios por si cambiaron los roles
                QMessageBox.information(
                    self,
                    "Rol Eliminado",
                    "El rol ha sido eliminado correctamente."
                )
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(
                self,
                "Error",
                f"Error al eliminar rol: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)
    
    # Métodos para gestionar permisos
    def show_add_permission_dialog(self):
        """Muestra el diálogo para agregar un nuevo permiso"""
        dialog = PermissionDialog(self, self.db_connection)
        if dialog.exec():
            self.load_permissions()
    
    def show_edit_permission_dialog(self):
        """Muestra el diálogo para editar un permiso existente"""
        # Obtener el permiso seleccionado
        selected = self.permissions_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor, seleccione un permiso para editar."
            )
            return
        
        # Obtener el ID del permiso
        index = self.permissions_proxy_model.mapToSource(selected[0])
        permission_id = int(self.permissions_model.item(index.row(), 0).text())
        
        # Mostrar diálogo de edición
        dialog = PermissionDialog(self, self.db_connection, permission_id)
        if dialog.exec():
            self.load_permissions()
            self.load_roles()  # Actualizar roles por si cambiaron los permisos
    
    def delete_permission(self):
        """Elimina un permiso seleccionado"""
        # Obtener el permiso seleccionado
        selected = self.permissions_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor, seleccione un permiso para eliminar."
            )
            return
        
        # Confirmar eliminación
        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar este permiso? Se eliminará de todos los roles que lo tengan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Obtener el ID del permiso
        index = self.permissions_proxy_model.mapToSource(selected[0])
        permission_id = int(self.permissions_model.item(index.row(), 0).text())
        
        # Eliminar permiso
        session = self.db_connection.get_session()
        try:
            permission = session.query(Permission).filter(Permission.id == permission_id).first()
            if permission:
                session.delete(permission)
                session.commit()
                self.load_permissions()
                self.load_roles()  # Actualizar roles por si cambiaron los permisos
                QMessageBox.information(
                    self,
                    "Permiso Eliminado",
                    "El permiso ha sido eliminado correctamente."
                )
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(
                self,
                "Error",
                f"Error al eliminar permiso: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)


class UserDialog(QDialog):
    """Diálogo para agregar o editar usuarios"""
    
    def __init__(self, parent=None, db_connection=None, user_id=None):
        """Inicializa el diálogo de usuario
        
        Args:
            parent (QWidget, optional): Widget padre
            db_connection (DatabaseConnection, optional): Conexión a la base de datos
            user_id (int, optional): ID del usuario a editar, None para nuevo usuario
        """
        super().__init__(parent)
        
        self.db_connection = db_connection
        self.user_id = user_id
        self.user = None
        
        # Configurar el diálogo
        self.setWindowTitle("Editar Usuario" if user_id else "Agregar Usuario")
        self.setMinimumWidth(400)
        
        # Cargar el usuario si se está editando
        if user_id:
            self.load_user()
        
        # Inicializar la interfaz
        self.init_ui()
    
    def load_user(self):
        """Carga los datos del usuario a editar"""
        session = self.db_connection.get_session()
        try:
            self.user = session.query(User).filter(User.id == self.user_id).first()
        except SQLAlchemyError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar usuario: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)
    
    def init_ui(self):
        """Inicializa los componentes de la interfaz"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Campos del formulario
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingrese nombre de usuario")
        if self.user:
            self.username_input.setText(self.user.username)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese contraseña" if not self.user else "Dejar en blanco para mantener la actual")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Ingrese nombre completo")
        if self.user:
            self.fullname_input.setText(self.user.full_name)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ingrese correo electrónico")
        if self.user:
            self.email_input.setText(self.user.email)
        
        self.role_combo = QComboBox()
        self.load_roles_combo()
        
        self.active_checkbox = QCheckBox("Usuario activo")
        self.active_checkbox.setChecked(True if not self.user else self.user.is_active)
        
        # Agregar campos al formulario
        form_layout.addRow("Usuario:", self.username_input)
        form_layout.addRow("Contraseña:", self.password_input)
        form_layout.addRow("Nombre Completo:", self.fullname_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Rol:", self.role_combo)
        form_layout.addRow("", self.active_checkbox)
        
        main_layout.addLayout(form_layout)
        
        # Botones
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_user)
        button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(button_box)
    
    def load_roles_combo(self):
        """Carga los roles disponibles en el combo"""
        if not self.db_connection:
            return
        
        session = self.db_connection.get_session()
        try:
            roles = session.query(Role).all()
            
            self.role_combo.clear()
            self.role_combo.addItem("Seleccione un rol", None)
            
            for role in roles:
                self.role_combo.addItem(role.name, role.id)
                
            # Seleccionar el rol actual si se está editando
            if self.user and self.user.role_id:
                index = self.role_combo.findData(self.user.role_id)
                if index >= 0:
                    self.role_combo.setCurrentIndex(index)
        except SQLAlchemyError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar roles: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)
    
    def save_user(self):
        """Guarda los datos del usuario"""
        # Validar campos
        username = self.username_input.text().strip()
        password = self.password_input.text()
        fullname = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        role_id = self.role_combo.currentData()
        is_active = self.active_checkbox.isChecked()
        
        # Validar campos obligatorios
        if not username:
            QMessageBox.warning(
                self,
                "Campo Requerido",
                "El nombre de usuario es obligatorio."
            )
            self.username_input.setFocus()
            return
        
        if not fullname:
            QMessageBox.warning(
                self,
                "Campo Requerido",
                "El nombre completo es obligatorio."
            )
            self.fullname_input.setFocus()
            return
        
        if not email:
            QMessageBox.warning(
                self,
                "Campo Requerido",
                "El correo electrónico es obligatorio."
            )
            self.email_input.setFocus()
            return
        
        if not role_id:
            QMessageBox.warning(
                self,
                "Campo Requerido",
                "Debe seleccionar un rol para el usuario."
            )
            self.role_combo.setFocus()
            return
        
        # Guardar usuario
        session = self.db_connection.get_session()
        try:
            if self.user_id:  # Actualizar usuario existente
                user = session.query(User).filter(User.id == self.user_id).first()
                if user:
                    user.username = username
                    user.full_name = fullname
                    user.email = email
                    user.role_id = role_id
                    user.is_active = is_active
                    
                    # Actualizar contraseña solo si se proporciona una nueva
                    if password:
                        user.set_password(password)
                    
                    session.commit()
                    QMessageBox.information(
                        self,
                        "Usuario Actualizado",
                        "El usuario ha sido actualizado correctamente."
                    )
                    self.accept()
            else:  # Crear nuevo usuario
                if not password:
                    QMessageBox.warning(
                        self,
                        "Campo Requerido",
                        "La contraseña es obligatoria para nuevos usuarios."
                    )
                    self.password_input.setFocus()
                    return
                
                # Verificar si el usuario ya existe
                existing_user = session.query(User).filter(User.username == username).first()
                if existing_user:
                    QMessageBox.warning(
                        self,
                        "Usuario Duplicado",
                        "Ya existe un usuario con ese nombre de usuario."
                    )
                    self.username_input.setFocus()
                    return
                
                # Crear nuevo usuario
                new_user = User(
                    username=username,
                    full_name=fullname,
                    email=email,
                    role_id=role_id,
                    is_active=is_active
                )
                new_user.set_password(password)
                
                session.add(new_user)
                session.commit()
                
                QMessageBox.information(
                    self,
                    "Usuario Creado",
                    "El usuario ha sido creado correctamente."
                )
                self.accept()
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar usuario: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)


class RoleDialog(QDialog):
    """Diálogo para agregar o editar roles"""
    
    def __init__(self, parent=None, db_connection=None, role_id=None):
        """Inicializa el diálogo de rol
        
        Args:
            parent (QWidget, optional): Widget padre
            db_connection (DatabaseConnection, optional): Conexión a la base de datos
            role_id (int, optional): ID del rol a editar, None para nuevo rol
        """
        super().__init__(parent)
        
        self.db_connection = db_connection
        self.role_id = role_id
        self.role = None
        
        # Configurar el diálogo
        self.setWindowTitle("Editar Rol" if role_id else "Agregar Rol")
        self.setMinimumWidth(400)
        
        # Cargar el rol si se está editando
        if role_id:
            self.load_role()
        
        # Inicializar la interfaz
        self.init_ui()
    
    def load_role(self):
        """Carga los datos del rol a editar"""
        session = self.db_connection.get_session()
        try:
            self.role = session.query(Role).filter(Role.id == self.role_id).first()
        except SQLAlchemyError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar rol: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)
    
    def init_ui(self):
        """Inicializa los componentes de la interfaz"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Campos del formulario
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ingrese nombre del rol")
        if self.role:
            self.name_input.setText(self.role.name)
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Ingrese descripción del rol")
        if self.role:
            self.description_input.setText(self.role.description or "")
        
        # Agregar campos al formulario
        form_layout.addRow("Nombre:", self.name_input)
        form_layout.addRow("Descripción:", self.description_input)
        
        main_layout.addLayout(form_layout)
        
        # Botones
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_role)
        button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(button_box)
    
    def save_role(self):
        """Guarda los datos del rol"""
        # Validar campos
        name = self.name_input.text().strip()
        description = self.description_input.text().strip()
        
        # Validar campos obligatorios
        if not name:
            QMessageBox.warning(
                self,
                "Campo Requerido",
                "El nombre del rol es obligatorio."
            )
            self.name_input.setFocus()
            return
        
        # Guardar rol
        session = self.db_connection.get_session()
        try:
            if self.role_id:  # Actualizar rol existente
                role = session.query(Role).filter(Role.id == self.role_id).first()
                if role:
                    role.name = name
                    role.description = description
                    
                    session.commit()
                    QMessageBox.information(
                        self,
                        "Rol Actualizado",
                        "El rol ha sido actualizado correctamente."
                    )
                    self.accept()
            else:  # Crear nuevo rol
                # Verificar si el rol ya existe
                existing_role = session.query(Role).filter(Role.name == name).first()
                if existing_role:
                    QMessageBox.warning(
                        self,
                        "Rol Duplicado",
                        "Ya existe un rol con ese nombre."
                    )
                    self.name_input.setFocus()
                    return
                
                # Crear nuevo rol
                new_role = Role(
                    name=name,
                    description=description
                )
                
                session.add(new_role)
                session.commit()
                
                QMessageBox.information(
                    self,
                    "Rol Creado",
                    "El rol ha sido creado correctamente."
                )
                self.accept()
        except SQLAlchemyError as e:
            session.rollback()
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar rol: {str(e)}"
            )
        finally:
            self.db_connection.close_session(session)
# column_selector_farmacia.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
                             QPushButton, QLabel, QFrame, QScrollArea, QWidget,
                             QGroupBox, QGridLayout)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon
import json
import os


class ColumnSelectorDialog(QDialog):
    """
    Diálogo para seleccionar qué columnas mostrar en la tabla de farmacia
    """
    columns_changed = pyqtSignal(dict)  # Señal que emite las columnas seleccionadas

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Configurar Columnas - Módulo Farmacia")
        self.setModal(True)
        self.resize(450, 600)

        # Definir todas las columnas disponibles (excepto foto)
        self.available_columns = {
            'id': {'name': 'ID', 'visible': True, 'required': True},
            'nombre': {'name': 'Nombre', 'visible': True, 'required': True},
            'presentacion': {'name': 'Presentación', 'visible': True, 'required': False},
            'laboratorio': {'name': 'Laboratorio', 'visible': True, 'required': False},
            'existencias': {'name': 'Existencias', 'visible': True, 'required': False},
            'fecha': {'name': 'Fecha de Vencimiento', 'visible': True, 'required': False},
            'tarjeta': {'name': 'Precio Tarjeta', 'visible': True, 'required': False},
            'efectivo': {'name': 'Precio Efectivo', 'visible': True, 'required': False},
            'indicacion': {'name': 'Indicación', 'visible': False, 'required': False},
            'contra': {'name': 'Contraindicación', 'visible': False, 'required': False},
            'dosis': {'name': 'Dosis', 'visible': False, 'required': False},
            'comision': {'name': 'Comisión', 'visible': False, 'required': False},
            'costo': {'name': 'Costo', 'visible': False, 'required': False}
        }

        self.checkboxes = {}
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        layout = QVBoxLayout()

        # Título
        title_label = QLabel("Seleccionar Columnas a Mostrar")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Descripción
        desc_label = QLabel("Selecciona qué columnas deseas ver en la tabla de farmacia")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)

        # Área de scroll para las columnas
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Agrupar columnas por categorías
        self.create_column_groups(scroll_layout)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Botones de acción
        self.create_action_buttons(layout)

        self.setLayout(layout)

    def create_column_groups(self, layout):
        """Crear grupos de columnas organizados por categorías"""

        # Grupo: Información Básica
        basic_group = QGroupBox("Información Básica")
        basic_layout = QGridLayout()

        basic_columns = ['id', 'nombre', 'presentacion', 'laboratorio']
        for i, col_key in enumerate(basic_columns):
            col_info = self.available_columns[col_key]
            checkbox = QCheckBox(col_info['name'])
            checkbox.setChecked(col_info['visible'])

            # Deshabilitar columnas requeridas
            if col_info['required']:
                checkbox.setEnabled(False)
                checkbox.setToolTip("Esta columna es obligatoria")
                checkbox.setStyleSheet("QCheckBox { color: #666; }")

            self.checkboxes[col_key] = checkbox
            basic_layout.addWidget(checkbox, i // 2, i % 2)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # Grupo: Inventario y Precios
        inventory_group = QGroupBox("Inventario y Precios")
        inventory_layout = QGridLayout()

        inventory_columns = ['existencias', 'fecha', 'tarjeta', 'efectivo', 'costo', 'comision']
        for i, col_key in enumerate(inventory_columns):
            col_info = self.available_columns[col_key]
            checkbox = QCheckBox(col_info['name'])
            checkbox.setChecked(col_info['visible'])
            self.checkboxes[col_key] = checkbox
            inventory_layout.addWidget(checkbox, i // 2, i % 2)

        inventory_group.setLayout(inventory_layout)
        layout.addWidget(inventory_group)

        # Grupo: Información Médica
        medical_group = QGroupBox("Información Médica")
        medical_layout = QVBoxLayout()

        medical_columns = ['indicacion', 'contra', 'dosis']
        for col_key in medical_columns:
            col_info = self.available_columns[col_key]
            checkbox = QCheckBox(col_info['name'])
            checkbox.setChecked(col_info['visible'])
            self.checkboxes[col_key] = checkbox
            medical_layout.addWidget(checkbox)

        medical_group.setLayout(medical_layout)
        layout.addWidget(medical_group)

    def create_action_buttons(self, layout):
        """Crear botones de acción"""
        button_layout = QHBoxLayout()

        # Botón para seleccionar todo
        select_all_btn = QPushButton("Seleccionar Todo")
        select_all_btn.clicked.connect(self.select_all)
        select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        # Botón para deseleccionar todo
        deselect_all_btn = QPushButton("Deseleccionar Todo")
        deselect_all_btn.clicked.connect(self.deselect_all)
        deselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)

        # Botón para restaurar por defecto
        default_btn = QPushButton("Restaurar Predeterminado")
        default_btn.clicked.connect(self.restore_defaults)
        default_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addWidget(default_btn)
        layout.addLayout(button_layout)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Botones principales
        main_button_layout = QHBoxLayout()

        apply_btn = QPushButton("Aplicar")
        apply_btn.clicked.connect(self.apply_changes)
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)

        main_button_layout.addStretch()
        main_button_layout.addWidget(apply_btn)
        main_button_layout.addWidget(cancel_btn)
        layout.addLayout(main_button_layout)

    def select_all(self):
        """Seleccionar todas las columnas"""
        for checkbox in self.checkboxes.values():
            if checkbox.isEnabled():
                checkbox.setChecked(True)

    def deselect_all(self):
        """Deseleccionar todas las columnas (excepto las requeridas)"""
        for checkbox in self.checkboxes.values():
            if checkbox.isEnabled():
                checkbox.setChecked(False)

    def restore_defaults(self):
        """Restaurar configuración predeterminada"""
        default_visible = ['id', 'nombre', 'presentacion', 'laboratorio',
                           'existencias', 'fecha', 'tarjeta', 'efectivo']

        for col_key, checkbox in self.checkboxes.items():
            checkbox.setChecked(col_key in default_visible)

    def apply_changes(self):
        """Aplicar los cambios y cerrar el diálogo"""
        selected_columns = {}

        for col_key, checkbox in self.checkboxes.items():
            selected_columns[col_key] = checkbox.isChecked()

        # Guardar configuración
        self.save_settings(selected_columns)

        # Emitir señal con las columnas seleccionadas
        self.columns_changed.emit(selected_columns)

        self.accept()

    def get_settings_path(self):
        """Obtener la ruta del archivo de configuración"""
        # Crear directorio de configuración si no existe
        config_dir = os.path.join(os.path.expanduser("~"), ".hidrocolon")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return os.path.join(config_dir, "farmacia_columns.json")

    def save_settings(self, columns):
        """Guardar configuración en archivo JSON"""
        try:
            settings_path = self.get_settings_path()
            with open(settings_path, 'w') as f:
                json.dump(columns, f, indent=2)
        except Exception as e:
            print(f"Error al guardar configuración: {e}")

    def load_settings(self):
        """Cargar configuración desde archivo JSON"""
        try:
            settings_path = self.get_settings_path()
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    saved_columns = json.load(f)

                # Aplicar configuración guardada
                for col_key, checkbox in self.checkboxes.items():
                    if col_key in saved_columns:
                        checkbox.setChecked(saved_columns[col_key])

        except Exception as e:
            print(f"Error al cargar configuración: {e}")


# Clase para gestionar las columnas en la tabla principal
class FarmaciaColumnManager:
    """
    Gestor de columnas para la tabla de farmacia
    """

    def __init__(self, table_widget, parent_window):
        self.table = table_widget
        self.parent = parent_window

        # Mapeo de columnas con sus índices y información
        self.column_mapping = {
            'id': {'index': 0, 'header': 'ID', 'width': 60},
            'nombre': {'index': 1, 'header': 'Nombre', 'width': 200},
            'presentacion': {'index': 2, 'header': 'Presentación', 'width': 120},
            'laboratorio': {'index': 3, 'header': 'Laboratorio', 'width': 100},
            'existencias': {'index': 4, 'header': 'Existencias', 'width': 80},
            'fecha': {'index': 5, 'header': 'Fecha de Vencimiento', 'width': 120},
            'tarjeta': {'index': 6, 'header': 'Precio Tarjeta', 'width': 100},
            'efectivo': {'index': 7, 'header': 'Precio Efectivo', 'width': 100},
            'indicacion': {'index': 8, 'header': 'Indicación', 'width': 150},
            'contra': {'index': 9, 'header': 'Contraindicación', 'width': 150},
            'dosis': {'index': 10, 'header': 'Dosis', 'width': 150},
            'costo': {'index': 11, 'header': 'Costo', 'width': 80},
            'comision': {'index': 12, 'header': 'Comisión', 'width': 80}
        }

        self.visible_columns = self.load_column_settings()

    def open_column_selector(self):
        """Abrir el diálogo selector de columnas"""
        dialog = ColumnSelectorDialog(self.parent)
        dialog.columns_changed.connect(self.update_columns)
        dialog.exec_()

    def update_columns(self, selected_columns):
        """Actualizar las columnas visibles en la tabla"""
        self.visible_columns = selected_columns
        self.apply_column_visibility()

        # Recargar datos de la tabla
        if hasattr(self.parent, 'cargarTablafarmacia'):
            self.parent.cargarTablafarmacia()

    def apply_column_visibility(self):
        """Aplicar la visibilidad de columnas a la tabla"""
        # Configurar número total de columnas
        total_columns = len(self.column_mapping) + 1  # +1 para columna de acciones
        self.table.setColumnCount(total_columns)

        # Configurar headers y visibilidad
        headers = []
        for col_key, col_info in self.column_mapping.items():
            if self.visible_columns.get(col_key, False):
                headers.append(col_info['header'])
                self.table.setColumnHidden(col_info['index'], False)
                self.table.setColumnWidth(col_info['index'], col_info['width'])
            else:
                headers.append(col_info['header'])  # Siempre agregar el header
                self.table.setColumnHidden(col_info['index'], True)

        headers.append("Acciones")  # Columna de acciones siempre visible
        self.table.setHorizontalHeaderLabels(headers)

    def get_visible_column_indices(self):
        """Obtener los índices de las columnas visibles"""
        visible_indices = []
        for col_key, col_info in self.column_mapping.items():
            if self.visible_columns.get(col_key, False):
                visible_indices.append(col_info['index'])
        return visible_indices

    def get_column_data_for_row(self, data_row):
        """Obtener los datos de una fila según las columnas visibles"""
        # Mapear datos según las columnas de la base de datos
        db_columns = ['id', 'nombre', 'presentacion', 'laboratorio', 'existencias',
                      'fecha', 'tarjeta', 'efectivo', 'indicacion', 'contra', 'dosis', 'comision']

        row_data = []
        for i, col_key in enumerate(db_columns):
            if col_key in self.column_mapping:
                row_data.append(str(data_row[i]) if i < len(data_row) else "")

        return row_data

    def load_column_settings(self):
        """Cargar configuración de columnas"""
        try:
            config_dir = os.path.join(os.path.expanduser("~"), ".hidrocolon")
            settings_path = os.path.join(config_dir, "farmacia_columns.json")

            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error al cargar configuración: {e}")

        # Configuración por defecto
        return {
            'id': True,
            'nombre': True,
            'presentacion': True,
            'laboratorio': True,
            'existencias': True,
            'fecha': True,
            'tarjeta': True,
            'efectivo': True,
            'indicacion': False,
            'contra': False,
            'dosis': False,
            'comision': False
        }
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QCheckBox, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QGroupBox, QGridLayout, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import pymysql


class VentanaExtras(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.extras_seleccionados = []
        self.db_connection = None
        self.cursor = None
        self.conectar_bd()
        self.setup_ui()
        self.cargar_extras_bd()

    def conectar_bd(self):
        """Conecta a la base de datos MySQL"""
        try:
            self.db_connection = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",  # Cambia por tu contraseña
                database="bdhidrocolon",
                charset='utf8mb4'
            )
            self.cursor = self.db_connection.cursor()

        except Exception as e:
            QMessageBox.critical(self, "Error de Conexión",
                                 f"No se pudo conectar a la base de datos:\n{e}")
            self.db_connection = None
            self.cursor = None

    def setup_ui(self):
        self.setWindowTitle("Seleccionar Extras para el Medicamento")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        layout = QVBoxLayout()

        # Título
        titulo = QLabel("Seleccionar Extras")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Instrucciones IMPORTANTES
        instrucciones = QLabel(
            "⚠️ IMPORTANTE: Los extras seleccionados se asociarán al medicamento pero NO se descontarán del inventario hasta que se VENDA el medicamento.")
        instrucciones.setWordWrap(True)
        instrucciones.setStyleSheet(
            "color: #d63384; margin: 10px; padding: 10px; background-color: #f8d7da; border: 1px solid #f1aeb5; border-radius: 5px; font-weight: bold;")
        layout.addWidget(instrucciones)

        # Sección de extras disponibles
        extras_group = QGroupBox("Extras Disponibles en Inventario")
        extras_layout = QVBoxLayout()

        # Tabla de extras
        self.tabla_extras = QTableWidget()
        self.tabla_extras.setColumnCount(5)
        self.tabla_extras.setHorizontalHeaderLabels([
            "Seleccionar", "Nombre", "Stock", "Unidad", "Descripción"
        ])

        # Configurar tabla
        header = self.tabla_extras.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Nombre
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Stock
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Unidad
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Descripción

        self.tabla_extras.setMaximumHeight(250)
        self.tabla_extras.setAlternatingRowColors(True)
        extras_layout.addWidget(self.tabla_extras)

        extras_group.setLayout(extras_layout)
        layout.addWidget(extras_group)

        # Sección de extras personalizados (para agregar nuevos)
        custom_group = QGroupBox("Agregar Nuevo Extra al Inventario")
        custom_layout = QGridLayout()

        custom_layout.addWidget(QLabel("Nombre:"), 0, 0)
        self.txt_nombre_nuevo = QTextEdit()
        self.txt_nombre_nuevo.setMaximumHeight(40)
        self.txt_nombre_nuevo.setPlaceholderText("Nombre del nuevo extra...")
        custom_layout.addWidget(self.txt_nombre_nuevo, 0, 1)

        custom_layout.addWidget(QLabel("Descripción:"), 1, 0)
        self.txt_descripcion_nuevo = QTextEdit()
        self.txt_descripcion_nuevo.setMaximumHeight(60)
        self.txt_descripcion_nuevo.setPlaceholderText("Descripción del extra...")
        custom_layout.addWidget(self.txt_descripcion_nuevo, 1, 1)

        custom_layout.addWidget(QLabel("Cantidad inicial:"), 2, 0)
        self.spin_cantidad_nuevo = QSpinBox()
        self.spin_cantidad_nuevo.setRange(0, 9999)
        self.spin_cantidad_nuevo.setValue(10)
        custom_layout.addWidget(self.spin_cantidad_nuevo, 2, 1)

        btn_agregar_nuevo = QPushButton("➕ Agregar al Inventario")
        btn_agregar_nuevo.clicked.connect(self.agregar_extra_nuevo)
        btn_agregar_nuevo.setStyleSheet("QPushButton { background-color: #198754; color: white; padding: 8px; }")
        custom_layout.addWidget(btn_agregar_nuevo, 3, 0, 1, 2)

        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)

        # Lista de extras seleccionados
        seleccionados_label = QLabel("Extras que se asociarán al medicamento:")
        seleccionados_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(seleccionados_label)

        self.txt_extras_seleccionados = QTextEdit()
        self.txt_extras_seleccionados.setMaximumHeight(100)
        self.txt_extras_seleccionados.setReadOnly(True)
        self.txt_extras_seleccionados.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc;")
        layout.addWidget(self.txt_extras_seleccionados)

        # Botones principales
        botones_layout = QHBoxLayout()

        btn_aceptar = QPushButton("✅ Asociar Extras al Medicamento")
        btn_aceptar.clicked.connect(self.aceptar_extras)
        btn_aceptar.setStyleSheet(
            "QPushButton { background-color: #0d6efd; color: white; padding: 10px; font-weight: bold; }")

        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #dc3545; color: white; padding: 10px; }")

        btn_limpiar = QPushButton("🔄 Limpiar Selección")
        btn_limpiar.clicked.connect(self.limpiar_seleccion)
        btn_limpiar.setStyleSheet("QPushButton { background-color: #fd7e14; color: white; padding: 10px; }")

        btn_actualizar = QPushButton("🔄 Actualizar Lista")
        btn_actualizar.clicked.connect(self.cargar_extras_bd)
        btn_actualizar.setStyleSheet("QPushButton { background-color: #6f42c1; color: white; padding: 10px; }")

        botones_layout.addWidget(btn_aceptar)
        botones_layout.addWidget(btn_limpiar)
        botones_layout.addWidget(btn_actualizar)
        botones_layout.addWidget(btn_cancelar)

        layout.addLayout(botones_layout)
        self.setLayout(layout)

    def cargar_extras_bd(self):
        """Carga los extras desde la base de datos"""
        if not self.cursor:
            self.mostrar_error_conexion()
            return

        try:
            query = '''
                SELECT id, nombre, cantidad, unidad, descripcion 
                FROM extras 
                WHERE activo = 1 
                ORDER BY nombre
            '''
            self.cursor.execute(query)
            extras = self.cursor.fetchall()

            self.tabla_extras.setRowCount(len(extras))

            for row, (id_extra, nombre, cantidad, unidad, descripcion) in enumerate(extras):
                # Checkbox para seleccionar
                checkbox = QCheckBox()
                checkbox.setProperty("extra_id", id_extra)
                checkbox.setProperty("extra_nombre", nombre)
                checkbox.stateChanged.connect(self.actualizar_extras)

                # NO deshabilitar por stock - permitir seleccionar aunque no haya stock
                # Solo mostrar advertencia visual
                if cantidad <= 0:
                    checkbox.setToolTip("⚠️ Sin stock actualmente - se verificará al vender")
                elif cantidad <= 5:
                    checkbox.setToolTip("⚠️ Stock bajo - se verificará al vender")

                self.tabla_extras.setCellWidget(row, 0, checkbox)

                # Nombre
                item_nombre = QTableWidgetItem(nombre)
                self.tabla_extras.setItem(row, 1, item_nombre)

                # Stock
                item_stock = QTableWidgetItem(str(cantidad))
                if cantidad <= 0:
                    item_stock.setForeground(QColor("red"))
                    item_stock.setToolTip("Sin stock")
                elif cantidad <= 5:  # Stock bajo
                    item_stock.setForeground(QColor("orange"))
                    item_stock.setToolTip("Stock bajo")
                else:
                    item_stock.setForeground(QColor("green"))

                item_stock.setTextAlignment(Qt.AlignCenter)
                self.tabla_extras.setItem(row, 2, item_stock)

                # Unidad
                item_unidad = QTableWidgetItem(unidad or "Unidades")
                item_unidad.setTextAlignment(Qt.AlignCenter)
                self.tabla_extras.setItem(row, 3, item_unidad)

                # Descripción
                item_desc = QTableWidgetItem(descripcion or "")
                self.tabla_extras.setItem(row, 4, item_desc)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar extras: {e}")

    def mostrar_error_conexion(self):
        """Muestra mensaje de error de conexión"""
        self.tabla_extras.setRowCount(1)
        self.tabla_extras.setItem(0, 1, QTableWidgetItem("❌ Sin conexión a la base de datos"))
        self.tabla_extras.setItem(0, 2, QTableWidgetItem(""))
        self.tabla_extras.setItem(0, 3, QTableWidgetItem(""))
        self.tabla_extras.setItem(0, 4, QTableWidgetItem("Revisa la conexión a MySQL"))

    def actualizar_extras(self):
        """Actualiza la lista de extras seleccionados"""
        self.extras_seleccionados = []

        for row in range(self.tabla_extras.rowCount()):
            checkbox = self.tabla_extras.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                nombre = checkbox.property("extra_nombre")
                if nombre:
                    self.extras_seleccionados.append(nombre)

        self.actualizar_texto_seleccionados()

    def agregar_extra_nuevo(self):
        """Agrega un nuevo extra al inventario"""
        if not self.cursor:
            QMessageBox.warning(self, "Error", "No hay conexión a la base de datos")
            return

        nombre = self.txt_nombre_nuevo.toPlainText().strip()
        descripcion = self.txt_descripcion_nuevo.toPlainText().strip()
        cantidad = self.spin_cantidad_nuevo.value()

        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre del extra es obligatorio")
            return

        try:
            # Insertar nuevo extra
            query = '''
                INSERT INTO extras (nombre, descripcion, cantidad, unidad, stock_minimo, activo)
                VALUES (%s, %s, %s, 'Unidades', 5, 1)
            '''
            self.cursor.execute(query, (nombre, descripcion, cantidad))
            self.db_connection.commit()

            # Limpiar campos
            self.txt_nombre_nuevo.clear()
            self.txt_descripcion_nuevo.clear()
            self.spin_cantidad_nuevo.setValue(10)

            # Recargar tabla
            self.cargar_extras_bd()

            QMessageBox.information(self, "Éxito", f"Extra '{nombre}' agregado al inventario correctamente")

        except pymysql.IntegrityError:
            QMessageBox.warning(self, "Error", "Ya existe un extra con ese nombre")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar extra: {e}")

    def actualizar_texto_seleccionados(self):
        """Actualiza el texto que muestra los extras seleccionados"""
        if self.extras_seleccionados:
            texto = "• " + "\n• ".join(self.extras_seleccionados)
            texto += "\n\n💡 Estos extras se consumirán del inventario cuando se VENDA el medicamento"
        else:
            texto = "Ningún extra seleccionado"
        self.txt_extras_seleccionados.setPlainText(texto)

    def limpiar_seleccion(self):
        """Limpia toda la selección de extras"""
        for row in range(self.tabla_extras.rowCount()):
            checkbox = self.tabla_extras.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)

        self.extras_seleccionados = []
        self.actualizar_texto_seleccionados()

    def aceptar_extras(self):
        """CAMBIO PRINCIPAL: NO consumir extras aquí, solo asociarlos"""
        if not self.extras_seleccionados:
            respuesta = QMessageBox.question(self, "Sin extras",
                                             "No has seleccionado ningún extra. ¿Deseas continuar sin extras?",
                                             QMessageBox.Yes | QMessageBox.No)
            if respuesta == QMessageBox.No:
                return

        # IMPORTANTE: NO CONSUMIR EXTRAS AQUÍ
        # Solo enviar la lista para asociar al medicamento

        # Enviar extras al formulario principal
        if hasattr(self.parent, 'recibir_extras'):
            self.parent.recibir_extras(self.extras_seleccionados)

        if self.extras_seleccionados:
            QMessageBox.information(self, "Extras Asociados",
                                    f"✅ Se han asociado {len(self.extras_seleccionados)} extras al medicamento.\n\n"
                                    f"📦 Extras: {', '.join(self.extras_seleccionados)}\n\n"
                                    f"⚠️ Se descontarán del inventario cuando se VENDA el medicamento.")
        else:
            QMessageBox.information(self, "Sin Extras", "Medicamento sin extras asociados.")

        self.accept()

    def closeEvent(self, event):
        """Se ejecuta al cerrar la ventana"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.db_connection:
                self.db_connection.close()
        except:
            pass
        event.accept()

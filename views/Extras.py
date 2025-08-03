from datetime import datetime, date, timedelta
import datetime as dt
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                             QLineEdit, QSpinBox, QDoubleSpinBox, QDialog, QGridLayout,
                             QWidget, QHeaderView, QComboBox, QTextEdit, QFrame,
                             QGroupBox, QDateEdit, QCheckBox, QApplication)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import pymysql
import datetime
from typing import List, Dict


class DialogoAgregarExtra(QDialog):
    """Diálogo para agregar o editar un extra"""

    def __init__(self, parent=None, extra_data=None, es_edicion=False):
        super().__init__(parent)
        self.extra_data = extra_data
        self.es_edicion = es_edicion
        self.setup_ui()

        if es_edicion and extra_data:
            self.cargar_datos_extra()

    def setup_ui(self):
        self.setWindowTitle("Editar Extra" if self.es_edicion else "Agregar Nuevo Extra")
        self.setFixedSize(450, 500)
        self.setModal(True)

        layout = QVBoxLayout()

        # Título
        titulo = QLabel("Editar Extra" if self.es_edicion else "Nuevo Extra")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Formulario
        form_frame = QGroupBox("Información del Extra")
        form_layout = QGridLayout()

        # Nombre
        form_layout.addWidget(QLabel("Nombre del Extra:"), 0, 0)
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ej: Algodón, Jeringa, etc.")
        form_layout.addWidget(self.txt_nombre, 0, 1)

        # Descripción
        form_layout.addWidget(QLabel("Descripción:"), 1, 0)
        self.txt_descripcion = QTextEdit()
        self.txt_descripcion.setMaximumHeight(80)
        self.txt_descripcion.setPlaceholderText("Descripción detallada del extra...")
        form_layout.addWidget(self.txt_descripcion, 1, 1)

        # Cantidad actual
        form_layout.addWidget(QLabel("Cantidad en Stock:"), 2, 0)
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(0, 9999)
        form_layout.addWidget(self.spin_cantidad, 2, 1)

        # Unidad de medida
        form_layout.addWidget(QLabel("Unidad:"), 3, 0)
        self.combo_unidad = QComboBox()
        self.combo_unidad.addItems(["Unidades", "Gramos", "Mililitros", "Metros", "Cajas", "Paquetes"])
        form_layout.addWidget(self.combo_unidad, 3, 1)

        # Stock mínimo
        form_layout.addWidget(QLabel("Stock Mínimo:"), 4, 0)
        self.spin_stock_minimo = QSpinBox()
        self.spin_stock_minimo.setRange(0, 999)
        self.spin_stock_minimo.setValue(5)
        form_layout.addWidget(self.spin_stock_minimo, 4, 1)

        # Costo unitario
        form_layout.addWidget(QLabel("Costo Unitario (Q):"), 5, 0)
        self.spin_costo = QDoubleSpinBox()
        self.spin_costo.setRange(0.0, 9999.99)
        self.spin_costo.setDecimals(2)
        form_layout.addWidget(self.spin_costo, 5, 1)

        # Proveedor
        form_layout.addWidget(QLabel("Proveedor:"), 6, 0)
        self.txt_proveedor = QLineEdit()
        self.txt_proveedor.setPlaceholderText("Nombre del proveedor")
        form_layout.addWidget(self.txt_proveedor, 6, 1)

        # Fecha de vencimiento
        form_layout.addWidget(QLabel("Fecha Vencimiento:"), 7, 0)
        self.date_vencimiento = QDateEdit()
        self.date_vencimiento.setDate(QDate.currentDate().addYears(1))
        self.date_vencimiento.setCalendarPopup(True)
        form_layout.addWidget(self.date_vencimiento, 7, 1)

        # Activo
        self.chk_activo = QCheckBox("Extra activo")
        self.chk_activo.setChecked(True)
        form_layout.addWidget(self.chk_activo, 8, 0, 1, 2)

        form_frame.setLayout(form_layout)
        layout.addWidget(form_frame)

        # Botones
        botones_layout = QHBoxLayout()

        btn_guardar = QPushButton("Actualizar" if self.es_edicion else "Guardar")
        btn_guardar.clicked.connect(self.guardar_extra)
        btn_guardar.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 8px; font-weight: bold; }")

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 8px; }")

        botones_layout.addWidget(btn_guardar)
        botones_layout.addWidget(btn_cancelar)

        layout.addLayout(botones_layout)
        self.setLayout(layout)

    def mostrar_reporte(self):
        """Muestra un reporte detallado del inventario de extras - DATETIME CORREGIDO"""
        try:
            # ✅ CORRECCIÓN: Importación local de datetime
            from datetime import datetime

            cursor = self.conn.cursor()
            cursor.execute("""
                           SELECT nombre,
                                  cantidad,
                                  unidad,
                                  stock_minimo,
                                  costo_unitario,
                                  (cantidad * costo_unitario) as valor_total,
                                  CASE
                                      WHEN cantidad <= stock_minimo THEN 'BAJO'
                                      ELSE 'OK'
                                      END                     as estado
                           FROM extras
                           ORDER BY nombre
                           """)
            inventario = cursor.fetchall()
            cursor.close()

            if not inventario:
                QMessageBox.information(self, "Sin datos", "No hay extras registrados para mostrar.")
                return

            # Crear ventana de diálogo para el reporte
            dialogo_reporte = QDialog(self)
            dialogo_reporte.setWindowTitle("Reporte de Inventario de Extras")
            dialogo_reporte.setMinimumSize(800, 600)

            layout = QVBoxLayout()

            # Texto del reporte
            texto_reporte = QTextEdit()
            texto_reporte.setReadOnly(True)

            reporte = "REPORTE DE INVENTARIO DE EXTRAS\n"
            reporte += "=" * 50 + "\n\n"
            # ✅ CORRECCIÓN: Uso correcto de datetime.now()
            reporte += f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"

            total_items = len(inventario)
            valor_total = sum(float(item[5]) for item in inventario)
            items_bajo_stock = sum(1 for item in inventario if item[6] == 'BAJO')

            reporte += f"Resumen:\n"
            reporte += f"- Total de extras: {total_items}\n"
            reporte += f"- Valor total del inventario: Q{valor_total:.2f}\n"
            reporte += f"- Items con stock bajo: {items_bajo_stock}\n\n"

            reporte += "Detalle del inventario:\n"
            reporte += "-" * 80 + "\n"
            reporte += f"{'Nombre':<20} {'Stock':<8} {'Unidad':<10} {'Mín.':<6} {'Costo':<10} {'Valor':<10} {'Estado':<8}\n"
            reporte += "-" * 80 + "\n"

            for item in inventario:
                nombre, cantidad, unidad, stock_min, costo, valor, estado = item
                reporte += f"{nombre:<20} {cantidad:<8} {unidad:<10} {stock_min:<6} Q{float(costo):<9.2f} Q{float(valor):<9.2f} {estado:<8}\n"

            texto_reporte.setPlainText(reporte)
            layout.addWidget(texto_reporte)

            # Botones
            botones_layout = QHBoxLayout()
            btn_exportar = QPushButton("Exportar a Archivo")
            btn_cerrar = QPushButton("Cerrar")

            btn_exportar.clicked.connect(lambda: self.exportar_reporte(reporte))
            btn_cerrar.clicked.connect(dialogo_reporte.accept)

            botones_layout.addWidget(btn_exportar)
            botones_layout.addWidget(btn_cerrar)
            layout.addLayout(botones_layout)

            dialogo_reporte.setLayout(layout)
            dialogo_reporte.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar reporte: {e}")
            print(f"Error en mostrar_reporte: {e}")

    def exportar_reporte(self, contenido):
        """Exporta el reporte a un archivo de texto - DATETIME CORREGIDO"""
        try:
            # ✅ CORRECCIÓN: Importación local de datetime
            from datetime import datetime
            from PyQt5.QtWidgets import QFileDialog

            archivo, _ = QFileDialog.getSaveFileName(
                self, "Guardar Reporte",
                f"reporte_inventario_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                "Archivos de texto (*.txt)"
            )

            if archivo:
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)

                QMessageBox.information(self, "Éxito", f"Reporte exportado correctamente a:\n{archivo}")

                # Intentar abrir el archivo automáticamente
                try:
                    import subprocess
                    import platform

                    system = platform.system()
                    if system == 'Windows':
                        import os
                        os.startfile(archivo)
                    elif system == 'Darwin':  # macOS
                        subprocess.call(['open', archivo])
                    else:  # Linux
                        subprocess.call(['xdg-open', archivo])
                except:
                    pass  # Si no se puede abrir automáticamente, no hay problema

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar reporte: {e}")
            print(f"Error en exportar_reporte: {e}")

    def cargar_datos_extra(self):
        """Carga los datos del extra para edición"""
        if self.extra_data:
            self.txt_nombre.setText(str(self.extra_data.get('nombre', '')))
            self.txt_descripcion.setPlainText(str(self.extra_data.get('descripcion', '')))
            self.spin_cantidad.setValue(int(self.extra_data.get('cantidad', 0)))

            unidad = str(self.extra_data.get('unidad', 'Unidades'))
            index = self.combo_unidad.findText(unidad)
            if index >= 0:
                self.combo_unidad.setCurrentIndex(index)

            self.spin_stock_minimo.setValue(int(self.extra_data.get('stock_minimo', 5)))
            self.spin_costo.setValue(float(self.extra_data.get('costo_unitario', 0.0)))
            self.txt_proveedor.setText(str(self.extra_data.get('proveedor', '')))

            # Fecha de vencimiento
            fecha_venc = self.extra_data.get('fecha_vencimiento')
            if fecha_venc:
                try:
                    if isinstance(fecha_venc, str):
                        fecha = QDate.fromString(fecha_venc, "yyyy-MM-dd")
                    else:
                        fecha = QDate(fecha_venc)
                    self.date_vencimiento.setDate(fecha)
                except:
                    pass

            self.chk_activo.setChecked(bool(self.extra_data.get('activo', True)))

    def guardar_extra(self):
        """Valida y guarda el extra"""
        if not self.txt_nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre del extra es obligatorio")
            return

        self.extra_guardado = {
            'nombre': self.txt_nombre.text().strip(),
            'descripcion': self.txt_descripcion.toPlainText().strip(),
            'cantidad': self.spin_cantidad.value(),
            'unidad': self.combo_unidad.currentText(),
            'stock_minimo': self.spin_stock_minimo.value(),
            'costo_unitario': self.spin_costo.value(),
            'proveedor': self.txt_proveedor.text().strip(),
            'fecha_vencimiento': self.date_vencimiento.date().toString("yyyy-MM-dd"),
            'activo': self.chk_activo.isChecked()
        }

        self.accept()


class DialogoMovimientoStock(QDialog):
    """Diálogo para registrar entrada o salida de stock"""

    def __init__(self, parent=None, extra_nombre="", operacion="entrada"):
        super().__init__(parent)
        self.extra_nombre = extra_nombre
        self.operacion = operacion  # "entrada" o "salida"
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"{'Entrada' if self.operacion == 'entrada' else 'Salida'} de Stock")
        self.setFixedSize(400, 300)
        self.setModal(True)

        layout = QVBoxLayout()

        # Título
        titulo = QLabel(f"{'Entrada' if self.operacion == 'entrada' else 'Salida'} de Stock")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Info del extra
        info_label = QLabel(f"Extra: {self.extra_nombre}")
        info_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(info_label)

        # Formulario
        form_layout = QGridLayout()

        # Cantidad
        form_layout.addWidget(QLabel("Cantidad:"), 0, 0)
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 9999)
        form_layout.addWidget(self.spin_cantidad, 0, 1)

        # Motivo/Observaciones
        form_layout.addWidget(QLabel("Motivo/Observaciones:"), 1, 0)
        self.txt_observaciones = QTextEdit()
        self.txt_observaciones.setMaximumHeight(100)

        if self.operacion == "entrada":
            self.txt_observaciones.setPlaceholderText("Ej: Compra, donación, etc.")
        else:
            self.txt_observaciones.setPlaceholderText("Ej: Uso en medicamento, consumo interno, etc.")

        form_layout.addWidget(self.txt_observaciones, 1, 1)

        # Si es entrada, mostrar costo
        if self.operacion == "entrada":
            form_layout.addWidget(QLabel("Costo Total (Q):"), 2, 0)
            self.spin_costo_total = QDoubleSpinBox()
            self.spin_costo_total.setRange(0.0, 99999.99)
            self.spin_costo_total.setDecimals(2)
            form_layout.addWidget(self.spin_costo_total, 2, 1)

        layout.addLayout(form_layout)

        # Botones
        botones_layout = QHBoxLayout()

        btn_confirmar = QPushButton("Confirmar")
        btn_confirmar.clicked.connect(self.confirmar_movimiento)
        btn_confirmar.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; }")

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 8px; }")

        botones_layout.addWidget(btn_confirmar)
        botones_layout.addWidget(btn_cancelar)

        layout.addLayout(botones_layout)
        self.setLayout(layout)

    def confirmar_movimiento(self):
        """Confirma el movimiento de stock"""
        if self.spin_cantidad.value() <= 0:
            QMessageBox.warning(self, "Error", "La cantidad debe ser mayor a 0")
            return

        self.movimiento_data = {
            'cantidad': self.spin_cantidad.value(),
            'observaciones': self.txt_observaciones.toPlainText().strip(),
            'operacion': self.operacion
        }

        if self.operacion == "entrada" and hasattr(self, 'spin_costo_total'):
            self.movimiento_data['costo_total'] = self.spin_costo_total.value()

        self.accept()


class VentanaGestionExtras(QMainWindow):
    """Ventana principal para gestión de extras"""

    def __init__(self):
        super().__init__()
        self.db_connection = None
        self.cursor = None
        self.setup_ui()
        self.conectar_eventos()
        self.conectar_bd()
        self.crear_tablas()
        self.cargar_extras()

    def setup_ui(self):
        self.setWindowTitle("Gestión de Extras - Control de Inventario")
        self.setMinimumSize(1200, 700)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Título principal
        titulo = QLabel("Gestión de Extras e Inventario")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #2E86AB; margin: 10px; padding: 10px;")
        layout.addWidget(titulo)

        # Panel de controles superior
        controles_frame = QFrame()
        controles_frame.setFrameShape(QFrame.StyledPanel)
        controles_layout = QHBoxLayout(controles_frame)

        # Botones principales
        self.btn_agregar = QPushButton("➕ Nuevo Extra")
        self.btn_agregar.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; }")

        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_editar.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 10px; }")
        self.btn_editar.setEnabled(False)

        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_eliminar.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 10px; }")
        self.btn_eliminar.setEnabled(False)

        self.btn_entrada = QPushButton("📥 Entrada Stock")
        self.btn_entrada.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 10px; }")
        self.btn_entrada.setEnabled(False)

        self.btn_salida = QPushButton("📤 Salida Stock")
        self.btn_salida.setStyleSheet("QPushButton { background-color: #9C27B0; color: white; padding: 10px; }")
        self.btn_salida.setEnabled(False)

        # Filtros
        controles_layout.addWidget(QLabel("Filtrar:"))
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Todos", "Stock Bajo", "Activos", "Inactivos", "Próximos a Vencer"])

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por nombre...")
        self.txt_buscar.setMaximumWidth(200)

        # Agregar botones y filtros
        controles_layout.addWidget(self.btn_agregar)
        controles_layout.addWidget(self.btn_editar)
        controles_layout.addWidget(self.btn_eliminar)
        controles_layout.addStretch()
        controles_layout.addWidget(self.btn_entrada)
        controles_layout.addWidget(self.btn_salida)
        controles_layout.addStretch()
        controles_layout.addWidget(self.combo_filtro)
        controles_layout.addWidget(self.txt_buscar)

        layout.addWidget(controles_frame)

        # Tabla de extras
        self.tabla_extras = QTableWidget()
        self.tabla_extras.setColumnCount(10)
        self.tabla_extras.setHorizontalHeaderLabels([
            "ID", "Nombre", "Descripción", "Stock", "Unidad",
            "Stock Mín.", "Costo Unit.", "Proveedor", "Vencimiento", "Estado"
        ])

        # Configurar tabla
        header = self.tabla_extras.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nombre
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Descripción
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Stock
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Unidad
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Stock Mín
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Costo
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Proveedor
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Vencimiento
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Estado

        self.tabla_extras.setAlternatingRowColors(True)
        self.tabla_extras.setSelectionBehavior(QTableWidget.SelectRows)

        layout.addWidget(self.tabla_extras)

        # Panel de resumen inferior
        resumen_frame = QFrame()
        resumen_frame.setFrameShape(QFrame.StyledPanel)
        resumen_layout = QHBoxLayout(resumen_frame)

        self.lbl_total_extras = QLabel("Total de Extras: 0")
        self.lbl_stock_bajo = QLabel("Stock Bajo: 0")
        #self.lbl_valor_inventario = QLabel("Valor Inventario: Q0.00")

        for lbl in [self.lbl_total_extras, self.lbl_stock_bajo]:
            lbl.setFont(QFont("Arial", 10, QFont.Bold))

        resumen_layout.addWidget(self.lbl_total_extras)
        resumen_layout.addStretch()
        resumen_layout.addWidget(self.lbl_stock_bajo)
        resumen_layout.addStretch()

        #resumen_layout.addWidget(self.lbl_valor_inventario)

        layout.addWidget(resumen_frame)

    def conectar_eventos(self):
        """Conecta todos los eventos de la interfaz"""
        self.btn_agregar.clicked.connect(self.agregar_extra)
        self.btn_editar.clicked.connect(self.editar_extra)
        self.btn_eliminar.clicked.connect(self.eliminar_extra)
        self.btn_entrada.clicked.connect(self.entrada_stock)
        self.btn_salida.clicked.connect(self.salida_stock)

        self.tabla_extras.itemSelectionChanged.connect(self.seleccion_cambiada)
        self.tabla_extras.itemDoubleClicked.connect(self.editar_extra)

        self.combo_filtro.currentTextChanged.connect(self.aplicar_filtros)
        self.txt_buscar.textChanged.connect(self.aplicar_filtros)

    def conectar_bd(self):
        """Conecta a la base de datos MySQL"""
        try:
            self.db_connection = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",  # Cambia por tu contraseña
                database="bdhidrocolon",  # Usa la misma base de datos que tu sistema
                charset='utf8mb4'
            )
            self.cursor = self.db_connection.cursor()
            print("Conexión exitosa a la base de datos MySQL")

        except Exception as e:
            QMessageBox.critical(self, "Error de Conexión",
                                 f"No se pudo conectar a la base de datos MySQL:\n{e}")
            self.db_connection = None
            self.cursor = None

    def crear_tablas(self):
        """Crea las tablas necesarias si no existen"""
        if not self.cursor:
            return

        try:
            # Crear tabla de extras
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS extras (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) UNIQUE NOT NULL,
                    descripcion TEXT,
                    cantidad INT DEFAULT 0,
                    unidad VARCHAR(50) DEFAULT 'Unidades',
                    stock_minimo INT DEFAULT 5,
                    costo_unitario DECIMAL(10,2) DEFAULT 0.00,
                    proveedor VARCHAR(100),
                    fecha_vencimiento DATE,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')

            # Crear tabla de movimientos de stock
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS movimientos_stock_extras (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    extra_id INT,
                    tipo ENUM('entrada', 'salida') NOT NULL,
                    cantidad INT NOT NULL,
                    costo_total DECIMAL(10,2) DEFAULT 0.00,
                    observaciones TEXT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (extra_id) REFERENCES extras(id) ON DELETE CASCADE
                )
            ''')

            self.db_connection.commit()
            print("Tablas creadas correctamente")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al crear tablas: {e}")

    def cargar_extras(self):
        """Carga todos los extras en la tabla"""
        if not self.cursor:
            return

        try:
            query = '''
                SELECT id, nombre, descripcion, cantidad, unidad, stock_minimo, 
                       costo_unitario, proveedor, fecha_vencimiento, activo
                FROM extras 
                ORDER BY nombre
            '''
            self.cursor.execute(query)
            extras = self.cursor.fetchall()

            self.tabla_extras.setRowCount(len(extras))

            for row, extra in enumerate(extras):
                # Llenar cada columna
                for col, valor in enumerate(extra):
                    if col == 9:  # Estado (activo/inactivo)
                        item = QTableWidgetItem("Activo" if valor else "Inactivo")
                        item.setForeground(QColor("green") if valor else QColor("red"))
                    elif col == 6:  # Costo unitario
                        item = QTableWidgetItem(f"Q{valor:.2f}")
                    elif col == 8 and valor:  # Fecha de vencimiento
                        item = QTableWidgetItem(str(valor))
                    else:
                        item = QTableWidgetItem(str(valor) if valor is not None else "")

                    # Colorear filas con stock bajo
                    if col == 3 and valor is not None and extra[5] is not None and valor <= extra[5]:
                        item.setBackground(QColor("#ffebee"))

                    item.setTextAlignment(Qt.AlignCenter)
                    self.tabla_extras.setItem(row, col, item)

            self.actualizar_resumen()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar extras: {e}")

    def actualizar_resumen(self):
        """Actualiza el panel de resumen"""
        if not self.cursor:
            return

        try:
            # Total de extras
            self.cursor.execute("SELECT COUNT(*) FROM extras WHERE activo = 1")
            total = self.cursor.fetchone()[0]

            # Stock bajo
            self.cursor.execute("SELECT COUNT(*) FROM extras WHERE cantidad <= stock_minimo AND activo = 1")
            stock_bajo = self.cursor.fetchone()[0]

            # Valor del inventario
            self.cursor.execute("SELECT SUM(cantidad * costo_unitario) FROM extras WHERE activo = 1")
            valor_total = self.cursor.fetchone()[0] or 0

            self.lbl_total_extras.setText(f"Total de Extras: {total}")
            self.lbl_stock_bajo.setText(f"Stock Bajo: {stock_bajo}")
            self.lbl_stock_bajo.setStyleSheet("color: red;" if stock_bajo > 0 else "color: green;")
            #self.lbl_valor_inventario.setText(f"Valor Inventario: Q{valor_total:.2f}")

        except Exception as e:
            print(f"Error al actualizar resumen: {e}")

    def seleccion_cambiada(self):
        """Se ejecuta cuando cambia la selección en la tabla"""
        tiene_seleccion = len(self.tabla_extras.selectedItems()) > 0
        self.btn_editar.setEnabled(tiene_seleccion)
        self.btn_eliminar.setEnabled(tiene_seleccion)
        self.btn_entrada.setEnabled(tiene_seleccion)
        self.btn_salida.setEnabled(tiene_seleccion)

    def agregar_extra(self):
        """Abre el diálogo para agregar un nuevo extra"""
        dialogo = DialogoAgregarExtra(self)
        if dialogo.exec_() == QDialog.Accepted:
            self.guardar_extra_bd(dialogo.extra_guardado)

    def editar_extra(self):
        """Abre el diálogo para editar el extra seleccionado"""
        fila_seleccionada = self.tabla_extras.currentRow()
        if fila_seleccionada < 0:
            return

        extra_id = int(self.tabla_extras.item(fila_seleccionada, 0).text())
        extra_data = self.obtener_extra_por_id(extra_id)

        if extra_data:
            dialogo = DialogoAgregarExtra(self, extra_data, es_edicion=True)
            if dialogo.exec_() == QDialog.Accepted:
                self.actualizar_extra_bd(extra_id, dialogo.extra_guardado)

    def eliminar_extra(self):
        """Elimina el extra seleccionado"""
        fila_seleccionada = self.tabla_extras.currentRow()
        if fila_seleccionada < 0:
            return

        nombre_extra = self.tabla_extras.item(fila_seleccionada, 1).text()

        respuesta = QMessageBox.question(self, "Confirmar Eliminación",
                                         f"¿Está seguro de eliminar el extra '{nombre_extra}'?\n\n"
                                         "Esta acción no se puede deshacer.",
                                         QMessageBox.Yes | QMessageBox.No)

        if respuesta == QMessageBox.Yes:
            extra_id = int(self.tabla_extras.item(fila_seleccionada, 0).text())
            self.eliminar_extra_bd(extra_id)

    def entrada_stock(self):
        """Registra entrada de stock"""
        self.movimiento_stock("entrada")

    def salida_stock(self):
        """Registra salida de stock"""
        self.movimiento_stock("salida")

    def movimiento_stock(self, tipo):
        """Maneja movimientos de entrada y salida de stock"""
        fila_seleccionada = self.tabla_extras.currentRow()
        if fila_seleccionada < 0:
            return

        extra_id = int(self.tabla_extras.item(fila_seleccionada, 0).text())
        nombre_extra = self.tabla_extras.item(fila_seleccionada, 1).text()
        stock_actual = int(self.tabla_extras.item(fila_seleccionada, 3).text())

        dialogo = DialogoMovimientoStock(self, nombre_extra, tipo)

        if dialogo.exec_() == QDialog.Accepted:
            cantidad = dialogo.movimiento_data['cantidad']

            # Validar salida de stock
            if tipo == "salida" and cantidad > stock_actual:
                QMessageBox.warning(self, "Stock Insuficiente",
                                    f"No hay suficiente stock. Disponible: {stock_actual}")
                return

            self.registrar_movimiento_bd(extra_id, dialogo.movimiento_data)

    def aplicar_filtros(self):
        """Aplica filtros de búsqueda y categoría"""
        filtro = self.combo_filtro.currentText()
        busqueda = self.txt_buscar.text().lower()

        for fila in range(self.tabla_extras.rowCount()):
            mostrar = True

            # Filtro por texto
            if busqueda:
                nombre = self.tabla_extras.item(fila, 1).text().lower()
                descripcion = self.tabla_extras.item(fila, 2).text().lower()
                if busqueda not in nombre and busqueda not in descripcion:
                    mostrar = False

            # Filtro por categoría
            if mostrar and filtro != "Todos":
                if filtro == "Stock Bajo":
                    stock = int(self.tabla_extras.item(fila, 3).text())
                    stock_min = int(self.tabla_extras.item(fila, 5).text())
                    mostrar = stock <= stock_min
                elif filtro == "Activos":
                    estado = self.tabla_extras.item(fila, 9).text()
                    mostrar = estado == "Activo"
                elif filtro == "Inactivos":
                    estado = self.tabla_extras.item(fila, 9).text()
                    mostrar = estado == "Inactivo"
                elif filtro == "Próximos a Vencer":
                    # Implementar lógica de vencimiento
                    try:
                        fecha_venc = self.tabla_extras.item(fila, 8).text()
                        if fecha_venc and fecha_venc != "None":
                            from datetime import datetime, timedelta
                            fecha_vencimiento = datetime.strptime(fecha_venc, "%Y-%m-%d")
                            fecha_limite = datetime.now() + timedelta(days=30)
                            mostrar = fecha_vencimiento <= fecha_limite
                        else:
                            mostrar = False
                    except:
                        mostrar = False

            self.tabla_extras.setRowHidden(fila, not mostrar)

    # Métodos de base de datos
    def guardar_extra_bd(self, extra_data):
        """Guarda un nuevo extra en la base de datos"""
        if not self.cursor:
            QMessageBox.warning(self, "Error", "No hay conexión a la base de datos")
            return

        try:
            query = '''
                INSERT INTO extras (nombre, descripcion, cantidad, unidad, stock_minimo,
                                  costo_unitario, proveedor, fecha_vencimiento, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            valores = (
                extra_data['nombre'], extra_data['descripcion'], extra_data['cantidad'],
                extra_data['unidad'], extra_data['stock_minimo'], extra_data['costo_unitario'],
                extra_data['proveedor'], extra_data['fecha_vencimiento'], extra_data['activo']
            )

            self.cursor.execute(query, valores)
            self.db_connection.commit()

            QMessageBox.information(self, "Éxito", f"Extra '{extra_data['nombre']}' agregado correctamente")
            self.cargar_extras()

        except pymysql.IntegrityError:
            QMessageBox.warning(self, "Error", "Ya existe un extra con ese nombre")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar extra: {e}")

    def actualizar_extra_bd(self, extra_id, extra_data):
        """Actualiza un extra existente en la base de datos"""
        if not self.cursor:
            return

        try:
            query = '''
                UPDATE extras SET nombre=%s, descripcion=%s, cantidad=%s, unidad=%s, stock_minimo=%s,
                                costo_unitario=%s, proveedor=%s, fecha_vencimiento=%s, activo=%s,
                                fecha_actualizacion=NOW()
                WHERE id=%s
            '''
            valores = (
                extra_data['nombre'], extra_data['descripcion'], extra_data['cantidad'],
                extra_data['unidad'], extra_data['stock_minimo'], extra_data['costo_unitario'],
                extra_data['proveedor'], extra_data['fecha_vencimiento'], extra_data['activo'],
                extra_id
            )

            self.cursor.execute(query, valores)
            self.db_connection.commit()

            QMessageBox.information(self, "Éxito", f"Extra '{extra_data['nombre']}' actualizado correctamente")
            self.cargar_extras()

        except pymysql.IntegrityError:
            QMessageBox.warning(self, "Error", "Ya existe otro extra con ese nombre")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar extra: {e}")

    def eliminar_extra_bd(self, extra_id):
        """Elimina un extra de la base de datos"""
        if not self.cursor:
            return

        try:
            # Primero eliminar movimientos asociados
            self.cursor.execute("DELETE FROM movimientos_stock_extras WHERE extra_id=%s", (extra_id,))

            # Luego eliminar el extra
            self.cursor.execute("DELETE FROM extras WHERE id=%s", (extra_id,))
            self.db_connection.commit()

            QMessageBox.information(self, "Éxito", "Extra eliminado correctamente")
            self.cargar_extras()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar extra: {e}")

    def obtener_extra_por_id(self, extra_id):
        """Obtiene los datos de un extra por su ID"""
        if not self.cursor:
            return None

        try:
            query = '''
                SELECT id, nombre, descripcion, cantidad, unidad, stock_minimo,
                       costo_unitario, proveedor, fecha_vencimiento, activo
                FROM extras WHERE id=%s
            '''
            self.cursor.execute(query, (extra_id,))
            resultado = self.cursor.fetchone()

            if resultado:
                return {
                    'id': resultado[0],
                    'nombre': resultado[1],
                    'descripcion': resultado[2],
                    'cantidad': resultado[3],
                    'unidad': resultado[4],
                    'stock_minimo': resultado[5],
                    'costo_unitario': resultado[6],
                    'proveedor': resultado[7],
                    'fecha_vencimiento': resultado[8],
                    'activo': resultado[9]
                }
            return None

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al obtener extra: {e}")
            return None

    def registrar_movimiento_bd(self, extra_id, movimiento_data):
        """Registra un movimiento de entrada o salida de stock"""
        if not self.cursor:
            return

        try:
            # Obtener stock actual
            self.cursor.execute("SELECT cantidad FROM extras WHERE id=%s", (extra_id,))
            resultado = self.cursor.fetchone()
            if not resultado:
                raise ValueError("Extra no encontrado")

            stock_actual = resultado[0]

            # Calcular nuevo stock
            cantidad = movimiento_data['cantidad']
            if movimiento_data['operacion'] == 'entrada':
                nuevo_stock = stock_actual + cantidad
            else:  # salida
                nuevo_stock = stock_actual - cantidad
                if nuevo_stock < 0:
                    raise ValueError("Stock no puede ser negativo")

            # Registrar movimiento
            query_mov = '''
                INSERT INTO movimientos_stock_extras (extra_id, tipo, cantidad, costo_total, observaciones)
                VALUES (%s, %s, %s, %s, %s)
            '''
            costo_total = movimiento_data.get('costo_total', 0.0)
            valores_mov = (
                extra_id, movimiento_data['operacion'], cantidad,
                costo_total, movimiento_data['observaciones']
            )

            self.cursor.execute(query_mov, valores_mov)

            # Actualizar stock del extra
            self.cursor.execute("UPDATE extras SET cantidad=%s WHERE id=%s", (nuevo_stock, extra_id))

            # Si es entrada y hay costo, actualizar costo unitario promedio
            if movimiento_data['operacion'] == 'entrada' and costo_total > 0:
                costo_unitario_nuevo = costo_total / cantidad
                # Calcular promedio ponderado con stock anterior
                if stock_actual > 0:
                    self.cursor.execute("SELECT costo_unitario FROM extras WHERE id=%s", (extra_id,))
                    costo_anterior = self.cursor.fetchone()[0]

                    # Promedio ponderado
                    costo_promedio = ((stock_actual * costo_anterior) + costo_total) / nuevo_stock
                    self.cursor.execute("UPDATE extras SET costo_unitario=%s WHERE id=%s", (costo_promedio, extra_id))
                else:
                    self.cursor.execute("UPDATE extras SET costo_unitario=%s WHERE id=%s",
                                        (costo_unitario_nuevo, extra_id))

            self.db_connection.commit()

            operacion_texto = "Entrada" if movimiento_data['operacion'] == 'entrada' else "Salida"
            QMessageBox.information(self, "Éxito",
                                    f"{operacion_texto} de {cantidad} unidades registrada correctamente")

            self.cargar_extras()

        except ValueError as ve:
            QMessageBox.warning(self, "Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar movimiento: {e}")

    def obtener_extras_para_medicamento(self):
        """Obtiene lista de extras activos para usar en medicamentos"""
        if not self.cursor:
            return []

        try:
            query = "SELECT nombre FROM extras WHERE activo=1 AND cantidad > 0 ORDER BY nombre"
            self.cursor.execute(query)
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error al obtener extras: {e}")
            return []

    def consumir_extra_por_medicamento(self, nombre_extra, cantidad=1):
        """Consume un extra cuando se usa en un medicamento"""
        if not self.cursor:
            return False, "No hay conexión a la base de datos"

        try:
            # Buscar el extra por nombre
            self.cursor.execute("SELECT id, cantidad FROM extras WHERE nombre=%s AND activo=1", (nombre_extra,))
            resultado = self.cursor.fetchone()

            if not resultado:
                return False, f"Extra '{nombre_extra}' no encontrado o inactivo"

            extra_id, stock_actual = resultado

            if stock_actual < cantidad:
                return False, f"Stock insuficiente. Disponible: {stock_actual}, Requerido: {cantidad}"

            # Registrar movimiento de salida
            movimiento_data = {
                'cantidad': cantidad,
                'operacion': 'salida',
                'observaciones': 'Consumo por medicamento'
            }

            self.registrar_movimiento_bd(extra_id, movimiento_data)
            return True, "Extra consumido correctamente"

        except Exception as e:
            return False, f"Error al consumir extra: {e}"

    def verificar_stock_bajo(self):
        """Verifica y retorna lista de extras con stock bajo"""
        if not self.cursor:
            return []

        try:
            query = '''
                SELECT nombre, cantidad, stock_minimo 
                FROM extras 
                WHERE cantidad <= stock_minimo AND activo=1
                ORDER BY (cantidad - stock_minimo)
            '''
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al verificar stock bajo: {e}")
            return []

    def generar_reporte_inventario(self):
        """Genera un reporte completo del inventario"""
        if not self.cursor:
            QMessageBox.warning(self, "Error", "No hay conexión a la base de datos")
            return

        try:
            # Obtener datos del inventario
            query = '''
                SELECT nombre, cantidad, unidad, stock_minimo, costo_unitario,
                       (cantidad * costo_unitario) as valor_total,
                       CASE WHEN cantidad <= stock_minimo THEN 'BAJO' ELSE 'OK' END as estado_stock
                FROM extras 
                WHERE activo=1 
                ORDER BY nombre
            '''
            self.cursor.execute(query)
            inventario = self.cursor.fetchall()

            # Crear ventana de reporte
            dialogo_reporte = QDialog(self)
            dialogo_reporte.setWindowTitle("Reporte de Inventario")
            dialogo_reporte.setMinimumSize(800, 600)

            layout = QVBoxLayout()

            # Texto del reporte
            texto_reporte = QTextEdit()
            texto_reporte.setReadOnly(True)

            reporte = "REPORTE DE INVENTARIO DE EXTRAS\n"
            reporte += "=" * 50 + "\n\n"
            reporte += f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"

            total_items = len(inventario)
            valor_total = sum(float(item[5]) for item in inventario)
            items_bajo_stock = sum(1 for item in inventario if item[6] == 'BAJO')

            reporte += f"Resumen:\n"
            reporte += f"- Total de extras: {total_items}\n"
            reporte += f"- Valor total del inventario: Q{valor_total:.2f}\n"
            reporte += f"- Items con stock bajo: {items_bajo_stock}\n\n"

            reporte += "Detalle del inventario:\n"
            reporte += "-" * 80 + "\n"
            reporte += f"{'Nombre':<20} {'Stock':<8} {'Unidad':<10} {'Mín.':<6} {'Costo':<10} {'Valor':<10} {'Estado':<8}\n"
            reporte += "-" * 80 + "\n"

            for item in inventario:
                nombre, cantidad, unidad, stock_min, costo, valor, estado = item
                reporte += f"{nombre:<20} {cantidad:<8} {unidad:<10} {stock_min:<6} Q{float(costo):<9.2f} Q{float(valor):<9.2f} {estado:<8}\n"

            texto_reporte.setPlainText(reporte)
            layout.addWidget(texto_reporte)

            # Botones
            botones_layout = QHBoxLayout()
            btn_exportar = QPushButton("Exportar a Archivo")
            btn_cerrar = QPushButton("Cerrar")

            btn_exportar.clicked.connect(lambda: self.exportar_reporte(reporte))
            btn_cerrar.clicked.connect(dialogo_reporte.accept)

            botones_layout.addWidget(btn_exportar)
            botones_layout.addWidget(btn_cerrar)
            layout.addLayout(botones_layout)

            dialogo_reporte.setLayout(layout)
            dialogo_reporte.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar reporte: {e}")

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


# CLASE PARA INTEGRAR CON EL SISTEMA DE MEDICAMENTOS
class GestorExtras:
    """Clase para gestionar extras desde otros módulos del sistema"""

    def __init__(self):
        self.db_connection = None
        self.cursor = None
        self.conectar_bd()

    def conectar_bd(self):
        """Conecta a la base de datos de extras"""
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
            print(f"Error conectando a BD de extras: {e}")

    def obtener_extras_disponibles(self):
        """Obtiene lista de extras disponibles para medicamentos"""
        if not self.cursor:
            return []

        try:
            self.cursor.execute("SELECT nombre FROM extras WHERE activo=1 AND cantidad > 0 ORDER BY nombre")
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error obteniendo extras: {e}")
            return []

    def consumir_extras(self, extras_lista):
        """Consume una lista de extras (para uso con medicamentos)"""
        if not self.cursor or not extras_lista:
            return True, "Sin extras para consumir"

        try:
            for extra_nombre in extras_lista:
                # Verificar stock
                self.cursor.execute("SELECT id, cantidad FROM extras WHERE nombre=%s AND activo=1", (extra_nombre,))
                resultado = self.cursor.fetchone()

                if not resultado:
                    return False, f"Extra '{extra_nombre}' no disponible"

                extra_id, stock = resultado
                if stock <= 0:
                    return False, f"Sin stock de '{extra_nombre}'"

                # Consumir 1 unidad
                nuevo_stock = stock - 1
                self.cursor.execute("UPDATE extras SET cantidad=%s WHERE id=%s", (nuevo_stock, extra_id))

                # Registrar movimiento
                self.cursor.execute('''
                    INSERT INTO movimientos_stock_extras (extra_id, tipo, cantidad, observaciones)
                    VALUES (%s, 'salida', 1, 'Consumo por medicamento')
                ''', (extra_id,))

            self.db_connection.commit()
            return True, "Extras consumidos correctamente"

        except Exception as e:
            self.db_connection.rollback()
            return False, f"Error consumiendo extras: {e}"

    def __del__(self):
        """Cierra la conexión al destruir el objeto"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.db_connection:
                self.db_connection.close()
        except:
            pass


# FUNCIÓN PRINCIPAL PARA ABRIR LA VENTANA
def abrir_gestion_extras():
    """Función para abrir la ventana de gestión de extras"""
    import sys

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    ventana = VentanaGestionExtras()
    ventana.show()

    return ventana


# CLASE ACTUALIZADA PARA LA VENTANA DE SELECCIÓN DE EXTRAS (para medicamentos)
class VentanaExtrasActualizada(QDialog):
    """Ventana mejorada para seleccionar extras al agregar medicamentos"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.extras_seleccionados = []
        self.gestor_extras = GestorExtras()
        self.setup_ui()
        self.cargar_extras_disponibles()

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

        # Instrucciones
        instrucciones = QLabel(
            "Selecciona los extras que se incluyen con este medicamento. Los extras seleccionados se descontarán automáticamente del inventario.")
        instrucciones.setWordWrap(True)
        instrucciones.setStyleSheet(
            "color: #666; margin: 10px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(instrucciones)

        # Lista de extras disponibles
        extras_label = QLabel("Extras disponibles en inventario:")
        extras_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(extras_label)

        # Tabla de extras disponibles
        self.tabla_extras_disponibles = QTableWidget()
        self.tabla_extras_disponibles.setColumnCount(4)
        self.tabla_extras_disponibles.setHorizontalHeaderLabels(["Seleccionar", "Nombre", "Stock", "Unidad"])

        # Configurar tabla
        header = self.tabla_extras_disponibles.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Checkbox
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nombre
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Stock
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Unidad

        self.tabla_extras_disponibles.setMaximumHeight(200)
        layout.addWidget(self.tabla_extras_disponibles)

        # Lista de extras seleccionados
        seleccionados_label = QLabel("Extras seleccionados:")
        seleccionados_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(seleccionados_label)

        self.txt_extras_seleccionados = QTextEdit()
        self.txt_extras_seleccionados.setMaximumHeight(100)
        self.txt_extras_seleccionados.setReadOnly(True)
        self.txt_extras_seleccionados.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc;")
        layout.addWidget(self.txt_extras_seleccionados)

        # Botones
        botones_layout = QHBoxLayout()

        btn_aceptar = QPushButton("Confirmar Selección")
        btn_aceptar.clicked.connect(self.confirmar_seleccion)
        btn_aceptar.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 8px; font-weight: bold; }")

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 8px; }")

        btn_gestionar = QPushButton("Gestionar Inventario")
        btn_gestionar.clicked.connect(self.abrir_gestion_inventario)
        btn_gestionar.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px; }")

        botones_layout.addWidget(btn_aceptar)
        botones_layout.addWidget(btn_gestionar)
        botones_layout.addWidget(btn_cancelar)

        layout.addLayout(botones_layout)
        self.setLayout(layout)

    def cargar_extras_disponibles(self):
        """Carga los extras disponibles desde la base de datos"""
        try:
            if not self.gestor_extras.cursor:
                self.tabla_extras_disponibles.setRowCount(1)
                self.tabla_extras_disponibles.setItem(0, 1, QTableWidgetItem("No hay conexión a la base de datos"))
                return

            query = "SELECT nombre, cantidad, unidad FROM extras WHERE activo=1 ORDER BY nombre"
            self.gestor_extras.cursor.execute(query)
            extras = self.gestor_extras.cursor.fetchall()

            self.tabla_extras_disponibles.setRowCount(len(extras))

            for row, (nombre, cantidad, unidad) in enumerate(extras):
                # Checkbox
                checkbox = QCheckBox()
                checkbox.stateChanged.connect(self.actualizar_seleccion)
                self.tabla_extras_disponibles.setCellWidget(row, 0, checkbox)

                # Nombre
                self.tabla_extras_disponibles.setItem(row, 1, QTableWidgetItem(nombre))

                # Stock
                item_stock = QTableWidgetItem(str(cantidad))
                if cantidad <= 0:
                    item_stock.setForeground(QColor("red"))
                    checkbox.setEnabled(False)
                self.tabla_extras_disponibles.setItem(row, 2, item_stock)

                # Unidad
                self.tabla_extras_disponibles.setItem(row, 3, QTableWidgetItem(unidad))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar extras: {e}")

    def actualizar_seleccion(self):
        """Actualiza la lista de extras seleccionados"""
        self.extras_seleccionados = []

        for row in range(self.tabla_extras_disponibles.rowCount()):
            checkbox = self.tabla_extras_disponibles.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                nombre = self.tabla_extras_disponibles.item(row, 1).text()
                self.extras_seleccionados.append(nombre)

        # Actualizar texto
        if self.extras_seleccionados:
            texto = "• " + "\n• ".join(self.extras_seleccionados)
        else:
            texto = "Ningún extra seleccionado"

        self.txt_extras_seleccionados.setPlainText(texto)

    def confirmar_seleccion(self):
        """Confirma la selección de extras"""
        if not self.extras_seleccionados:
            respuesta = QMessageBox.question(self, "Sin extras",
                                             "No has seleccionado ningún extra. ¿Deseas continuar sin extras?",
                                             QMessageBox.Yes | QMessageBox.No)
            if respuesta == QMessageBox.No:
                return

        # Enviar extras al formulario principal
        if hasattr(self.parent, 'recibir_extras'):
            self.parent.recibir_extras(self.extras_seleccionados)

        self.accept()

    def abrir_gestion_inventario(self):
        """Abre la ventana de gestión de inventario de extras"""
        try:
            ventana_gestion = VentanaGestionExtras()
            ventana_gestion.exec_()
            # Recargar extras después de cerrar la ventana de gestión
            self.cargar_extras_disponibles()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al abrir gestión de inventario: {e}")



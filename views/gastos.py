import sys

import pymysql
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QWidget, QLabel, QMessageBox,
                             QHBoxLayout, QLineEdit, QHeaderView, QComboBox, QDialog,
                             QFormLayout, QListWidget, QAbstractItemView, QDialogButtonBox)
from PyQt5.QtCore import Qt
from openpyxl.styles.alignment import horizontal_alignments


class DialogoNuevoTipoGasto(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Nuevo Tipo de Gasto")
        self.setGeometry(300, 300, 300, 100)
        self.initUI()

    def initUI(self):
        layout = QFormLayout()
        self.setLayout(layout)

        self.txt_nuevo_tipo = QLineEdit()
        layout.addRow("Nombre del nuevo tipo de gasto:", self.txt_nuevo_tipo)

        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.accept)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)

        btn_layout.addWidget(btn_guardar)
        btn_layout.addWidget(btn_cancelar)
        layout.addRow("", btn_layout)

    def get_nuevo_tipo(self):
        return self.txt_nuevo_tipo.text()


class DialogoGestionTiposGasto(QDialog):
    def __init__(self, tipos_gasto, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestionar Tipos de Gasto")
        self.setGeometry(300, 300, 400, 300)
        self.tipos_gasto = tipos_gasto
        self.tipos_a_eliminar = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Instrucciones
        lbl_instrucciones = QLabel("Seleccione los tipos de gasto que desea eliminar:")
        layout.addWidget(lbl_instrucciones)

        # Lista de tipos de gasto
        self.list_tipos = QListWidget()
        self.list_tipos.setSelectionMode(QAbstractItemView.MultiSelection)
        for tipo in self.tipos_gasto:
            self.list_tipos.addItem(tipo)
        layout.addWidget(self.list_tipos)

        # Advertencia
        lbl_advertencia = QLabel("NOTA: Solo se eliminarán los tipos que no estén asociados a gastos existentes.")
        lbl_advertencia.setStyleSheet("color: red")
        layout.addWidget(lbl_advertencia)

        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_tipos_a_eliminar(self):
        items_seleccionados = self.list_tipos.selectedItems()
        return [item.text() for item in items_seleccionados]


class GastosApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gastos")
        self.setGeometry(500, 225, 900, 500)
        self.tipos_gasto = ["Administrativo", "Compras", "Servicios", "Mantenimiento", "Personal", "Otros"]
        self.initUI()
        self.conectar_bd()
        self.cargar_tipos_gasto()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Título
        lbl_titulo = QLabel("Gastos")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)

        # Formulario para agregar registros
        form_layout = QHBoxLayout()

        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setPlaceholderText("Descripción")
        form_layout.addWidget(self.txt_descripcion)

        self.txt_comprobante = QLineEdit()
        self.txt_comprobante.setPlaceholderText("Monto")
        form_layout.addWidget(self.txt_comprobante)

        # Layout para el combo y los botones de gestión
        cmb_layout = QHBoxLayout()

        self.cmb_tipo_gasto = QComboBox()
        self.cmb_tipo_gasto.addItems(self.tipos_gasto)
        cmb_layout.addWidget(self.cmb_tipo_gasto)

        # Botón para agregar un nuevo tipo de gasto
        btn_nuevo_tipo = QPushButton("+")
        btn_nuevo_tipo.setToolTip("Agregar nuevo tipo de gasto")
        btn_nuevo_tipo.setFixedWidth(30)
        btn_nuevo_tipo.clicked.connect(self.agregar_nuevo_tipo_gasto)
        cmb_layout.addWidget(btn_nuevo_tipo)

        # Botón para gestionar tipos de gasto (eliminar)
        btn_gestionar_tipos = QPushButton("⚙️")
        btn_gestionar_tipos.setToolTip("Gestionar tipos de gasto")
        btn_gestionar_tipos.setFixedWidth(30)
        btn_gestionar_tipos.clicked.connect(self.gestionar_tipos_gasto)
        cmb_layout.addWidget(btn_gestionar_tipos)

        form_layout.addLayout(cmb_layout)

        btn_agregar = QPushButton("Agregar")
        btn_agregar.clicked.connect(self.agregar_registro)
        form_layout.addWidget(btn_agregar)

        layout.addLayout(form_layout)

        # Crear tabla
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Descripción", "Monto", "Monto_final", "TIPO DE GASTO"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        # Botones inferiores
        btn_layout = QHBoxLayout()

        btn_guardar = QPushButton("Guardar en Base de Datos")
        btn_guardar.clicked.connect(self.guardar_en_bd)
        btn_layout.addWidget(btn_guardar)

        btn_limpiar = QPushButton("Limpiar Tabla")
        btn_limpiar.clicked.connect(self.limpiar_tabla)
        btn_layout.addWidget(btn_limpiar)

        layout.addLayout(btn_layout)

        # Label para el total
        self.lbl_total = QLabel("Total de Gastos: Q0.00")
        self.lbl_total.setAlignment(Qt.AlignRight)
        layout.addWidget(self.lbl_total)

    def conectar_bd(self):
        try:
            self.conn = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",
                database="bdhidrocolon"
            )
            print("Conexión a la base de datos exitosa")

            # Crear tabla si no existe
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gastos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    descripcion VARCHAR(200),
                    no_comprobante VARCHAR(50),
                    monto DECIMAL(10,2),
                    tipo_gasto VARCHAR(50),
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Crear tabla para tipos de gasto si no existe
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tipos_gasto (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) UNIQUE
                )
            ''')

            # Insertar tipos de gasto predeterminados si la tabla está vacía
            cursor.execute("SELECT COUNT(*) FROM tipos_gasto")
            count = cursor.fetchone()[0]

            if count == 0:
                for tipo in self.tipos_gasto:
                    cursor.execute("INSERT INTO tipos_gasto (nombre) VALUES (%s)", (tipo,))

            self.conn.commit()
            cursor.close()

        except Exception as err:
            QMessageBox.critical(self, "Error de BD", f"Error al conectar a MySQL: {err}")

    def cargar_tipos_gasto(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT nombre FROM tipos_gasto ORDER BY nombre")
            tipos = cursor.fetchall()
            cursor.close()

            # Actualizar la lista local de tipos de gasto
            self.tipos_gasto = [tipo[0] for tipo in tipos]

            # Actualizar el combobox
            self.cmb_tipo_gasto.clear()
            self.cmb_tipo_gasto.addItems(self.tipos_gasto)

        except Exception as err:
            print(f"Error al cargar tipos de gasto: {err}")

    def agregar_nuevo_tipo_gasto(self):
        dialogo = DialogoNuevoTipoGasto(self)
        if dialogo.exec_():
            nuevo_tipo = dialogo.get_nuevo_tipo()
            if nuevo_tipo and nuevo_tipo not in self.tipos_gasto:
                try:
                    cursor = self.conn.cursor()
                    cursor.execute("INSERT INTO tipos_gasto (nombre) VALUES (%s)", (nuevo_tipo,))
                    self.conn.commit()
                    cursor.close()

                    # Actualizar la lista de tipos de gasto
                    self.cargar_tipos_gasto()
                    QMessageBox.information(self, "Éxito", f"Tipo de gasto '{nuevo_tipo}' agregado correctamente.")

                except Exception as err:
                    QMessageBox.critical(self, "Error", f"No se pudo agregar el tipo de gasto: {err}")
            elif nuevo_tipo in self.tipos_gasto:
                QMessageBox.warning(self, "Advertencia", "Este tipo de gasto ya existe.")
            else:
                QMessageBox.warning(self, "Advertencia", "Debe ingresar un nombre para el tipo de gasto.")

    def gestionar_tipos_gasto(self):
        dialogo = DialogoGestionTiposGasto(self.tipos_gasto, self)
        if dialogo.exec_():
            tipos_a_eliminar = dialogo.get_tipos_a_eliminar()
            if tipos_a_eliminar:
                self.eliminar_tipos_gasto(tipos_a_eliminar)
            else:
                QMessageBox.information(self, "Información", "No se seleccionó ningún tipo de gasto para eliminar.")

    def eliminar_tipos_gasto(self, tipos_a_eliminar):
        try:
            cursor = self.conn.cursor()

            # Verificar qué tipos se pueden eliminar (no están asociados a gastos)
            tipos_no_eliminables = []
            tipos_eliminados = []

            for tipo in tipos_a_eliminar:
                # Verificar si el tipo está siendo usado
                cursor.execute("SELECT COUNT(*) FROM gastos WHERE tipo_gasto = %s", (tipo,))
                count = cursor.fetchone()[0]

                if count > 0:
                    tipos_no_eliminables.append(tipo)
                else:
                    # Eliminar el tipo
                    cursor.execute("DELETE FROM tipos_gasto WHERE nombre = %s", (tipo,))
                    tipos_eliminados.append(tipo)

            self.conn.commit()

            # Actualizar la lista de tipos de gasto
            self.cargar_tipos_gasto()

            # Mostrar resultados
            mensaje = ""
            if tipos_eliminados:
                mensaje += f"Se eliminaron {len(tipos_eliminados)} tipos de gasto.\n"
            if tipos_no_eliminables:
                mensaje += f"No se pudieron eliminar los siguientes tipos porque están en uso:\n- " + "\n- ".join(
                    tipos_no_eliminables)

            QMessageBox.information(self, "Resultado", mensaje)

            cursor.close()

        except Exception as err:
            QMessageBox.critical(self, "Error", f"Error al eliminar tipos de gasto: {err}")

    def agregar_registro(self):
        try:
            # Obtener datos del formulario
            descripcion = self.txt_descripcion.text()
            no_comprobante = self.txt_comprobante.text()
            tipo_gasto = self.cmb_tipo_gasto.currentText()

            # Validar que haya datos
            if not descripcion:
                QMessageBox.warning(self, "Datos incompletos", "Debe ingresar una descripción")
                return

            # Validar que el comprobante sea un número
            try:
                valor_comprobante = float(no_comprobante)
                # Calcular el monto (número de comprobante menos el 6%)
                descuento = valor_comprobante * 0.06
                monto = valor_comprobante - descuento
            except ValueError:
                QMessageBox.warning(self, "Error", "El número de comprobante debe ser un número válido")
                return

            # Agregar fila a la tabla
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # Insertar datos en la fila
            self.table.setItem(row_position, 0, QTableWidgetItem(descripcion))
            self.table.setItem(row_position, 1, QTableWidgetItem(no_comprobante))
            self.table.setItem(row_position, 2, QTableWidgetItem(f"{monto:.2f}"))
            self.table.setItem(row_position, 3, QTableWidgetItem(tipo_gasto))

            # Actualizar total
            self.actualizar_total()

            # Limpiar campos de entrada
            self.txt_descripcion.clear()
            self.txt_comprobante.clear()
            self.txt_descripcion.setFocus()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar registro: {e}")

    def actualizar_total(self):
        total = 0

        for row in range(self.table.rowCount()):
            try:
                total += float(self.table.item(row, 2).text())
            except (ValueError, AttributeError):
                pass

        self.lbl_total.setText(f"Total de Gastos: Q{total:.2f}")

    def guardar_en_bd(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Advertencia", "No hay datos para guardar")
            return

        try:
            cursor = self.conn.cursor()

            # Preparar la consulta
            query = '''
                INSERT INTO gastos 
                (descripcion, no_comprobante, monto, tipo_gasto) 
                VALUES (%s, %s, %s, %s)
            '''

            # Recopilar datos de cada fila
            registros = 0
            for row in range(self.table.rowCount()):
                descripcion = self.table.item(row, 0).text()
                no_comprobante = self.table.item(row, 1).text()
                monto = float(self.table.item(row, 2).text())
                tipo_gasto = self.table.item(row, 3).text()

                # Insertar en la base de datos
                datos = (descripcion, no_comprobante, monto, tipo_gasto)
                cursor.execute(query, datos)
                registros += 1

            self.conn.commit()
            cursor.close()

            QMessageBox.information(self, "Éxito",
                                    f"{registros} registros guardados correctamente en la base de datos.")
            self.limpiar_tabla()

        except Exception as err:
            QMessageBox.critical(self, "Error de BD", f"Error al guardar datos: {err}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {e}")

    def limpiar_tabla(self):
        self.table.setRowCount(0)
        self.actualizar_total()

    def closeEvent(self, event):
        # Cerrar la conexión a la base de datos al cerrar la aplicación
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
                print("Conexión a la base de datos cerrada")
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")
        event.accept()


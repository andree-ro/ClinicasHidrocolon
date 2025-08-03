import sys

import pymysql
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QWidget, QLabel, QMessageBox,
                             QHBoxLayout, QLineEdit, QHeaderView)
from PyQt5.QtCore import Qt


class IngresoTarjetaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ingreso Tarjeta")
        self.setGeometry(500, 225, 800, 500)
        self.initUI()
        self.conectar_bd()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Título
        lbl_titulo = QLabel("Ingreso Tarjeta")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)

        # Formulario para agregar registros
        form_layout = QHBoxLayout()

        self.txt_voucher = QLineEdit()
        self.txt_voucher.setPlaceholderText("No. Voucher")
        form_layout.addWidget(self.txt_voucher)

        self.txt_paciente = QLineEdit()
        self.txt_paciente.setPlaceholderText("Nombre paciente")
        form_layout.addWidget(self.txt_paciente)

        self.txt_total = QLineEdit()
        self.txt_total.setPlaceholderText("Total Real")
        form_layout.addWidget(self.txt_total)

        btn_agregar = QPushButton("Agregar")
        btn_agregar.clicked.connect(self.agregar_registro)
        form_layout.addWidget(btn_agregar)

        layout.addLayout(form_layout)

        # Crear tabla
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["No. Voucher", "Nombre paciente", "Total Real", "Total en Bancos"])
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

        # Label para totales
        self.lbl_totales = QLabel("Total Real: Q0.00 | Total en Bancos: Q0.00")
        self.lbl_totales.setAlignment(Qt.AlignRight)
        layout.addWidget(self.lbl_totales)

    def conectar_bd(self):
        try:
            self.conn = pymysql.connect(
                host="127.0.0.1",
                user="root",  # Cambia esto a tu usuario de MySQL
                password="2332",  # Cambia esto a tu contraseña de MySQL
                database="bdhidrocolon"  # Asegúrate de crear esta base de datos primero
            )
            print("Conexión a la base de datos exitosa")

            # Crear tabla si no existe
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ingreso_tarjeta (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    no_voucher VARCHAR(50),
                    nombre_paciente VARCHAR(100),
                    total_real DECIMAL(10,2),
                    total_bancos DECIMAL(10,2),
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
            cursor.close()

        except Exception as err:
            QMessageBox.critical(self, "Error de BD", f"Error al conectar a MySQL: {err}")

    def agregar_registro(self):
        try:
            # Obtener datos del formulario
            no_voucher = self.txt_voucher.text()
            nombre_paciente = self.txt_paciente.text()

            # Validar que el total sea un número
            try:
                total_real = float(self.txt_total.text())
            except ValueError:
                QMessageBox.warning(self, "Error", "El total debe ser un número válido")
                return

            # Calcular el total en bancos (menos 6%)
            total_bancos = total_real * 0.94  # 100% - 6% = 94%

            # Agregar fila a la tabla
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # Insertar datos en la fila
            self.table.setItem(row_position, 0, QTableWidgetItem(no_voucher))
            self.table.setItem(row_position, 1, QTableWidgetItem(nombre_paciente))
            self.table.setItem(row_position, 2, QTableWidgetItem(f"{total_real:.2f}"))
            self.table.setItem(row_position, 3, QTableWidgetItem(f"{total_bancos:.2f}"))

            # Actualizar totales
            self.actualizar_totales()

            # Limpiar campos de entrada
            self.txt_voucher.clear()
            self.txt_paciente.clear()
            self.txt_total.clear()
            self.txt_voucher.setFocus()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar registro: {e}")

    def actualizar_totales(self):
        total_real = 0
        total_bancos = 0

        for row in range(self.table.rowCount()):
            try:
                total_real += float(self.table.item(row, 2).text())
                total_bancos += float(self.table.item(row, 3).text())
            except (ValueError, AttributeError):
                pass

        self.lbl_totales.setText(f"Total Real: Q{total_real:.2f} | Total en Bancos: Q{total_bancos:.2f}")

    def guardar_en_bd(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Advertencia", "No hay datos para guardar")
            return

        try:
            cursor = self.conn.cursor()

            # Preparar la consulta
            query = '''
                INSERT INTO ingreso_tarjeta 
                (no_voucher, nombre_paciente, total_real, total_bancos) 
                VALUES (%s, %s, %s, %s)
            '''

            # Recopilar datos de cada fila
            registros = 0
            for row in range(self.table.rowCount()):
                no_voucher = self.table.item(row, 0).text()
                nombre_paciente = self.table.item(row, 1).text()
                total_real = float(self.table.item(row, 2).text())
                total_bancos = float(self.table.item(row, 3).text())

                # Insertar en la base de datos
                datos = (no_voucher, nombre_paciente, total_real, total_bancos)
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
        self.actualizar_totales()


#if __name__ == "__main__":
#    app = QApplication(sys.argv)
#    window = IngresoTarjetaApp()
#    window.show()
#    sys.exit(app.exec_())
import sys

import pymysql
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QPushButton, QWidget, QLabel, QMessageBox,
                             QHBoxLayout, QLineEdit, QHeaderView)
from PyQt5.QtCore import Qt


class IngresoTransferenciaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ingreso Transferencia")
        self.setGeometry(500, 225, 800, 500)
        self.initUI()
        self.conectar_bd()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Título
        lbl_titulo = QLabel("Ingreso Transferencia")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)

        # Formulario para agregar registros
        form_layout = QHBoxLayout()

        self.txt_boleta = QLineEdit()
        self.txt_boleta.setPlaceholderText("No. Boleta")
        form_layout.addWidget(self.txt_boleta)

        self.txt_paciente = QLineEdit()
        self.txt_paciente.setPlaceholderText("Nombre paciente")
        form_layout.addWidget(self.txt_paciente)

        self.txt_total = QLineEdit()
        self.txt_total.setPlaceholderText("Total")
        form_layout.addWidget(self.txt_total)

        btn_agregar = QPushButton("Agregar")
        btn_agregar.clicked.connect(self.agregar_registro)
        form_layout.addWidget(btn_agregar)

        layout.addLayout(form_layout)

        # Crear tabla
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["No. Boleta", "Nombre paciente", "Total"])
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
        self.lbl_total = QLabel("Total: Q0.00")
        self.lbl_total.setAlignment(Qt.AlignRight)
        layout.addWidget(self.lbl_total)

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
                CREATE TABLE IF NOT EXISTS ingreso_transferencia (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    no_boleta VARCHAR(50),
                    nombre_paciente VARCHAR(100),
                    total DECIMAL(10,2),
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
            no_boleta = self.txt_boleta.text()
            nombre_paciente = self.txt_paciente.text()

            # Validar que haya datos
            if not no_boleta or not nombre_paciente:
                QMessageBox.warning(self, "Datos incompletos",
                                    "Debe ingresar el número de boleta y el nombre del paciente")
                return

            # Validar que el total sea un número
            try:
                total = float(self.txt_total.text())
            except ValueError:
                QMessageBox.warning(self, "Error", "El total debe ser un número válido")
                return

            # Agregar fila a la tabla
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # Insertar datos en la fila
            self.table.setItem(row_position, 0, QTableWidgetItem(no_boleta))
            self.table.setItem(row_position, 1, QTableWidgetItem(nombre_paciente))
            self.table.setItem(row_position, 2, QTableWidgetItem(f"{total:.2f}"))

            # Actualizar total
            self.actualizar_total()

            # Limpiar campos de entrada
            self.txt_boleta.clear()
            self.txt_paciente.clear()
            self.txt_total.clear()
            self.txt_boleta.setFocus()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar registro: {e}")

    def actualizar_total(self):
        total = 0

        for row in range(self.table.rowCount()):
            try:
                total += float(self.table.item(row, 2).text())
            except (ValueError, AttributeError):
                pass

        self.lbl_total.setText(f"Total: Q{total:.2f}")

    def guardar_en_bd(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Advertencia", "No hay datos para guardar")
            return

        try:
            cursor = self.conn.cursor()

            # Preparar la consulta
            query = '''
                INSERT INTO ingreso_transferencia 
                (no_boleta, nombre_paciente, total) 
                VALUES (%s, %s, %s)
            '''

            # Recopilar datos de cada fila
            registros = 0
            for row in range(self.table.rowCount()):
                no_boleta = self.table.item(row, 0).text()
                nombre_paciente = self.table.item(row, 1).text()
                total = float(self.table.item(row, 2).text())

                # Insertar en la base de datos
                datos = (no_boleta, nombre_paciente, total)
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


#if __name__ == "__main__":
#    app = QApplication(sys.argv)
#    window = IngresoTransferenciaApp()
#    window.show()
#    sys.exit(app.exec_())
import sys

import pymysql
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QHeaderView,
    QDialog, QGridLayout
)
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, Qt
from datetime import datetime, date
import calendar


class ConsultaChequesMensuales(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Consulta de Cheques Mensuales")
        self.setGeometry(700, 225, 1000, 600)
        self.setup_ui()
        self.cargar_cheques_mes_actual()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Cheques del Mes Actual")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        # Selector de mes
        mes_label = QLabel("Seleccionar mes:")
        self.mes_selector = QComboBox()
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.mes_selector.addItems(meses)
        # Establecer el mes actual
        mes_actual = datetime.now().month - 1  # -1 porque los índices comienzan en 0
        self.mes_selector.setCurrentIndex(mes_actual)
        self.mes_selector.currentIndexChanged.connect(self.cargar_cheques_mes_seleccionado)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(mes_label)
        header_layout.addWidget(self.mes_selector)

        layout.addLayout(header_layout)

        # Tabla de cheques
        self.tabla_cheques = QTableWidget()
        self.tabla_cheques.setColumnCount(7)  # Añadimos una columna para ID
        self.tabla_cheques.setHorizontalHeaderLabels(
            ["ID", "No. Cheque", "Fecha", "Nombre", "Detalle", "Monto", "Estado"])
        self.tabla_cheques.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_cheques.setColumnHidden(0, True)  # Ocultamos la columna ID
        layout.addWidget(self.tabla_cheques)

        # Botones inferiores
        botones_layout = QHBoxLayout()

        self.guardar_cambios_btn = QPushButton("Guardar Cambios")
        self.guardar_cambios_btn.clicked.connect(self.guardar_cambios)

        self.cerrar_btn = QPushButton("Cerrar")
        self.cerrar_btn.clicked.connect(self.close)

        botones_layout.addWidget(self.guardar_cambios_btn)
        botones_layout.addWidget(self.cerrar_btn)

        layout.addLayout(botones_layout)
        self.setLayout(layout)

    def cargar_cheques_mes_actual(self):
        self.cargar_cheques_mes_seleccionado()

    def cargar_cheques_mes_seleccionado(self):
        mes_seleccionado = self.mes_selector.currentIndex() + 1  # +1 porque enero es 1, no 0
        anio_actual = datetime.now().year

        # Obtener el primer y último día del mes seleccionado
        ultimo_dia = calendar.monthrange(anio_actual, mes_seleccionado)[1]
        fecha_inicio = f"{anio_actual}-{mes_seleccionado:02d}-01"
        fecha_fin = f"{anio_actual}-{mes_seleccionado:02d}-{ultimo_dia:02d}"

        try:
            # Conectar a la base de datos
            conn = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",
                database="bdhidrocolon"
            )
            cursor = conn.cursor()

            # Consultar los cheques del mes seleccionado
            cursor.execute("""
                SELECT id, no_cheque, fecha, emitido_a, detalle, monto, estado 
                FROM cheques 
                WHERE fecha BETWEEN %s AND %s
                ORDER BY fecha
            """, (fecha_inicio, fecha_fin))

            cheques = cursor.fetchall()

            # Limpiar la tabla
            self.tabla_cheques.setRowCount(0)

            # Llenar la tabla con los datos
            for cheque in cheques:
                row = self.tabla_cheques.rowCount()
                self.tabla_cheques.insertRow(row)

                # Convertir fecha a string si es necesario
                fecha_str = cheque[2].strftime("%Y-%m-%d") if isinstance(cheque[2], date) else str(cheque[2])

                # Llenar las celdas
                self.tabla_cheques.setItem(row, 0, QTableWidgetItem(str(cheque[0])))  # ID oculto
                self.tabla_cheques.setItem(row, 1, QTableWidgetItem(str(cheque[1])))  # No. Cheque
                self.tabla_cheques.setItem(row, 2, QTableWidgetItem(fecha_str))  # Fecha
                self.tabla_cheques.setItem(row, 3, QTableWidgetItem(str(cheque[3])))  # Nombre
                self.tabla_cheques.setItem(row, 4, QTableWidgetItem(str(cheque[4])))  # Detalle
                self.tabla_cheques.setItem(row, 5, QTableWidgetItem(f"{float(cheque[5]):.2f}"))  # Monto

                # Usar combobox para el estado
                estado_combo = QComboBox()
                estado_combo.addItems(["Pagado", "Circulación"])
                estado_combo.setCurrentText(str(cheque[6]))
                self.tabla_cheques.setCellWidget(row, 6, estado_combo)

            cursor.close()
            conn.close()

        except Exception as err:
            QMessageBox.critical(self, "Error de MySQL", str(err))

    def guardar_cambios(self):
        try:
            # Conectar a la base de datos
            conn = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",
                database="bdhidrocolon"
            )
            cursor = conn.cursor()

            # Recorrer la tabla y actualizar los estados
            cambios_realizados = 0
            for row in range(self.tabla_cheques.rowCount()):
                cheque_id = self.tabla_cheques.item(row, 0).text()
                estado_combo = self.tabla_cheques.cellWidget(row, 6)
                nuevo_estado = estado_combo.currentText()

                # Actualizar el estado en la base de datos
                cursor.execute("""
                    UPDATE cheques SET estado = %s WHERE id = %s
                """, (nuevo_estado, cheque_id))
                cambios_realizados += cursor.rowcount

            conn.commit()
            cursor.close()
            conn.close()

            QMessageBox.information(self, "Éxito", f"Se actualizaron {cambios_realizados} registros correctamente")

        except Exception as err:
            QMessageBox.critical(self, "Error de MySQL", str(err))


class RegistroCheques(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro de Cheques")
        self.setGeometry(100, 100, 900, 500)
        self.setup_ui()
        self.conectar_db()

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Registro de Cheques")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Campos de entrada
        form_layout = QHBoxLayout()

        self.cheque_input = QLineEdit()
        self.cheque_input.setPlaceholderText("No. Cheque")

        self.fecha_input = QDateEdit()
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setCalendarPopup(True)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Emitido a nombre de")

        self.detalle_input = QLineEdit()
        self.detalle_input.setPlaceholderText("Detalle de gasto")

        self.monto_input = QLineEdit()
        self.monto_input.setPlaceholderText("Monto (Q)")

        self.estado_input = QComboBox()
        self.estado_input.addItems(["Pagado", "Circulación"])

        self.agregar_btn = QPushButton("Agregar")
        self.agregar_btn.clicked.connect(self.agregar_fila)

        form_layout.addWidget(self.cheque_input)
        form_layout.addWidget(self.fecha_input)
        form_layout.addWidget(self.nombre_input)
        form_layout.addWidget(self.detalle_input)
        form_layout.addWidget(self.monto_input)
        form_layout.addWidget(self.estado_input)
        form_layout.addWidget(self.agregar_btn)

        layout.addLayout(form_layout)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["No. Cheque", "Fecha", "Nombre", "Detalle", "Monto", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla)

        # Botones inferiores
        botones_layout = QHBoxLayout()
        self.guardar_btn = QPushButton("Guardar en Base de Datos")
        self.guardar_btn.clicked.connect(self.guardar_bd)

        self.limpiar_btn = QPushButton("Limpiar Tabla")
        self.limpiar_btn.clicked.connect(self.limpiar_tabla)

        # Nuevo botón para consultar cheques mensuales
        self.consultar_btn = QPushButton("Consultar Cheques Mensuales")
        self.consultar_btn.clicked.connect(self.abrir_consulta_mensual)

        self.total_label = QLabel("Total gastado: Q0.00")
        botones_layout.addWidget(self.guardar_btn)
        botones_layout.addWidget(self.limpiar_btn)
        botones_layout.addWidget(self.consultar_btn)
        botones_layout.addWidget(self.total_label)

        layout.addLayout(botones_layout)
        self.setLayout(layout)

    def conectar_db(self):
        try:
            self.conn = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",
                database="bdhidrocolon"
            )
            self.cursor = self.conn.cursor()
            print("Conexión exitosa")
        except Exception as err:
            QMessageBox.critical(self, "Error de conexión", str(err))

    def agregar_fila(self):
        cheque = self.cheque_input.text()
        fecha = self.fecha_input.date().toString("yyyy-MM-dd")
        nombre = self.nombre_input.text()
        detalle = self.detalle_input.text()
        monto = self.monto_input.text()
        estado = self.estado_input.currentText()

        if not (cheque and nombre and detalle and monto):
            QMessageBox.warning(self, "Campos incompletos", "Completa todos los campos")
            return

        try:
            monto = float(monto)
        except ValueError:
            QMessageBox.warning(self, "Error", "Monto debe ser numérico")
            return

        row = self.tabla.rowCount()
        self.tabla.insertRow(row)
        self.tabla.setItem(row, 0, QTableWidgetItem(cheque))
        self.tabla.setItem(row, 1, QTableWidgetItem(fecha))
        self.tabla.setItem(row, 2, QTableWidgetItem(nombre))
        self.tabla.setItem(row, 3, QTableWidgetItem(detalle))
        self.tabla.setItem(row, 4, QTableWidgetItem(f"{monto:.2f}"))
        self.tabla.setItem(row, 5, QTableWidgetItem(estado))

        self.actualizar_total()
        self.cheque_input.clear()
        self.nombre_input.clear()
        self.detalle_input.clear()
        self.monto_input.clear()

    def actualizar_total(self):
        total = 0
        for i in range(self.tabla.rowCount()):
            total += float(self.tabla.item(i, 4).text())
        self.total_label.setText(f"Total gastado: Q{total:.2f}")

    def limpiar_tabla(self):
        self.tabla.setRowCount(0)
        self.actualizar_total()

    def guardar_bd(self):
        if self.tabla.rowCount() == 0:
            QMessageBox.information(self, "Sin datos", "No hay datos para guardar")
            return

        try:
            for i in range(self.tabla.rowCount()):
                datos = [self.tabla.item(i, col).text() for col in range(6)]

                # Guardar en tabla 'cheques'
                self.cursor.execute("""
                    INSERT INTO cheques (no_cheque, fecha, emitido_a, detalle, monto, estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, datos)

                # Extraer datos para gastos
                descripcion = datos[3]  # detalle
                no_comprobante = datos[0]  # no_cheque
                monto = float(datos[4])
                tipo_gasto = "Cheque"
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                dato = monto * 0.06

                # Guardar en tabla 'gastos'
                self.cursor.execute("""
                    INSERT INTO gastos (descripcion, no_comprobante, monto, tipo_gasto, fecha)
                    VALUES (%s, %s, %s, %s, %s)
                """, (descripcion, monto, dato, tipo_gasto, fecha_actual))

            self.conn.commit()
            QMessageBox.information(self, "Éxito", "Datos guardados correctamente en ambas tablas")
            self.limpiar_tabla()
        except Exception as err:
            QMessageBox.critical(self, "Error de MySQL", str(err))

    def abrir_consulta_mensual(self):
        dialog = ConsultaChequesMensuales(self)
        dialog.exec_()


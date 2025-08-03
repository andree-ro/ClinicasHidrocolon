import sys
import pymysql
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, QMessageBox,
                             QTextEdit, QCheckBox)
from PyQt5.QtCore import Qt


class CashRegisterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro de Efectivo")
        self.setGeometry(500, 225, 600, 700)
        self.initUI()
        self.conectar_bd()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Crear tabla
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Cantidad", "Descripción", "Monto", "Total"])

        # Filas para cada denominación
        denominaciones = [
            ("Billetes de", "Q200"),
            ("Billetes de", "Q100"),
            ("Billetes de", "Q50"),
            ("Billetes de", "Q20"),
            ("Billetes de", "Q10"),
            ("Billetes de", "Q5"),
            ("Monedas", "Q1"),
            ("Monedas", "Q0.50"),
            ("Monedas", "Q0.25"),
            ("Monedas", "Q0.10"),
            ("Monedas", "Q0.05")
        ]

        self.table.setRowCount(len(denominaciones))

        # Llenar tabla con denominaciones
        for i, (desc, monto) in enumerate(denominaciones):
            # Columna Cantidad (editable)
            cantidad_item = QTableWidgetItem("0")
            self.table.setItem(i, 0, cantidad_item)

            # Columna Descripción (no editable)
            desc_item = QTableWidgetItem(desc)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 1, desc_item)

            # Columna Monto (no editable)
            monto_item = QTableWidgetItem(monto)
            monto_item.setFlags(monto_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 2, monto_item)

            # Columna Total (se calculará automáticamente)
            total_item = QTableWidgetItem("0.00")
            total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 3, total_item)

        # CONEXIÓN MEJORADA: Se ejecuta al cambiar cualquier celda
        self.table.cellChanged.connect(self.actualizar_total_automatico)
        main_layout.addWidget(self.table)

        # Label para el total general
        self.lbl_total = QLabel("Total de efectivo: Q0.00")
        self.lbl_total.setAlignment(Qt.AlignRight)
        self.lbl_total.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        main_layout.addWidget(self.lbl_total)

        # Checkbox para habilitar/deshabilitar justificación (OPCIONAL)
        self.chk_justificacion = QCheckBox("Agregar justificación (opcional)")
        self.chk_justificacion.stateChanged.connect(self.toggle_justificacion)
        main_layout.addWidget(self.chk_justificacion)

        # Área de justificación
        self.justificacion_widget = QWidget()
        justificacion_layout = QVBoxLayout(self.justificacion_widget)

        lbl_justificacion = QLabel("Justificación (opcional):")
        justificacion_layout.addWidget(lbl_justificacion)

        # Campo de texto para la justificación
        self.txt_justificacion = QTextEdit()
        self.txt_justificacion.setPlaceholderText("Ingrese una justificación si es necesario...")
        self.txt_justificacion.setMinimumHeight(100)
        justificacion_layout.addWidget(self.txt_justificacion)

        # Inicialmente oculto
        self.justificacion_widget.setVisible(False)
        main_layout.addWidget(self.justificacion_widget)

        # Botón Guardar
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.guardar_en_bd)
        btn_guardar.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 10px; font-size: 14px; font-weight: bold;")
        main_layout.addWidget(btn_guardar)

    def toggle_justificacion(self, state):
        # Mostrar u ocultar el área de justificación según el estado del checkbox
        self.justificacion_widget.setVisible(state == Qt.Checked)

    def conectar_bd(self):
        try:
            self.conn = pymysql.connect(
                host="127.0.0.1",
                user="root",  # Cambia esto a tu usuario de MySQL
                password="2332",  # Cambia esto a tu contraseña de MySQL
                database="bdhidrocolon"  # Asegúrate de crear esta base de datos primero
            )
            print("Conexión a la base de datos exitosa")

            cursor = self.conn.cursor()

            # Crear tabla si no existe
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS registro_caja
                           (
                               id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               descripcion
                               VARCHAR
                           (
                               50
                           ),
                               monto DECIMAL
                           (
                               10,
                               2
                           ),
                               cantidad INT,
                               total DECIMAL
                           (
                               10,
                               2
                           ),
                               fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                               )
                           ''')

            # Verificar si la columna justificacion existe, si no, agregarla
            try:
                cursor.execute("SELECT justificacion FROM registro_caja LIMIT 1")
                print("Columna 'justificacion' ya existe")
            except pymysql.err.OperationalError as e:
                if "Unknown column" in str(e):
                    print("Agregando columna 'justificacion' a la tabla...")
                    cursor.execute("ALTER TABLE registro_caja ADD COLUMN justificacion TEXT NULL")
                    print("Columna 'justificacion' agregada exitosamente")
                else:
                    raise e

            self.conn.commit()
            cursor.close()

        except Exception as err:
            QMessageBox.critical(self, "Error de BD", f"Error al conectar a MySQL: {err}")

    def actualizar_total_automatico(self, row, column):
        """Método mejorado que actualiza automáticamente cuando cambias una cantidad"""
        if column == 0:  # Solo si cambia la columna de cantidad
            try:
                cantidad_texto = self.table.item(row, 0).text()
                # Validar que sea un número válido
                if not cantidad_texto or cantidad_texto.strip() == "":
                    cantidad = 0
                else:
                    cantidad = int(cantidad_texto)

                monto_texto = self.table.item(row, 2).text().replace("Q", "").replace(",", ".")
                monto = float(monto_texto)

                total = cantidad * monto

                # Actualizar celda de total
                self.table.item(row, 3).setText(f"{total:.2f}")

                # IMPORTANTE: Actualizar el total general automáticamente
                self.actualizar_total_general()

            except (ValueError, AttributeError):
                self.table.item(row, 3).setText("0.00")
                self.actualizar_total_general()

    def actualizar_total_general(self):
        """Método para actualizar solo el total general sin recalcular las filas"""
        gran_total = 0

        for row in range(self.table.rowCount()):
            try:
                total_texto = self.table.item(row, 3).text()
                total = float(total_texto)
                gran_total += total
            except (ValueError, AttributeError):
                pass

        self.lbl_total.setText(f"Total de efectivo: Q{gran_total:.2f}")

    def calcular_totales(self):
        """Método para recalcular todos los totales manualmente"""
        gran_total = 0

        for row in range(self.table.rowCount()):
            try:
                cantidad = int(self.table.item(row, 0).text() or "0")
                monto_texto = self.table.item(row, 2).text().replace("Q", "").replace(",", ".")
                monto = float(monto_texto)

                total = cantidad * monto
                self.table.item(row, 3).setText(f"{total:.2f}")

                gran_total += total
            except (ValueError, AttributeError):
                self.table.item(row, 3).setText("0.00")

        self.lbl_total.setText(f"Total de efectivo: Q{gran_total:.2f}")

    def limpiar_tabla(self):
        """Método para limpiar toda la tabla"""
        reply = QMessageBox.question(self, 'Confirmar',
                                     '¿Está seguro de que desea limpiar todos los datos?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            for row in range(self.table.rowCount()):
                self.table.item(row, 0).setText("0")
                self.table.item(row, 3).setText("0.00")

            self.lbl_total.setText("Total de efectivo: Q0.00")
            self.txt_justificacion.clear()
            self.chk_justificacion.setChecked(False)

    def guardar_en_bd(self):
        try:
            # Verificar si hay datos para guardar
            total_efectivo = 0
            for row in range(self.table.rowCount()):
                cantidad = int(self.table.item(row, 0).text() or "0")
                total_efectivo += cantidad

            if total_efectivo == 0:
                QMessageBox.warning(self, "Advertencia", "No hay datos para guardar.")
                return

            # Obtener la justificación OPCIONAL
            justificacion = ""
            if self.chk_justificacion.isChecked():
                justificacion = self.txt_justificacion.toPlainText().strip()

            cursor = self.conn.cursor()

            # Verificar si la columna justificacion existe en la tabla
            tiene_justificacion = True
            try:
                cursor.execute("SHOW COLUMNS FROM registro_caja LIKE 'justificacion'")
                resultado = cursor.fetchone()
                if not resultado:
                    tiene_justificacion = False
            except:
                tiene_justificacion = False

            # Preparar la consulta según si existe la columna justificacion
            if tiene_justificacion:
                query = '''
                        INSERT INTO registro_caja
                            (descripcion, monto, cantidad, total, justificacion)
                        VALUES (%s, %s, %s, %s, %s) \
                        '''
            else:
                query = '''
                        INSERT INTO registro_caja
                            (descripcion, monto, cantidad, total)
                        VALUES (%s, %s, %s, %s) \
                        '''

            # Recopilar datos de cada fila (solo las que tienen cantidad > 0)
            registros_guardados = 0
            for row in range(self.table.rowCount()):
                cantidad = int(self.table.item(row, 0).text() or "0")

                # Solo guardar si hay cantidad
                if cantidad > 0:
                    descripcion = self.table.item(row, 1).text()
                    monto_texto = self.table.item(row, 2).text().replace("Q", "").replace(",", ".")
                    monto = float(monto_texto)
                    total_texto = self.table.item(row, 3).text()
                    total = float(total_texto)

                    # Insertar según si existe la columna justificacion
                    if tiene_justificacion:
                        datos = (descripcion, monto, cantidad, total, justificacion)
                    else:
                        datos = (descripcion, monto, cantidad, total)

                    cursor.execute(query, datos)
                    registros_guardados += 1

            self.conn.commit()
            cursor.close()

            # Mensaje de éxito
            mensaje_exito = f"Se guardaron {registros_guardados} registros correctamente en la base de datos."
            if justificacion and tiene_justificacion:
                mensaje_exito += f"\nJustificación incluida: {justificacion[:50]}..."
            elif justificacion and not tiene_justificacion:
                mensaje_exito += "\nNota: La justificación no se guardó (columna no existe en BD)."
            else:
                mensaje_exito += "\nSin justificación adicional."

            QMessageBox.information(self, "Éxito", mensaje_exito)

            # NUEVO: Cerrar la ventana automáticamente después de guardar
            print("Cerrando ventana automáticamente...")
            self.close()

        except Exception as err:
            QMessageBox.critical(self, "Error de BD", f"Error al guardar datos: {err}")
            print(f"Error completo: {err}")  # Para debug

    def closeEvent(self, event):
        """Método que se ejecuta al cerrar la ventana"""
        try:
            # Cerrar conexión a la base de datos si existe
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
                print("Conexión a la base de datos cerrada correctamente")
        except Exception as e:
            print(f"Error al cerrar conexión: {e}")

        # Aceptar el evento de cierre
        event.accept()


# Función main para ejecutar la aplicación
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CashRegisterApp()
    window.show()
    sys.exit(app.exec_())
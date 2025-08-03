from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox
import sql_structures.farmacia
import datetime


class Metodos_ventas(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        import pymysql
        try:
            self.conexion = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",
                database="bdhidrocolon"
            )
            print("✅ Conexión a BD establecida en Metodos_ventas")
        except Exception as e:
            print(f"❌ Error conectando a BD: {e}")
            self.conexion = None
        self.fecha_actual = datetime.date.today()

    def agregar_a_ventas(self, producto, cantidad, total, fecha, tipo, doctor, usuario='admin', paciente_id=None):
        try:
            cursor = self.conexion.cursor()

            # SIN INCLUIR ID - que se genere automáticamente
            query = """
                    INSERT INTO ventas (producto, cantidad, total, fecha, accion, doctor, usuario, paciente_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
                    """

            cursor.execute(query, (producto, cantidad, total, fecha, tipo, doctor, usuario, paciente_id))
            self.conexion.commit()
            cursor.close()

            print(f"✅ Venta registrada: {producto} - Q{total}")
            return True

        except Exception as e:
            print(f"❌ Error al registrar venta: {e}")
            print(
                f"🔍 Datos que se intentaron insertar: {producto}, {cantidad}, {total}, {fecha}, {tipo}, {doctor}, {usuario}, {paciente_id}")
            return False

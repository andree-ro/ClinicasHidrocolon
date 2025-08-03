from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
import sql_structures.jornadas
from .Modificar_vitacora import *
from sql_structures.manager import Manager
# import datetime
from datetime import date


class jornadas(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\CU-Jornadas.ui', self)
        self.btn_agregar_jorna.clicked.connect(self.agregarJornadas)
        self.pushButton_8.clicked.connect(self.cancelar)
        self.vita = AgregarVitacora()
        self.fecha_actual = date.today()

    def agregarJornadas(self):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        try:
            jornadas = sql_structures.Jornadas(self.le_agNombreJornada.text(),
                                                self.le_agMontoTarjeta.text(),
                                                self.le_agMontoEfectivo.text(),self.le_agMontoEfectivo_2.text())
            jornadas.management('agre_jornadas')
            self.vita.agregarvitacora("Agregar", "Usuarios", self.fecha_actual, usuario, self.le_agNombreJornada.text())
            self.le_agNombreJornada.clear()
            self.le_agMontoTarjeta.clear()
            self.le_agMontoEfectivo.clear()
            self.le_agMontoEfectivo_2.clear()

        except Exception as e:
            QMessageBox.about(self, 'Aviso', 'Error de agregado!')
        self.switch_window.emit('ingresar_jornada')

    def editarJornadas(self, id, dato, columna):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()

        try:
            jornadas = sql_structures.Jornadas("", "", "", "",columna, dato, id)
            self.vita.agregarvitacora("Actualizar", "Usuarios", self.fecha_actual, usuario, dato)
            jornadas.management('edit_jornadas')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error de agregado!')

    def eliminar_jornadas(self, id):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        try:
            jornadas = sql_structures.Jornadas('',
                                                         '',
                                                         '',
                                                         '',
                                                         '',"",
                                                         id)
            p = jornadas.jornada_elimin()
            self.vita.agregarvitacora("Eliminar", "Usuarios", self.fecha_actual, usuario, p)
            QMessageBox.about(self, 'Aviso', 'Se elimino con exito!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Eliminacion fallida!')

    def actualizarjornadas(self, id, dato, columna):
        try:
            from .ventanaFuncional import VentanaFuncional
            usuario = VentanaFuncional.enviar_usuario()
            management = Manager()
            if columna == "Nombre":
                d = management.get_dato_tables(id, "jornadas", "nombre")
                data = f"{d[0][0]} cambio a {dato}"
                self.vita.agregarvitacora("Actualizar", "Jornadas", self.fecha_actual, usuario, data)
            elif columna == "Tarjeta":
                de = management.get_dato_tables(id, "jornadas", "nombre")
                d = management.get_dato_tables(id, "jornadas", "tarjeta")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Jornadas", self.fecha_actual, usuario, data)
            elif columna == "Efectivo":
                de = management.get_dato_tables(id, "jornadas", "nombre")
                d = management.get_dato_tables(id, "jornadas", "efectivo")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "jornadas", self.fecha_actual, usuario, data)
            jornadas = sql_structures.Jornadas("", "", "", columna, dato, id)
            jornadas.management('edit_jornadas')

            QMessageBox.about(self, 'Aviso', 'Actualizado correctamente!')
        except Exception as e:
            QMessageBox.about(self, 'Aviso', 'Error al actualizar!')

    def cancelar(self):
        self.switch_window.emit('cancelar_jorda')

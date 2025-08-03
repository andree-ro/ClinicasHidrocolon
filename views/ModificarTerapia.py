from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
import sql_structures.terapias
from .Modificar_vitacora import *
import datetime
from sql_structures.manager import Manager

class AgregarTerapia(QMainWindow):

    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super(AgregarTerapia, self).__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\CU-Terapias.ui', self)
        self.btn_agregar_terapia.clicked.connect(self.agregarTerapia)
        self.pushButton_8.clicked.connect(self.cancelar)
        self.vita = AgregarVitacora()
        self.fecha_actual = datetime.date.today()

    def agregarTerapia(self):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        print(str(usuario))
        try:
            terapia = sql_structures.Terapias(self.le_agNombreTerapias.text(),
                                              self.le_agMontoTarjetaTerapias.text(),
                                              self.le_agMontoEfectivoTerapias.text(),
                                              self.le_agMontoEfectivoTerapias_2.text(),
                                              self.le_agMontoEfectivoTerapias_3.text())

            terapia.management('agre_inventarioTerapia')

            self.vita.agregarvitacora("Agregar", "Terapias", self.fecha_actual, usuario, self.le_agNombreTerapias.text())
            QMessageBox.about(self, 'Aviso', 'Agregado correctamente!')
            # self.parent.cargarTablaFarmacia()
            self.le_agNombreTerapias.clear()
            self.le_agMontoTarjetaTerapias.clear()
            self.le_agMontoEfectivoTerapias.clear()
            self.le_agMontoEfectivoTerapias_2.clear()
            self.le_agMontoEfectivoTerapias_3.clear()

        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error de agregado!')
        self.switch_window.emit('ingresar_terapia')

    def eliminar_terapias(self, id):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        print(str(usuario))
        try:
            jornadas = sql_structures.Terapias('',
                                               '',
                                               '',
                                               '',
                                               '',"","",
                                               id)
            p = jornadas.terapia_elimin()

            self.vita.agregarvitacora("Eliminar", "Terapias", self.fecha_actual, usuario, p)
            QMessageBox.about(self, 'Aviso', 'Se elimino con exito!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Eliminacion fallida!')

    def actualizarTerapia(self, id, dato, columna):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        try:
            management = Manager()
            if columna == "Nombre":
                d = management.get_dato_tables(id, "terapias", "nombre")
                data = f"{d[0][0]} cambio a {dato}"
                self.vita.agregarvitacora("Actualizar", "Terapias", self.fecha_actual, usuario, data)
            elif columna == "Tarjeta":
                de = management.get_dato_tables(id, "terapias", "nombre")
                d = management.get_dato_tables(id, "terapias", "tarjeta")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Terapias", self.fecha_actual, usuario, data)
            elif columna == "Efectivo":
                de = management.get_dato_tables(id, "terapias", "nombre")
                d = management.get_dato_tables(id, "terapias", "efectivo")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Terapias", self.fecha_actual, usuario, data)
            medicamento = sql_structures.Terapias("",
                                                  "",
                                                  "",'',"",
                                                  columna,
                                                  dato,
                                                  id)
            medicamento.management('edit_inventarioTerapia')
            QMessageBox.about(self, 'Aviso', 'Actualizado correctamente!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error al actualizar!')

    def cancelar(self):
        self.switch_window.emit('cancelar_terapia')

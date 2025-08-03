from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
import sql_structures.combos
from .Modificar_vitacora import *
import datetime
from sql_structures.manager import Manager


class AgregarCombos(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\CU-Combos.ui', self)
        self.btn_agregar_combo.clicked.connect(self.agregarpromociones)
        self.pushButton_8.clicked.connect(self.cancelar)
        self.vita = AgregarVitacora()
        self.fecha_actual = datetime.date.today()

    def agregarpromociones(self):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        print(str(usuario))
        try:
            medicamento = sql_structures.Combos(self.le_agCombo.text(),
                                                            self.le_agtarejeta_c.text(),
                                                            self.le_agefectivo_combo.text(),
                                                self.le_agefectivo_combo_3.text())
            medicamento.management('agre_promociones')

            self.vita.agregarvitacora("Agregar", "Combos", self.fecha_actual, usuario, self.le_agCombo.text())
            self.le_agCombo.clear()
            self.le_agtarejeta_c.clear()
            self.le_agefectivo_combo.clear()
            self.le_agefectivo_combo_3.clear()
            QMessageBox.about(self, 'Aviso', 'Agregado correctamente!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error de agregado!')
        self.switch_window.emit('ingresar_combo')

    def actualizarpromociones(self, id, dato, columna):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        print(str(usuario))
        try:
            management = Manager()
            if columna == "nombre":
                d = management.get_dato_tables(id, "promociones", "nombre")
                data = f"{d[0][0]} cambio a {dato}"
                self.vita.agregarvitacora("Actualizar", "Combos", self.fecha_actual, usuario, data)
            elif columna == "Tarjeta":
                de = management.get_dato_tables(id, "promociones", "nombre")
                d = management.get_dato_tables(id, "promociones", "tarjeta")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Combos", self.fecha_actual, usuario, data)
            elif columna == "Efectivo":
                de = management.get_dato_tables(id, "promociones", "nombre")
                d = management.get_dato_tables(id, "promociones", "efectivo")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Combos", self.fecha_actual, usuario, data)
            medicamento = sql_structures.Combos("",
                                                       "",
                                                       "",'',
                                                        columna, dato, id)
            medicamento.management('edit_promociones')
            QMessageBox.about(self, 'Aviso', 'Actualizado correctamente!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error al actualizar!')

    def eliminarpromociones(self, id):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        print(str(usuario))
        try:
            doctor = sql_structures.Combos('',
                                           '',
                                           '',
                                           '',
                                           '','',
                                           id)
            p = doctor.promociones_elimin()
            self.vita.agregarvitacora("Eliminar", "Combos", self.fecha_actual, usuario, p)
            QMessageBox.about(self, 'Aviso', 'Se elimino con exito!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Eliminacion fallida!')
        self.switch_window.emit('eliminar_medi')

    def cancelar(self):
        self.switch_window.emit('cancelar_combo')

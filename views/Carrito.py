from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox
import sql_structures.farmacia
import datetime
from .Modificar_vitacora import *


class Metodos_carrito(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.fecha_actual = datetime.date.today()
        self.vita = AgregarVitacora()

    def agregar_a_carrito(self, nombre, existencia, tarjeta, efectivo, medicamentos_id, terapias_id,
                          promociones_id, jordas_id, ultrasonidos_id, consumibles_id):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        try:
            medicamento = sql_structures.Carrito(nombre, existencia, tarjeta, efectivo, medicamentos_id, terapias_id,
                                                 promociones_id, jordas_id, ultrasonidos_id, consumibles_id)
            medicamento.management('agre_carrito')
            self.vita.agregarvitacora("Agrego", "Cierre", self.fecha_actual, usuario,
                                      f"Un producto a carrito {nombre}, {existencia}")
            #QMessageBox.about(self, 'Aviso', 'Agregado correctamente!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error de agregado!')

    def actualizar_a_carrito(self, id, dato, columna):

        try:
            medicamento = sql_structures.Carrito("",
                                                 "",
                                                 "",
                                                 "",
                                                 columna, dato, id)
            medicamento.management('edit_inventarioFarmacia')

            QMessageBox.about(self, 'Aviso', 'Actualizado correctamente!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error al actualizar!!!!')

    def actualizar_a_carrito_nuevo(self, id, tarjeta,  efectivo, existencias):
        print('si entra')
        try:
            medicamento = sql_structures.Carrito("",
                                                 existencias,
                                                 tarjeta,
                                                 efectivo,
                                                 "", "",
                                                 "", "",
                                                 "", "",
                                                 "", "",
                                                 id)
            medicamento.management('edit_carrito')

            #QMessageBox.about(self, 'Aviso', 'Actualizado correctamente!')
        except Exception as e:
            print(e)
            #QMessageBox.about(self, 'Aviso', 'Error al actualizar!')

    def eliminar_a_carritoo(self, id):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()

        try:
            doctor = sql_structures.Carrito('',
                                            '',
                                            '',
                                            '',
                                            '', '', '', '', '',
                                            '', '', '',
                                            id)
            doctor.management('elimin_carrito')
            self.vita.agregarvitacora("Eliminar", "Cierre", self.fecha_actual, usuario,
                                      "Un producto a carrito")
            #QMessageBox.about(self, 'Aviso', 'Se elimino con exito!')
        except Exception as e:
            print(e)
            #QMessageBox.about(self, 'Aviso', 'Eliminacion fallida!')

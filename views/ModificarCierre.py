from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
import sql_structures.cierre
from .Modificar_vitacora import *
import datetime
from .datos_cliente import *
from datetime import date

class AgregarCierre(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super(AgregarCierre, self).__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\CU-Usuarios.ui', self)
        self.vita = AgregarVitacora()
        self.fecha_actual = date.today()

    def agregarcierre(self, nombre, cantidad, tarjeta, efectivo, monto, fecha, usuario, carrito_id):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        numero = DatosCliente.get_numero()
        try:
            medicamento = sql_structures.Cierre(nombre, cantidad, tarjeta, efectivo, monto, fecha, usuario, carrito_id)
            medicamento.management('agre_cierre')
            dato = f"Se realizo una venta con numero {numero}"
            #self.vita.agregarvitacora("Agregar", "Cierre", self.fecha_actual, usuario,
            #                          dato)
            # QMessageBox.about(self, 'Aviso', 'Agregado correctamente!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error de agregado!')
        # self.switch_window.emit('ingresar_combo')

    def eliminar_cierre(self, id):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        from .codigoAnulacion import CodigoAnulacion
        self.codigoAnulacion = CodigoAnulacion()
        numerro = self.codigoAnulacion.get_numerro()
        try:
            jornadas = sql_structures.Cierre('',
                                                '',
                                                '',
                                                '',
                                                '',
                                                '', '', '',
                                             '',
                                             '',
                                                id)
            jornadas.management('elimi_cierre')
            #dato = f"Se retiro una venta con numero {numerro} "
           # self.vita.agregarvitacora("Eliminar", "Cierre", self.fecha_actual, usuario,
            #                          dato)
            QMessageBox.about(self, 'Aviso', 'Se elimino con exito!')

            self.codigoAnulacion.show()
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Eliminacion fallida!')


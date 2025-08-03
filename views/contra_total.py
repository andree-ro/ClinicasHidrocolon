from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from .ModificarCierre import *
from .ventanaFuncional import VentanaFuncional
from sql_structures.manager import Manager  # Si Manager está directamente en manager.py
from encrypt import *
from .ModificarMedicamentos import *
from .modificar_ventas import *

class Contra_total(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)
    _porcentaje = ""  # Variable de clase

    def __init__(self):
        super(Contra_total, self).__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\contraseña_total.ui', self)
        self.por = 0
        self.pushButton_7.clicked.connect(self.recibir)
        self.cierre = AgregarCierre()
        self.mana = Manager()
        self.medicamento = AgregarMedi()
        self.funcional = VentanaFuncional()
        self.venta = Metodos_ventas()

    def recibir(self):
        try:
            encrip = Metodo()
            refue = Metodos_refuerzo()
            key = "abcdefghijkl12345678!@#$"
            key1 = "~Marp~__842631597"
            a = ""
            offset = 8
            encrypted = ""
            valor = self.lineEdit.text()
            c = encrip.encrypt(offset, valor, key)
            usuario = self.mana.get_usuario(c)
            if usuario[0][0] == "Administrador":
                try:

                    ide = VentanaFuncional.get_contra()
                    articulos_venta = self.mana.get_id_carrito(ide)
                    # Procesar cada artículo en la venta
                    for articulo in articulos_venta:
                        id_e = self.mana.get_id_carrito_id(articulo[0], ide)
                        cantidad = self.mana.get_cantidad(id_e)
                        id_medi = self.mana.get_idddd(articulo[1])

                        if id_medi:
                            # item = manager.get_carrito_medic("medicamentos", "id", id_medi[0][0], "nombre", nombre)
                            item = self.mana.get_carrito("medicamentos", "id", id_medi[0][0])
                            if item:
                                existencias = item[0][1]  # item[0][1] es existencias
                                nuevas_existencias = existencias + cantidad[0][0]
                                self.medicamento.actualizarMedicamentor(id_medi[0][0], nuevas_existencias, "existencias")
                                self.cierre.eliminar_cierre(id_e)
                            else:
                                pass
                        import  datetime

                        tiempo = datetime.date.today()
                        datos = self.mana.get_id_carrito_id_uni_ve(ide)
                        print(datos)
                        for dato in datos:
                            print(dato[1], dato[2], dato[4], tiempo, "Anulacion")
                            self.venta.agregar_a_ventas(dato[1], dato[2], dato[4], tiempo, "Anulacion")
                            print(0)
                        else:
                            print(1)
                            self.cierre.eliminar_cierre(id_e)

                except Exception as e:
                    print(e)
                    return False, f"Error al anular la venta: {str(e)}"

            else:
                QMessageBox.about(self, 'Aviso', 'Contraseña invalida!')
            self.switch_window.emit('abr_contra')
            self.lineEdit.clear()
        except Exception as e:
            print(e)


    @classmethod
    def get_porcentaje(cls):
        return cls._porcentaje

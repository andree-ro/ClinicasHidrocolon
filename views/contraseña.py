from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from .ModificarCierre import *
from .ventanaFuncional import VentanaFuncional
from sql_structures.manager import Manager  # Si Manager está directamente en manager.py
from encrypt import *
from .ModificarMedicamentos import *

class Contrasena(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)
    _porcentaje = ""  # Variable de clase

    def __init__(self):
        super(Contrasena, self).__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\contraseña.ui', self)
        self.por = 0
        self.pushButton_7.clicked.connect(self.recibir)
        self.cierre = AgregarCierre()
        self.mana = Manager()
        self.medicamento = AgregarMedi()

    def recibir(self):
        try:
            encrip = Metodo()
            refue = Metodos_refuerzo()
            key = "abcdefghijkl12345678!@#$"
            # key = 'protodrjympg15599357!@#$'
            key1 = "~Marp~__842631597"
            a = ""
            offset = 8
            encrypted = ""
            valor = self.lineEdit.text()
            c = encrip.encrypt(offset, valor, key)
            usuario = self.mana.get_usuario(c)
            ide = VentanaFuncional.get_contra()
            if usuario[0][0] == "Administrador":
                articulos= self.mana.get_id_carrito(ide)
                id_e = self.mana.get_id_carrito_id_uni(articulos[0][0])
                cantidad = self.mana.get_cantidad(id_e)
                nombre = self.mana.get_name(id_e)
                id_medi = self.mana.get_idddd(nombre[0][0])
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
                else:
                    self.cierre.eliminar_cierre(id_e)

            else:
                QMessageBox.about(self, 'Aviso', 'Contraseña invalida!')
            self.switch_window.emit('abr_contra')
            self.lineEdit.clear()

        except Exception as e:
            print(e)


    @classmethod
    def get_porcentaje(cls):
        return cls._porcentaje

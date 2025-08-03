from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtCore import Qt, QTimer
from .ventanaFuncional import VentanaFuncional
from sql_structures.manager import Manager  # Si Manager está directamente en manager.py
from encrypt import *
from .descuentosMedi import *

class Contra(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super(Contra, self).__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\contraseña.ui', self)
        self.por = 0
        self.pushButton_7.clicked.connect(self.recibir)
        self.mana = Manager()

    def recibir(self):
        print(1)
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
            print(valor)
            # usuario = sql_structures.Manager()
            # contrasena = usuario.iniciar_contra(valor)
            c = encrip.encrypt(offset, valor, key)
            print(c)
            usuario = self.mana.get_usuario(c)
            print(usuario[0][0])
            ide = VentanaFuncional.get_contra()
            print(ide)
            if usuario[0][0] == "Administrador":
                from .descuentosMedi import DescuentoMedi
                self.DescuentoMedi = DescuentoMedi()
                self.DescuentoMedi.show()
                self.switch_window.emit('cancelar_contra_des')
            else:
                print("contraseña invalida")
            self.switch_window.emit('abr_contra')
            self.lineEdit.clear()
        except Exception as e:
            print(e)

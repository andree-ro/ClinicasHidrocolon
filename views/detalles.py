from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from sql_structures.manager import Manager
from .ventanaFuncional import VentanaFuncional


class Detalles(QMainWindow):
    _porcentaje = ""
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super(Detalles, self).__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\detalles.ui', self)
        self.por = 0
        # self.btn_ingresar.clicked.connect(self.show_page_descuentos)
        #self.pushButton_8.clicked.connect(self.recibir)
        self.mana = Manager()
        self.ventana = VentanaFuncional()
        self.recibir()

    def recibir(self):
        try:
            id = VentanaFuncional.enviar_detalle()
            datos = self.mana.get_detalle(id)
            self.label.setText(datos[0][0])
            self.label_3.setText(datos[0][1])
            self.label_4.setText(datos[0][2])

            dato = datos[0][3]
            pixmap = QPixmap(dato)
            pixmap = pixmap.scaled(250, 250, aspectRatioMode=1)  # Mantiene proporción
            self.label_2.setPixmap(pixmap)
        except Exception as e:
            print(e)

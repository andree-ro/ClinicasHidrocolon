from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem


class Lab(QMainWindow):
    _porcentaje = ""
    _porcentaje2 = ""
    _porcentaje_com = ""
    _porcentaje_eliminar = ""
    # Variable de clase
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super(Lab, self).__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\lab.ui', self)
        self.por = 0
        # self.btn_ingresar.clicked.connect(self.show_page_descuentos)
        self.pushButton_7.clicked.connect(self.recibir)
        self.pushButton_9.clicked.connect(self.recibir_editar)
        self.pushButton_8.clicked.connect(self.recibir_eliminar)
        self.cargar_elementos()

    def cargar_elementos(self):
        """Carga los elementos desde los archivos a los combobox"""
        try:
            # Cargar elementos de laboratorio
            with open('elementos_lab.txt', 'r') as archivo:
                elementos = archivo.read().split(',')
                elementos = list(set([e.strip() for e in elementos if e.strip()]))  # Eliminar duplicados
                self.comboBox.clear()
                self.cbox_agPresentacion_2.clear()
                self.comboBox.addItems(elementos)
                self.cbox_agPresentacion_2.addItems(elementos)
        except:
            pass

    def recibir(self):
        valor = self.le_agNombreMedicamento.text()
        Lab._porcentaje = valor
        self.por = Lab._porcentaje
        print(f"{Lab._porcentaje}")
        self.switch_window.emit('ingresar_lab')
        print(f"{Lab._porcentaje}")
        self.le_agNombreMedicamento.clear()

    def recibir_eliminar(self):
        valor = self.comboBox.currentText()
        Lab._porcentaje_eliminar = valor
        self.switch_window.emit('eliminar_lab')
        print(f"{Lab._porcentaje_eliminar}")
        self.cargar_elementos()

    def recibir_editar(self):
        valor2 = self.cbox_agPresentacion_2.currentText()
        valor = self.lineEdit.text()
        Lab._porcentaje2 = valor
        Lab._porcentaje_com = valor2
        self.por = Lab._porcentaje
        print(f"{Lab._porcentaje_eliminar}")
        self.switch_window.emit('editar_lab')
        print(f"{Lab._porcentaje_eliminar}")
        self.lineEdit.clear()
        self.cargar_elementos()

    @classmethod
    def get_porcentaje(cls):
        return cls._porcentaje

    @classmethod
    def get_porcentaje_2(cls):
        return cls._porcentaje2

    @classmethod
    def get_porcentaje_com(cls):
        return cls._porcentaje_com

    @classmethod
    def get_porcentaje_eli(cls):
        return cls._porcentaje_eliminar

from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
import sql_structures.vitacora

class AgregarVitacora(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super(AgregarVitacora, self).__init__()
        #loadUi('views/CU-Terapias.ui', self)

    def agregarvitacora(self, accion, modulo, modificado, fecha, usuario):
        try:
            terapia = sql_structures.Vitacora(accion, modulo, modificado, fecha, usuario)
            terapia.management('agre_vitacora')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error de agregado!')


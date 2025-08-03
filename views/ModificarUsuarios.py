from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
import sql_structures.usuario
from .Modificar_vitacora import *
import datetime
from sql_structures.manager import Manager

class AgregarUsuarios(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super(AgregarUsuarios, self).__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\CU-Usuarios.ui', self)
        self.btn_agregar_usuario.clicked.connect(self.new_user)
        self.btn_cancelar_usuarios.clicked.connect(self.cancelar)
        self.vita = AgregarVitacora()
        self.fecha_actual = datetime.date.today()

    def new_user(self):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        print(str(usuario))
        try:
            usuarios = sql_structures.Usuarios(self.le_agNombreUsuario.text(),
                                               self.le_agUsuario.text(),
                                               self.comboBox.currentText())
            usuarios.new_use()

            self.vita.agregarvitacora("Agregar", "Usuarios",  self.fecha_actual, usuario, self.le_agNombreUsuario.text())
            self.le_agNombreUsuario.clear()
            self.le_agUsuario.clear()
            QMessageBox.about(self, 'Aviso', 'Agregado correctamente!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error de agregado!')

    def update_user(self, id, dato, columna):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        print(str(usuario))
        try:
            management = Manager()
            if columna == "Usuario":
                d = management.get_dato_tables(id, "usuario", "usuario")
                data = f"{d[0][0]} cambio a {dato}"
                self.vita.agregarvitacora("Actualizar", "Usuarios", self.fecha_actual, usuario, data)
            elif columna == "Contraseña":
                de = management.get_dato_tables(id, "usuario", "usuario")
                d = management.get_dato_tables(id, "usuario", "contraseña")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Usuarios", self.fecha_actual, usuario, data)
            elif columna == "Rol":
                de = management.get_dato_tables(id, "usuario", "usuario")
                d = management.get_dato_tables(id, "usuario", "rol")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Usuarios", self.fecha_actual, usuario, data)
            usuarios = sql_structures.Usuarios("", "", "",
                                                           columna, dato, id)
            usuarios.update_user()
            QMessageBox.about(self, 'Aviso', 'Modificado correctamente!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error al modificar!')

    def delete_user(self, id):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        print(str(usuario))
        try:
            usuarios = sql_structures.Usuarios('', '', '', '', '', id)
            p = usuarios.delete_user()
            self.vita.agregarvitacora("Eliminar", "Usuarios",  self.fecha_actual, usuario, p)
            QMessageBox.about(self, 'Aviso', 'Eliminado correctamente!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error al eliminar!')

    def cancelar(self):
        self.switch_window.emit('cancelar_usuario')


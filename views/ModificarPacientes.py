from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
import sql_structures.pacientes
from .Modificar_vitacora import *
import datetime
from sql_structures.manager import Manager

class AgregarPacientes(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(AgregarPacientes, self).__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\CU-Pacientes.ui', self)
        self.btn_agregar_pacientes.clicked.connect(self.agregarPaciente)
        self.pushButton_8.clicked.connect(self.cancelar)
        self.vita = AgregarVitacora()
        #self.fecha_actual = datetime.date.today()
        self.fecha_actual = datetime.datetime.now()

    def agregarPaciente(self):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        print(str(usuario))
        try:
            paciente = sql_structures.Pacientes(self.le_agNombrePaciente.text(),
                                                self.le_agApellido.text(),
                                                self.le_agDpi.text(),
                                                self.le_agTelefono.text(),
                                                self.dateEdit_3.date().toString("yyyy-MM-dd"),
                                                self.dateEdit_2.date().toString("yyyy-MM-dd"),
                                                self.dateEdit.date().toString("yyyy-MM-dd"), "")

            paciente.management('agre_paciente')

            self.vita.agregarvitacora("Agregar", "Pacientes", self.fecha_actual, usuario, self.le_agNombrePaciente.text())
            self.le_agNombrePaciente.clear(),
            self.le_agApellido.clear(),
            self.le_agTelefono.clear(),
            self.le_agDpi.clear()
            QMessageBox.about(self, 'Aviso', 'Agregado correctamente!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error de agregado!')
        self.switch_window.emit('ingresar_paciente')

    def eliminar_paciente(self, id):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        print(str(usuario))
        try:

            jornadas = sql_structures.Pacientes('',
                                                '',
                                                '',
                                                '',
                                                '',
                                                '', '', '',"", "",
                                                id)
            P = jornadas.paciente_elimin()
            self.vita.agregarvitacora("Eliminar", "Pacientes", self.fecha_actual, usuario, P)
            QMessageBox.about(self, 'Aviso', 'Se elimino con exito!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Eliminacion fallida!')

    def actualizarPaciente(self, id, dato, columna):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        #print(str(usuario))
        #print(columna)
        try:
            management = Manager()
            print(columna)
            if columna == "Nombre ":
                print(columna)
                d = management.get_dato_tables(id, "paciente", "nombre")
                print(columna)
                data = f"{d[0][0]} cambio a {dato}"
                print(data)
                self.vita.agregarvitacora("Actualizar", "Pacientes", self.fecha_actual, usuario, data)
            elif columna == "Apellido":
                de = management.get_dato_tables(id, "paciente", "nombre")
                d = management.get_dato_tables(id, "paciente", "apellido")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Pacientes", self.fecha_actual, usuario, data)
            elif columna == "telefono":
                de = management.get_dato_tables(id, "paciente", "nombre")
                d = management.get_dato_tables(id, "paciente", "telefono")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                print(data)
                self.vita.agregarvitacora("Actualizar", "Pacientes", self.fecha_actual, usuario, data)
            elif columna == "dpi":
                de = management.get_dato_tables(id, "paciente", "nombre")
                d = management.get_dato_tables(id, "paciente", "dpi")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Pacientes", self.fecha_actual, usuario, data)
            elif columna == "fecha":
                de = management.get_dato_tables(id, "paciente", "nombre")
                d = management.get_dato_tables(id, "paciente", "fecha")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Pacientes", self.fecha_actual, usuario, data)
            elif columna == "cita":
                de = management.get_dato_tables(id, "paciente", "nombre")
                d = management.get_dato_tables(id, "paciente", "cita")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Pacientes", self.fecha_actual, usuario, data)
            elif columna == "cumpleaños":
                de = management.get_dato_tables(id, "paciente", "nombre")
                d = management.get_dato_tables(id, "paciente", "cumpleaños")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Pacientes", self.fecha_actual, usuario, data)
            medicamento = sql_structures.Pacientes("",
                                                   "",
                                                   "",
                                                   "", '', '', '', '',
                                                   columna,
                                                   dato,
                                                   id)
            medicamento.management('edit_paciente')
            QMessageBox.about(self, 'Aviso', 'Actualizado correctamente!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error al actualizar!')

    def cancelar(self):
        self.switch_window.emit('cancelar_paciente')

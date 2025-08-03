import random
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import *

import sql_structures
from encrypt import *
from sql_structures import *
from .ventanaFuncional import VentanaFuncional


class VentanaPrincipal(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)
    datos_enviados = QtCore.pyqtSignal(int, str)
    dato = QtCore.pyqtSignal(str)

    def __init__(self):
        try:
            super(VentanaPrincipal, self).__init__()
            loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\InicioSesion.ui', self)
            self.ventana = VentanaFuncional()

            self.btn_ingreso_sis.clicked.connect(self.iniciar_sesion)
            #self.btn_ingreso_sis.clicked.connect(self.ingreso_sis)
            # self.btn_ingreso_sis.clicked.connect(self.ingreso_sis)

            self.frases = {
                1: "La educación es el arma más poderosa que puedes usar para cambiar el mundo. - Nelson Mandela",
                2: "La vida es lo que pasa mientras estás ocupado haciendo otros planes. - John Lennon",
                3: "El único modo de hacer un gran trabajo es amar lo que haces. - Steve Jobs",
                4: "El éxito no es la clave de la felicidad. La felicidad es la clave del éxito. - Albert Schweitzer",
                5: "La vida es 10% lo que te sucede y 90% cómo reaccionas a ello. - Charles R. Swindoll"
            }
            frase = random.choice(list(self.frases.values()))
            self.label_frases.setText(frase)

            blur_effect = QGraphicsBlurEffect()
            blur_effect.setBlurRadius(10)
            self.label_imagen.setGraphicsEffect(blur_effect)
        except Exception as e:
            print(e)

    def ingreso_sis(self):
        self.switch_window.emit('ventana')

    def iniciar_sesion(self):
        try:
            encrip = Metodo()
            refue = Metodos_refuerzo()
            key = "abcdefghijkl12345678!@#$"
            # key = 'protodrjympg15599357!@#$'
            key1 = "~Marp~__842631597"
            a = ""
            offset = 8
            encrypted = ""
            try:
                self.usuario_comprobacion = self.Ini_usu.text()
                usuario = sql_structures.Manager()
                rol = usuario.iniciar_ses(self.usuario_comprobacion)
                contrasena_comprobacion = self.Ini_contra.text()
                contrasena = usuario.iniciar_contra(self.usuario_comprobacion)
                c = encrip.decrypt(offset, contrasena, key)
                if contrasena_comprobacion == c:
                    t = True
                    if rol == 1:
                        print('hola')
                        self.ingreso_sis()
                        print('hola')
                        self.datos_enviados.emit(rol, self.usuario_comprobacion)
                        print('hola')
                        self.Ini_usu.clear()
                        self.Ini_contra.clear()
                    elif rol == 2:
                        self.ingreso_sis()
                        self.datos_enviados.emit(rol, self.usuario_comprobacion)
                        self.Ini_usu.clear()
                        self.Ini_contra.clear()
                    elif rol == 3:
                        self.ingreso_sis()
                        self.datos_enviados.emit(rol, self.usuario_comprobacion)
                        self.Ini_usu.clear()
                        self.Ini_contra.clear()

                    else:
                        QMessageBox.about(self, 'Aviso', 'Usuario incorrecto!')
                else:
                    QMessageBox.about(self, 'Aviso', 'Contraseña incorrecta!')
            except Exception as e:
                print(e)
                QMessageBox.about(self, 'Aviso', 'Cedenciales incorrectas!')

        except Exception as e:
            print(e)
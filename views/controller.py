from .ventanaFuncional import *
from .main_view import *
from .ModificarMedicamentos import *
from .Jornadas import *
from .ModificarTerapia import *
from .ModificarPacientes import *
from .ModificarCombos import *
from .ModificarUsuarios import *
from .ModificarCierre import *
from .ModificarExistencia import *
from .contraseña import *
from .lab import *
from .presentacion import *
from .contra_desc import *
from .contra_total import *
from .efectivo import CashRegisterApp  # Ajusta según el nombre y ubicación real
from PyQt5.QtWidgets import QMessageBox

class Controller:
    def __init__(self):
        self.main = VentanaPrincipal()
        self.ventana = VentanaFuncional()
        self.AgregarMedi = AgregarMedi()
        self.AgregarJorda = jornadas()
        self.AgregarTerapia = AgregarTerapia()
        self.AgregarPaciente = AgregarPacientes()
        self.AgregarCombo = AgregarCombos()
        self.AgregarUsuarios = AgregarUsuarios()
        self.AgregarCierre = AgregarCierre()
        self.Existencia = Existencias()
        self.contra = Contrasena()
        self.Laboratorio = Lab()
        self.Presentacion =     Presen()
        self.Des_contr = Contra()
        self.contra_total = Contra_total()
        self.dato = []

        self.caja_chica = None  # Nueva ventana


    def ya_se_ingreso_caja_chica_hoy(self):
        try:

            conn = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",
                database="bdhidrocolon"
            )

            print(2)
            cursor = conn.cursor()
            cursor.execute("""
                   SELECT COUNT(*) FROM registro_caja
                   WHERE DATE(fecha) = CURDATE()
               """)
            print(2)
            resultado = cursor.fetchone()
            print(2)
            cursor.close()
            print(2)
            conn.close()

            return resultado[0] > 0

        except Exception as err:
            QMessageBox.critical(None, "Error de BD", f"No se pudo verificar caja chica:\n{err}")
            return True  # Para no seguir abriendo la ventana por error

    def show_main(self):
        self.main.switch_window.connect(self.handle_main_navigation)
        self.main.show()

    def show_ventana(self):
        self.ventana.switch_window.connect(self.handle_ventana_navigation)
        self.ventana.show()
        self.main.datos_enviados.connect(self.ventana.bloqueo)
        #self.main.datos_enviados.connect(self.ventana.enviar_usuario)
        # self.Existencia.dato.connect(self.ventana.agregar_medicamento_a_carrito)

    def show_medicamento(self):
        self.AgregarMedi.switch_window.connect(self.handle_Agre_Medi_navigation)
        self.AgregarMedi.show()

    def show_terapia(self):
        self.AgregarTerapia.switch_window.connect(self.handle_Agre_terapia_navigation)
        self.AgregarTerapia.show()

    def show_jornada(self):
        self.AgregarJorda.switch_window.connect(self.handle_Agre_jornada_navigation)
        self.AgregarJorda.show()

    def show_paciente(self):
        self.AgregarPaciente.switch_window.connect(self.handle_Agre_paciente_navigation)
        self.AgregarPaciente.show()

    def show_combo(self):
        self.AgregarCombo.switch_window.connect(self.handle_Agre_combo_navigation)
        self.AgregarCombo.show()

    def show_usuarios(self):
        self.AgregarUsuarios.switch_window.connect(self.handle_Agre_usuario_navigation)
        self.AgregarUsuarios.show()

    def show_cierre(self):
        self.AgregarCierre.switch_window.connect(self.handle_Agre_cierre_navigation)
        self.AgregarCierre.show()

    def show_contra(self):
        self.contra.switch_window.connect(self.handle_cierre_navigation)
        self.contra.show()

    def show_cita(self):
        self.contra.switch_window.connect(self.handle_cierre_navigation)
        self.contra.show()

    def show_cumple(self):
        self.contra.switch_window.connect(self.handle_cierre_navigation)
        self.contra.show()

    def show_lab(self):
        self.Laboratorio.switch_window.connect(self.handle_Agre_lab_navigation)
        self.Laboratorio.show()

    def show_pre(self):
        self.Presentacion.switch_window.connect(self.handle_Agre_pre_navigation)
        self.Presentacion.show()

    def show_contra_d(self):
        self.Des_contr.switch_window.connect(self.handle_Des_contr_navigation)
        self.Des_contr.show()

    def show_contra_total(self):
        self.contra_total.switch_window.connect(self.handle_contra_total_navigation)
        self.contra_total.show()

    def handle_main_navigation(self, view):
        try:
            print(1)
            if view == 'ventana':
                print(1)
                #self.show_ventana()
                if not self.ya_se_ingreso_caja_chica_hoy():
                    print(1)
                    self.show_ventana()
                    self.main.close()
                    self.caja_chica = CashRegisterApp()
                    self.caja_chica.show()
                    self.caja_chica.closeEvent = self.continuar_despues_caja
                else:
                    self.show_ventana()
                    self.main.close()
        except Exception as e:
            print(e)

    def continuar_despues_caja(self, event):
        self.caja_chica.close()
        self.show_ventana()
        self.main.close()

    def handle_ventana_navigation(self, view):
        if view == 'medicina':
            self.show_medicamento()
        elif view == "terapia":
            self.show_terapia()
        elif view == "jornada":
            self.show_jornada()
        elif view == "paciente":
            self.show_paciente()
        elif view == "combo":
            self.show_combo()
        elif view == "usuarios":
            self.show_usuarios()
        elif view == "cierre":
            self.show_cierre()
        elif view == "contra":
            self.show_contra()
        elif view == "contra_total":
            self.show_contra_total()
        elif view == "descu_contra":
            self.show_contra_d()
        elif view == "sesion":
            self.main.show()
            self.ventana.close()

    def handle_Agre_Medi_navigation(self, view):
        if view == 'ingresar_medi':
            self.AgregarMedi.close()
            self.ventana.cargarTablaFarmacia()
        elif view == 'cancelar_medi':
            self.AgregarMedi.close()
        elif view == 'show_lab':
            self.show_lab()
        elif view == 'show_pre':
            self.show_pre()

    def handle_cierre_navigation(self, view):
        if view == 'abr_contra':
            self.contra.close()

    def handle_Agre_terapia_navigation(self, view):
        if view == 'ingresar_terapia':
            self.AgregarTerapia.close()
            self.ventana.cargarTablaTerapias()
        elif view == 'cancelar_terapia':
            self.AgregarTerapia.close()

    def handle_Agre_jornada_navigation(self, view):
        if view == 'ingresar_jornada':
            self.AgregarJorda.close()
            self.ventana.cargarTablaJornadas()
        elif view == 'cancelar_jorda':
            self.AgregarJorda.close()

    def handle_Agre_combo_navigation(self, view):
        if view == 'ingresar_combo':
            self.AgregarCombo.close()
            self.ventana.cargarTablaCombo()
        elif view == 'cancelar_combo':
            self.AgregarCombo.close()

    def handle_Agre_paciente_navigation(self, view):
        if view == 'ingresar_paciente':
            self.AgregarPaciente.close()
            self.ventana.cargarTablaPacientes()
        elif view == 'cancelar_paciente':
            self.AgregarPaciente.close()

    def handle_Agre_usuario_navigation(self, view):
        if view == 'ingresar_usuario':
            self.AgregarUsuarios.close()
            self.ventana.cargarTablaUsuario()
        elif view == 'cancelar_usuario':
            self.AgregarUsuarios.close()

    def handle_Agre_cierre_navigation(self, view):
        if view == 'ingresar_cierre':
            self.AgregarCierre.close()
            self.ventana.cargarTablaCierre()
        elif view == 'cancelar_medi':
            self.AgregarCierre.close()

    def handle_Agre_lab_navigation(self, view):
        if view == 'ingresar_lab':
            self.Laboratorio.close()
            self.AgregarMedi.nue_lab()
        if view == 'eliminar_lab':
            self.Laboratorio.close()
            self.AgregarMedi.eliminar_lab()
        if view == 'editar_lab':
            self.Laboratorio.close()
            self.AgregarMedi.modificar_lab()
        elif view == 'cancelar_lab':
            self.Laboratorio.close()

    def handle_Agre_pre_navigation(self, view):
        if view == 'ingresar_pre':
            self.Presentacion.close()
            self.AgregarMedi.nue_pre()
        if view == 'eliminar_pre':
            self.Laboratorio.close()
            self.AgregarMedi.eliminar_pre()
        if view == 'editar_pre':
            self.Laboratorio.close()
            self.AgregarMedi.modificar_pre()
        elif view == 'cancelar_lab':
            self.Presentacion.close()

    def handle_Des_contr_navigation(self, view):
        if view == 'ingresar_contra':
            self.Des_contr.close()
            self.AgregarMedi.nue_pre()
        elif view == 'cancelar_contra_des':
            self.Des_contr.close()

    def handle_contra_total_navigation(self, view):
        if view == 'ingresar_contra_total':
            self.Des_contr.close()
            self.AgregarMedi.nue_pre()
        elif view == 'cancelar_contra_total':
            self.Des_contr.close()



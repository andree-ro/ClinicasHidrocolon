from PyQt5.QtCore import QSettings
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QFileDialog, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog
import sql_structures.farmacia
from .Modificar_vitacora import *
from sql_structures.manager import Manager
import datetime
from .lab import *
from .presentacion import *
from .VentanaExtras import VentanaExtras
from sql_structures import InventarioFarmacia
import sql_structures


class AgregarMedi(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\CU-Medicamentos.ui', self)
        self.instalar_enter_autoavance()

        # Variable para saber si estamos editando
        self.modo_edicion = False
        self.id_medicamento_editar = None
        self.lineEdit.setPlaceholderText("%")

        # Cambiar el texto del botón según el modo
        self.btn_agregar_medi.clicked.connect(self.guardar_medicamento)

        self.pushButton_8.clicked.connect(self.cancelar)
        self.lab = Lab()
        self.Pre = Presen()
        self.vita = AgregarVitacora()
        self.fecha_actual = datetime.date.today()
        self.btn_agregar_medi_3.clicked.connect(self.IniciarDes)
        self.btn_agregar_medi_2.clicked.connect(self.Iniciar)
        self.pushButton_9.clicked.connect(self.cargar_imagen)
        self.imagen = ""
        self.conectar_eventos_extras()
        self.cargar_elementos()

    def conectar_eventos_extras(self):
        """Conecta el checkbox de extras"""
        self.extras_medicamento = []

        # Conectar el checkbox (asumiendo que se llama checkBox en tu .ui)
        # Si tiene otro nombre, cámbialo aquí
        if hasattr(self, 'checkBox'):  # Si existe el checkbox en tu UI
            self.checkBox.stateChanged.connect(self.on_extras_changed)
        else:
            print("Advertencia: No se encontró el checkbox 'checkBox' en la UI")

    def on_extras_changed(self, state):
        """Se ejecuta cuando cambia el estado del checkbox extras"""
        if state == QtCore.Qt.Checked:
            self.abrir_ventana_extras()
        else:
            self.extras_medicamento = []
            print("Extras limpiados")

    def abrir_ventana_extras(self):
        """Abre la ventana para seleccionar extras"""
        try:
            ventana_extras = VentanaExtras(self)

            if ventana_extras.exec_() == QDialog.Accepted:
                self.extras_medicamento = ventana_extras.extras_seleccionados
                print(f"Extras seleccionados: {self.extras_medicamento}")
            else:
                # Si se canceló, desmarcar el checkbox
                self.checkBox.setChecked(False)
                self.extras_medicamento = []

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al abrir ventana de extras: {e}")
            print(f"Error: {e}")

    def recibir_extras(self, extras_lista):
        """Recibe la lista de extras seleccionados"""
        self.extras_medicamento = extras_lista
        print(f"Extras recibidos: {extras_lista}")

    def instalar_enter_autoavance(self):
        for widget in self.findChildren(QLineEdit):
            widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if isinstance(obj, QLineEdit) and event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                self.focusNextChild()
                return True
        return super().eventFilter(obj, event)

    def cargar_elementos(self):
        """Carga los elementos desde los archivos a los combobox"""
        try:
            # Cargar elementos de presentación
            with open('elementos.txt', 'r') as archivo:
                elementos = archivo.read().split(',')
                elementos = list(set([e.strip() for e in elementos if e.strip()]))  # Eliminar duplicados
                self.cbox_agPresentacion_2.clear()
                self.cbox_agPresentacion_2.addItems(elementos)

            # Cargar elementos de laboratorio
            with open('elementos_lab.txt', 'r') as archivo:
                elementos = archivo.read().split(',')
                elementos = list(set([e.strip() for e in elementos if e.strip()]))  # Eliminar duplicados
                self.cbox_agLab.clear()
                self.cbox_agLab.addItems(elementos)
        except:
            pass

    def agregarMedicamento(self):
        try:
            settings = QSettings("empresa", "usuarioActual")
            usuario = settings.value("usuario", "")

            # El orden correcto según la clase InventarioFarmacia es:
            # nombre, presentacion, laboratorio, existencias, fecha, tarjeta, efectivo,
            # indicacion, contra, dosis, comision, costo, foto

            medicamento = sql_structures.InventarioFarmacia(
                self.le_agNombreMedicamento.text(),  # nombre
                self.cbox_agPresentacion_2.currentText(),  # presentacion
                self.cbox_agLab.currentText(),  # laboratorio
                self.le_agExistencias.text() or "0",  # existencias
                self.dateEdit.date().toString("yyyy-MM-dd"),  # fecha
                self.le_agMontoTarjeta.text() or "0",  # tarjeta
                self.le_agMontoEfectivo.text() or "0",  # efectivo
                self.le_agMontoEfectivo_2.text() or "",  # indicacion
                self.le_agMontoEfectivo_4.text() or "",  # contra
                self.le_agMontoEfectivo_3.text() or "",  # dosis
                self.le_agMontoEfectivo_5.text() or "0",  # costo (ahora va primero)
                self.lineEdit.text() or "0",  # comision (ahora va después)
                self.imagen  # foto
            )

            medicamento.management('agre_inventarioFarmacia')

            # GUARDAR EXTRAS ASOCIADOS AL MEDICAMENTO (si existen)
            if hasattr(self, 'extras_medicamento') and self.extras_medicamento:
                medicamento_id = self.obtener_ultimo_medicamento_id()
                if medicamento_id:
                    self.guardar_extras_medicamento(medicamento_id, self.extras_medicamento)

            self.vita.agregarvitacora("Agregar", "Farmacia", self.fecha_actual, usuario,
                                      f"{self.le_agNombreMedicamento.text()}")

            self.limpiar_formulario()
            QMessageBox.about(self, 'Aviso', 'Medicamento agregado correctamente!')

        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', f'Error de agregado: {str(e)}')

        self.switch_window.emit('ingresar_medi')

    def crear_tabla_medicamento_extras(self):
        """Crear tabla de relación medicamento-extras si no existe"""
        try:
            import pymysql
            connection = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",  # Cambia por tu contraseña
                database="bdhidrocolon",
                charset='utf8mb4'
            )
            cursor = connection.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medicamento_extras (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    medicamento_id INT NOT NULL,
                    extra_nombre VARCHAR(100) NOT NULL,
                    fecha_asociacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_medicamento (medicamento_id),
                    INDEX idx_extra (extra_nombre)
                )
            ''')

            connection.commit()
            cursor.close()
            connection.close()
            print("✅ Tabla medicamento_extras verificada/creada")

        except Exception as e:
            print(f"Error creando tabla medicamento_extras: {e}")

    def obtener_ultimo_medicamento_id(self):
        """Obtiene el ID del último medicamento insertado"""
        try:
            import pymysql
            connection = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",  # Cambia por tu contraseña
                database="bdhidrocolon",
                charset='utf8mb4'
            )
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM medicamentos ORDER BY id DESC LIMIT 1;")
            #connection.commit()
            medicamento_id = cursor.fetchone()[0]
            return medicamento_id
        except Exception as e:
            print(f"Error obteniendo ID del medicamento: {e}")
            return None

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.le_agNombreMedicamento.clear()
        self.le_agExistencias.clear()
        self.le_agMontoTarjeta.clear()
        self.le_agMontoEfectivo.clear()
        self.le_agMontoEfectivo_2.clear()
        self.le_agMontoEfectivo_4.clear()
        self.le_agMontoEfectivo_3.clear()
        self.le_agMontoEfectivo_5.clear()
        self.lineEdit.clear()

        # Limpiar extras y desmarcar checkbox
        self.extras_medicamento = []
        if hasattr(self, 'checkBox'):
            self.checkBox.setChecked(False)

    def guardar_extras_medicamento(self, medicamento_id, extras_lista):
        """Guarda los extras asociados a un medicamento"""
        if not medicamento_id or not extras_lista:
            return

        try:
            import pymysql
            connection = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",
                database="bdhidrocolon",
                charset='utf8mb4'
            )
            cursor = connection.cursor()

            # Insertar cada extra asociado al medicamento
            for extra_nombre in extras_lista:
                cursor.execute('''
                    INSERT INTO medicamento_extras (medicamento_id, extra_nombre)
                    VALUES (%s, %s)
                ''', (medicamento_id, extra_nombre))

            connection.commit()
            print(f"✅ Extras guardados para medicamento {medicamento_id}: {extras_lista}")

        except Exception as e:
            print(f"❌ Error al guardar extras del medicamento: {e}")

    def actualizarMedicamentor(self, id, dato, columna):
        try:
            from .ventanaFuncional import VentanaFuncional
            usuario = VentanaFuncional.enviar_usuario()
            print(str(usuario))
            management = Manager()
            if columna == "Nombre":
                d = management.get_dato_tables(id, "medicamentos", "nombre")
                data = f"{d[0][0]} cambio a {dato}"
                self.vita.agregarvitacora("Actualizar", "Farmacia", self.fecha_actual, usuario, data)
            elif columna == "presentacion":
                de = management.get_dato_tables(id, "medicamentos", "nombre")
                d = management.get_dato_tables(id, "medicamentos", "presentacion")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Farmacia", self.fecha_actual, usuario, data)
            elif columna == "Laboratorio":
                de = management.get_dato_tables(id, "medicamentos", "nombre")
                d = management.get_dato_tables(id, "medicamentos", "laboratorio")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Farmacia", self.fecha_actual, usuario, data)
            elif columna == "Existencias":
                de = management.get_dato_tables(id, "medicamentos", "nombre")
                d = management.get_dato_tables(id, "medicamentos", "existencias")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Farmacia", self.fecha_actual, usuario, data)
            elif columna == "Fecha":
                de = management.get_dato_tables(id, "medicamentos", "nombre")
                d = management.get_dato_tables(id, "medicamentos", "fecha")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Farmacia", self.fecha_actual, usuario, data)
            elif columna == "Tarjeta":
                de = management.get_dato_tables(id, "medicamentos", "nombre")
                d = management.get_dato_tables(id, "medicamentos", "tarjeta")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Farmacia", self.fecha_actual, usuario, data)
            elif columna == "Efectivo":
                de = management.get_dato_tables(id, "medicamentos", "nombre")
                d = management.get_dato_tables(id, "medicamentos", "efectivo")
                data = f"{de[0][0]} tenía {d[0][0]} se modifico a {dato}"
                self.vita.agregarvitacora("Actualizar", "Farmacia", self.fecha_actual, usuario, data)
            medicamento = sql_structures.InventarioFarmacia("","","",
                                                            "",
                                                       "",
                                                       "",
                                                       "",
                                                       '','','','','','',
                                                        columna, dato, id)
            medicamento.management('edit_inventarioFarmacia')
            # QMessageBox.about(self, 'Aviso', 'Actualizado correctamente!')
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Error al actualizar!')

    def eliminarMedicamento(self, id):
        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        print(str(usuario))
        try:
            doctor = sql_structures.InventarioFarmacia('',
                                                    '',
                                          '','',
                                              '','','',
                                           '',"", " ",
                                            "","","",'','',
                                           id)
            p = doctor.inventarioFarmacia_elimin()
            QMessageBox.about(self, 'Aviso', 'Se elimino con exito!')
            self.vita.agregarvitacora("Eliminar", "Farmacia", self.fecha_actual, usuario, p)
        except Exception as e:
            print(e)
            QMessageBox.about(self, 'Aviso', 'Eliminacion fallida!')
        self.switch_window.emit('eliminar_medi')

    def cancelar(self):
        self.switch_window.emit('cancelar_medi')

    def IniciarDes(self):
        self.switch_window.emit('show_lab')

    def Iniciar(self):
        self.switch_window.emit('show_pre')

    def nue_lab(self):
        self.porcentajet = self.lab.get_porcentaje()
        # Verificar si ya existe antes de agregar
        items = [self.cbox_agLab.itemText(i) for i in range(self.cbox_agLab.count())]
        if self.porcentajet and self.porcentajet not in items:
            self.cbox_agLab.addItem(self.porcentajet)
            self.guardar_elementos_lab()
        self.cargar_elementos()     # Guardar después de agregar

    def eliminar_lab(self):
        self.porcentajet = self.lab.get_porcentaje_eli()
        if self.porcentajet:
            indice = self.cbox_agLab.findText(self.porcentajet)
            if indice != -1:  # Si se encuentra el elemento
                self.cbox_agLab.removeItem(indice)
                self.guardar_elementos_lab()
        self.cargar_elementos()                # # Guardar después de agregar

    def modificar_lab(self):
        self.porcentajet_li = self.lab.get_porcentaje_2()
        self.porcentajet_com = self.lab.get_porcentaje_com()

        indice = self.cbox_agLab.findText(self.porcentajet_com)

        if indice != -1:  # Si encuentra el dato anterior
            self.cbox_agLab.removeItem(indice)  # Elimina el dato anterior
            self.cbox_agLab.insertItem(indice, self.porcentajet_li)  # Inserta el nuevo dato en la misma posición
            self.guardar_elementos_lab()  # Guarda los cambios en el archivo
            return True
        self.cargar_elementos()
        return False

    def nue_pre(self):
        self.porcentajet = self.Pre.get_porcentaje()
        # Verificar si ya existe antes de agregar
        items = [self.cbox_agPresentacion_2.itemText(i) for i in range(self.cbox_agPresentacion_2.count())]
        if self.porcentajet and self.porcentajet not in items:
            self.cbox_agPresentacion_2.addItem(self.porcentajet)
            self.guardar_elementos_presentacion()
        self.cargar_elementos()     # Guardar después de agregar

    def eliminar_pre(self):
        print(1)
        self.porcentajet = self.Pre.get_porcentaje_eli()
        print(1)
        if self.porcentajet:
            indice = self.cbox_agPresentacion_2.findText(self.porcentajet)
            print(1)
            if indice != -1:  # Si se encuentra el elemento
                self.cbox_agPresentacion_2.removeItem(indice)
                print(1)
                self.guardar_elementos_presentacion()
        self.cargar_elementos()                # # Guardar después de agregar

    def modificar_pre(self):
        # Verificar si existe el dato a modificar

        self.porcentajet_li = self.Pre.get_porcentaje_2()
        self.porcentajet_com = self.Pre.get_porcentaje_com()

        indice = self.cbox_agPresentacion_2.findText(self.porcentajet_com)

        if indice != -1:  # Si encuentra el dato anterior
            self.cbox_agPresentacion_2.removeItem(indice)  # Elimina el dato anterior
            self.cbox_agPresentacion_2.insertItem(indice, self.porcentajet_li)  # Inserta el nuevo dato en la misma posición
            self.guardar_elementos_presentacion()  # Guarda los cambios en el archivo
            return True
        self.cargar_elementos()
        return False

    def closeEvent(self, event):
        self.guardar_elementos_presentacion()
        self.guardar_elementos_lab()
        event.accept()

    def guardar_elementos_presentacion(self):
        """Guarda los elementos de presentación al archivo"""
        try:
            elementos = []
            for i in range(self.cbox_agPresentacion_2.count()):
                elemento = self.cbox_agPresentacion_2.itemText(i).strip()
                if elemento:  # Solo agregar si no está vacío
                    elementos.append(elemento)

            if elementos:  # Solo escribir si hay elementos
                with open('elementos.txt', 'w') as archivo:
                    archivo.write(','.join(elementos))
        except Exception as e:
            print(f"Error al guardar elementos de presentación: {e}")

    def guardar_elementos_lab(self):
        """Guarda los elementos de laboratorio al archivo"""
        try:
            elementos = []
            for i in range(self.cbox_agLab.count()):
                elemento = self.cbox_agLab.itemText(i).strip()
                if elemento:  # Solo agregar si no está vacío
                    elementos.append(elemento)

            if elementos:  # Solo escribir si hay elementos
                with open('elementos_lab.txt', 'w') as archivo:
                    archivo.write(','.join(elementos))
        except Exception as e:
            print(f"Error al guardar elementos de laboratorio: {e}")



    def cargar_imagen(self):
        opciones = QFileDialog.Options()
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "",
                                                 "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)", options=opciones)

        if archivo:
            pixmap = QPixmap(archivo)
            pixmap = pixmap.scaled(self.label_2.width(), self.label_2.height(), aspectRatioMode=1)  # Mantiene proporción
            self.imagen = archivo
            self.label_2.setPixmap(pixmap)

    def cargar_medicamento_para_editar(self, id_medicamento):
        """Carga los datos del medicamento para editar"""
        try:
            self.modo_edicion = True
            self.id_medicamento_editar = id_medicamento

            # Cambiar el texto del botón y título de la ventana
            self.btn_agregar_medi.setText("Actualizar Medicamento")
            self.setWindowTitle("Editar Medicamento")

            # Obtener datos del medicamento
            manager = Manager()

            # Obtener todos los campos
            nombre = manager.get_dato_tables(id_medicamento, "medicamentos", "nombre")
            presentacion = manager.get_dato_tables(id_medicamento, "medicamentos", "presentacion")
            laboratorio = manager.get_dato_tables(id_medicamento, "medicamentos", "laboratorio")
            existencias = manager.get_dato_tables(id_medicamento, "medicamentos", "existencias")
            fecha = manager.get_dato_tables(id_medicamento, "medicamentos", "fecha")
            tarjeta = manager.get_dato_tables(id_medicamento, "medicamentos", "tarjeta")
            efectivo = manager.get_dato_tables(id_medicamento, "medicamentos", "efectivo")
            indicacion = manager.get_dato_tables(id_medicamento, "medicamentos", "indicacion")
            contra = manager.get_dato_tables(id_medicamento, "medicamentos", "contra")
            dosis = manager.get_dato_tables(id_medicamento, "medicamentos", "dosis")
            comision = manager.get_dato_tables(id_medicamento, "medicamentos", "comision")
            costo = manager.get_dato_tables(id_medicamento, "medicamentos", "costo")
            foto = manager.get_dato_tables(id_medicamento, "medicamentos", "foto")

            if nombre and nombre[0]:
                # Cargar nombre
                self.le_agNombreMedicamento.setText(str(nombre[0][0] or ""))

                # Cargar presentación
                if presentacion and presentacion[0]:
                    index = self.cbox_agPresentacion_2.findText(str(presentacion[0][0] or ""))
                    if index >= 0:
                        self.cbox_agPresentacion_2.setCurrentIndex(index)

                # Cargar laboratorio
                if laboratorio and laboratorio[0]:
                    index = self.cbox_agLab.findText(str(laboratorio[0][0] or ""))
                    if index >= 0:
                        self.cbox_agLab.setCurrentIndex(index)

                # Cargar existencias
                if existencias and existencias[0]:
                    self.le_agExistencias.setText(str(existencias[0][0] or "0"))

                # Cargar fecha
                if fecha and fecha[0] and fecha[0][0]:
                    from PyQt5.QtCore import QDate
                    fecha_str = str(fecha[0][0])
                    fecha_obj = QDate.fromString(fecha_str, "yyyy-MM-dd")
                    if fecha_obj.isValid():
                        self.dateEdit.setDate(fecha_obj)

                # Cargar precios
                if tarjeta and tarjeta[0]:
                    self.le_agMontoTarjeta.setText(str(tarjeta[0][0] or "0"))
                if efectivo and efectivo[0]:
                    self.le_agMontoEfectivo.setText(str(efectivo[0][0] or "0"))

                # Cargar indicación - en le_agMontoEfectivo_2
                if indicacion and indicacion[0]:
                    self.le_agMontoEfectivo_2.setText(str(indicacion[0][0] or ""))

                # Cargar contraindicación - en le_agMontoEfectivo_4
                if contra and contra[0]:
                    self.le_agMontoEfectivo_4.setText(str(contra[0][0] or ""))

                # Cargar dosis - en le_agMontoEfectivo_3
                if dosis and dosis[0]:
                    self.le_agMontoEfectivo_3.setText(str(dosis[0][0] or ""))

                # Cargar comisión - CORREGIDO
                if comision and comision[0]:
                    self.le_agMontoEfectivo_5.setText(str(comision[0][0] or "0"))

                    # Cargar costo - CORREGIDO
                if costo and costo[0]:
                    self.lineEdit.setText(str(costo[0][0] or "0"))

                # Cargar imagen
                if foto and foto[0] and foto[0][0]:
                    self.imagen = foto[0][0]

            else:
                QMessageBox.warning(self, "Advertencia", "No se encontraron datos del medicamento")
                self.close()

        except Exception as e:
            print(f"Error al cargar medicamento: {e}")
            QMessageBox.critical(self, "Error", f"Error al cargar los datos: {str(e)}")
            self.close()

    def cargar_extras_medicamento(self, id_medicamento):
        """Carga los extras asociados al medicamento"""
        try:
            manager = sql_structures.manager.Manager()

            # Consulta para obtener extras del medicamento
            query = """
                    SELECT e.id, e.nombre, me.cantidad
                    FROM medicamento_extras me
                             JOIN extras e ON me.extra_id = e.id
                    WHERE me.medicamento_id = %s \
                    """

            extras = manager.ejecutar_consulta_personalizada(query, (id_medicamento,))

            if extras:
                self.extras_medicamento = [(extra[0], extra[2]) for extra in extras]
                # Si tienes un checkbox o indicador de extras
                # self.checkbox_extras.setChecked(True)

        except Exception as e:
            print(f"Error al cargar extras: {e}")

    def guardar_medicamento(self):
        """Guarda o actualiza el medicamento según el modo"""
        if self.modo_edicion:
            self.actualizar_medicamento()
        else:
            self.agregarMedicamento()

    def actualizar_medicamento(self):
        """Actualiza el medicamento existente"""
        try:
            settings = QSettings("empresa", "usuarioActual")
            usuario = settings.value("usuario", "")

            # Validar campos obligatorios
            if not self.le_agNombreMedicamento.text() or not self.le_agExistencias.text():
                QMessageBox.warning(self, 'Aviso', 'Por favor complete los campos obligatorios')
                return

            # Usar el Manager para actualizar cada campo
            manager = sql_structures.manager.Manager()

            # Actualizar cada campo individualmente usando el método existente
            manager.update_table_with_id('medicamentos', ['nombre'], 'nombre',
                                         self.le_agNombreMedicamento.text(), self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', ['presentacion'], 'presentacion',
                                         self.cbox_agPresentacion_2.currentText(), self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', ['laboratorio'], 'laboratorio',
                                         self.cbox_agLab.currentText(), self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', ['existencias'], 'existencias',
                                         self.le_agExistencias.text(), self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', ['fecha'], 'fecha',
                                         self.dateEdit.date().toString("yyyy-MM-dd"), self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', ['tarjeta'], 'tarjeta',
                                         self.le_agMontoTarjeta.text() or "0", self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', ['efectivo'], 'efectivo',
                                         self.le_agMontoEfectivo.text() or "0", self.id_medicamento_editar)

            if self.lineEdit.text():
                manager.update_table_with_id('medicamentos', ['comision'], 'comision',
                                             self.lineEdit.text(), self.id_medicamento_editar)

            if self.imagen:
                manager.update_table_with_id('medicamentos', ['foto'], 'foto',
                                             self.imagen, self.id_medicamento_editar)

            # Actualizar extras si es necesario
            if hasattr(self, 'extras_medicamento') and self.extras_medicamento:
                self.actualizar_extras_medicamento(self.id_medicamento_editar, self.extras_medicamento)

            # Registrar en vitácora
            self.vita.agregarvitacora(
                "Actualizar",
                "Farmacia",
                self.fecha_actual,
                usuario,
                f"Medicamento actualizado: {self.le_agNombreMedicamento.text()}"
            )

            QMessageBox.information(self, 'Éxito', 'Medicamento actualizado correctamente')

            # Emitir señal para recargar tabla y cerrar ventana
            self.switch_window.emit("actualizado")
            self.close()

        except Exception as e:
            print(f"Error al actualizar medicamento: {e}")
            QMessageBox.critical(self, 'Error', f'Error al actualizar: {str(e)}')

    def actualizar_extras_medicamento(self, medicamento_id, extras_lista):
        """Actualiza los extras asociados al medicamento"""
        try:
            manager = sql_structures.manager.Manager()

            # Primero eliminar extras existentes
            query_delete = "DELETE FROM medicamento_extras WHERE medicamento_id = %s"
            manager.ejecutar_consulta_personalizada(query_delete, (medicamento_id,))

            # Luego insertar los nuevos
            if extras_lista:
                for extra_id, cantidad in extras_lista:
                    query_insert = """
                                   INSERT INTO medicamento_extras (medicamento_id, extra_id, cantidad)
                                   VALUES (%s, %s, %s) \
                                   """
                    manager.ejecutar_consulta_personalizada(
                        query_insert,
                        (medicamento_id, extra_id, cantidad)
                    )

        except Exception as e:
            print(f"Error al actualizar extras: {e}")

    def actualizar_medicamento(self):
        """Actualiza el medicamento existente"""
        try:
            settings = QSettings("empresa", "usuarioActual")
            usuario = settings.value("usuario", "")

            # Validar campos obligatorios
            if not self.le_agNombreMedicamento.text() or not self.le_agExistencias.text():
                QMessageBox.warning(self, 'Aviso', 'Por favor complete los campos obligatorios')
                return

            # Crear instancia del gestor
            manager = Manager()
            columns_ingreso = ['id']  # ← Aquí defines la columna ID correctamente

            # Actualizar campos de texto
            manager.update_table_with_id('medicamentos', columns_ingreso, 'nombre',
                                         self.le_agNombreMedicamento.text(), self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', columns_ingreso, 'presentacion',
                                         self.cbox_agPresentacion_2.currentText(), self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', columns_ingreso, 'laboratorio',
                                         self.cbox_agLab.currentText(), self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', columns_ingreso, 'fecha',
                                         self.dateEdit.date().toString("yyyy-MM-dd"), self.id_medicamento_editar)

            # Actualizar campos numéricos
            manager.update_table_with_id('medicamentos', columns_ingreso, 'existencias',
                                         int(self.le_agExistencias.text() or 0), self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', columns_ingreso, 'tarjeta',
                                         float(self.le_agMontoTarjeta.text() or 0), self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', columns_ingreso, 'efectivo',
                                         float(self.le_agMontoEfectivo.text() or 0), self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', columns_ingreso, 'comision',
                                         int(self.lineEdit.text() or 0), self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', columns_ingreso, 'costo',
                                         float(self.le_agMontoEfectivo_5.text() or 0), self.id_medicamento_editar)

            # Actualizar campos de texto adicionales
            manager.update_table_with_id('medicamentos', columns_ingreso, 'indicacion',
                                         self.le_agMontoEfectivo_2.text() or "", self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', columns_ingreso, 'contra',
                                         self.le_agMontoEfectivo_4.text() or "", self.id_medicamento_editar)
            manager.update_table_with_id('medicamentos', columns_ingreso, 'dosis',
                                         self.le_agMontoEfectivo_3.text() or "", self.id_medicamento_editar)

            # Actualizar imagen si existe
            if self.imagen:
                manager.update_table_with_id('medicamentos', columns_ingreso, 'foto',
                                             self.imagen, self.id_medicamento_editar)

            # Registrar en bitácora
            self.vita.agregarvitacora(
                "Actualizar",
                "Farmacia",
                self.fecha_actual,
                usuario,
                f"Medicamento actualizado: {self.le_agNombreMedicamento.text()}"
            )

            QMessageBox.information(self, 'Éxito', 'Medicamento actualizado correctamente')

            # Emitir señal para recargar tabla y cerrar ventana
            self.switch_window.emit("actualizado")
            self.close()

        except Exception as e:
            print(f"Error al actualizar medicamento: {e}")
            QMessageBox.critical(self, 'Error', f'Error al actualizar: {str(e)}')




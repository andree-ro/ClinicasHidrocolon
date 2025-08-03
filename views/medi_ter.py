from PyQt5 import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QSpinBox, QPushButton, QMessageBox,
                             QTableWidget, QTableWidgetItem, QWidget, QCheckBox,
                             QLineEdit, QCompleter, QListWidget, QListWidgetItem,
                             QFrame)
from PyQt5.QtCore import Qt, QTimer
from sql_structures.manager import Manager
import sql_structures


class DialogoTerapia(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.medicamentos_seleccionados = []
        self.medicamentos_cache = []
        self.medicamentos_filtrados = []
        self.setup_ui()
        self.cargar_medicamentos()

        # Timer para búsqueda con delay
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.realizar_busqueda)

    def setup_ui(self):
        self.setWindowTitle("Terapia")
        self.setMinimumWidth(800)
        layout = QVBoxLayout()

        self.chk_requiere_medicamentos = QCheckBox("Este combo requiere medicamentos")
        self.chk_requiere_medicamentos.stateChanged.connect(self.toggle_seccion_medicamentos)
        layout.addWidget(self.chk_requiere_medicamentos)

        self.widget_medicamentos = QWidget()
        layout_medicamentos = QVBoxLayout()

        # Sección de búsqueda mejorada
        self.setup_search_section(layout_medicamentos)

        # Tabla de medicamentos seleccionados
        self.tabla_medicamentos = QTableWidget()
        self.tabla_medicamentos.setColumnCount(4)
        self.tabla_medicamentos.setHorizontalHeaderLabels([
            "Medicamento", "Cantidad", "Disponible", "Acciones"
        ])
        self.tabla_medicamentos.setAlternatingRowColors(True)
        layout_medicamentos.addWidget(self.tabla_medicamentos)

        self.widget_medicamentos.setLayout(layout_medicamentos)
        layout.addWidget(self.widget_medicamentos)
        self.widget_medicamentos.hide()

        layout_botones = QHBoxLayout()
        self.btn_aceptar = QPushButton("Registrar terapia")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_aceptar.clicked.connect(self.aceptar)
        self.btn_cancelar.clicked.connect(self.reject)
        layout_botones.addWidget(self.btn_aceptar)
        layout_botones.addWidget(self.btn_cancelar)
        layout.addLayout(layout_botones)

        self.setLayout(layout)

    def setup_search_section(self, layout_medicamentos):
        """Configura la sección de búsqueda mejorada"""
        # Frame contenedor para el buscador
        search_frame = QFrame()
        search_frame.setFrameStyle(QFrame.Box)
        search_layout = QVBoxLayout()

        # Barra de búsqueda
        search_bar_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Buscar medicamento por nombre, principio activo o código...")
        self.search_box.textChanged.connect(self.on_search_text_changed)
        self.search_box.returnPressed.connect(self.agregar_primer_resultado)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_busqueda)
        self.btn_limpiar.setMaximumWidth(80)

        search_bar_layout.addWidget(self.search_box)
        search_bar_layout.addWidget(self.btn_limpiar)
        search_layout.addLayout(search_bar_layout)

        # Lista de resultados
        self.lista_resultados = QListWidget()
        self.lista_resultados.setMaximumHeight(150)
        self.lista_resultados.itemDoubleClicked.connect(self.agregar_medicamento_desde_lista)
        self.lista_resultados.hide()
        search_layout.addWidget(self.lista_resultados)

        # Botones de acción
        botones_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Seleccionado")
        self.btn_agregar.clicked.connect(self.agregar_medicamento_seleccionado)
        self.btn_agregar.setEnabled(False)

        self.lbl_contador = QLabel("0 medicamentos encontrados")
        self.lbl_contador.setStyleSheet("color: gray; font-size: 10px;")

        botones_layout.addWidget(self.btn_agregar)
        botones_layout.addStretch()
        botones_layout.addWidget(self.lbl_contador)
        search_layout.addLayout(botones_layout)

        search_frame.setLayout(search_layout)
        layout_medicamentos.addWidget(search_frame)

    def cargar_medicamentos(self):
        """Carga todos los medicamentos desde la base de datos"""
        try:
            manager = sql_structures.Manager()
            medicamentos_data = manager.print_table('medicamentos')

            # Asegurar que sea una lista
            if isinstance(medicamentos_data, tuple):
                self.medicamentos_cache = list(medicamentos_data)
            else:
                self.medicamentos_cache = medicamentos_data if medicamentos_data else []

            self.medicamentos_filtrados = self.medicamentos_cache.copy()
            print(f"Medicamentos cargados: {len(self.medicamentos_cache)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar medicamentos: {e}")
            self.medicamentos_cache = []
            self.medicamentos_filtrados = []

    def on_search_text_changed(self, texto):
        """Maneja el cambio de texto en el buscador con delay"""
        self.search_timer.stop()
        if texto.strip():
            self.search_timer.start(300)  # Delay de 300ms
        else:
            self.limpiar_resultados()

    def realizar_busqueda(self):
        """Realiza la búsqueda con múltiples criterios"""
        texto = self.search_box.text().strip().lower()

        if not texto:
            self.limpiar_resultados()
            return

        # Verificar que tenemos medicamentos cargados
        if not self.medicamentos_cache:
            self.limpiar_resultados()
            self.lbl_contador.setText("No hay medicamentos cargados")
            self.lbl_contador.setStyleSheet("color: red; font-size: 10px;")
            return

        # Limpiar estilo de error
        self.search_box.setStyleSheet("")

        # Filtrar medicamentos
        resultados = []

        for medicamento in self.medicamentos_cache:
            try:
                # Validar que el medicamento tenga la estructura esperada
                if not medicamento or len(medicamento) < 2:
                    continue

                # Suponiendo estructura: [id, nombre, descripcion, precio, ...]
                id_med = medicamento[0]
                nombre = str(medicamento[1]).lower() if medicamento[1] else ""

                if not nombre:  # Saltar si no hay nombre
                    continue

                # Búsqueda por múltiples criterios

                # 1. Coincidencia exacta en el nombre
                if texto == nombre:
                    resultados.insert(0, medicamento)  # Prioridad alta
                    continue

                # 2. Nombre comienza con el texto
                elif nombre.startswith(texto):
                    resultados.insert(0 if not resultados else 1, medicamento)
                    continue

                # 3. Contiene el texto
                elif texto in nombre:
                    resultados.append(medicamento)
                    continue

                # 4. Búsqueda por palabras individuales
                palabras_busqueda = texto.split()
                palabras_nombre = nombre.split()

                if all(any(palabra in palabra_nombre for palabra_nombre in palabras_nombre)
                       for palabra in palabras_busqueda):
                    resultados.append(medicamento)
                    continue

                # 5. Búsqueda por código/ID si es numérico
                if texto.isdigit() and str(id_med) == texto:
                    resultados.insert(0, medicamento)
                    continue

            except Exception as e:
                print(f"Error procesando medicamento: {medicamento}, Error: {e}")
                continue

        self.mostrar_resultados(resultados)

    def mostrar_resultados(self, resultados):
        """Muestra los resultados de búsqueda en la lista"""
        self.lista_resultados.clear()
        self.medicamentos_filtrados = resultados

        if not resultados:
            self.lista_resultados.hide()
            self.lbl_contador.setText("No se encontraron medicamentos")
            self.lbl_contador.setStyleSheet("color: red; font-size: 10px;")
            self.btn_agregar.setEnabled(False)
            return

        # Mostrar hasta 10 resultados
        for i, medicamento in enumerate(resultados[:10]):
            try:
                if not medicamento or len(medicamento) < 2:
                    continue

                manager = sql_structures.Manager()
                disponible = manager.get_existencias(medicamento[0])

                # Crear item con información detallada
                nombre_med = str(medicamento[1]) if medicamento[1] else "Sin nombre"
                texto_item = nombre_med

                # Agregar descripción si existe
                if len(medicamento) > 2 and medicamento[2]:
                    descripcion = str(medicamento[2])[:50]
                    if len(str(medicamento[2])) > 50:
                        descripcion += "..."
                    texto_item += f" - {descripcion}"

                texto_item += f" (Disponible: {disponible})"

                item = QListWidgetItem(texto_item)
                item.setData(Qt.UserRole, medicamento)  # Guardar datos del medicamento

                # Colorear según disponibilidad
                if disponible <= 0:
                    item.setBackground(Qt.lightGray)
                    texto_item += " - SIN STOCK"
                    item.setText(texto_item)
                elif disponible <= 5:
                    item.setBackground(Qt.yellow)

                self.lista_resultados.addItem(item)

            except Exception as e:
                print(f"Error mostrando medicamento: {medicamento}, Error: {e}")
                continue

        # Seleccionar primer item si hay resultados
        if self.lista_resultados.count() > 0:
            self.lista_resultados.setCurrentRow(0)
            self.btn_agregar.setEnabled(True)
        else:
            self.btn_agregar.setEnabled(False)

        self.lista_resultados.show()

        # Actualizar contador
        total_text = f"{len(resultados)} medicamento(s) encontrado(s)"
        if len(resultados) > 10:
            total_text += f" (mostrando primeros 10)"
        self.lbl_contador.setText(total_text)
        self.lbl_contador.setStyleSheet("color: green; font-size: 10px;")

    def limpiar_resultados(self):
        """Limpia los resultados de búsqueda"""
        self.lista_resultados.clear()
        self.lista_resultados.hide()
        self.lbl_contador.setText("0 medicamentos encontrados")
        self.lbl_contador.setStyleSheet("color: gray; font-size: 10px;")
        self.btn_agregar.setEnabled(False)
        self.medicamentos_filtrados = []

    def limpiar_busqueda(self):
        """Limpia el campo de búsqueda"""
        self.search_box.clear()
        self.search_box.setStyleSheet("")
        self.limpiar_resultados()

    def agregar_primer_resultado(self):
        """Agrega el primer resultado cuando se presiona Enter"""
        if self.lista_resultados.count() > 0:
            primer_item = self.lista_resultados.item(0)
            medicamento = primer_item.data(Qt.UserRole)
            self.agregar_fila_medicamento(medicamento)
            self.limpiar_busqueda()

    def agregar_medicamento_seleccionado(self):
        """Agrega el medicamento seleccionado de la lista"""
        item_actual = self.lista_resultados.currentItem()
        if item_actual:
            medicamento = item_actual.data(Qt.UserRole)
            self.agregar_fila_medicamento(medicamento)
            self.limpiar_busqueda()

    def agregar_medicamento_desde_lista(self, item):
        """Agrega medicamento al hacer doble clic en la lista"""
        medicamento = item.data(Qt.UserRole)
        self.agregar_fila_medicamento(medicamento)
        self.limpiar_busqueda()

    def buscar_medicamento(self, texto):
        """Método legacy mantenido por compatibilidad"""
        # Este método se mantiene por si hay referencias en el código original
        pass

    def agregar_fila_medicamento(self, medicamento):
        """Agrega una fila con el medicamento a la tabla"""
        # Verificar si ya está agregado
        for fila in range(self.tabla_medicamentos.rowCount()):
            nombre_existente = self.tabla_medicamentos.cellWidget(fila, 0).text()
            if nombre_existente == str(medicamento[1]):
                QMessageBox.information(self, "Información",
                                        f"El medicamento '{medicamento[1]}' ya está agregado")
                return

        fila_actual = self.tabla_medicamentos.rowCount()
        self.tabla_medicamentos.insertRow(fila_actual)

        # Nombre medicamento
        lbl_nombre = QLabel(str(medicamento[1]))

        # Cantidad
        spin_cantidad = QSpinBox()
        spin_cantidad.setMinimum(1)

        # Disponibilidad
        manager = sql_structures.Manager()
        disponible = manager.get_existencias(medicamento[0])
        lbl_disponible = QLabel(str(disponible))

        if disponible <= 0:
            spin_cantidad.setEnabled(False)
            lbl_disponible.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.warning(self, "Sin Stock",
                                f"El medicamento '{medicamento[1]}' no tiene stock disponible")
        else:
            spin_cantidad.setMaximum(disponible)

        # Botón eliminar
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(lambda: self.eliminar_fila(fila_actual))

        # Configurar widgets en la tabla
        self.tabla_medicamentos.setCellWidget(fila_actual, 0, lbl_nombre)
        self.tabla_medicamentos.setCellWidget(fila_actual, 1, spin_cantidad)
        self.tabla_medicamentos.setCellWidget(fila_actual, 2, lbl_disponible)
        self.tabla_medicamentos.setCellWidget(fila_actual, 3, btn_eliminar)

    def toggle_seccion_medicamentos(self, state):
        """Muestra/oculta la sección de medicamentos"""
        self.widget_medicamentos.setVisible(state == 2)
        if not state == 2:
            self.tabla_medicamentos.setRowCount(0)
            self.limpiar_busqueda()

    def eliminar_fila(self, fila):
        """Elimina una fila de la tabla"""
        self.tabla_medicamentos.removeRow(fila)
        # Reindexar botones de eliminar
        for i in range(self.tabla_medicamentos.rowCount()):
            btn = self.tabla_medicamentos.cellWidget(i, 3)
            if btn:
                btn.clicked.disconnect()
                btn.clicked.connect(lambda checked, row=i: self.eliminar_fila(row))

    def actualizar_total(self):
        """Método legacy mantenido por compatibilidad"""
        # Se mantiene por si hay referencias en el código original
        pass

    def aceptar(self):
        """Procesa la aceptación del diálogo"""
        try:
            if self.chk_requiere_medicamentos.isChecked():
                medicamentos = []
                for fila in range(self.tabla_medicamentos.rowCount()):
                    nombre = self.tabla_medicamentos.cellWidget(fila, 0).text()
                    cantidad = self.tabla_medicamentos.cellWidget(fila, 1).value()

                    # Buscar ID del medicamento
                    med_id = None
                    for med in self.medicamentos_cache:
                        if str(med[1]) == nombre:
                            med_id = med[0]
                            break

                    if med_id:
                        medicamentos.append({
                            'id': med_id,
                            'cantidad': cantidad
                        })

                if not medicamentos:
                    QMessageBox.warning(self, "Aviso", "Debe agregar al menos un medicamento")
                    return

                self.medicamentos_seleccionados = medicamentos
            else:
                self.medicamentos_seleccionados = []

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar la selección: {e}")
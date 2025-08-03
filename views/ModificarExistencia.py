from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, QMessageBox,
                             QHeaderView, QAbstractItemView, QShortcut)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
import sql_structures


class Existencias(QMainWindow):
    switch_window = QtCore.pyqtSignal(str)
    dato = QtCore.pyqtSignal(int)
    _porcentaje = 0

    def __init__(self):
        super(Existencias, self).__init__()

        # Cargar el UI mejorado
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\CantidadesExistencias.ui', self)

        # Variables de estado
        self.por = 0
        self.valor = 0
        self.producto_seleccionado = None
        self.tipo_producto = None
        self.productos_agregados = 0  # NUEVO: Contador

        # Importar aquí para evitar importación circular
        from .ventanaFuncional import VentanaFuncional
        self.ventana = VentanaFuncional()

        # Configurar la tabla de resultados
        self.configurar_tabla_resultados()

        # Conectar eventos
        self.conectar_eventos()

        # NUEVO: Configurar atajos de teclado
        self.configurar_atajos_teclado()

        # Cargar todos los productos al inicio
        self.cargar_todos_productos()

    def configurar_atajos_teclado(self):
        """Configura atajos de teclado para mayor velocidad"""
        # Ctrl+F para enfocar búsqueda
        shortcut_buscar = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_buscar.activated.connect(lambda: self.lineEdit_busqueda.setFocus())

        # Escape para limpiar búsqueda
        shortcut_limpiar = QShortcut(QKeySequence("Escape"), self)
        shortcut_limpiar.activated.connect(self.limpiar_busqueda)

        # Ctrl+Enter para agregar rápido
        shortcut_agregar = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut_agregar.activated.connect(self.agregar_al_carrito)

        # F1 para enfocar cantidad
        shortcut_cantidad = QShortcut(QKeySequence("F1"), self)
        shortcut_cantidad.activated.connect(lambda: self.lineEdit_cantidad.setFocus())

    def configurar_tabla_resultados(self):
        """Configura la tabla de resultados de búsqueda"""
        # Configurar encabezados
        headers = ["Tipo", "Nombre", "Presentación", "Stock", "Precio"]
        self.tabla_resultados.setColumnCount(len(headers))
        self.tabla_resultados.setHorizontalHeaderLabels(headers)

        # Configurar ancho de columnas
        header = self.tabla_resultados.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Tipo
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nombre
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Presentación
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Stock
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Precio

        # Configurar selección
        self.tabla_resultados.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_resultados.setSelectionMode(QAbstractItemView.SingleSelection)

    def conectar_eventos(self):
        """Conecta todos los eventos de la interfaz"""
        # Eventos de búsqueda
        self.lineEdit_busqueda.textChanged.connect(self.buscar_productos)
        self.btn_limpiar_busqueda.clicked.connect(self.limpiar_busqueda)

        # Eventos de tabla
        self.tabla_resultados.itemSelectionChanged.connect(self.producto_seleccionado_cambio)
        self.tabla_resultados.itemDoubleClicked.connect(self.seleccionar_producto_doble_click)

        # Eventos de cantidad y botones
        self.lineEdit_cantidad.returnPressed.connect(self.agregar_al_carrito)
        self.btn_agregar.clicked.connect(self.agregar_al_carrito)
        self.btn_cancelar.clicked.connect(self.finalizar_y_cerrar)  # CAMBIO: Nueva función

    def buscar_productos(self):
        """Busca productos en toda la base de datos"""
        texto_busqueda = self.lineEdit_busqueda.text().strip()

        if len(texto_busqueda) < 1:
            self.cargar_todos_productos()
            return

        resultados = []
        manager = sql_structures.Manager()

        try:
            # 1. BUSCAR MEDICAMENTOS
            try:
                medicamentos = manager.busqueda_medicina(texto_busqueda)
                for med in medicamentos:
                    if len(med) >= 8:  # Asegurar que tiene todos los campos
                        stock = med[4] if med[4] is not None else 0
                        precio = f"T:{med[6]} E:{med[7]}" if len(med) > 7 else "N/D"
                        resultados.append({
                            'tipo': 'Medicamento',
                            'id': med[0],
                            'nombre': med[1],
                            'presentacion': med[2] if med[2] else '',
                            'stock': stock,
                            'precio': precio,
                            'categoria': 'medicamento',
                            'datos_completos': med
                        })
            except Exception as e:
                print(f"Error buscando medicamentos: {e}")

            # 2. BUSCAR TERAPIAS
            try:
                terapias = manager.busqueda("terapias", texto_busqueda)
                for ter in terapias:
                    if len(ter) >= 4:
                        resultados.append({
                            'tipo': 'Terapia',
                            'id': ter[0],
                            'nombre': ter[1],
                            'presentacion': ter[2] if len(ter) > 2 else '',
                            'stock': 'Ilimitado',
                            'precio': f"T:{ter[3]}" if len(ter) > 3 else "N/D",
                            'categoria': 'terapia',
                            'datos_completos': ter
                        })
            except Exception as e:
                print(f"Error buscando terapias: {e}")

            # 3. BUSCAR JORNADAS/PROMOCIONES
            try:
                promociones = manager.busqueda("promociones", texto_busqueda)
                for prom in promociones:
                    if len(prom) >= 3:
                        resultados.append({
                            'tipo': 'Promoción',
                            'id': prom[0],
                            'nombre': prom[1],
                            'presentacion': '',
                            'stock': 'Ilimitado',
                            'precio': f"T:{prom[2]}" if len(prom) > 2 else "N/D",
                            'categoria': 'promocion',
                            'datos_completos': prom
                        })
            except Exception as e:
                print(f"Error buscando promociones: {e}")

            # 4. BUSCAR EXTRAS
            try:
                # Buscar extras manualmente ya que no hay método específico
                conexion = manager.conexion
                cursor = conexion.cursor()

                query = """
                        SELECT id, nombre, descripcion, cantidad, unidad
                        FROM extras
                        WHERE activo = 1 \
                          AND (
                            nombre LIKE %s OR
                            descripcion LIKE %s
                            )
                        ORDER BY nombre \
                        """
                cursor.execute(query, (f"%{texto_busqueda}%", f"%{texto_busqueda}%"))
                extras = cursor.fetchall()

                for extra in extras:
                    resultados.append({
                        'tipo': 'Extra',
                        'id': extra[0],
                        'nombre': extra[1],
                        'presentacion': extra[4] if extra[4] else 'Unidad',
                        'stock': extra[3] if extra[3] is not None else 0,
                        'precio': 'Incluido',
                        'categoria': 'extra',
                        'datos_completos': extra
                    })
            except Exception as e:
                print(f"Error buscando extras: {e}")

            # Mostrar resultados
            self.mostrar_resultados(resultados)

        except Exception as e:
            print(f"Error general en búsqueda: {e}")
            self.label_contador.setText("Error en la búsqueda")

    def cargar_todos_productos(self):
        """Carga todos los productos disponibles al inicio"""
        self.lineEdit_busqueda.setText("")
        manager = sql_structures.Manager()
        resultados = []

        try:
            # Cargar medicamentos
            medicamentos = manager.print_table_farmacia()
            for med in medicamentos[:20]:  # Limitar a 20 inicialmente
                if len(med) >= 8:
                    stock = med[4] if med[4] is not None else 0
                    precio = f"T:{med[6]} E:{med[7]}" if len(med) > 7 else "N/D"
                    resultados.append({
                        'tipo': 'Medicamento',
                        'id': med[0],
                        'nombre': med[1],
                        'presentacion': med[2] if med[2] else '',
                        'stock': stock,
                        'precio': precio,
                        'categoria': 'medicamento',
                        'datos_completos': med
                    })

            self.mostrar_resultados(resultados)
            self.label_contador.setText(f"Mostrando {len(resultados)} medicamentos (escribe para buscar más)")

        except Exception as e:
            print(f"Error cargando productos iniciales: {e}")

    def mostrar_resultados(self, resultados):
        """Muestra los resultados en la tabla"""
        self.tabla_resultados.setRowCount(len(resultados))

        for fila, producto in enumerate(resultados):
            try:
                # Tipo
                item_tipo = QTableWidgetItem(producto['tipo'])
                item_tipo.setData(Qt.UserRole, producto)  # Guardar datos completos
                self.tabla_resultados.setItem(fila, 0, item_tipo)

                # Nombre
                item_nombre = QTableWidgetItem(producto['nombre'])
                self.tabla_resultados.setItem(fila, 1, item_nombre)

                # Presentación
                item_presentacion = QTableWidgetItem(producto['presentacion'])
                self.tabla_resultados.setItem(fila, 2, item_presentacion)

                # Stock
                stock = producto['stock']
                item_stock = QTableWidgetItem(str(stock))

                # Colorear según stock
                if isinstance(stock, int):
                    if stock <= 0:
                        item_stock.setBackground(Qt.red)
                        item_stock.setForeground(Qt.white)
                    elif stock <= 5:
                        item_stock.setBackground(Qt.yellow)
                else:
                    # Para terapias y promociones (stock ilimitado)
                    item_stock.setBackground(Qt.green)
                    item_stock.setForeground(Qt.white)

                self.tabla_resultados.setItem(fila, 3, item_stock)

                # Precio
                item_precio = QTableWidgetItem(producto['precio'])
                self.tabla_resultados.setItem(fila, 4, item_precio)

            except Exception as e:
                print(f"Error mostrando producto en fila {fila}: {e}")

        # Actualizar contador
        if len(resultados) == 0:
            self.label_contador.setText("❌ No se encontraron productos")
            self.label_contador.setStyleSheet("color: red; font: 9pt 'Nunito';")
        else:
            self.label_contador.setText(f"✅ {len(resultados)} productos encontrados")
            self.label_contador.setStyleSheet("color: green; font: 9pt 'Nunito';")

    def producto_seleccionado_cambio(self):
        """Se ejecuta cuando cambia la selección en la tabla"""
        items_seleccionados = self.tabla_resultados.selectedItems()

        if not items_seleccionados:
            self.limpiar_seleccion()
            return

        # Obtener la fila seleccionada
        fila = items_seleccionados[0].row()
        item_tipo = self.tabla_resultados.item(fila, 0)

        if item_tipo:
            self.producto_seleccionado = item_tipo.data(Qt.UserRole)
            self.actualizar_info_producto_seleccionado()

    def seleccionar_producto_doble_click(self, item):
        """Selecciona producto al hacer doble clic"""
        if item:
            self.producto_seleccionado_cambio()
            # Enfocar el campo de cantidad para agilizar el proceso
            self.lineEdit_cantidad.setFocus()

    def actualizar_info_producto_seleccionado(self):
        """Actualiza la información del producto seleccionado"""
        if not self.producto_seleccionado:
            return

        producto = self.producto_seleccionado

        # Actualizar etiqueta del producto
        nombre_completo = f"{producto['tipo']}: {producto['nombre']}"
        if producto['presentacion']:
            nombre_completo += f" ({producto['presentacion']})"

        self.label_producto_seleccionado.setText(f"📦 Producto seleccionado: {nombre_completo}")

        # Actualizar stock disponible
        stock = producto['stock']
        if isinstance(stock, int):
            self.label_stock_disponible.setText(f"Stock disponible: {stock} unidades")
            if stock <= 0:
                self.label_stock_disponible.setStyleSheet("color: red; font: bold 9pt 'Nunito';")
                self.btn_agregar.setEnabled(False)
            elif stock <= 5:
                self.label_stock_disponible.setStyleSheet("color: orange; font: bold 9pt 'Nunito';")
                self.btn_agregar.setEnabled(True)
            else:
                self.label_stock_disponible.setStyleSheet("color: green; font: bold 9pt 'Nunito';")
                self.btn_agregar.setEnabled(True)
        else:
            # Stock ilimitado (terapias, promociones)
            self.label_stock_disponible.setText("Stock: Ilimitado")
            self.label_stock_disponible.setStyleSheet("color: green; font: bold 9pt 'Nunito';")
            self.btn_agregar.setEnabled(True)

        # Establecer valores para compatibilidad con el sistema actual
        self.valor = producto['id']
        self.tipo_producto = producto['categoria']

    def limpiar_seleccion(self):
        """Limpia la selección actual"""
        self.producto_seleccionado = None
        self.valor = 0
        self.tipo_producto = None
        self.label_producto_seleccionado.setText("📦 Producto seleccionado: Ninguno")
        self.label_stock_disponible.setText("Stock disponible: --")
        self.btn_agregar.setEnabled(False)

    def limpiar_busqueda(self):
        """Limpia el campo de búsqueda y recarga todos los productos"""
        self.lineEdit_busqueda.clear()
        self.cargar_todos_productos()
        self.limpiar_seleccion()

    def validar_cantidad(self):
        """Valida la cantidad ingresada"""
        try:
            texto_cantidad = self.lineEdit_cantidad.text().strip()

            if not texto_cantidad:
                return 0, "Por favor ingrese una cantidad"

            cantidad = int(texto_cantidad)

            if cantidad <= 0:
                return 0, "La cantidad debe ser mayor a 0"

            # Validar stock para productos con stock limitado
            if self.producto_seleccionado and isinstance(self.producto_seleccionado['stock'], int):
                stock_disponible = self.producto_seleccionado['stock']
                if cantidad > stock_disponible:
                    return 0, f"Cantidad solicitada ({cantidad}) excede el stock disponible ({stock_disponible})"

            return cantidad, None

        except ValueError:
            return 0, "Por favor ingrese un número válido"

    def agregar_al_carrito(self):
        """Agrega el producto seleccionado al carrito - MEJORADO PARA MANTENER ABIERTO"""
        try:
            # Validar que hay un producto seleccionado
            if not self.producto_seleccionado:
                QMessageBox.warning(self, "Error", "Por favor selecciona un producto de la tabla")
                return

            # Validar cantidad
            cantidad, error = self.validar_cantidad()
            if error:
                QMessageBox.warning(self, "Error", error)
                return

            producto_nombre = self.producto_seleccionado['nombre']

            # Procesar según el tipo de producto
            if self.tipo_producto == 'medicamento':
                self.agregar_medicamento_al_carrito(cantidad)
            elif self.tipo_producto == 'terapia':
                self.agregar_terapia_al_carrito(cantidad)
            elif self.tipo_producto == 'promocion':
                self.agregar_promocion_al_carrito(cantidad)
            elif self.tipo_producto == 'extra':
                self.agregar_extra_al_carrito(cantidad)
            else:
                QMessageBox.warning(self, "Error", "Tipo de producto no reconocido")
                return

            # NUEVO: Contar productos agregados
            self.productos_agregados += 1
            self.actualizar_titulo()

            # NUEVO: Confirmación rápida
            QMessageBox.information(self, "✅ Agregado",
                                    f"'{producto_nombre}' (x{cantidad}) agregado.\n\n"
                                    f"🛒 Total: {self.productos_agregados} productos\n\n"
                                    "Continúa agregando o presiona 'Finalizar'")

            # Actualizar datos
            self.ventana.cargarTablaFarmacia_sin()
            self.ventana.cargarTablacarrito()

            # NUEVO: Limpiar para siguiente producto
            self.limpiar_para_siguiente()

            # ======== CAMBIO PRINCIPAL ========
            # COMENTAR ESTA LÍNEA PARA NO CERRAR:
            # self.close()
            # ===================================

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")

    def actualizar_titulo(self):
        """Actualiza el título de la ventana con contador"""
        if self.productos_agregados == 0:
            titulo = "Agregar Productos al Carrito"
        else:
            titulo = f"Agregar Productos - 🛒 {self.productos_agregados} agregados"
        self.setWindowTitle(titulo)

    def limpiar_para_siguiente(self):
        """Limpia la selección para agregar siguiente producto"""
        # Limpiar cantidad
        self.lineEdit_cantidad.clear()

        # Limpiar selección de tabla
        self.tabla_resultados.clearSelection()
        self.limpiar_seleccion()

        # Enfocar búsqueda para siguiente producto
        self.lineEdit_busqueda.setFocus()

    def finalizar_y_cerrar(self):
        """NUEVO: Finaliza y cierra con resumen"""
        if self.productos_agregados > 0:
            QMessageBox.information(self, "🎉 ¡Listo!",
                                    f"Se agregaron {self.productos_agregados} productos al carrito.\n\n"
                                    "¡Listos para procesar la venta!")
        self.close()

    def agregar_medicamento_al_carrito(self, cantidad):
        """Agrega medicamento al carrito"""
        # Guardar para compatibilidad con el sistema actual
        Existencias._porcentaje = cantidad
        self.por = cantidad
        self.dato.emit(cantidad)

        # Usar el método existente
        self.ventana.agregar_medicamento_a_carrito(cantidad, self.valor)

    def agregar_terapia_al_carrito(self, cantidad):
        """Agrega terapia al carrito"""
        try:
            manager = sql_structures.Manager()
            terapia = self.producto_seleccionado['datos_completos']

            # Usar método similar al de medicamentos pero para terapias
            nombre = terapia[1]
            precio_tarjeta = terapia[3] if len(terapia) > 3 else 0
            precio_efectivo = terapia[4] if len(terapia) > 4 else precio_tarjeta

            total_tarjeta = cantidad * precio_tarjeta
            total_efectivo = cantidad * precio_efectivo

            self.ventana.carrito.agregar_a_carrito(
                nombre, total_efectivo, cantidad, total_tarjeta,
                -1, -1, self.valor, -1, -1, -1
            )

        except Exception as e:
            raise Exception(f"Error agregando terapia: {e}")

    def agregar_promocion_al_carrito(self, cantidad):
        """Agrega promoción al carrito"""
        try:
            manager = sql_structures.Manager()
            promocion = self.producto_seleccionado['datos_completos']

            nombre = promocion[1]
            precio_tarjeta = promocion[2] if len(promocion) > 2 else 0
            precio_efectivo = promocion[3] if len(promocion) > 3 else precio_tarjeta

            total_tarjeta = cantidad * precio_tarjeta
            total_efectivo = cantidad * precio_efectivo

            self.ventana.carrito.agregar_a_carrito(
                nombre, total_efectivo, cantidad, total_tarjeta,
                -1, self.valor, -1, -1, -1, -1
            )

        except Exception as e:
            raise Exception(f"Error agregando promoción: {e}")

    def agregar_extra_al_carrito(self, cantidad):
        """Agrega extra al carrito"""
        try:
            # Los extras generalmente se asocian a medicamentos
            # Aquí se puede agregar como producto independiente
            extra = self.producto_seleccionado['datos_completos']
            nombre = f"Extra: {extra[1]}"

            # Los extras normalmente no tienen precio directo, asignar 0
            self.ventana.carrito.agregar_a_carrito(
                nombre, 0, cantidad, 0,
                -1, -1, -1, -1, -1, self.valor
            )

            # Reducir cantidad del extra en inventario
            manager = sql_structures.Manager()
            conexion = manager.conexion
            cursor = conexion.cursor()

            cursor.execute(
                "UPDATE extras SET cantidad = cantidad - %s WHERE id = %s",
                (cantidad, self.valor)
            )
            conexion.commit()

        except Exception as e:
            raise Exception(f"Error agregando extra: {e}")

    def recibir2(self, valor):
        """Método de compatibilidad con el sistema actual"""
        print(f'valor 2: {valor}')
        self.valor = valor

    @classmethod
    def get_porcentaje(cls):
        """Método de compatibilidad con el sistema actual"""
        return cls._porcentaje

    def closeEvent(self, event):
        """Se ejecuta al cerrar la ventana"""
        # Resetear contador para próxima vez
        self.productos_agregados = 0
        self.limpiar_seleccion()
        event.accept()

    def showEvent(self, event):
        """Se ejecuta al mostrar la ventana"""
        # Resetear contador cada vez que se abre
        self.productos_agregados = 0
        self.actualizar_titulo()

        # Enfocar búsqueda para empezar rápido
        self.lineEdit_busqueda.setFocus()
        event.accept()
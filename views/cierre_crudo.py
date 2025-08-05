import sys
import datetime
from datetime import datetime, date, timedelta
import datetime as dt

import pymysql
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QGridLayout, QMessageBox, QFrame, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os
from datetime import datetime
import datetime
from .efectivo import CashRegisterApp

class CierreApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Cierre")
        self.setGeometry(700, 100, 800, 700)  # Incrementado el tamaño para acomodar las tablas
        # Denominaciones de billetes y monedas
        self.denominaciones = [
            ("Billetes de", 200.00, "Q200"),
            ("Billetes de", 100.00, "Q100"),
            ("Billetes de", 50.00, "Q50"),
            ("Billetes de", 20.00, "Q20"),
            ("Billetes de", 10.00, "Q10"),
            ("Billetes de", 5.00, "Q5"),
            ("Monedas", 1.00, "Q1"),
            ("Monedas", 0.50, "Q0.50"),
            ("Monedas", 0.25, "Q0.25"),
            ("Monedas", 0.10, "Q0.10"),
            ("Monedas", 0.05, "Q0.05")
        ]

        # Conexión a la base de datos
        try:
            self.db_connection = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",
                database="bdhidrocolon"
            )
            self.cursor = self.db_connection.cursor()

            # Verificar si las tablas de cierre existen, sino crearlas
            self.crear_tablas_cierre()
            self.verificar_tabla_cierre()
            self.verificar_y_reparar_tabla_cierre_neto()

        except Exception as err:
            QMessageBox.critical(self, "Error de base de datos",
                                 f"No se pudo conectar a la base de datos: {err}")
            self.db_connection = None
            self.cursor = None

        self.initUI()
        # Cargar datos automáticamente si hay conexión a la BD
        if self.db_connection:
            self.obtener_datos_db()

    def capitalizar_texto(self, texto):
        """
        Función auxiliar para capitalizar correctamente los textos
        - Primera letra de cada frase en mayúscula
        - Resto en minúsculas
        - Respeta nombres propios básicos
        """
        if not texto:
            return ""

        # Convertir a string si no lo es
        texto = str(texto)

        # Casos especiales que deben mantenerse en mayúsculas
        palabras_especiales = ['ID', 'PDF', 'POS', 'BD', 'CEO', 'CFO', 'CTO', 'IV', 'III', 'II', 'VI', 'VII', 'VIII',
                               'IX', 'X']

        # Dividir en palabras
        palabras = texto.split()
        resultado = []

        for palabra in palabras:
            # Si es una palabra especial, mantenerla en mayúsculas
            if palabra.upper() in palabras_especiales:
                resultado.append(palabra.upper())
            # Si es la primera palabra, capitalizar
            elif len(resultado) == 0:
                resultado.append(palabra.capitalize())
            # Si es después de punto, capitalizar
            elif len(resultado) > 0 and resultado[-1].endswith('.'):
                resultado.append(palabra.capitalize())
            # Si contiene números (como códigos), mantener como está
            elif any(char.isdigit() for char in palabra):
                resultado.append(palabra)
            # Resto en minúsculas
            else:
                resultado.append(palabra.lower())

        return ' '.join(resultado)

    def formatear_nombre_producto(self, nombre):
        """Formatea específicamente nombres de productos"""
        if not nombre:
            return ""

        # Remover emojis de ajuste si existen
        nombre_limpio = str(nombre).replace("🔧 AJUSTE:", "").strip()

        # Capitalizar correctamente
        return self.capitalizar_texto(nombre_limpio)

    def crear_tablas_cierre(self):
        """Crear las tablas para cierre crudo y neto si no existen"""
        try:
            # Tabla cierre_crudo
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS cierre_crudo (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fecha DATE NOT NULL,
                    venta_neta DECIMAL(10,2) NOT NULL,
                    gastos DECIMAL(10,2) NOT NULL,
                    visa DECIMAL(10,2) NOT NULL,
                    comision_dra DECIMAL(10,2) NOT NULL,
                    impuestos_efectivo DECIMAL(10,2) NOT NULL,
                    impuestos_transferencia DECIMAL(10,2) NOT NULL,
                    impuestos_visa DECIMAL(10,2) NOT NULL,
                    totales DECIMAL(10,2) NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabla cierre_neto
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS cierre_neto (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fecha DATE NOT NULL,
                    efectivo_neto DECIMAL(10,2) NOT NULL,
                    tarjeta_neto DECIMAL(10,2) NOT NULL,
                    transferencia_neto DECIMAL(10,2) NOT NULL,
                    total_ingresos_netos DECIMAL(10,2) NOT NULL,
                    total_gastos DECIMAL(10,2) NOT NULL,
                    total_impuestos DECIMAL(10,2) NOT NULL,
                    comisiones DECIMAL(10,2) NOT NULL,
                    total_deducciones DECIMAL(10,2) NOT NULL,
                    resultado_neto DECIMAL(10,2) NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.db_connection.commit()
        except Exception as err:
            QMessageBox.critical(self, "Error de base de datos",
                                 f"Error al crear tablas de cierre: {err}")

    def initUI(self):
        """Configurar la interfaz de usuario - VERSIÓN CORREGIDA"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Título principal
        title_label = QLabel("Sistema de Cierre")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # SECCIÓN 1: CAMPOS DE ENTRADA
        self.crear_seccion_entrada(main_layout)

        # SECCIÓN 2: BOTONES DE ACCIÓN
        self.crear_botones_accion(main_layout)

        # SECCIÓN 3: TABLAS DE RESULTADOS
        self.crear_seccion_resultados(main_layout)

        # SECCIÓN 4: BOTONES PRINCIPALES
        self.crear_botones_principales(main_layout)

    def crear_botones_principales(self, main_layout):
        """Crea los botones principales (Guardar, Exportar, Cierre por Turno)"""

        # Botones principales
        button_layout = QHBoxLayout()

        self.btn_guardar = QPushButton("💾 Guardar en Base de Datos")
        self.btn_guardar.clicked.connect(self.guardar_cierre_completo)
        self.btn_guardar.setStyleSheet("QPushButton { background-color: #17a2b8; color: white; padding: 10px; }")
        button_layout.addWidget(self.btn_guardar)

        self.btn_exportar = QPushButton("📄 Exportar Reporte")
        self.btn_exportar.clicked.connect(self.exportar_reporte)
        self.btn_exportar.setStyleSheet("QPushButton { background-color: #ffc107; color: black; padding: 10px; }")
        button_layout.addWidget(self.btn_exportar)

        # NUEVO: Botón de Cierre por Turno
        self.btn_cierre_turno = QPushButton("🔄 Cierre por Turno")
        self.btn_cierre_turno.clicked.connect(self.ejecutar_cierre_por_turno)
        self.btn_cierre_turno.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        button_layout.addWidget(self.btn_cierre_turno)

        main_layout.addLayout(button_layout)

    def setup_cierre_principal(self):
        """Configura la interfaz principal de cierre (combinando funcionalidades)"""

        # Widget central para todo el contenido
        central_widget = self.centralWidget()
        main_layout = QVBoxLayout(central_widget)

        # Título principal
        title_label = QLabel("Sistema de Cierre")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # SECCIÓN 1: CAMPOS DE ENTRADA (antes estaban en cierre crudo)
        self.crear_seccion_entrada(main_layout)

        # SECCIÓN 2: BOTONES DE ACCIÓN
        self.crear_botones_accion(main_layout)

        # SECCIÓN 3: TABLAS DE RESULTADOS (antes estaban en cierre neto)
        self.crear_seccion_resultados(main_layout)

        # SECCIÓN 4: CONFIRMACIÓN Y BOTONES PRINCIPALES
        self.crear_seccion_confirmacion_y_botones_principales(main_layout)

    def crear_seccion_resultados(self, main_layout):
        """Crea las tablas de resultados"""

        # Layout horizontal para las tablas
        tables_layout = QHBoxLayout()

        # Layout izquierdo para tablas principales
        left_tables_layout = QVBoxLayout()

        # Tabla Ingresos Netos
        ingresos_label = QLabel("Ingresos Netos")
        ingresos_label.setFont(QFont("Arial", 12, QFont.Bold))
        ingresos_label.setAlignment(Qt.AlignCenter)
        left_tables_layout.addWidget(ingresos_label)

        self.tabla_ingresos_netos = QTableWidget()
        self.tabla_ingresos_netos.setColumnCount(2)
        self.tabla_ingresos_netos.setHorizontalHeaderLabels(["Concepto", "Valor"])
        self.tabla_ingresos_netos.setRowCount(4)

        conceptos_ingresos = ["Efectivo Neto", "Tarjeta Neto", "Transferencia Neto", "Total Ingresos Netos"]
        for i, concepto in enumerate(conceptos_ingresos):
            self.tabla_ingresos_netos.setItem(i, 0, QTableWidgetItem(concepto))
            valor_item = QTableWidgetItem("0.00")
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla_ingresos_netos.setItem(i, 1, valor_item)

        self.tabla_ingresos_netos.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_ingresos_netos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_ingresos_netos.verticalHeader().setVisible(False)
        self.tabla_ingresos_netos.setEditTriggers(QTableWidget.NoEditTriggers)
        left_tables_layout.addWidget(self.tabla_ingresos_netos)

        # Tabla Gastos y Deducciones
        deducciones_label = QLabel("Gastos y Deducciones")
        deducciones_label.setFont(QFont("Arial", 12, QFont.Bold))
        deducciones_label.setAlignment(Qt.AlignCenter)
        left_tables_layout.addWidget(deducciones_label)

        self.tabla_deducciones = QTableWidget()
        self.tabla_deducciones.setColumnCount(2)
        self.tabla_deducciones.setHorizontalHeaderLabels(["Concepto", "Valor"])
        self.tabla_deducciones.setRowCount(5)

        conceptos_deducciones = ["Total Gastos", "Total Impuestos", "Comisiones Bancarias", "Comisiones",
                                 "Total Deducciones"]
        for i, concepto in enumerate(conceptos_deducciones):
            self.tabla_deducciones.setItem(i, 0, QTableWidgetItem(concepto))
            valor_item = QTableWidgetItem("0.00")
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla_deducciones.setItem(i, 1, valor_item)

        self.tabla_deducciones.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_deducciones.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_deducciones.verticalHeader().setVisible(False)
        self.tabla_deducciones.setEditTriggers(QTableWidget.NoEditTriggers)
        left_tables_layout.addWidget(self.tabla_deducciones)

        # Tabla Resultado Final
        resultado_label = QLabel("Resultado Final")
        resultado_label.setFont(QFont("Arial", 12, QFont.Bold))
        resultado_label.setAlignment(Qt.AlignCenter)
        left_tables_layout.addWidget(resultado_label)

        self.tabla_resultado_final = QTableWidget()
        self.tabla_resultado_final.setColumnCount(2)
        self.tabla_resultado_final.setHorizontalHeaderLabels(["Concepto", "Valor"])
        self.tabla_resultado_final.setRowCount(3)

        conceptos_resultado = ["Total a depositar ventas", "Total a depositar impuestos", "Total"]
        for i, concepto in enumerate(conceptos_resultado):
            self.tabla_resultado_final.setItem(i, 0, QTableWidgetItem(concepto))
            valor_item = QTableWidgetItem("0.00")
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla_resultado_final.setItem(i, 1, valor_item)
            # Hacer bold el texto
            self.tabla_resultado_final.item(i, 0).setFont(QFont("Arial", 10, QFont.Bold))
            self.tabla_resultado_final.item(i, 1).setFont(QFont("Arial", 10, QFont.Bold))

        self.tabla_resultado_final.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_resultado_final.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_resultado_final.verticalHeader().setVisible(False)
        self.tabla_resultado_final.setEditTriggers(QTableWidget.NoEditTriggers)
        left_tables_layout.addWidget(self.tabla_resultado_final)

        tables_layout.addLayout(left_tables_layout)

        # Panel de confirmación a la derecha (más ancho)
        self.crear_panel_confirmacion(tables_layout)

        main_layout.addLayout(tables_layout)

    def crear_panel_confirmacion(self, parent_layout):
        """Crea el panel de confirmación de dinero físico - ORIGINAL"""

        confirmacion_frame = QFrame()
        confirmacion_frame.setFrameShape(QFrame.StyledPanel)
        confirmacion_frame.setMaximumWidth(300)
        confirmacion_layout = QVBoxLayout(confirmacion_frame)

        # Título
        confirmacion_title = QLabel("Confirmación de Dinero Físico")
        confirmacion_title.setFont(QFont("Arial", 12, QFont.Bold))
        confirmacion_title.setAlignment(Qt.AlignCenter)
        confirmacion_title.setWordWrap(True)
        confirmacion_layout.addWidget(confirmacion_title)

        # NUEVO: Botón para abrir ventana de denominaciones
        btn_abrir_denominaciones = QPushButton("💰 Ingresar Efectivo Físico")
        btn_abrir_denominaciones.clicked.connect(self.abrir_ventana_denominaciones)
        btn_abrir_denominaciones.setStyleSheet(
            "QPushButton { background-color: #28a745; color: white; font-weight: bold; padding: 10px; border-radius: 5px; }")
        confirmacion_layout.addWidget(btn_abrir_denominaciones)

        # Campo para mostrar el total (solo lectura)
        self.lbl_efectivo_fisico_total = QLabel("Efectivo físico: Q0.00")
        self.lbl_efectivo_fisico_total.setStyleSheet(
            "background-color: #e9ecef; padding: 8px; border-radius: 3px; font-weight: bold;")
        confirmacion_layout.addWidget(self.lbl_efectivo_fisico_total)

        # Campo de cheques
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Cheques:"), 0, 0)
        self.txt_cheques_fisicos = QLineEdit("0.00")
        self.txt_cheques_fisicos.setValidator(QDoubleValidator())
        self.txt_cheques_fisicos.textChanged.connect(self.verificar_cuadre)
        form_layout.addWidget(self.txt_cheques_fisicos, 0, 1)
        confirmacion_layout.addLayout(form_layout)

        # Tabla de verificación
        self.tabla_verificacion = QTableWidget()
        self.tabla_verificacion.setColumnCount(2)
        self.tabla_verificacion.setHorizontalHeaderLabels(["Concepto", "Valor"])
        self.tabla_verificacion.setRowCount(4)

        conceptos_verificacion = ["Efectivo Calculado", "Efectivo Físico", "Diferencia Efectivo", "Estado del Cuadre"]
        for i, concepto in enumerate(conceptos_verificacion):
            self.tabla_verificacion.setItem(i, 0, QTableWidgetItem(concepto))
            valor_item = QTableWidgetItem("0.00")
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla_verificacion.setItem(i, 1, valor_item)

        self.tabla_verificacion.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_verificacion.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_verificacion.verticalHeader().setVisible(False)
        self.tabla_verificacion.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_verificacion.setMaximumHeight(150)
        confirmacion_layout.addWidget(self.tabla_verificacion)

        # Indicador de estado
        self.lbl_estado_cuadre = QLabel("⚠️ Sin verificar")
        self.lbl_estado_cuadre.setAlignment(Qt.AlignCenter)
        self.lbl_estado_cuadre.setFont(QFont("Arial", 10, QFont.Bold))
        self.lbl_estado_cuadre.setStyleSheet(
            "background-color: #FFF3CD; border: 1px solid #FFEAA7; padding: 8px; border-radius: 4px;")
        confirmacion_layout.addWidget(self.lbl_estado_cuadre)

        # Botón de confirmación
        self.btn_confirmar_cuadre = QPushButton("Confirmar Cuadre")
        self.btn_confirmar_cuadre.clicked.connect(self.confirmar_cuadre_final)
        self.btn_confirmar_cuadre.setEnabled(False)
        confirmacion_layout.addWidget(self.btn_confirmar_cuadre)

        parent_layout.addWidget(confirmacion_frame)

    def limpiar_tabla_efectivo_fisico(self):
        """Limpiar toda la tabla de efectivo físico"""
        for row in range(self.tabla_efectivo_fisico.rowCount()):
            cantidad_item = self.tabla_efectivo_fisico.item(row, 0)
            total_item = self.tabla_efectivo_fisico.item(row, 2)

            cantidad_item.setText("0")
            total_item.setText("0.00")

        self.actualizar_total_efectivo_general()

    def calcular_total_efectivo_fisico(self, item):
        """Calcular el total de efectivo físico cuando cambia una cantidad"""
        try:
            if item.column() == 0:  # Solo si cambió la cantidad
                row = item.row()

                # Obtener cantidad ingresada
                cantidad_text = item.text().strip()
                if not cantidad_text:
                    cantidad = 0
                else:
                    cantidad = int(cantidad_text)

                # Obtener valor unitario
                valor_unitario = self.denominaciones[row][1]

                # Calcular total para esta fila
                total_fila = cantidad * valor_unitario

                # Actualizar columna total
                total_item = self.tabla_efectivo_fisico.item(row, 2)
                total_item.setText(f"{total_fila:.2f}")

                # Actualizar total general
                self.actualizar_total_efectivo_general()

        except (ValueError, TypeError):
            # Si hay error en la conversión, poner 0
            item.setText("0")

    def actualizar_total_efectivo_general(self):
        """Actualizar el total general de efectivo físico"""
        total = 0.0

        for row in range(self.tabla_efectivo_fisico.rowCount()):
            total_item = self.tabla_efectivo_fisico.item(row, 2)
            if total_item:
                total_text = total_item.text().replace(',', '')
                try:
                    total += float(total_text)
                except ValueError:
                    pass

        # Actualizar label del total
        self.lbl_total_efectivo_fisico.setText(f"TOTAL EFECTIVO: Q{total:.2f}")

        # Actualizar también en la tabla de verificación
        if hasattr(self, 'tabla_verificacion'):
            self.tabla_verificacion.item(1, 1).setText(f"{total:.2f}")

        # Verificar cuadre automáticamente
        self.verificar_cuadre()

    def crear_seccion_confirmacion_y_botones_principales(self, main_layout):
        """Crea los botones principales (Guardar, Exportar, Cierre por Turno)"""

        # Botones principales
        button_layout = QHBoxLayout()

        self.btn_guardar = QPushButton("💾 Guardar en Base de Datos")
        self.btn_guardar.clicked.connect(self.guardar_cierre_completo)
        self.btn_guardar.setStyleSheet("QPushButton { background-color: #17a2b8; color: white; padding: 10px; }")
        button_layout.addWidget(self.btn_guardar)

        self.btn_exportar = QPushButton("📄 Exportar Reporte")
        self.btn_exportar.clicked.connect(self.exportar_reporte)
        self.btn_exportar.setStyleSheet("QPushButton { background-color: #ffc107; color: black; padding: 10px; }")
        button_layout.addWidget(self.btn_exportar)

        # NUEVO: Botón de Cierre por Turno
        self.btn_cierre_turno = QPushButton("🔄 Cierre por Turno")
        self.btn_cierre_turno.clicked.connect(self.ejecutar_cierre_por_turno)
        self.btn_cierre_turno.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        button_layout.addWidget(self.btn_cierre_turno)

        main_layout.addLayout(button_layout)

    def guardar_cierre_completo(self):
        """Guarda el cierre completo en BD y REINICIA el sistema"""
        try:
            print("💾 === INICIANDO GUARDADO Y REINICIO ===")

            # PASO 1: Verificar que hay datos para guardar
            if not hasattr(self, 'valores_crudo') or not hasattr(self, 'valores_neto'):
                QMessageBox.warning(self, "Error", "Primero debe calcular el cierre antes de guardar.")
                return False

            # PASO 2: Guardar cierre crudo
            print("💾 Guardando cierre crudo...")
            if not self.guardar_cierre_crudo():
                return False

            # PASO 3: Guardar cierre neto
            print("💾 Guardando cierre neto...")
            if not self.guardar_cierre_neto():
                return False

            # PASO 4: Mostrar confirmación de guardado
            QMessageBox.information(
                self,
                "✅ Cierre Guardado",
                """📊 ¡Cierre guardado exitosamente en la base de datos!

    🔄 A continuación el sistema se reiniciará completamente."""
            )

            # PASO 5: REINICIAR SISTEMA COMPLETO
            print("🔄 Reiniciando sistema...")
            if self.reiniciar_sistema_completo():
                print("✅ === GUARDADO Y REINICIO COMPLETADO ===")
                return True
            else:
                QMessageBox.warning(
                    self,
                    "⚠️ Advertencia",
                    "El cierre se guardó correctamente, pero hubo problemas al reiniciar el sistema.\n\nPuede reiniciar manualmente presionando 'Limpiar'."
                )
                return True

        except Exception as e:
            print(f"❌ Error en guardado y reinicio: {e}")
            QMessageBox.critical(self, "Error", f"Error al guardar y reiniciar: {e}")
            return False

    def crear_botones_accion(self, main_layout):
        """Crea los botones de acción (Cargar Datos, Calcular, Limpiar)"""

        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)

        # Botón Cargar Datos
        self.btn_cargar_datos = QPushButton("📁 Cargar Datos")
        self.btn_cargar_datos.clicked.connect(self.obtener_datos_db)
        self.btn_cargar_datos.setStyleSheet("QPushButton { background-color: #007bff; color: white; padding: 8px; }")
        button_layout.addWidget(self.btn_cargar_datos)

        # Botón Calcular
        self.btn_calcular = QPushButton("🧮 Calcular Cierre")
        self.btn_calcular.clicked.connect(self.calcular_cierre_completo)
        self.btn_calcular.setStyleSheet("QPushButton { background-color: #28a745; color: white; padding: 8px; }")
        button_layout.addWidget(self.btn_calcular)

        # Botón Limpiar
        self.btn_limpiar = QPushButton("🗑️ Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_todo)
        self.btn_limpiar.setStyleSheet("QPushButton { background-color: #6c757d; color: white; padding: 8px; }")
        button_layout.addWidget(self.btn_limpiar)

        main_layout.addWidget(button_frame)

    def limpiar_todo(self):
        """LIMPIA TODO EL SISTEMA COMPLETAMENTE - VERSIÓN QUE SÍ FUNCIONA"""
        try:
            print("🧹 === LIMPIANDO TODO EL SISTEMA ===")

            # 1. LIMPIAR TODOS LOS CAMPOS DE TEXTO
            self.txt_ingreso_efectivo.clear()
            self.txt_ingreso_efectivo.setText("0.00")

            self.txt_ingreso_tarjeta.clear()
            self.txt_ingreso_tarjeta.setText("0.00")

            self.txt_ingreso_transferencia.clear()
            self.txt_ingreso_transferencia.setText("0.00")

            self.txt_total_gastos.clear()
            self.txt_total_gastos.setText("0.00")

            self.txt_total_real.clear()
            self.txt_total_real.setText("0.00")

            self.txt_total_banco.clear()
            self.txt_total_banco.setText("0.00")

            # 2. DESBLOQUEAR TODOS LOS CAMPOS
            self.txt_ingreso_efectivo.setReadOnly(False)
            self.txt_ingreso_tarjeta.setReadOnly(False)
            self.txt_ingreso_transferencia.setReadOnly(False)
            self.txt_total_gastos.setReadOnly(False)
            self.txt_total_real.setReadOnly(False)
            self.txt_total_banco.setReadOnly(False)

            # 3. RESTAURAR ESTILO NORMAL A LOS CAMPOS
            estilo_normal = """
                QLineEdit {
                    background-color: white;
                    border: 1px solid #cccccc;
                    color: black;
                    padding: 5px;
                }
            """
            self.txt_ingreso_efectivo.setStyleSheet(estilo_normal)
            self.txt_ingreso_tarjeta.setStyleSheet(estilo_normal)
            self.txt_ingreso_transferencia.setStyleSheet(estilo_normal)
            self.txt_total_gastos.setStyleSheet(estilo_normal)
            self.txt_total_real.setStyleSheet(estilo_normal)
            self.txt_total_banco.setStyleSheet(estilo_normal)

            # 4. LIMPIAR TABLA DE INGRESOS NETOS
            if hasattr(self, 'tabla_ingresos_netos'):
                for row in range(self.tabla_ingresos_netos.rowCount()):
                    if self.tabla_ingresos_netos.item(row, 1):
                        self.tabla_ingresos_netos.item(row, 1).setText("0.00")

            # 5. LIMPIAR TABLA DE DEDUCCIONES
            if hasattr(self, 'tabla_deducciones'):
                for row in range(self.tabla_deducciones.rowCount()):
                    if self.tabla_deducciones.item(row, 1):
                        self.tabla_deducciones.item(row, 1).setText("0.00")

            # 6. LIMPIAR TABLA DE RESULTADO FINAL
            if hasattr(self, 'tabla_resultado_final'):
                for row in range(self.tabla_resultado_final.rowCount()):
                    if self.tabla_resultado_final.item(row, 1):
                        self.tabla_resultado_final.item(row, 1).setText("0.00")
                        # Quitar colores
                        self.tabla_resultado_final.item(row, 1).setForeground(Qt.black)

            # 7. LIMPIAR CONFIRMACIÓN DE DINERO FÍSICO
            if hasattr(self, 'txt_efectivo_fisico'):
                self.txt_efectivo_fisico.clear()
                self.txt_efectivo_fisico.setText("0.00")

            if hasattr(self, 'txt_cheques_fisicos'):
                self.txt_cheques_fisicos.clear()
                self.txt_cheques_fisicos.setText("0.00")

            # 8. LIMPIAR TABLA DE VERIFICACIÓN
            if hasattr(self, 'tabla_verificacion'):
                try:
                    if self.tabla_verificacion.item(0, 1):
                        self.tabla_verificacion.item(0, 1).setText("0.00")  # Efectivo Calculado
                    if self.tabla_verificacion.item(1, 1):
                        self.tabla_verificacion.item(1, 1).setText("0.00")  # Efectivo Físico
                    if self.tabla_verificacion.item(2, 1):
                        self.tabla_verificacion.item(2, 1).setText("0.00")  # Diferencia
                    if self.tabla_verificacion.item(3, 1):
                        self.tabla_verificacion.item(3, 1).setText("❌ NO CUADRA")  # Estado
                except:
                    pass

            # 9. RESETEAR ESTADO DE CUADRE
            if hasattr(self, 'lbl_estado_cuadre'):
                self.lbl_estado_cuadre.setText("❌ NO CUADRA")
                self.lbl_estado_cuadre.setStyleSheet(
                    "background-color: #ffebee; color: #c62828; padding: 5px; border-radius: 3px;")

            # 10. RESETEAR BOTÓN DE CONFIRMACIÓN
            if hasattr(self, 'btn_confirmar_cuadre'):
                self.btn_confirmar_cuadre.setText("Confirmar Cuadre")
                self.btn_confirmar_cuadre.setEnabled(False)

            # 11. LIMPIAR VARIABLES EN MEMORIA
            variables_a_eliminar = [
                'valores_crudo', 'valores_neto', 'efectivo_inicial',
                'ventas_efectivo', 'ventas_tarjeta', 'ventas_transferencia',
                'tarjeta_inicial', 'comision_dra_valor', '_ejecutando_cierre_turno'
            ]

            for var in variables_a_eliminar:
                if hasattr(self, var):
                    delattr(self, var)
                    print(f"  ✅ {var} eliminado")

            # 12. MOSTRAR CONFIRMACIÓN
            QMessageBox.information(
                self,
                "✅ Sistema Limpiado",
                "🧹 ¡Todo el sistema ha sido limpiado!\n\nTodos los campos están en 0.\nListo para nuevo turno."
            )

            print("✅ === SISTEMA LIMPIADO COMPLETAMENTE ===")

        except Exception as e:
            print(f"❌ Error al limpiar: {e}")
            QMessageBox.critical(self, "Error", f"Error al limpiar: {e}")
            import traceback
            traceback.print_exc()

    def verificar_estado_sistema(self):
        """Verifica el estado actual del sistema para debug"""
        try:
            print("\n🔍 === VERIFICACIÓN DEL ESTADO DEL SISTEMA ===")

            # Verificar valores en campos
            print("📝 Valores en campos:")
            print(f"   • Efectivo: {self.txt_ingreso_efectivo.text()}")
            print(f"   • Tarjeta: {self.txt_ingreso_tarjeta.text()}")
            print(f"   • Transferencia: {self.txt_ingreso_transferencia.text()}")
            print(f"   • Gastos: {self.txt_total_gastos.text()}")

            # Verificar variables en memoria
            print("💭 Variables en memoria:")
            print(f"   • valores_crudo: {'SÍ' if hasattr(self, 'valores_crudo') else 'NO'}")
            print(f"   • valores_neto: {'SÍ' if hasattr(self, 'valores_neto') else 'NO'}")
            print(f"   • efectivo_inicial: {'SÍ' if hasattr(self, 'efectivo_inicial') else 'NO'}")

            # Verificar estado de campos
            print("🔒 Estado de campos:")
            print(f"   • Efectivo readonly: {self.txt_ingreso_efectivo.isReadOnly()}")
            print(f"   • Tarjeta readonly: {self.txt_ingreso_tarjeta.isReadOnly()}")

            # Verificar tablas
            print("📊 Estado de tablas:")
            if hasattr(self, 'tabla_ingresos_netos'):
                valor_efectivo = self.tabla_ingresos_netos.item(0, 1).text() if self.tabla_ingresos_netos.item(0,
                                                                                                               1) else "N/A"
                print(f"   • tabla_ingresos_netos[0,1]: {valor_efectivo}")

            if hasattr(self, 'tabla_deducciones'):
                valor_gastos = self.tabla_deducciones.item(0, 1).text() if self.tabla_deducciones.item(0, 1) else "N/A"
                print(f"   • tabla_deducciones[0,1]: {valor_gastos}")

            print("=" * 50)

        except Exception as e:
            print(f"❌ Error en verificación: {e}")

    def calcular_cierre_completo(self):
        """FUNCIÓN CALCULAR CIERRE COMPLETO - CORREGIDA según especificaciones del usuario"""
        try:
            print("🔄 Iniciando cálculo de cierre completo...")

            # ✅ OBTENER DATOS DE ENTRADA
            ingreso_efectivo = float(self.txt_ingreso_efectivo.text() or '0')  # 101.0 (total)
            ingreso_tarjeta = float(self.txt_ingreso_tarjeta.text() or '0')  # 600.0
            ingreso_transferencia = float(self.txt_ingreso_transferencia.text() or '0')  # 100.0
            total_gastos = float(self.txt_total_gastos.text() or '0')  # 10.0
            total_real = float(self.txt_total_real.text() or '0')  # 600.0
            total_banco = float(self.txt_total_banco.text() or '0')  # 282.0

            # ✅ SEPARAR VENTAS DEL DINERO INICIAL - CORREGIDO
            efectivo_inicial = getattr(self, 'efectivo_inicial', 1.0)  # Usuario dice que tenía 1 quetzal inicial
            ventas_efectivo = ingreso_efectivo - efectivo_inicial  # 101 - 1 = 100 (solo ventas)
            ventas_tarjeta = ingreso_tarjeta  # 600 (solo ventas)
            ventas_transferencia = ingreso_transferencia  # 100 (solo ventas)

            print(f"📊 Valores separados:")
            print(f"   - Efectivo inicial: Q{efectivo_inicial:.2f}")
            print(f"   - Ventas efectivo: Q{ventas_efectivo:.2f}")
            print(f"   - Ventas tarjeta: Q{ventas_tarjeta:.2f}")
            print(f"   - Ventas transferencia: Q{ventas_transferencia:.2f}")

            # ✅ CALCULAR VENTA NETA (solo suma de ventas sin impuestos)
            venta_neta = ventas_efectivo + ventas_tarjeta + ventas_transferencia  # 100 + 600 + 100 = 800

            # ✅ OBTENER COMISIONES DE DOCTORES (de la base de datos)
            comision_dra = getattr(self, 'comision_dra_valor', 0.0)  # Valor obtenido de BD

            # ✅ CALCULAR IMPUESTOS PARA CIERRE CRUDO (solo para referencia)
            impuestos_efectivo_crudo = ventas_efectivo * 0.16  # 100 * 0.16 = 16.00
            impuestos_tarjeta_crudo = ventas_tarjeta * 0.06  # 600 * 0.06 = 36.00 (solo POS)
            impuestos_transferencia_crudo = ventas_transferencia * 0.16  # 100 * 0.16 = 16.00

            total_impuestos_crudo = impuestos_efectivo_crudo + impuestos_tarjeta_crudo + impuestos_transferencia_crudo

            print(f"📊 Impuestos para cierre crudo:")
            print(f"   - Impuestos efectivo (16%): Q{impuestos_efectivo_crudo:.2f}")
            print(f"   - Impuestos tarjeta POS (6%): Q{impuestos_tarjeta_crudo:.2f}")
            print(f"   - Impuestos transferencia (16%): Q{impuestos_transferencia_crudo:.2f}")
            print(f"   - TOTAL IMPUESTOS CRUDO: Q{total_impuestos_crudo:.2f}")

            # ✅ CALCULAR TOTALES CON IMPUESTOS
            totales_con_impuestos = venta_neta + total_impuestos_crudo

            print(f"📊 Cálculos principales:")
            print(f"   - Venta neta (solo ventas): Q{venta_neta:.2f}")
            print(f"   - Gastos: Q{total_gastos:.2f}")
            print(f"   - TOTALES CON IMPUESTOS: Q{totales_con_impuestos:.2f}")

            # ✅ GUARDAR VALORES PARA CÁLCULO NETO
            self.valores_crudo = {
                'venta_neta': venta_neta,
                'gastos': total_gastos,
                'visa': ventas_tarjeta,
                'comision_dra': comision_dra,
                'impuestos_efectivo': impuestos_efectivo_crudo,
                'impuestos_transferencia': impuestos_transferencia_crudo,
                'impuestos_visa': impuestos_tarjeta_crudo,
                'totales': totales_con_impuestos,
                # Valores separados para cálculo neto
                'efectivo_inicial': efectivo_inicial,
                'ventas_efectivo': ventas_efectivo,  # 100
                'ventas_tarjeta': ventas_tarjeta,  # 600
                'ventas_transferencia': ventas_transferencia,  # 100
                'total_impuestos_crudo': total_impuestos_crudo
            }

            # ✅ LLAMAR AL CÁLCULO NETO
            self.calcular_neto()

            print("✅ Cálculo de cierre completado")
            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            QMessageBox.critical(self, "Error", f"Error al calcular: {e}")
            return False

    def actualizar_tablas_resultados(self):
        """FUNCIÓN ACTUALIZAR TABLAS - CORREGIDA según especificaciones del usuario"""

        if not hasattr(self, 'valores_neto'):
            return

        # ✅ ACTUALIZAR TABLA DE INGRESOS NETOS
        valores_ingresos = [
            self.valores_neto['efectivo_neto'],  # 84.00
            self.valores_neto['tarjeta_neto'],  # 473.76
            self.valores_neto['transferencia_neto'],  # 84.00
            self.valores_neto['total_ingresos_netos']  # 641.76
        ]

        for i, valor in enumerate(valores_ingresos):
            self.tabla_ingresos_netos.item(i, 1).setText(f"{valor:.2f}")

        # ✅ ACTUALIZAR TABLA DE GASTOS Y DEDUCCIONES
        valores_deducciones = [
            self.valores_neto['total_gastos'],  # 10.00
            self.valores_neto['total_impuestos'],  # 158.24
            self.valores_neto['comisiones_bancarias'],  # 36.00
            self.valores_neto['comisiones'],  # 0.00
            self.valores_neto['total_deducciones']  # 204.24
        ]

        for i, valor in enumerate(valores_deducciones):
            self.tabla_deducciones.item(i, 1).setText(f"{valor:.2f}")

        # ✅ ACTUALIZAR TABLA DE RESULTADO FINAL
        # Estos son los valores que aparecen en la sección "Resultado Final"
        total_depositar_ventas = self.valores_neto['total_depositar_ventas']  # 595.76
        total_depositar_impuestos = self.valores_neto['total_depositar_impuestos']  # 158.24
        total_final = self.valores_neto['total_final']  # 754.00

        valores_resultado = [
            total_depositar_ventas,  # Total a depositar ventas
            total_depositar_impuestos,  # Total a depositar impuestos
            total_final  # Total final
        ]

        for i, valor in enumerate(valores_resultado):
            self.tabla_resultado_final.item(i, 1).setText(f"{valor:.2f}")
            # Aplicar color verde
            self.tabla_resultado_final.item(i, 1).setForeground(Qt.darkGreen)

        print("✅ Tablas actualizadas correctamente:")
        print(f"   - Ingresos netos: {valores_ingresos}")
        print(f"   - Deducciones: {valores_deducciones}")
        print(f"   - Resultado final: {valores_resultado}")

    def crear_seccion_entrada(self, main_layout):
        """Crea la sección de campos de entrada de datos"""

        # Frame contenedor para los campos de entrada
        entrada_frame = QFrame()
        entrada_frame.setFrameShape(QFrame.StyledPanel)
        entrada_layout = QVBoxLayout(entrada_frame)

        # Título de sección
        entrada_title = QLabel("Datos de Entrada")
        entrada_title.setFont(QFont("Arial", 14, QFont.Bold))
        entrada_title.setAlignment(Qt.AlignCenter)
        entrada_layout.addWidget(entrada_title)

        # Layout de grid para los campos
        campos_layout = QGridLayout()

        # CAMPOS DE INGRESOS
        ingresos_label = QLabel("INGRESOS:")
        ingresos_label.setFont(QFont("Arial", 10, QFont.Bold))
        campos_layout.addWidget(ingresos_label, 0, 0, 1, 4)

        # Efectivo
        campos_layout.addWidget(QLabel("Efectivo:"), 1, 0)
        self.txt_ingreso_efectivo = QLineEdit()
        self.txt_ingreso_efectivo.setValidator(QDoubleValidator())
        campos_layout.addWidget(self.txt_ingreso_efectivo, 1, 1)

        # Tarjeta
        campos_layout.addWidget(QLabel("Tarjeta:"), 1, 2)
        self.txt_ingreso_tarjeta = QLineEdit()
        self.txt_ingreso_tarjeta.setValidator(QDoubleValidator())
        campos_layout.addWidget(self.txt_ingreso_tarjeta, 1, 3)

        # Transferencia
        campos_layout.addWidget(QLabel("Transferencia:"), 2, 0)
        self.txt_ingreso_transferencia = QLineEdit()
        self.txt_ingreso_transferencia.setValidator(QDoubleValidator())
        campos_layout.addWidget(self.txt_ingreso_transferencia, 2, 1)

        # CAMPOS DE GASTOS Y OTROS
        gastos_label = QLabel("GASTOS Y OTROS:")
        gastos_label.setFont(QFont("Arial", 10, QFont.Bold))
        campos_layout.addWidget(gastos_label, 3, 0, 1, 4)

        # Total Gastos
        campos_layout.addWidget(QLabel("Total Gastos:"), 4, 0)
        self.txt_total_gastos = QLineEdit()
        self.txt_total_gastos.setValidator(QDoubleValidator())
        campos_layout.addWidget(self.txt_total_gastos, 4, 1)

        # Total Real
        campos_layout.addWidget(QLabel("Total Real:"), 4, 2)
        self.txt_total_real = QLineEdit()
        self.txt_total_real.setValidator(QDoubleValidator())
        campos_layout.addWidget(self.txt_total_real, 4, 3)

        # Total Banco
        campos_layout.addWidget(QLabel("Total Banco:"), 5, 0)
        self.txt_total_banco = QLineEdit()
        self.txt_total_banco.setValidator(QDoubleValidator())
        campos_layout.addWidget(self.txt_total_banco, 5, 1)

        entrada_layout.addLayout(campos_layout)
        main_layout.addWidget(entrada_frame)

    def verificar_cuadre(self):
        """Verifica si el dinero físico cuadra con los cálculos - CORREGIDO"""
        try:
            if not hasattr(self, 'valores_neto'):
                return

            # Obtener valores ingresados por el usuario
            efectivo_fisico = self.obtener_total_efectivo_fisico()
            cheques_fisicos = float(self.txt_cheques_fisicos.text() or 0)

            # ✅ CORRECCIÓN: Efectivo calculado = inicial + ventas (SIN restar impuestos)
            efectivo_inicial = getattr(self, 'efectivo_inicial', 0.0)
            ventas_efectivo = getattr(self, 'ventas_efectivo', 0.0)
            efectivo_calculado = efectivo_inicial + ventas_efectivo  # NO restar impuestos aquí

            # Calcular diferencia
            diferencia_efectivo = efectivo_fisico - efectivo_calculado

            # Actualizar tabla de verificación
            self.tabla_verificacion.item(0, 1).setText(f"{efectivo_calculado:.2f}")  # Efectivo Calculado
            self.tabla_verificacion.item(1, 1).setText(f"{efectivo_fisico:.2f}")  # Efectivo Físico
            self.tabla_verificacion.item(2, 1).setText(f"{diferencia_efectivo:.2f}")  # Diferencia

            # Determinar estado del cuadre
            if abs(diferencia_efectivo) <= 0.01:  # Tolerar 1 centavo de diferencia
                estado = "✅ CUADRA"
                color_estado = "background-color: #D4EDDA; border: 1px solid #C3E6CB; color: #155724;"
                self.tabla_verificacion.item(2, 1).setForeground(Qt.darkGreen)
                self.btn_confirmar_cuadre.setEnabled(True)
            else:
                estado = "❌ NO CUADRA"
                color_estado = "background-color: #F8D7DA; border: 1px solid #F5C6CB; color: #721C24;"
                if diferencia_efectivo > 0:
                    self.tabla_verificacion.item(2, 1).setForeground(Qt.darkGreen)  # Sobra dinero
                else:
                    self.tabla_verificacion.item(2, 1).setForeground(Qt.red)  # Falta dinero
                self.btn_confirmar_cuadre.setEnabled(False)

            self.tabla_verificacion.item(3, 1).setText(estado)
            self.lbl_estado_cuadre.setText(estado)
            self.lbl_estado_cuadre.setStyleSheet(f"{color_estado} padding: 8px; border-radius: 4px; font-weight: bold;")

            print(f"🔍 Verificación de cuadre:")
            print(f"  • Efectivo inicial: Q{efectivo_inicial:.2f}")
            print(f"  • Ventas efectivo: Q{ventas_efectivo:.2f}")
            print(f"  • Efectivo calculado: Q{efectivo_calculado:.2f}")
            print(f"  • Efectivo físico: Q{efectivo_fisico:.2f}")
            print(f"  • Diferencia: Q{diferencia_efectivo:.2f}")
            print(f"  • Estado: {estado}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al verificar cuadre: {e}")

    def confirmar_cuadre_final(self):
        """Confirma que el cuadre ha sido verificado y es correcto"""
        try:
            diferencia = float(self.tabla_verificacion.item(2, 1).text().replace('Q', ''))
            efectivo_fisico = float(self.txt_efectivo_fisico.text() or 0)

            mensaje = f"""
            CONFIRMACIÓN DE CUADRE EXITOSA

            Efectivo físico: Q{efectivo_fisico:.2f}
            Diferencia: Q{diferencia:.2f}

            ¿Desea guardar esta confirmación?
            """

            respuesta = QMessageBox.question(self, "Confirmar Cuadre", mensaje,
                                             QMessageBox.Yes | QMessageBox.No)

            if respuesta == QMessageBox.Yes:
                # Aquí puedes guardar la confirmación en la base de datos si es necesario
                self.lbl_estado_cuadre.setText("✅ CONFIRMADO")
                self.lbl_estado_cuadre.setStyleSheet(
                    "background-color: #D1ECF1; border: 1px solid #BEE5EB; padding: 8px; border-radius: 4px; font-weight: bold;")

                QMessageBox.information(self, "Cuadre Confirmado",
                                        "El cuadre ha sido confirmado y registrado correctamente.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al confirmar cuadre: {e}")

    def obtener_datos_db(self):
        """FUNCIÓN CARGAR DATOS - CORREGIDA para obtener comisiones correctamente"""
        if not self.db_connection:
            QMessageBox.warning(self, "Advertencia", "No hay conexión a la base de datos")
            return

        try:
            # Obtener la fecha actual en formato YYYY-MM-DD
            import datetime
            fecha_actual = datetime.date.today().strftime('%Y-%m-%d')

            print(f"📅 Cargando datos para: {fecha_actual}")

            # =====================================================
            # 1. OBTENER EFECTIVO: INICIAL + VENTAS
            # =====================================================

            # Efectivo inicial del día (CORREGIDO - usar registro_caja)
            self.cursor.execute("""
                                SELECT SUM(total)
                                FROM registro_caja
                                WHERE DATE (fecha) = %s
                                """, (fecha_actual,))
            efectivo_data = self.cursor.fetchone()
            efectivo_inicial = float(efectivo_data[0]) if efectivo_data and efectivo_data[
                0] else 1.0  # Usuario dice 1 quetzal

            # Ventas en efectivo del día actual
            self.cursor.execute("""
                                SELECT SUM(efectivo)
                                FROM cierre
                                WHERE DATE (fecha) = %s
                                """, (fecha_actual,))
            ventas_efectivo_data = self.cursor.fetchone()
            ventas_efectivo = float(ventas_efectivo_data[0]) if ventas_efectivo_data and ventas_efectivo_data[
                0] else 0.00

            # Total efectivo
            total_efectivo = efectivo_inicial + ventas_efectivo
            self.txt_ingreso_efectivo.setText(str(total_efectivo))

            # =====================================================
            # 2. OBTENER TARJETA: INICIAL + VENTAS
            # =====================================================

            # Ingresos iniciales de tarjeta
            self.cursor.execute("""
                                SELECT total_real, total_bancos
                                FROM ingreso_tarjeta
                                WHERE DATE (fecha) = %s
                                    LIMIT 1
                                """, (fecha_actual,))
            tarjeta_data = self.cursor.fetchone()
            tarjeta_inicial = float(tarjeta_data[0]) if tarjeta_data and tarjeta_data[0] else 0.00
            total_banco = float(tarjeta_data[1]) if tarjeta_data and tarjeta_data[1] else 0.00

            # Ventas en tarjeta del día actual
            self.cursor.execute("""
                                SELECT SUM(tarjeta)
                                FROM cierre
                                WHERE DATE (fecha) = %s
                                """, (fecha_actual,))
            ventas_tarjeta_data = self.cursor.fetchone()
            ventas_tarjeta = float(ventas_tarjeta_data[0]) if ventas_tarjeta_data and ventas_tarjeta_data[0] else 0.00

            # Total tarjeta
            total_tarjeta = tarjeta_inicial + ventas_tarjeta
            self.txt_ingreso_tarjeta.setText(str(total_tarjeta))
            self.txt_total_real.setText(str(total_tarjeta))
            self.txt_total_banco.setText(str(total_banco))

            # =====================================================
            # 3. OBTENER TRANSFERENCIAS
            # =====================================================

            self.cursor.execute("""
                                SELECT total
                                FROM ingreso_transferencia
                                WHERE DATE (fecha) = %s
                                    LIMIT 1
                                """, (fecha_actual,))
            transferencia_data = self.cursor.fetchone()
            if transferencia_data:
                self.txt_ingreso_transferencia.setText(str(transferencia_data[0]) if transferencia_data[0] else "0.00")
            else:
                self.txt_ingreso_transferencia.setText("0.00")

            # =====================================================
            # 4. OBTENER GASTOS
            # =====================================================

            self.cursor.execute("""
                                SELECT SUM(monto)
                                FROM gastos
                                WHERE DATE (fecha) = %s
                                """, (fecha_actual,))
            gastos_data = self.cursor.fetchone()
            if gastos_data and gastos_data[0]:
                self.txt_total_gastos.setText(str(gastos_data[0]))
            else:
                self.txt_total_gastos.setText("0.00")

            # =====================================================
            # 5. OBTENER COMISIONES DE DOCTORES - CORREGIDO
            # =====================================================

            print("🔍 Buscando comisiones de doctores...")
            self.cursor.execute("""
                                SELECT SUM(monto)
                                FROM pagos_comisiones
                                WHERE DATE (fecha) = %s
                                """, (fecha_actual,))
            comision_data = self.cursor.fetchone()
            self.comision_dra_valor = float(comision_data[0]) if comision_data and comision_data[0] else 0.00

            print(f"💰 Comisión doctores encontrada: Q{self.comision_dra_valor:.2f}")

            # =====================================================
            # 6. GUARDAR SEPARACIÓN PARA CÁLCULOS
            # =====================================================

            self.efectivo_inicial = efectivo_inicial
            self.ventas_efectivo = ventas_efectivo
            self.tarjeta_inicial = tarjeta_inicial
            self.ventas_tarjeta = ventas_tarjeta

            print(f"📊 Datos separados:")
            print(f"   - Efectivo inicial: Q{efectivo_inicial:.2f}")
            print(f"   - Ventas efectivo: Q{ventas_efectivo:.2f}")
            print(f"   - Tarjeta inicial: Q{tarjeta_inicial:.2f}")
            print(f"   - Ventas tarjeta: Q{ventas_tarjeta:.2f}")
            print(f"   - Comisiones doctores: Q{self.comision_dra_valor:.2f}")

            # Comprobar si ya existe un cierre para hoy y cargar datos
            self.cargar_cierre_existente(fecha_actual)

            # =====================================================
            # 7. BLOQUEAR CAMPOS PARA SOLO LECTURA
            # =====================================================

            self.bloquear_campos_entrada()

            # Mostrar mensaje detallado
            mensaje_detalle = f"""📊 Datos cargados del {fecha_actual}:

    💰 EFECTIVO:
    • Inicial: Q{efectivo_inicial:.2f}
    • Ventas: Q{ventas_efectivo:.2f}
    • Total efectivo: Q{total_efectivo:.2f}

    💳 TARJETA:
    • Inicial: Q{tarjeta_inicial:.2f}
    • Ventas: Q{ventas_tarjeta:.2f}
    • Total tarjeta: Q{total_tarjeta:.2f}

    💸 GASTOS: Q{float(self.txt_total_gastos.text()):.2f}

    👩‍⚕️ COMISIONES DOCTORES: Q{self.comision_dra_valor:.2f}

    📋 NOTA: Los campos están bloqueados para evitar edición manual.
    Los impuestos se aplicarán SOLO a las ventas."""

            QMessageBox.information(self, "Datos cargados", mensaje_detalle)

            # Calcular automáticamente al cargar datos
            self.calcular_cierre_completo()

            print("✅ Datos cargados exitosamente")

        except Exception as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al obtener datos: {err}")

    def bloquear_campos_entrada(self):
        """Bloquea los campos de entrada para evitar edición manual"""
        try:
            # Hacer campos de solo lectura
            self.txt_ingreso_efectivo.setReadOnly(True)
            self.txt_ingreso_tarjeta.setReadOnly(True)
            self.txt_ingreso_transferencia.setReadOnly(True)
            self.txt_total_gastos.setReadOnly(True)
            self.txt_total_real.setReadOnly(True)
            self.txt_total_banco.setReadOnly(True)

            # Cambiar estilo para indicar que están bloqueados
            estilo_bloqueado = """
                QLineEdit {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    color: #666666;
                }
            """

            self.txt_ingreso_efectivo.setStyleSheet(estilo_bloqueado)
            self.txt_ingreso_tarjeta.setStyleSheet(estilo_bloqueado)
            self.txt_ingreso_transferencia.setStyleSheet(estilo_bloqueado)
            self.txt_total_gastos.setStyleSheet(estilo_bloqueado)
            self.txt_total_real.setStyleSheet(estilo_bloqueado)
            self.txt_total_banco.setStyleSheet(estilo_bloqueado)

            print("✅ Campos bloqueados correctamente")

        except Exception as e:
            print(f"Error al bloquear campos: {e}")

    def desbloquear_campos_entrada(self):
        """Desbloquea los campos de entrada (por si necesitas editarlos manualmente)"""
        try:
            # Hacer campos editables
            self.txt_ingreso_efectivo.setReadOnly(False)
            self.txt_ingreso_tarjeta.setReadOnly(False)
            self.txt_ingreso_transferencia.setReadOnly(False)
            self.txt_total_gastos.setReadOnly(False)
            self.txt_total_real.setReadOnly(False)
            self.txt_total_banco.setReadOnly(False)

            # Restaurar estilo normal
            estilo_normal = """
                QLineEdit {
                    background-color: white;
                    border: 1px solid #aaaaaa;
                    color: black;
                }
            """

            self.txt_ingreso_efectivo.setStyleSheet(estilo_normal)
            self.txt_ingreso_tarjeta.setStyleSheet(estilo_normal)
            self.txt_ingreso_transferencia.setStyleSheet(estilo_normal)
            self.txt_total_gastos.setStyleSheet(estilo_normal)
            self.txt_total_real.setStyleSheet(estilo_normal)
            self.txt_total_banco.setStyleSheet(estilo_normal)

            print("✅ Campos desbloqueados correctamente")

        except Exception as e:
            print(f"Error al desbloquear campos: {e}")

    def cargar_cierre_existente(self, fecha):
        """Cargar cierre existente para la fecha especificada si existe"""
        try:
            # Comprobar si existe cierre crudo para la fecha
            self.cursor.execute("""
                SELECT * FROM cierre_crudo WHERE fecha = %s LIMIT 1
            """, (fecha,))
            cierre_crudo = self.cursor.fetchone()

            if cierre_crudo:
                QMessageBox.information(self, "Cierre existente",
                                        f"Existe un cierre para el {fecha}. Puedes calcular de nuevo o ver los datos ya guardados.")

                # Opcionalmente, se podrían cargar datos del cierre existente en las tablas
                # Pero se ha decidido solo notificar al usuario para que pueda recalcular con datos actualizados

        except Exception as err:
            QMessageBox.warning(self, "Error", f"No se pudo verificar cierres existentes: {err}")

    def calcular_neto(self):
        """FUNCIÓN CALCULAR NETO - CORREGIDA PARA EVITAR ERRORES DE BD"""
        try:
            if not hasattr(self, 'valores_crudo'):
                QMessageBox.warning(self, "Advertencia", "Primero debe calcular el Cierre")
                return

            print("🧮 === INICIANDO CÁLCULO NETO CORREGIDO ===")

            # ✅ OBTENER VALORES BASE
            ventas_efectivo = self.valores_crudo.get('ventas_efectivo', 0)  # 100
            ventas_tarjeta = self.valores_crudo.get('ventas_tarjeta', 0)  # 600
            ventas_transferencia = self.valores_crudo.get('ventas_transferencia', 0)  # 100
            gastos = self.valores_crudo.get('gastos', 0)  # 10.0

            print(f"📊 Valores base:")
            print(f"   - Ventas efectivo: Q{ventas_efectivo:.2f}")
            print(f"   - Ventas tarjeta: Q{ventas_tarjeta:.2f}")
            print(f"   - Ventas transferencia: Q{ventas_transferencia:.2f}")
            print(f"   - Gastos: Q{gastos:.2f}")

            # ✅ CÁLCULO 1: EFECTIVO NETO = venta - 16%
            impuestos_efectivo = ventas_efectivo * 0.16  # 100 * 0.16 = 16.00
            efectivo_neto = ventas_efectivo - impuestos_efectivo  # 100 - 16 = 84.00

            # ✅ CÁLCULO 2: TARJETA NETO = (venta - 6% POS) - 16% empresa
            impuesto_pos = ventas_tarjeta * 0.06  # 600 * 0.06 = 36.00
            resto_despues_pos = ventas_tarjeta - impuesto_pos  # 600 - 36 = 564.00
            impuesto_empresa_tarjeta = resto_despues_pos * 0.16  # 564 * 0.16 = 90.24
            tarjeta_neto = resto_despues_pos - impuesto_empresa_tarjeta  # 564 - 90.24 = 473.76

            # ✅ CÁLCULO 3: TRANSFERENCIA NETO = venta - 16%
            impuestos_transferencia = ventas_transferencia * 0.16  # 100 * 0.16 = 16.00
            transferencia_neto = ventas_transferencia - impuestos_transferencia  # 100 - 16 = 84.00

            # ✅ CÁLCULO 4: TOTAL INGRESOS NETOS
            total_ingresos_netos = efectivo_neto + tarjeta_neto + transferencia_neto
            # 84.00 + 473.76 + 84.00 = 641.76

            # ✅ CÁLCULO 5: TOTAL IMPUESTOS (suma de TODOS los impuestos aplicados)
            total_impuestos = (impuestos_efectivo +  # 16.00
                               impuesto_pos +  # 36.00
                               impuesto_empresa_tarjeta +  # 90.24
                               impuestos_transferencia)  # 16.00
            # Total: 158.24

            # ✅ CÁLCULO 6: COMISIONES BANCARIAS (6% sobre ventas de tarjeta)
            comisiones_bancarias = ventas_tarjeta * 0.06  # 600 * 0.06 = 36.00

            # ✅ CÁLCULO 7: COMISIONES (de doctores, etc.)
            comision_dra = self.valores_crudo.get('comision_dra', 0)  # Valor de BD

            # ✅ CÁLCULO 8: TOTAL DEDUCCIONES
            total_deducciones = (gastos +  # 10.00
                                 total_impuestos +  # 158.24
                                 comisiones_bancarias +  # 36.00
                                 comision_dra)  # 0.00
            # Total: 204.24

            # ✅ CÁLCULO 9: RESULTADO NETO FINAL (IMPORTANTE: Este es el que va a la BD)
            resultado_neto = total_ingresos_netos - gastos - comisiones_bancarias - comision_dra
            # 641.76 - 10.00 - 36.00 - 0.00 = 595.76

            # ✅ CÁLCULO 10: TOTAL A DEPOSITAR VENTAS (Para el reporte)
            total_depositar_ventas = resultado_neto  # Es lo mismo

            # ✅ CÁLCULO 11: TOTAL A DEPOSITAR IMPUESTOS (Para el reporte)
            total_depositar_impuestos = total_impuestos  # 158.24

            # ✅ CÁLCULO 12: TOTAL FINAL (Para el reporte)
            total_final = total_depositar_ventas + total_depositar_impuestos
            # 595.76 + 158.24 = 754.00

            print(f"🎯 RESULTADOS FINALES:")
            print(f"   - Efectivo neto: Q{efectivo_neto:.2f}")
            print(f"   - Tarjeta neto: Q{tarjeta_neto:.2f}")
            print(f"   - Transferencia neto: Q{transferencia_neto:.2f}")
            print(f"   - Total ingresos netos: Q{total_ingresos_netos:.2f}")
            print(f"   - Total impuestos: Q{total_impuestos:.2f}")
            print(f"   - Comisiones bancarias: Q{comisiones_bancarias:.2f}")
            print(f"   - Total deducciones: Q{total_deducciones:.2f}")
            print(f"   - RESULTADO NETO: Q{resultado_neto:.2f}")

            # ✅ GUARDAR TODOS LOS VALORES CALCULADOS (ASEGURAR QUE TODOS EXISTAN)
            self.valores_neto = {
                # Valores básicos para BD
                'efectivo_neto': float(efectivo_neto),
                'tarjeta_neto': float(tarjeta_neto),
                'transferencia_neto': float(transferencia_neto),
                'total_ingresos_netos': float(total_ingresos_netos),
                'total_gastos': float(gastos),
                'total_impuestos': float(total_impuestos),
                'comisiones_bancarias': float(comisiones_bancarias),
                'comisiones': float(comision_dra),
                'total_deducciones': float(total_deducciones),
                'resultado_neto': float(resultado_neto),  # ✅ ESTE ES CRÍTICO PARA LA BD

                # Valores adicionales para reporte
                'total_depositar_ventas': float(total_depositar_ventas),
                'total_depositar_impuestos': float(total_depositar_impuestos),
                'total_final': float(total_final),

                # Valores individuales para referencia
                'impuestos_efectivo': float(impuestos_efectivo),
                'impuesto_pos': float(impuesto_pos),
                'impuesto_empresa_tarjeta': float(impuesto_empresa_tarjeta),
                'impuestos_transferencia': float(impuestos_transferencia)
            }

            # ✅ VALIDAR QUE TODOS LOS VALORES SEAN NÚMEROS
            for key, value in self.valores_neto.items():
                if not isinstance(value, (int, float)) or value is None:
                    print(f"⚠️  ADVERTENCIA: Valor inválido para {key}: {value}")
                    self.valores_neto[key] = 0.0

            # ✅ ACTUALIZAR TABLAS DE LA INTERFAZ
            self.actualizar_tablas_resultados()

            # ✅ VERIFICAR CUADRE SI HAY DATOS INGRESADOS
            self.verificar_cuadre()

            print("✅ === CÁLCULO NETO COMPLETADO EXITOSAMENTE ===")

            # ✅ MOSTRAR MENSAJE FINAL AL USUARIO
            QMessageBox.information(
                self,
                "✅ Cálculo Completado",
                f"""🧮 Cálculo neto finalizado:

    💰 INGRESOS NETOS:
    - Efectivo: Q{efectivo_neto:.2f}
    - Tarjeta: Q{tarjeta_neto:.2f}  
    - Transferencia: Q{transferencia_neto:.2f}
    - Total: Q{total_ingresos_netos:.2f}

    📉 DEDUCCIONES:
    - Gastos: Q{gastos:.2f}
    - Impuestos: Q{total_impuestos:.2f}
    - Comisiones bancarias: Q{comisiones_bancarias:.2f}
    - Total: Q{total_deducciones:.2f}

    🎯 RESULTADO NETO: Q{resultado_neto:.2f}"""
            )

            return True

        except ValueError as e:
            error_msg = f"Error en los valores ingresados: {e}"
            print(f"❌ {error_msg}")
            QMessageBox.warning(self, "Error de datos", error_msg)
            return False
        except Exception as e:
            error_msg = f"Error al calcular cierre neto: {e}"
            print(f"❌ {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)
            import traceback
            traceback.print_exc()
            return False

    def guardar_cierre_crudo(self):
        """Guarda los resultados del cierre crudo en la base de datos - TOTALMENTE CORREGIDO"""
        try:
            # ✅ VERIFICAR QUE EXISTAN LOS VALORES CALCULADOS CON IMPUESTOS
            if not hasattr(self, 'valores_crudo'):
                QMessageBox.warning(self, "Advertencia", "Primero debe calcular el cierre")
                return False

            if not self.db_connection:
                QMessageBox.warning(self, "Advertencia", "No hay conexión a la base de datos")
                return False

            # ✅ VERIFICAR QUE LOS VALORES INCLUYAN IMPUESTOS CALCULADOS
            valores_requeridos = ['venta_neta', 'gastos', 'visa', 'comision_dra',
                                  'impuestos_efectivo', 'impuestos_transferencia',
                                  'impuestos_visa', 'totales']

            for valor in valores_requeridos:
                if valor not in self.valores_crudo:
                    QMessageBox.warning(self, "Error", f"Falta el valor {valor} en los cálculos. Recalcule el cierre.")
                    return False

            # ✅ VERIFICAR QUE LOS IMPUESTOS TENGAN VALORES (no sean 0 si hay ventas)
            venta_neta = self.valores_crudo.get('venta_neta', 0)
            total_impuestos = (self.valores_crudo.get('impuestos_efectivo', 0) +
                               self.valores_crudo.get('impuestos_transferencia', 0) +
                               self.valores_crudo.get('impuestos_visa', 0))

            if venta_neta > 0 and total_impuestos == 0:
                QMessageBox.warning(self, "Advertencia",
                                    "Los impuestos parecen estar en 0. Verifique que el cálculo sea correcto.")
                respuesta = QMessageBox.question(self, "Confirmar",
                                                 "¿Está seguro de que desea guardar con impuestos en 0?",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if respuesta == QMessageBox.No:
                    return False

            # ✅ CORRECCIÓN: Usar date.today() correctamente
            from datetime import date
            fecha_actual = date.today().strftime('%Y-%m-%d')

            # Comprobar si ya existe un registro para esta fecha
            self.cursor.execute("SELECT id FROM cierre_crudo WHERE fecha = %s", (fecha_actual,))
            existing_record = self.cursor.fetchone()

            if existing_record:
                # Actualizar registro existente - ASEGURAR QUE SE GUARDAN VALORES CON IMPUESTOS
                query = """
                        UPDATE cierre_crudo \
                        SET venta_neta              = %s, \
                            gastos                  = %s, \
                            visa                    = %s, \
                            comision_dra            = %s, \
                            impuestos_efectivo      = %s, \
                            impuestos_transferencia = %s, \
                            impuestos_visa          = %s, \
                            totales                 = %s, \
                            fecha_registro          = NOW()
                        WHERE fecha = %s \
                        """
                values = (
                    self.valores_crudo['venta_neta'],
                    self.valores_crudo['gastos'],
                    self.valores_crudo['visa'],
                    self.valores_crudo['comision_dra'],
                    self.valores_crudo['impuestos_efectivo'],
                    self.valores_crudo['impuestos_transferencia'],
                    self.valores_crudo['impuestos_visa'],
                    self.valores_crudo['totales'],  # ✅ ESTE DEBE INCLUIR IMPUESTOS
                    fecha_actual
                )
                self.cursor.execute(query, values)
                mensaje = "Cierre crudo actualizado con impuestos incluidos"
            else:
                # Crear nuevo registro - ASEGURAR QUE SE GUARDAN VALORES CON IMPUESTOS
                query = """
                        INSERT INTO cierre_crudo
                        (fecha, venta_neta, gastos, visa, comision_dra, impuestos_efectivo,
                         impuestos_transferencia, impuestos_visa, totales)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
                        """
                values = (
                    fecha_actual,
                    self.valores_crudo['venta_neta'],
                    self.valores_crudo['gastos'],
                    self.valores_crudo['visa'],
                    self.valores_crudo['comision_dra'],
                    self.valores_crudo['impuestos_efectivo'],
                    self.valores_crudo['impuestos_transferencia'],
                    self.valores_crudo['impuestos_visa'],
                    self.valores_crudo['totales']  # ✅ ESTE DEBE INCLUIR IMPUESTOS
                )
                self.cursor.execute(query, values)
                mensaje = "Cierre crudo guardado con impuestos incluidos"

            # Confirmar cambios
            self.db_connection.commit()

            # ✅ LOGS PARA VERIFICAR QUE SE GUARDARON LOS DATOS CORRECTOS
            print(f"✅ {mensaje}")
            print(f"📊 Valores guardados:")
            print(f"   - Venta neta: Q{self.valores_crudo['venta_neta']:.2f}")
            print(f"   - Impuestos efectivo: Q{self.valores_crudo['impuestos_efectivo']:.2f}")
            print(f"   - Impuestos transferencia: Q{self.valores_crudo['impuestos_transferencia']:.2f}")
            print(f"   - Impuestos visa: Q{self.valores_crudo['impuestos_visa']:.2f}")
            print(f"   - TOTALES (con impuestos): Q{self.valores_crudo['totales']:.2f}")
            print(f"   - Total impuestos: Q{total_impuestos:.2f}")

            # Verificar que el total sea mayor que venta neta (porque incluye impuestos)
            if self.valores_crudo['totales'] <= self.valores_crudo['venta_neta'] and total_impuestos > 0:
                print("⚠️  ADVERTENCIA: Los totales parecen no incluir impuestos correctamente")
            else:
                print("✅ Verificación: Los totales incluyen impuestos correctamente")

            # Solo mostrar mensaje si no es parte de un cierre por turno
            if not hasattr(self, '_ejecutando_cierre_turno'):
                QMessageBox.information(self, "Éxito", mensaje)

            return True

        except Exception as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al guardar cierre crudo: {err}")
            print(f"❌ Error detallado: {err}")
            import traceback
            traceback.print_exc()
            self.db_connection.rollback()
            return False

    def guardar_cierre_neto(self):
        """FUNCIÓN GUARDAR CIERRE NETO - MEJORADA CON VALIDACIONES Y MANEJO DE ERRORES"""
        if not hasattr(self, 'valores_neto'):
            QMessageBox.warning(self, "Advertencia", "Primero debe calcular el cierre")
            return False

        if not self.db_connection:
            QMessageBox.warning(self, "Advertencia", "No hay conexión a la base de datos")
            return False

        try:
            # ✅ VALIDAR QUE TODOS LOS VALORES EXISTAN
            valores_requeridos = [
                'efectivo_neto', 'tarjeta_neto', 'transferencia_neto', 'total_ingresos_netos',
                'total_gastos', 'total_impuestos', 'comisiones', 'total_deducciones', 'resultado_neto'
            ]

            for valor in valores_requeridos:
                if valor not in self.valores_neto:
                    QMessageBox.critical(self, "Error", f"Falta el valor {valor} en los cálculos. Recalcule el cierre.")
                    return False

                # Validar que el valor sea numérico
                try:
                    float(self.valores_neto[valor])
                except (ValueError, TypeError):
                    QMessageBox.critical(self, "Error", f"El valor {valor} no es válido: {self.valores_neto[valor]}")
                    return False

            # ✅ OBTENER FECHA ACTUAL
            fecha_actual = datetime.date.today().strftime('%Y-%m-%d')

            print(f"💾 Guardando cierre neto para {fecha_actual}")
            print(f"📊 Valores a guardar:")
            for key, value in self.valores_neto.items():
                if key in valores_requeridos:
                    print(f"   - {key}: Q{float(value):.2f}")

            # ✅ VERIFICAR SI YA EXISTE UN REGISTRO PARA ESTA FECHA
            self.cursor.execute("SELECT id FROM cierre_neto WHERE fecha = %s", (fecha_actual,))
            existing_record = self.cursor.fetchone()

            if existing_record:
                # ✅ ACTUALIZAR REGISTRO EXISTENTE
                query = """
                        UPDATE cierre_neto
                        SET efectivo_neto        = %s,
                            tarjeta_neto         = %s,
                            transferencia_neto   = %s,
                            total_ingresos_netos = %s,
                            total_gastos         = %s,
                            total_impuestos      = %s,
                            comisiones           = %s,
                            total_deducciones    = %s,
                            resultado_neto       = %s,
                            fecha_registro       = NOW()
                        WHERE fecha = %s \
                        """
                values = (
                    float(self.valores_neto['efectivo_neto']),
                    float(self.valores_neto['tarjeta_neto']),
                    float(self.valores_neto['transferencia_neto']),
                    float(self.valores_neto['total_ingresos_netos']),
                    float(self.valores_neto['total_gastos']),
                    float(self.valores_neto['total_impuestos']),
                    float(self.valores_neto['comisiones']),
                    float(self.valores_neto['total_deducciones']),
                    float(self.valores_neto['resultado_neto']),
                    fecha_actual
                )
                self.cursor.execute(query, values)
                mensaje = "Cierre neto actualizado en la base de datos"
            else:
                # ✅ CREAR NUEVO REGISTRO
                query = """
                        INSERT INTO cierre_neto
                        (fecha, efectivo_neto, tarjeta_neto, transferencia_neto, total_ingresos_netos,
                         total_gastos, total_impuestos, comisiones, total_deducciones, resultado_neto)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                        """
                values = (
                    fecha_actual,
                    float(self.valores_neto['efectivo_neto']),
                    float(self.valores_neto['tarjeta_neto']),
                    float(self.valores_neto['transferencia_neto']),
                    float(self.valores_neto['total_ingresos_netos']),
                    float(self.valores_neto['total_gastos']),
                    float(self.valores_neto['total_impuestos']),
                    float(self.valores_neto['comisiones']),
                    float(self.valores_neto['total_deducciones']),
                    float(self.valores_neto['resultado_neto'])
                )
                self.cursor.execute(query, values)
                mensaje = "Cierre neto guardado en la base de datos"

            # ✅ CONFIRMAR CAMBIOS
            self.db_connection.commit()

            print(f"✅ {mensaje}")
            print(f"📊 Resultado neto guardado: Q{float(self.valores_neto['resultado_neto']):.2f}")

            # Solo mostrar mensaje si no es parte de un cierre por turno
            if not hasattr(self, '_ejecutando_cierre_turno'):
                QMessageBox.information(self, "✅ Éxito", mensaje)

            return True

        except pymysql.Error as db_err:
            # Error específico de MySQL
            error_msg = f"Error de base de datos MySQL: {db_err}"
            print(f"❌ {error_msg}")
            QMessageBox.critical(self, "Error de Base de Datos", error_msg)
            try:
                self.db_connection.rollback()
            except:
                pass
            return False

        except Exception as err:
            # Error general
            error_msg = f"Error al guardar cierre neto: {err}"
            print(f"❌ {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)
            try:
                self.db_connection.rollback()
            except:
                pass
            import traceback
            traceback.print_exc()
            return False

    def exportar_reporte(self):
        """EXPORTA REPORTE PDF - VERSIÓN CON FORMATO PROFESIONAL"""
        try:
            from datetime import datetime
            import os
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            from reportlab.lib.units import inch

            if not hasattr(self, 'valores_crudo') or not hasattr(self, 'valores_neto'):
                QMessageBox.warning(self, "Advertencia", "Primero debe calcular el cierre")
                return False

            # Crear carpeta para reportes si no existe
            reports_dir = "reportes"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)

            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            hora_actual = datetime.now().strftime('%H-%M-%S')
            filename = f"{reports_dir}/reporte_cierre_{fecha_actual}_{hora_actual}.pdf"

            # Crear el documento PDF
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []

            # Estilos para el documento
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            subtitle_style = styles['Heading2']
            normal_style = styles['Normal']

            # Título del reporte - CORREGIDO: Solo primera letra mayúscula
            elements.append(Paragraph(f"Reporte de cierre - {fecha_actual}", title_style))
            elements.append(Spacer(1, 0.3 * inch))

            # =====================================================
            # PRODUCTOS VENDIDOS HOY - CORREGIDO
            # =====================================================
            try:
                elements.append(Paragraph("Productos vendidos hoy", subtitle_style))

                fecha_hoy = datetime.now().strftime('%Y-%m-%d')
                print(f"🔍 Buscando productos para la fecha: {fecha_hoy}")

                # CORREGIDO: Consulta mejorada para asegurar que funcione
                self.cursor.execute("""
                                    SELECT id,
                                           nombre,
                                           cantidad,
                                           tarjeta,
                                           efectivo,
                                           monto,
                                           usuario,
                                           fecha
                                    FROM cierre
                                    WHERE DATE (fecha) = %s
                                    ORDER BY fecha DESC
                                    """, (fecha_hoy,))
                productos_vendidos = self.cursor.fetchall()

                print(f"📊 Productos encontrados: {len(productos_vendidos)}")

                if productos_vendidos:
                    # CORREGIDO: Encabezados en formato normal
                    data_productos = [["ID", "Nombre", "Cantidad", "Tarjeta", "Efectivo", "Monto total", "Usuario"]]

                    total_efectivo_productos = 0
                    total_tarjeta_productos = 0
                    total_monto_productos = 0

                    for producto in productos_vendidos:
                        print(f"📝 Producto: {producto[1]} - Q{float(producto[5]):.2f}")

                        # Función simple para capitalizar
                        def capitalizar_texto(texto):
                            if not texto:
                                return ""
                            return str(texto).strip().capitalize()

                        data_productos.append([
                            str(producto[0]),
                            capitalizar_texto(producto[1]),  # CORREGIDO: Solo primera letra mayúscula
                            str(producto[2]),
                            f"Q{float(producto[3]):.2f}",
                            f"Q{float(producto[4]):.2f}",
                            f"Q{float(producto[5]):.2f}",
                            capitalizar_texto(producto[6])  # CORREGIDO: Solo primera letra mayúscula
                        ])

                        # Sumar totales
                        total_efectivo_productos += float(producto[4])
                        total_tarjeta_productos += float(producto[3])
                        total_monto_productos += float(producto[5])

                    # Agregar fila de totales
                    data_productos.append([
                        "", "TOTALES", "",
                        f"Q{total_tarjeta_productos:.2f}",
                        f"Q{total_efectivo_productos:.2f}",
                        f"Q{total_monto_productos:.2f}",
                        ""
                    ])

                    tabla_productos = Table(data_productos,
                                            colWidths=[0.8 * inch, 2 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch,
                                                       1 * inch])
                    tabla_productos.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                        # Fila de totales en color diferente
                        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
                        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(tabla_productos)

                    print(f"✅ Tabla de productos creada con {len(productos_vendidos)} productos")
                else:
                    print("⚠️ No se encontraron productos vendidos hoy")
                    elements.append(Paragraph("No hay productos vendidos hoy", normal_style))

                    # Debug: Verificar si hay datos en la tabla
                    self.cursor.execute("SELECT COUNT(*) FROM cierre")
                    total_registros = self.cursor.fetchone()[0]
                    print(f"🔍 Total de registros en tabla cierre: {total_registros}")

                    # Verificar registros de hoy con más detalle
                    self.cursor.execute("""
                                        SELECT DATE (fecha), COUNT (*)
                                        FROM cierre
                                        GROUP BY DATE (fecha)
                                        ORDER BY DATE (fecha) DESC
                                            LIMIT 5
                                        """)
                    fechas_disponibles = self.cursor.fetchall()
                    print(f"📅 Fechas disponibles en BD: {fechas_disponibles}")

                elements.append(Spacer(1, 0.3 * inch))
            except Exception as e:
                print(f"❌ Error al obtener productos: {e}")
                import traceback
                traceback.print_exc()
                elements.append(Paragraph(f"Error al cargar productos: {str(e)}", normal_style))

            # =====================================================
            # TABLA 1: INGRESOS - CORREGIDO
            # =====================================================
            elements.append(Paragraph("Cierre", subtitle_style))
            elements.append(Paragraph("Ingresos:", styles['Heading3']))

            # Obtener valores de manera segura
            try:
                ingreso_efectivo = float(getattr(self, 'txt_ingreso_efectivo', None).text() if hasattr(self,
                                                                                                       'txt_ingreso_efectivo') and self.txt_ingreso_efectivo else 0)
            except:
                ingreso_efectivo = self.valores_crudo.get('ventas_efectivo', 0)

            try:
                ingreso_tarjeta = float(getattr(self, 'txt_ingreso_tarjeta', None).text() if hasattr(self,
                                                                                                     'txt_ingreso_tarjeta') and self.txt_ingreso_tarjeta else 0)
            except:
                ingreso_tarjeta = self.valores_crudo.get('ventas_tarjeta', 0)

            try:
                ingreso_transferencia = float(getattr(self, 'txt_ingreso_transferencia', None).text() if hasattr(self,
                                                                                                                 'txt_ingreso_transferencia') and self.txt_ingreso_transferencia else 0)
            except:
                ingreso_transferencia = self.valores_crudo.get('ventas_transferencia', 0)

            total_ingresos = ingreso_efectivo + ingreso_tarjeta + ingreso_transferencia

            # CORREGIDO: Conceptos en formato normal
            data_ingresos = [
                ["Concepto", "Valor"],
                ["Ingreso efectivo", f"Q{ingreso_efectivo:.2f}"],
                ["Ingreso tarjeta", f"Q{ingreso_tarjeta:.2f}"],
                ["Ingreso transferencia", f"Q{ingreso_transferencia:.2f}"],
                ["Total ingresos", f"Q{total_ingresos:.2f}"]
            ]

            tabla_ingresos = Table(data_ingresos, colWidths=[3 * inch, 1.5 * inch])
            tabla_ingresos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(tabla_ingresos)
            elements.append(Spacer(1, 0.3 * inch))

            # =====================================================
            # TABLA 2: GASTOS Y DEDUCCIONES - CORREGIDO
            # =====================================================
            elements.append(Paragraph("Gastos y deducciones:", styles['Heading3']))

            # Obtener valores de manera segura
            try:
                gastos = float(
                    getattr(self, 'txt_gastos', None).text() if hasattr(self, 'txt_gastos') and self.txt_gastos else 0)
            except:
                gastos = self.valores_crudo.get('gastos', 0)

            try:
                comisiones = float(getattr(self, 'txt_comisiones', None).text() if hasattr(self,
                                                                                           'txt_comisiones') and self.txt_comisiones else 0)
            except:
                comisiones = self.valores_crudo.get('comisiones', 0)

            try:
                impuestos = float(getattr(self, 'txt_impuestos', None).text() if hasattr(self,
                                                                                         'txt_impuestos') and self.txt_impuestos else 0)
            except:
                impuestos = self.valores_crudo.get('impuestos', 0)

            try:
                impuestos_visa = float(getattr(self, 'txt_impuestos_visa', None).text() if hasattr(self,
                                                                                                   'txt_impuestos_visa') and self.txt_impuestos_visa else 0)
            except:
                impuestos_visa = self.valores_crudo.get('impuestos_visa', 0)

            totales_cierre = gastos + comisiones + impuestos + impuestos_visa

            # CORREGIDO: Conceptos en formato normal
            data_gastos = [
                ["Concepto", "Valor"],
                ["Gastos", f"Q{gastos:.2f}"],
                ["Comisiones", f"Q{comisiones:.2f}"],
                ["Impuestos", f"Q{impuestos:.2f}"],
                ["Impuestos visa", f"Q{impuestos_visa:.2f}"],
                ["Totales", f"Q{totales_cierre:.2f}"]
            ]

            tabla_gastos = Table(data_gastos, colWidths=[3 * inch, 1.5 * inch])
            tabla_gastos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(tabla_gastos)
            elements.append(Spacer(1, 0.3 * inch))

            # =====================================================
            # TABLA 3: CIERRE NETO - INGRESOS NETOS (CORREGIDO)
            # =====================================================
            elements.append(Paragraph("Cierre neto", subtitle_style))
            elements.append(Paragraph("Ingresos netos:", styles['Heading3']))

            efectivo_neto = self.valores_neto.get('efectivo_neto', 0)
            tarjeta_neto = self.valores_neto.get('tarjeta_neto', 0)
            transferencia_neto = self.valores_neto.get('transferencia_neto', 0)
            total_ingresos_netos = self.valores_neto.get('total_ingresos_netos', 0)

            # CORREGIDO: Conceptos en formato normal
            data_ingresos_netos = [
                ["Concepto", "Valor"],
                ["Efectivo neto", f"Q{efectivo_neto:.2f}"],
                ["Tarjeta neto", f"Q{tarjeta_neto:.2f}"],
                ["Transferencia neto", f"Q{transferencia_neto:.2f}"],
                ["Total ingresos netos", f"Q{total_ingresos_netos:.2f}"]
            ]

            tabla_ingresos_netos = Table(data_ingresos_netos, colWidths=[3 * inch, 1.5 * inch])
            tabla_ingresos_netos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(tabla_ingresos_netos)
            elements.append(Spacer(1, 0.2 * inch))

            # =====================================================
            # TABLA 4: GASTOS Y DEDUCCIONES NETO (CORREGIDO)
            # =====================================================
            elements.append(Paragraph("Gastos y deducciones:", styles['Heading3']))

            total_gastos = self.valores_neto.get('total_gastos', 0)
            total_impuestos = self.valores_neto.get('total_impuestos', 0)
            comisiones_bancarias_neto = self.valores_neto.get('comisiones_bancarias', 0)
            comisiones_neto = self.valores_neto.get('comisiones', 0)
            total_deducciones = self.valores_neto.get('total_deducciones', 0)

            # CORREGIDO: Conceptos en formato normal
            data_deducciones = [
                ["Concepto", "Valor"],
                ["Total gastos", f"Q{total_gastos:.2f}"],
                ["Total impuestos", f"Q{total_impuestos:.2f}"],
                ["Comisiones bancarias", f"Q{comisiones_bancarias_neto:.2f}"],
                ["Comisiones", f"Q{comisiones_neto:.2f}"],
                ["Total deducciones", f"Q{total_deducciones:.2f}"]
            ]

            tabla_deducciones = Table(data_deducciones, colWidths=[3 * inch, 1.5 * inch])
            tabla_deducciones.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(tabla_deducciones)
            elements.append(Spacer(1, 0.2 * inch))

            # =====================================================
            # TABLA 5: RESULTADO FINAL (CORREGIDO)
            # =====================================================
            elements.append(Paragraph("Resultado final:", styles['Heading3']))

            total_depositar_ventas = self.valores_neto.get('total_depositar_ventas', 0)
            total_depositar_impuestos = self.valores_neto.get('total_depositar_impuestos', 0)
            total_final = self.valores_neto.get('total_final', 0)

            # CORREGIDO: Conceptos en formato normal
            data_resultado_final = [
                ["Concepto", "Valor"],
                ["Total a depositar ventas", f"Q{total_depositar_ventas:.2f}"],
                ["Total a depositar impuestos", f"Q{total_depositar_impuestos:.2f}"],
                ["Total", f"Q{total_final:.2f}"]
            ]

            tabla_resultado_final = Table(data_resultado_final, colWidths=[3 * inch, 1.5 * inch])
            tabla_resultado_final.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('BACKGROUND', (0, -1), (1, -1), colors.darkgreen),
                ('TEXTCOLOR', (0, -1), (1, -1), colors.white),
                ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(tabla_resultado_final)
            elements.append(Spacer(1, 0.3 * inch))

            # =====================================================
            # PIE DE PÁGINA (CORREGIDO)
            # =====================================================
            elements.append(Spacer(1, 0.5 * inch))
            elements.append(Paragraph("=== Reporte generado ===", subtitle_style))
            elements.append(
                Paragraph(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                          normal_style))  # CORREGIDO: Sin .upper()

            # Construir el documento PDF
            doc.build(elements)

            QMessageBox.information(self, "✅ Éxito", f"📄 Reporte PDF generado exitosamente:\n\n{filename}")
            print(f"✅ PDF generado: {filename}")
            return True

        except Exception as e:
            print(f"❌ Error al exportar reporte: {e}")
            QMessageBox.critical(self, "Error", f"Error al exportar reporte: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def ejecutar_cierre_por_turno(self):
        """FUNCIÓN PRINCIPAL - CIERRE DE TURNO COMPLETO"""
        try:
            print("🔄 === INICIANDO CIERRE DE TURNO COMPLETO ===")

            # =====================================================
            # PASO 0: VERIFICAR QUE HAY DATOS PARA CERRAR
            # =====================================================
            if not hasattr(self, 'valores_crudo') or not hasattr(self, 'valores_neto'):
                QMessageBox.warning(
                    self,
                    "Datos Incompletos",
                    """⚠️ No hay datos calculados para cerrar.

    Debe seguir estos pasos:
    1️⃣ Presionar 'Cargar Datos'
    2️⃣ Presionar 'Calcular Cierre'  
    3️⃣ Intentar el cierre nuevamente"""
                )
                return

            # =====================================================
            # PASO 1: CONFIRMAR EL CIERRE CON EL USUARIO
            # =====================================================
            resultado_neto = self.valores_neto.get('resultado_neto', 0)
            total_impuestos = self.valores_neto.get('total_impuestos', 0)

            confirmacion = QMessageBox.question(
                self,
                "🔄 CONFIRMAR CIERRE DE TURNO",
                f"""⚠️ ATENCIÓN: Esto cerrará el turno DEFINITIVAMENTE

    📊 RESUMEN DEL CIERRE:
    - Resultado neto: Q{resultado_neto:.2f}
    - Total impuestos: Q{total_impuestos:.2f}

    🔥 ACCIONES QUE SE REALIZARÁN:
    1️⃣ Generar reporte PDF
    2️⃣ Borrar TODOS los datos del día de la BD
    3️⃣ Limpiar completamente el sistema
    4️⃣ Abrir ventana de billetes para nuevo turno

    ❗ ESTA ACCIÓN NO SE PUEDE DESHACER

    ¿Está seguro de proceder con el CIERRE DE TURNO?""",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if confirmacion != QMessageBox.Yes:
                print("❌ Usuario canceló el cierre de turno")
                return

            print("✅ Usuario confirmó el cierre de turno")

            # =====================================================
            # PASO 2: GENERAR REPORTE PDF
            # =====================================================
            print("📄 === PASO 1/4: GENERANDO REPORTE PDF ===")

            if self.exportar_reporte():
                print("✅ Reporte PDF generado exitosamente")
                QMessageBox.information(
                    self,
                    "✅ PDF Generado",
                    "📄 Reporte de cierre generado exitosamente.\n\nContinuando con el cierre..."
                )
            else:
                respuesta = QMessageBox.question(
                    self,
                    "⚠️ Error en PDF",
                    "❌ Error al generar el reporte PDF.\n\n¿Desea continuar con el cierre sin el reporte?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if respuesta != QMessageBox.Yes:
                    print("❌ Cierre cancelado por error en PDF")
                    return

            # =====================================================
            # PASO 3: GUARDAR DATOS EN HISTÓRICO ANTES DE BORRAR
            # =====================================================
            print("💾 === GUARDANDO EN HISTÓRICO ANTES DE BORRAR ===")

            try:
                # Guardar cierre crudo en histórico
                if not self.guardar_cierre_crudo():
                    QMessageBox.critical(self, "Error", "❌ Error al guardar cierre crudo en histórico")
                    return

                # Guardar cierre neto en histórico
                if not self.guardar_cierre_neto():
                    QMessageBox.critical(self, "Error", "❌ Error al guardar cierre neto en histórico")
                    return

                print("✅ Datos guardados en histórico exitosamente")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Error al guardar en histórico: {e}")
                return

            # =====================================================
            # PASO 4: BORRAR DATOS DEL DÍA DE LA BASE DE DATOS
            # =====================================================
            print("🔥 === PASO 2/4: BORRANDO DATOS DE LA BASE DE DATOS ===")

            if self.borrar_datos_dia_actual():
                print("✅ Datos del día borrados de la BD exitosamente")
                QMessageBox.information(
                    self,
                    "✅ Datos Borrados",
                    "🔥 Todos los datos del día han sido eliminados de la base de datos.\n\nContinuando..."
                )
            else:
                QMessageBox.critical(self, "Error", "❌ Error al borrar datos de la base de datos")
                return

            # =====================================================
            # PASO 5: LIMPIAR INTERFAZ DEL SISTEMA
            # =====================================================
            print("🧹 === PASO 3/4: LIMPIANDO INTERFAZ ===")

            if self.limpiar_interfaz_completa():
                print("✅ Interfaz limpiada exitosamente")
            else:
                print("⚠️ Error al limpiar interfaz, pero continuando...")

            # =====================================================
            # PASO 6: MOSTRAR CONFIRMACIÓN DE CIERRE EXITOSO
            # =====================================================
            QMessageBox.information(
                self,
                "✅ Cierre de Turno Completado",
                f"""🎉 ¡CIERRE DE TURNO COMPLETADO EXITOSAMENTE!

    📊 RESUMEN:
    - Resultado final: Q{resultado_neto:.2f}
    - Reporte PDF: ✅ Generado
    - Datos históricos: ✅ Guardados  
    - Datos del día: ✅ Eliminados
    - Sistema: ✅ Limpiado

    🆕 A continuación se abrirá la ventana de billetes para registrar el efectivo inicial del NUEVO TURNO."""
            )

            # =====================================================
            # PASO 7: ABRIR VENTANA DE BILLETES PARA NUEVO TURNO
            # =====================================================
            print("💰 === PASO 4/4: ABRIENDO VENTANA DE BILLETES ===")

            if self.abrir_ventana_billetes():
                print("✅ Ventana de billetes abierta exitosamente")
            else:
                print("⚠️ Error abriendo ventana de billetes")

            # =====================================================
            # PASO 8: CERRAR ESTA VENTANA (OPCIONAL)
            # =====================================================

            # OPCIONAL: Descomentar si quieres que se cierre la ventana de cierre
            # respuesta_cerrar = QMessageBox.question(
            #     self,
            #     "Cerrar Ventana",
            #     "¿Desea cerrar esta ventana de cierre?",
            #     QMessageBox.Yes | QMessageBox.No,
            #     QMessageBox.Yes
            # )
            #
            # if respuesta_cerrar == QMessageBox.Yes:
            #     self.close()

            print("🎉 === CIERRE DE TURNO COMPLETADO EXITOSAMENTE ===")

        except Exception as e:
            print(f"❌ ERROR CRÍTICO en cierre de turno: {e}")
            import traceback
            traceback.print_exc()

            QMessageBox.critical(
                self,
                "❌ Error Crítico",
                f"""💥 Ocurrió un error durante el cierre de turno:

    🔍 Error: {str(e)}

    ⚠️ IMPORTANTE:
    - Verifique el estado del sistema
    - Revise la conexión a la base de datos  
    - Contacte al administrador si es necesario

    📞 Para soporte, proporcione este error exacto."""
            )

    def borrar_datos_dia_actual(self):
        """BORRA TODOS LOS DATOS DEL DÍA ACTUAL DE LA BASE DE DATOS"""
        try:
            from datetime import date
            fecha_actual = date.today().strftime('%Y-%m-%d')

            print(f"🔥 Borrando datos del {fecha_actual}...")

            # BORRAR VENTAS DEL DÍA
            self.cursor.execute("DELETE FROM cierre WHERE DATE(fecha) = %s", (fecha_actual,))
            ventas_eliminadas = self.cursor.rowcount
            print(f"  ✅ Ventas eliminadas: {ventas_eliminadas} registros")

            # BORRAR GASTOS DEL DÍA
            self.cursor.execute("DELETE FROM gastos WHERE DATE(fecha) = %s", (fecha_actual,))
            gastos_eliminados = self.cursor.rowcount
            print(f"  ✅ Gastos eliminados: {gastos_eliminados} registros")

            # BORRAR REGISTRO DE CAJA DEL DÍA
            self.cursor.execute("DELETE FROM registro_caja WHERE DATE(fecha) = %s", (fecha_actual,))
            caja_eliminada = self.cursor.rowcount
            print(f"  ✅ Registro caja eliminado: {caja_eliminada} registros")

            # BORRAR INGRESOS DE TARJETA DEL DÍA
            self.cursor.execute("DELETE FROM ingreso_tarjeta WHERE DATE(fecha) = %s", (fecha_actual,))
            tarjeta_eliminada = self.cursor.rowcount
            print(f"  ✅ Ingresos tarjeta eliminados: {tarjeta_eliminada} registros")

            # BORRAR TRANSFERENCIAS DEL DÍA
            self.cursor.execute("DELETE FROM ingreso_transferencia WHERE DATE(fecha) = %s", (fecha_actual,))
            transferencias_eliminadas = self.cursor.rowcount
            print(f"  ✅ Transferencias eliminadas: {transferencias_eliminadas} registros")

            # BORRAR COMISIONES DEL DÍA
            self.cursor.execute("DELETE FROM pagos_comisiones WHERE DATE(fecha) = %s", (fecha_actual,))
            comisiones_eliminadas = self.cursor.rowcount
            print(f"  ✅ Comisiones eliminadas: {comisiones_eliminadas} registros")

            # CONFIRMAR CAMBIOS
            self.db_connection.commit()

            total_eliminados = (ventas_eliminadas + gastos_eliminados + caja_eliminada +
                                tarjeta_eliminada + transferencias_eliminadas + comisiones_eliminadas)

            print(f"🔥 TOTAL ELIMINADO: {total_eliminados} registros de la base de datos")
            return True

        except Exception as e:
            print(f"❌ Error al borrar datos: {e}")
            self.db_connection.rollback()
            QMessageBox.critical(self, "Error", f"Error al borrar datos de la BD: {e}")
            return False

    def limpiar_interfaz_completa(self):
        """Limpia TODOS los campos de la interfaz del sistema de cierre"""
        try:
            print("🧹 Limpiando interfaz completa...")

            # LIMPIAR Y DESBLOQUEAR CAMPOS DE TEXTO
            campos = [
                self.txt_ingreso_efectivo, self.txt_ingreso_tarjeta,
                self.txt_ingreso_transferencia, self.txt_total_gastos,
                self.txt_total_real, self.txt_total_banco
            ]

            estilo_normal = "background-color: white; border: 1px solid #cccccc; color: black; padding: 5px;"

            for campo in campos:
                campo.setReadOnly(False)
                campo.clear()
                campo.setText("0.00")
                campo.setStyleSheet(estilo_normal)

            # LIMPIAR TABLAS
            # Tabla ingresos netos
            try:
                for row in range(self.tabla_ingresos_netos.rowCount()):
                    if self.tabla_ingresos_netos.item(row, 1):
                        self.tabla_ingresos_netos.item(row, 1).setText("0.00")
            except:
                pass

            # Tabla deducciones
            try:
                for row in range(self.tabla_deducciones.rowCount()):
                    if self.tabla_deducciones.item(row, 1):
                        self.tabla_deducciones.item(row, 1).setText("0.00")
            except:
                pass

            # Tabla resultado final
            try:
                for row in range(self.tabla_resultado_final.rowCount()):
                    if self.tabla_resultado_final.item(row, 1):
                        self.tabla_resultado_final.item(row, 1).setText("0.00")
                        self.tabla_resultado_final.item(row, 1).setForeground(Qt.black)
            except:
                pass

            # Limpiar confirmación de dinero físico
            if hasattr(self, 'txt_efectivo_fisico'):
                self.txt_efectivo_fisico.clear()
                self.txt_efectivo_fisico.setText("0.00")
            if hasattr(self, 'txt_cheques_fisicos'):
                self.txt_cheques_fisicos.clear()
                self.txt_cheques_fisicos.setText("0.00")

            # Limpiar tabla de verificación
            try:
                if hasattr(self, 'tabla_verificacion'):
                    self.tabla_verificacion.item(0, 1).setText("0.00")  # Efectivo Calculado
                    self.tabla_verificacion.item(1, 1).setText("0.00")  # Efectivo Físico
                    self.tabla_verificacion.item(2, 1).setText("0.00")  # Diferencia
                    self.tabla_verificacion.item(3, 1).setText("❌ NO CUADRA")  # Estado
            except:
                pass

            # Resetear estado de cuadre
            if hasattr(self, 'lbl_estado_cuadre'):
                self.lbl_estado_cuadre.setText("❌ NO CUADRA")
                self.lbl_estado_cuadre.setStyleSheet("background-color: #ffebee; color: #c62828; padding: 5px;")

            # ELIMINAR VARIABLES DE MEMORIA
            variables_eliminar = [
                'valores_crudo', 'valores_neto', 'efectivo_inicial',
                'ventas_efectivo', 'ventas_tarjeta', 'ventas_transferencia',
                'tarjeta_inicial', 'comision_dra_valor'
            ]

            for var in variables_eliminar:
                if hasattr(self, var):
                    delattr(self, var)
                    print(f"  ✅ Variable {var} eliminada")

            print("✅ Interfaz limpiada completamente")
            return True

        except Exception as e:
            print(f"❌ Error limpiando interfaz: {e}")
            return False

    def abrir_ventana_billetes(self):
        """Abre la ventana de registro de billetes (CashRegisterApp)"""
        try:
            print("💰 Abriendo ventana de billetes...")

            from .efectivo import CashRegisterApp

            # Crear y mostrar la ventana de efectivo inicial
            self.ventana_billetes = CashRegisterApp()
            self.ventana_billetes.setWindowTitle("💰 Registro de Billetes - NUEVO TURNO")
            self.ventana_billetes.show()

            print("✅ Ventana de billetes abierta")
            return True

        except Exception as e:
            print(f"❌ Error abriendo ventana de billetes: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir la ventana de billetes.\n\nError: {e}\n\nAbra manualmente el módulo de Efectivo Inicial."
            )
            return False

    def abrir_ventana_efectivo_inicial(self):
        """Abre la ventana para registrar el efectivo inicial del nuevo turno"""
        try:
            print("💰 Creando ventana de efectivo inicial...")

            # Importar la clase CashRegisterApp
            from .efectivo import CashRegisterApp

            # Crear y mostrar la ventana de efectivo inicial
            self.ventana_efectivo_inicial = CashRegisterApp()

            # Personalizar la ventana para el nuevo turno
            self.ventana_efectivo_inicial.setWindowTitle("💰 Registro de Efectivo - NUEVO TURNO")

            # Mostrar la ventana
            self.ventana_efectivo_inicial.show()

            print("✅ Ventana de efectivo inicial abierta")

        except Exception as e:
            print(f"❌ Error al abrir ventana de efectivo inicial: {e}")
            QMessageBox.critical(
                self,
                "❌ Error",
                f"No se pudo abrir la ventana de efectivo inicial:\n\n{str(e)}\n\nPor favor abra manualmente el módulo de registro de efectivo."
            )

    def limpiar_sistema_nuevo_turno(self):
        """Limpia el sistema para preparar un nuevo turno"""
        try:
            print("🧹 Iniciando limpieza del sistema...")

            # Limpiar datos en memoria
            if hasattr(self, 'valores_crudo'):
                delattr(self, 'valores_crudo')
            if hasattr(self, 'valores_neto'):
                delattr(self, 'valores_neto')
            if hasattr(self, 'efectivo_inicial'):
                delattr(self, 'efectivo_inicial')
            if hasattr(self, 'ventas_efectivo'):
                delattr(self, 'ventas_efectivo')
            if hasattr(self, 'ventas_tarjeta'):
                delattr(self, 'ventas_tarjeta')

            # Limpiar campos de la interfaz
            self.limpiar_todo()

            print("✅ Sistema limpiado para nuevo turno")
            return True

        except Exception as e:
            print(f"❌ Error al limpiar sistema: {e}")
            return False

    def registrar_turno_cerrado(self):
        """Registra el turno cerrado en la base de datos para auditoría"""
        try:
            if not self.db_connection:
                print("❌ No hay conexión a la base de datos para registrar turno")
                return False

            cursor = self.db_connection.cursor()

            # Crear tabla de turnos cerrados si no existe
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS turnos_cerrados
                           (
                               id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               fecha_cierre
                               DATE
                               NOT
                               NULL,
                               hora_cierre
                               TIME
                               NOT
                               NULL,
                               usuario
                               VARCHAR
                           (
                               100
                           ),
                               efectivo_inicial DECIMAL
                           (
                               10,
                               2
                           ),
                               ventas_efectivo DECIMAL
                           (
                               10,
                               2
                           ),
                               ventas_tarjeta DECIMAL
                           (
                               10,
                               2
                           ),
                               impuestos_totales DECIMAL
                           (
                               10,
                               2
                           ),
                               resultado_neto DECIMAL
                           (
                               10,
                               2
                           ),
                               timestamp_cierre TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               notas TEXT
                               )
                           """)

            # Obtener datos del cierre
            fecha_actual = datetime.date.today().strftime('%Y-%m-%d')
            hora_actual = datetime.datetime.now().strftime('%H:%M:%S')
            usuario_actual = getattr(self, 'usuario_actual', 'Usuario desconocido')

            efectivo_inicial = self.valores_crudo.get('efectivo_inicial', 0)
            ventas_efectivo = self.valores_crudo.get('ventas_efectivo', 0)
            ventas_tarjeta = self.valores_crudo.get('ventas_tarjeta', 0)
            impuestos_totales = self.valores_neto.get('total_impuestos', 0)
            resultado_neto = self.valores_neto.get('resultado_neto', 0)

            # Registrar el turno cerrado
            cursor.execute("""
                           INSERT INTO turnos_cerrados
                           (fecha_cierre, hora_cierre, usuario, efectivo_inicial, ventas_efectivo,
                            ventas_tarjeta, impuestos_totales, resultado_neto, notas)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                           """, (
                               fecha_actual, hora_actual, usuario_actual, efectivo_inicial,
                               ventas_efectivo, ventas_tarjeta, impuestos_totales, resultado_neto,
                               f"Cierre por turno ejecutado manualmente"
                           ))

            self.db_connection.commit()
            cursor.close()

            print("✅ Turno cerrado registrado en base de datos")
            return True

        except Exception as e:
            print(f"❌ Error al registrar turno cerrado: {e}")
            return False

    def closeEvent(self, event):
            # Cerrar conexión a la base de datos al salir
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'db_connection') and self.db_connection:
                self.db_connection.close()
            event.accept()

            # Añadir estas importaciones al principio del archivo


            # Reemplazar la función exportar_reporte existente con esta:

    def calcular_crudo(self):
        """Método de compatibilidad - redirige al nuevo método"""
        try:
            self.calcular_cierre_completo()
        except AttributeError:
            QMessageBox.information(self, "Información", "Use el botón 'Calcular Cierre' en su lugar.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en cálculo: {e}")

    def limpiar_crudo(self):
        """Método de compatibilidad - redirige al nuevo método"""
        try:
            self.limpiar_todo()
        except AttributeError:
            QMessageBox.information(self, "Información", "Use el botón 'Limpiar' en su lugar.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al limpiar: {e}")

    def verificar_calculo_correcto(self):
        """Función para verificar que los cálculos estén correctos"""
        try:
            from datetime import datetime

            print("\n" + "=" * 50)
            print("🔍 VERIFICACIÓN DE CÁLCULOS DEL SISTEMA")
            print("=" * 50)
            print(f"📅 Fecha verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Verificar que existan los valores calculados
            if not hasattr(self, 'valores_crudo'):
                print("❌ ERROR: No hay valores_crudo calculados")
                return False

            # Obtener valores de entrada
            ingreso_efectivo = float(self.txt_ingreso_efectivo.text() or '0')
            ingreso_tarjeta = float(self.txt_ingreso_tarjeta.text() or '0')
            ingreso_transferencia = float(self.txt_ingreso_transferencia.text() or '0')

            print(f"\n📊 VALORES DE ENTRADA:")
            print(f"   • Efectivo: Q{ingreso_efectivo:.2f}")
            print(f"   • Tarjeta: Q{ingreso_tarjeta:.2f}")
            print(f"   • Transferencia: Q{ingreso_transferencia:.2f}")

            # Verificar cálculos de impuestos
            venta_total = ingreso_efectivo + ingreso_tarjeta + ingreso_transferencia
            impuestos_esperados = venta_total * 0.16

            impuestos_calculados = (self.valores_crudo.get('impuestos_efectivo', 0) +
                                    self.valores_crudo.get('impuestos_transferencia', 0) +
                                    self.valores_crudo.get('impuestos_visa', 0))

            print(f"\n🧮 VERIFICACIÓN DE IMPUESTOS:")
            print(f"   • Venta total: Q{venta_total:.2f}")
            print(f"   • Impuestos esperados (16%): Q{impuestos_esperados:.2f}")
            print(f"   • Impuestos calculados: Q{impuestos_calculados:.2f}")
            print(f"   • ¿Coinciden? {'✅ SÍ' if abs(impuestos_esperados - impuestos_calculados) < 0.01 else '❌ NO'}")

            # Verificar totales
            totales_esperados = venta_total + impuestos_esperados
            totales_guardados = self.valores_crudo.get('totales', 0)

            print(f"\n📋 VERIFICACIÓN DE TOTALES:")
            print(f"   • Totales esperados (venta + impuestos): Q{totales_esperados:.2f}")
            print(f"   • Totales guardados: Q{totales_guardados:.2f}")
            print(f"   • ¿Coinciden? {'✅ SÍ' if abs(totales_esperados - totales_guardados) < 0.01 else '❌ NO'}")

            # Verificar que totales > venta (porque incluyen impuestos)
            print(f"\n🔍 VERIFICACIÓN LÓGICA:")
            print(f"   • ¿Totales > Venta neta? {'✅ SÍ' if totales_guardados > venta_total else '❌ NO'}")
            print(f"   • Diferencia: Q{totales_guardados - venta_total:.2f}")

            # Resultado final
            es_correcto = (abs(impuestos_esperados - impuestos_calculados) < 0.01 and
                           abs(totales_esperados - totales_guardados) < 0.01 and
                           totales_guardados > venta_total)

            print(f"\n🎯 RESULTADO FINAL:")
            if es_correcto:
                print("✅ TODOS LOS CÁLCULOS SON CORRECTOS")
            else:
                print("❌ HAY ERRORES EN LOS CÁLCULOS")
                print("💡 Recomendación: Recalcular el cierre")

            print("=" * 50)

            return es_correcto

        except Exception as e:
            print(f"❌ Error en verificación: {e}")
            return False

    def debug_valores_guardado(self):
        """Función para debug al momento de guardar"""
        try:
            from datetime import datetime

            print(f"\n🐛 DEBUG ANTES DE GUARDAR - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 40)

            if hasattr(self, 'valores_crudo'):
                print("📊 Valores que se van a guardar:")
                for key, value in self.valores_crudo.items():
                    print(f"   {key}: {value}")

                # Verificaciones importantes
                venta_neta = self.valores_crudo.get('venta_neta', 0)
                totales = self.valores_crudo.get('totales', 0)
                total_impuestos = (self.valores_crudo.get('impuestos_efectivo', 0) +
                                   self.valores_crudo.get('impuestos_transferencia', 0) +
                                   self.valores_crudo.get('impuestos_visa', 0))

                print(f"\n🔍 Verificaciones:")
                print(f"   • Venta neta: Q{venta_neta:.2f}")
                print(f"   • Total impuestos: Q{total_impuestos:.2f}")
                print(f"   • Totales a guardar: Q{totales:.2f}")
                print(f"   • ¿Totales incluyen impuestos? {'✅' if totales > venta_neta else '❌'}")

                return True
            else:
                print("❌ No hay valores_crudo para guardar")
                return False

        except Exception as e:
            print(f"❌ Error en debug: {e}")
            return False

    def reiniciar_sistema_completo(self):
        """Reinicia completamente el sistema después del cierre - COMO SI FUERA LA PRIMERA VEZ"""
        try:
            print("🔄 === INICIANDO REINICIO COMPLETO DEL SISTEMA ===")

            # PASO 1: Limpiar todas las variables en memoria
            self.limpiar_variables_memoria()

            # PASO 2: Resetear todos los campos de la interfaz
            self.resetear_interfaz_completa()

            # PASO 3: Limpiar datos temporales de BD (opcional)

            # PASO 4: Mostrar mensaje de confirmación
            QMessageBox.information(
                self,
                "✅ Sistema Reiniciado",
                """🔄 ¡El sistema se ha reiniciado completamente!

    📊 Estado actual:
    - Todos los campos en 0
    - Variables de memoria limpiadas  
    - Sistema listo para nuevo turno
    - Datos anteriores guardados en BD

    💡 El sistema está como si fuera la primera vez que lo abres."""
            )

            print("✅ === REINICIO COMPLETO FINALIZADO ===")
            return True

        except Exception as e:
            print(f"❌ Error en reinicio completo: {e}")
            QMessageBox.critical(self, "Error", f"Error al reiniciar sistema: {e}")
            return False

    def limpiar_variables_memoria(self):
        """Limpia TODAS las variables almacenadas en memoria"""
        try:
            print("🧹 Limpiando variables en memoria...")

            # Limpiar valores calculados
            if hasattr(self, 'valores_crudo'):
                delattr(self, 'valores_crudo')
                print("  ✅ valores_crudo eliminado")

            if hasattr(self, 'valores_neto'):
                delattr(self, 'valores_neto')
                print("  ✅ valores_neto eliminado")

            # Limpiar datos de efectivo inicial
            if hasattr(self, 'efectivo_inicial'):
                delattr(self, 'efectivo_inicial')
                print("  ✅ efectivo_inicial eliminado")

            # Limpiar datos de ventas
            if hasattr(self, 'ventas_efectivo'):
                delattr(self, 'ventas_efectivo')
                print("  ✅ ventas_efectivo eliminado")

            if hasattr(self, 'ventas_tarjeta'):
                delattr(self, 'ventas_tarjeta')
                print("  ✅ ventas_tarjeta eliminado")

            if hasattr(self, 'ventas_transferencia'):
                delattr(self, 'ventas_transferencia')
                print("  ✅ ventas_transferencia eliminado")

            # Limpiar flags de estado
            if hasattr(self, '_ejecutando_cierre_turno'):
                delattr(self, '_ejecutando_cierre_turno')
                print("  ✅ flag de cierre eliminado")

            # Limpiar cualquier otra variable temporal
            variables_a_limpiar = ['datos_cargados', 'cierre_calculado', 'ultimo_calculo', 'cache_datos']
            for var in variables_a_limpiar:
                if hasattr(self, var):
                    delattr(self, var)
                    print(f"  ✅ {var} eliminado")

            print("✅ Variables en memoria limpiadas")
            return True

        except Exception as e:
            print(f"❌ Error limpiando variables: {e}")
            return False

    def resetear_interfaz_completa(self):
        """Resetea TODOS los campos de la interfaz a 0 o valores iniciales - CORREGIDO"""
        try:
            print("🖥️ Reseteando interfaz completa...")

            # RESETEAR CAMPOS DE ENTRADA
            print("  🔄 Reseteando campos de entrada...")
            self.txt_ingreso_efectivo.setText("0.00")
            self.txt_ingreso_tarjeta.setText("0.00")
            self.txt_ingreso_transferencia.setText("0.00")
            self.txt_total_gastos.setText("0.00")
            self.txt_total_real.setText("0.00")
            self.txt_total_banco.setText("0.00")

            # DESBLOQUEAR CAMPOS PRIMERO (por si estaban bloqueados)
            self.txt_ingreso_efectivo.setReadOnly(False)
            self.txt_ingreso_tarjeta.setReadOnly(False)
            self.txt_ingreso_transferencia.setReadOnly(False)
            self.txt_total_gastos.setReadOnly(False)
            self.txt_total_real.setReadOnly(False)
            self.txt_total_banco.setReadOnly(False)

            # RESETEAR ESTILOS A NORMAL
            estilo_normal = """
                QLineEdit {
                    background-color: white;
                    border: 1px solid #cccccc;
                    color: black;
                    padding: 5px;
                }
            """
            self.txt_ingreso_efectivo.setStyleSheet(estilo_normal)
            self.txt_ingreso_tarjeta.setStyleSheet(estilo_normal)
            self.txt_ingreso_transferencia.setStyleSheet(estilo_normal)
            self.txt_total_gastos.setStyleSheet(estilo_normal)
            self.txt_total_real.setStyleSheet(estilo_normal)
            self.txt_total_banco.setStyleSheet(estilo_normal)

            # RESETEAR TABLAS DE RESULTADOS
            print("  📊 Reseteando tablas...")

            # ✅ CORRECCIÓN: Tabla de Ingresos Netos (nombre correcto)
            if hasattr(self, 'tabla_ingresos_netos'):
                try:
                    for row in range(self.tabla_ingresos_netos.rowCount()):
                        self.tabla_ingresos_netos.item(row, 1).setText("0.00")
                    print("    ✅ tabla_ingresos_netos reseteada")
                except Exception as e:
                    print(f"    ⚠️ Error en tabla_ingresos_netos: {e}")

            # ✅ CORRECCIÓN: Tabla de Deducciones (nombre correcto en tu código)
            if hasattr(self, 'tabla_deducciones'):
                try:
                    for row in range(self.tabla_deducciones.rowCount()):
                        self.tabla_deducciones.item(row, 1).setText("0.00")
                    print("    ✅ tabla_deducciones reseteada")
                except Exception as e:
                    print(f"    ⚠️ Error en tabla_deducciones: {e}")

            # ✅ CORRECCIÓN: Tabla de Resultado Final
            if hasattr(self, 'tabla_resultado_final'):
                try:
                    for row in range(self.tabla_resultado_final.rowCount()):
                        self.tabla_resultado_final.item(row, 1).setText("0.00")
                        # Quitar colores
                        self.tabla_resultado_final.item(row, 1).setForeground(Qt.black)
                    print("    ✅ tabla_resultado_final reseteada")
                except Exception as e:
                    print(f"    ⚠️ Error en tabla_resultado_final: {e}")

            # ✅ RESETEAR CONFIRMACIÓN DE DINERO FÍSICO
            if hasattr(self, 'txt_efectivo_fisico'):
                self.txt_efectivo_fisico.setText("0.00")
            if hasattr(self, 'txt_cheques_fisicos'):
                self.txt_cheques_fisicos.setText("0.00")

            # ✅ RESETEAR TABLA DE VERIFICACIÓN
            if hasattr(self, 'tabla_verificacion'):
                try:
                    self.tabla_verificacion.item(0, 1).setText("0.00")  # Efectivo Calculado
                    self.tabla_verificacion.item(1, 1).setText("0.00")  # Efectivo Físico
                    self.tabla_verificacion.item(2, 1).setText("0.00")  # Diferencia
                    self.tabla_verificacion.item(3, 1).setText("⚠️ Sin verificar")  # Estado
                    print("    ✅ tabla_verificacion reseteada")
                except Exception as e:
                    print(f"    ⚠️ Error en tabla_verificacion: {e}")

            # ✅ RESETEAR ESTADO DE CUADRE
            if hasattr(self, 'lbl_estado_cuadre'):
                self.lbl_estado_cuadre.setText("⚠️ Sin verificar")
                self.lbl_estado_cuadre.setStyleSheet(
                    "background-color: #FFF3CD; border: 1px solid #FFEAA7; padding: 8px; border-radius: 4px;")

            # ✅ RESETEAR BOTÓN DE CONFIRMACIÓN
            if hasattr(self, 'btn_confirmar_cuadre'):
                self.btn_confirmar_cuadre.setText("Confirmar Cuadre")
                self.btn_confirmar_cuadre.setEnabled(False)
                self.btn_confirmar_cuadre.setStyleSheet("")

            print("✅ Interfaz completamente reseteada")
            return True

        except Exception as e:
            print(f"❌ Error reseteando interfaz: {e}")
            import traceback
            traceback.print_exc()
            return False

    def limpiar_datos_temporales_bd(self):
        """Limpia datos temporales del día actual en BD (OPCIONAL)"""
        try:
            print("🗄️ Limpiando datos temporales en BD...")

            # OPCIÓN 1: No limpiar nada de BD (recomendado para auditoría)
            print("  ℹ️ Manteniendo todos los datos en BD para auditoría")

            # OPCIÓN 2: Si quieres limpiar tabla de productos vendidos del día (descomenta si es necesario)
            # fecha_hoy = date.today().strftime('%Y-%m-%d')
            # self.cursor.execute("DELETE FROM productos_vendidos WHERE DATE(fecha) = %s", (fecha_hoy,))
            # self.db_connection.commit()
            # print(f"  ✅ Productos vendidos del {fecha_hoy} eliminados")

            return True

        except Exception as e:
            print(f"❌ Error limpiando datos temporales: {e}")
            return False

    def verificar_calculos(self):
        """FUNCIÓN PARA VERIFICAR Y DEBUGGEAR LOS CÁLCULOS"""
        print("🔍 === VERIFICACIÓN DETALLADA DE CÁLCULOS ===")

        if not hasattr(self, 'valores_neto'):
            print("❌ No hay valores calculados para verificar")
            return

        # ✅ MOSTRAR TODOS LOS VALORES CALCULADOS
        print("\n📊 VALORES CALCULADOS:")
        print("=" * 50)

        # Ingresos netos
        print("💰 INGRESOS NETOS:")
        print(f"   - Efectivo neto: Q{self.valores_neto['efectivo_neto']:.2f}")
        print(f"   - Tarjeta neto: Q{self.valores_neto['tarjeta_neto']:.2f}")
        print(f"   - Transferencia neto: Q{self.valores_neto['transferencia_neto']:.2f}")
        print(f"   - TOTAL INGRESOS NETOS: Q{self.valores_neto['total_ingresos_netos']:.2f}")

        # Deducciones
        print("\n📉 DEDUCCIONES:")
        print(f"   - Gastos: Q{self.valores_neto['total_gastos']:.2f}")
        print(f"   - Total impuestos: Q{self.valores_neto['total_impuestos']:.2f}")
        print(f"   - Comisiones bancarias: Q{self.valores_neto['comisiones_bancarias']:.2f}")
        print(f"   - Comisiones doctores: Q{self.valores_neto['comisiones']:.2f}")

        # Cálculo manual paso a paso
        print("\n🧮 CÁLCULO MANUAL DEL TOTAL A DEPOSITAR VENTAS:")
        print("=" * 50)

        total_ingresos = self.valores_neto['total_ingresos_netos']
        gastos = self.valores_neto['total_gastos']
        comisiones_bancarias = self.valores_neto['comisiones_bancarias']
        comisiones = self.valores_neto['comisiones']

        print(f"Total ingresos netos:     Q{total_ingresos:.2f}")
        print(f"(-) Gastos:               Q{gastos:.2f}")
        print(f"(-) Comisiones bancarias: Q{comisiones_bancarias:.2f}")
        print(f"(-) Comisiones doctores:  Q{comisiones:.2f}")
        print("-" * 40)

        total_depositar_calculado = total_ingresos - gastos - comisiones_bancarias - comisiones
        print(f"TOTAL A DEPOSITAR VENTAS: Q{total_depositar_calculado:.2f}")

        # Comparar con el valor que aparece en pantalla
        total_pantalla = self.valores_neto.get('total_depositar_ventas', 0)
        print(f"Total en pantalla:        Q{total_pantalla:.2f}")

        diferencia = total_pantalla - total_depositar_calculado
        if abs(diferencia) > 0.01:
            print(f"⚠️  DIFERENCIA ENCONTRADA: Q{diferencia:.2f}")
        else:
            print("✅ Los cálculos coinciden")

        # Verificar valores de entrada
        print("\n🔍 VERIFICACIÓN DE VALORES DE ENTRADA:")
        print("=" * 50)

        if hasattr(self, 'valores_crudo'):
            print("Ventas originales:")
            print(f"   - Ventas efectivo: Q{self.valores_crudo.get('ventas_efectivo', 0):.2f}")
            print(f"   - Ventas tarjeta: Q{self.valores_crudo.get('ventas_tarjeta', 0):.2f}")
            print(f"   - Ventas transferencia: Q{self.valores_crudo.get('ventas_transferencia', 0):.2f}")

            # Verificar comisiones bancarias
            ventas_tarjeta = self.valores_crudo.get('ventas_tarjeta', 0)
            comisiones_calculadas = ventas_tarjeta * 0.06
            print(f"\nComisiones bancarias:")
            print(f"   - Ventas tarjeta: Q{ventas_tarjeta:.2f}")
            print(f"   - 6% calculado: Q{comisiones_calculadas:.2f}")
            print(f"   - En valores_neto: Q{self.valores_neto['comisiones_bancarias']:.2f}")

            if abs(comisiones_calculadas - self.valores_neto['comisiones_bancarias']) > 0.01:
                print("⚠️  DIFERENCIA EN COMISIONES BANCARIAS")

        # Mostrar impuestos detallados
        print("\n💸 IMPUESTOS DETALLADOS:")
        print("=" * 50)
        if 'impuestos_efectivo' in self.valores_neto:
            print(f"   - Impuestos efectivo: Q{self.valores_neto['impuestos_efectivo']:.2f}")
            print(f"   - Impuestos POS: Q{self.valores_neto['impuesto_pos']:.2f}")
            print(f"   - Impuestos empresa tarjeta: Q{self.valores_neto['impuesto_empresa_tarjeta']:.2f}")
            print(f"   - Impuestos transferencia: Q{self.valores_neto['impuestos_transferencia']:.2f}")

            suma_impuestos = (self.valores_neto['impuestos_efectivo'] +
                              self.valores_neto['impuesto_pos'] +
                              self.valores_neto['impuesto_empresa_tarjeta'] +
                              self.valores_neto['impuestos_transferencia'])
            print(f"   - SUMA MANUAL: Q{suma_impuestos:.2f}")
            print(f"   - TOTAL IMPUESTOS: Q{self.valores_neto['total_impuestos']:.2f}")

        print("\n🎯 VALORES FINALES:")
        print("=" * 50)
        print(f"Total a depositar ventas:    Q{self.valores_neto.get('total_depositar_ventas', 0):.2f}")
        print(f"Total a depositar impuestos: Q{self.valores_neto.get('total_depositar_impuestos', 0):.2f}")
        print(f"Total final:                 Q{self.valores_neto.get('total_final', 0):.2f}")

        # Si la diferencia es Q630.84, verificar de dónde puede venir
        if abs(total_depositar_calculado - 630.84) < 1.0:
            print(f"\n🔍 ANÁLISIS DE LA DIFERENCIA CON Q630.84:")
            diferencia_630 = 630.84 - total_depositar_calculado
            print(f"Diferencia con Q630.84: Q{diferencia_630:.2f}")

            if abs(diferencia_630 - 35.08) < 1.0:
                print("💡 Posible causa: Las comisiones bancarias están mal calculadas")
                print("   Debería ser 36.00 pero tal vez se está usando otro valor")
            elif abs(diferencia_630 - 16.92) < 1.0:
                print("💡 Posible causa: Se está usando el total_banco (282) en lugar de ventas_tarjeta (600)")
                print("   282 * 0.06 = 16.92, pero debería ser 600 * 0.06 = 36.00")

        print("\n✅ === VERIFICACIÓN COMPLETADA ===")

    def agregarcierre(self, nombre_producto, cantidad, tarjeta, efectivo, monto_total, fecha_hora, usuario,
                      id_caja=None):
        """
        Método modificado para manejar ventas normales y de ajuste - REEMPLAZAR COMPLETO
        """
        try:
            if not self.db_connection:
                print("❌ No hay conexión a la base de datos para agregar venta")
                return False

            # ================================================================
            # DETECTAR SI ES VENTA DE AJUSTE
            # ================================================================
            es_ajuste = False
            fecha_original = fecha_hora
            justificacion = None
            usuario_ajuste = None

            try:
                from .ventanaFuncional import VentanaFuncional

                # Verificar si hay info de ajuste guardada
                if hasattr(VentanaFuncional, '_es_venta_ajuste') and VentanaFuncional._es_venta_ajuste:
                    es_ajuste = True
                    fecha_original = VentanaFuncional._fecha_ajuste or fecha_hora
                    justificacion = VentanaFuncional._motivo_ajuste or ""
                    usuario_ajuste = usuario

                    print(f"🔧 Registrando VENTA DE AJUSTE:")
                    print(f"   - Fecha original: {fecha_original}")
                    print(f"   - Justificación: {justificacion}")
                    print(f"   - Usuario ajuste: {usuario_ajuste}")
                else:
                    print(f"💰 Registrando venta normal: {nombre_producto} - Q{monto_total:.2f}")

            except Exception as e:
                print(f"⚠️ Error detectando ajuste: {e}")
                # Continuar como venta normal

            # ================================================================
            # PREPARAR CONSULTA SQL CON CAMPOS DE AJUSTE
            # ================================================================
            if es_ajuste:
                query = """
                        INSERT INTO cierre (nombre, cantidad, tarjeta, efectivo, monto, fecha, usuario, id_caja,
                                            es_ajuste, justificacion, fecha_original, usuario_ajuste, fecha_ajuste)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()) \
                        """

                values = (
                    nombre_producto,  # nombre
                    cantidad,  # cantidad
                    float(tarjeta),  # tarjeta
                    float(efectivo),  # efectivo
                    float(monto_total),  # monto
                    fecha_original,  # fecha (fecha original de la venta)
                    usuario,  # usuario
                    id_caja,  # id_caja
                    True,  # es_ajuste
                    justificacion,  # justificacion
                    fecha_original,  # fecha_original
                    usuario_ajuste  # usuario_ajuste
                )
            else:
                # Consulta normal (sin campos de ajuste)
                query = """
                        INSERT INTO cierre (nombre, cantidad, tarjeta, efectivo, monto, fecha, usuario, id_caja,
                                            es_ajuste, justificacion, fecha_original, usuario_ajuste, fecha_ajuste)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                        """

                values = (
                    nombre_producto,  # nombre
                    cantidad,  # cantidad
                    float(tarjeta),  # tarjeta
                    float(efectivo),  # efectivo
                    float(monto_total),  # monto
                    fecha_hora,  # fecha
                    usuario,  # usuario
                    id_caja,  # id_caja
                    False,  # es_ajuste
                    None,  # justificacion
                    None,  # fecha_original
                    None,  # usuario_ajuste
                    None  # fecha_ajuste
                )

            # ================================================================
            # EJECUTAR CONSULTA
            # ================================================================
            self.cursor.execute(query, values)
            self.db_connection.commit()

            # ================================================================
            # MENSAJE DE CONFIRMACIÓN
            # ================================================================
            if es_ajuste:
                print(f"✅ VENTA DE AJUSTE registrada exitosamente:")
                print(f"   - Producto: {nombre_producto}")
                print(f"   - Cantidad: {cantidad}")
                print(f"   - Efectivo: Q{efectivo:.2f}")
                print(f"   - Tarjeta: Q{tarjeta:.2f}")
                print(f"   - Total: Q{monto_total:.2f}")
                print(f"   - Fecha original: {fecha_original}")
                print(f"   - Justificación: {justificacion}")
                print(f"   - Usuario: {usuario}")
            else:
                print(f"✅ Venta normal registrada exitosamente:")
                print(f"   - Producto: {nombre_producto}")
                print(f"   - Cantidad: {cantidad}")
                print(f"   - Efectivo: Q{efectivo:.2f}")
                print(f"   - Tarjeta: Q{tarjeta:.2f}")
                print(f"   - Total: Q{monto_total:.2f}")
                print(f"   - Usuario: {usuario}")

            return True

        except Exception as e:
            print(f"❌ Error al agregar venta al cierre: {e}")
            # Hacer rollback en caso de error
            try:
                self.db_connection.rollback()
            except:
                pass
            return False

    def agregar_producto_cierre(self, producto, cantidad, precio_unitario, metodo_pago, usuario):
        """
        Método alternativo más detallado para agregar productos al cierre
        """
        try:
            from datetime import datetime

            # Calcular montos según método de pago
            monto_total = cantidad * precio_unitario

            if metodo_pago.lower() == 'efectivo':
                efectivo = monto_total
                tarjeta = 0.0
            elif metodo_pago.lower() == 'tarjeta':
                efectivo = 0.0
                tarjeta = monto_total
            else:
                # Pago mixto u otro tipo
                efectivo = monto_total / 2  # Por ejemplo, mitad y mitad
                tarjeta = monto_total / 2

            # Obtener timestamp actual
            fecha_hora = datetime.now()

            # Llamar al método principal
            return self.agregarcierre(
                nombre_producto=producto,
                cantidad=cantidad,
                tarjeta=tarjeta,
                efectivo=efectivo,
                monto_total=monto_total,
                fecha_hora=fecha_hora,
                usuario=usuario
            )

        except Exception as e:
            print(f"❌ Error en agregar_producto_cierre: {e}")
            return False

    def verificar_tabla_cierre(self):
        """
        Verifica que la tabla 'cierre' exista y tenga las columnas correctas
        """
        try:
            # Crear la tabla si no existe
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS cierre
                                (
                                    id
                                    INT
                                    AUTO_INCREMENT
                                    PRIMARY
                                    KEY,
                                    nombre
                                    VARCHAR
                                (
                                    255
                                ) NOT NULL,
                                    cantidad INT NOT NULL DEFAULT 1,
                                    tarjeta DECIMAL
                                (
                                    10,
                                    2
                                ) DEFAULT 0.00,
                                    efectivo DECIMAL
                                (
                                    10,
                                    2
                                ) DEFAULT 0.00,
                                    monto DECIMAL
                                (
                                    10,
                                    2
                                ) NOT NULL,
                                    fecha DATETIME NOT NULL,
                                    usuario VARCHAR
                                (
                                    100
                                ),
                                    id_caja INT DEFAULT NULL,
                                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                    )
                                """)

            self.db_connection.commit()
            print("✅ Tabla 'cierre' verificada/creada correctamente")
            return True

        except Exception as e:
            print(f"❌ Error al verificar tabla cierre: {e}")
            return False

    def verificar_y_reparar_tabla_cierre_neto(self):
        """
        Verifica que la tabla cierre_neto esté correctamente creada y la repara si es necesario
        """
        try:
            print("🔍 Verificando tabla cierre_neto...")

            # Verificar si la tabla existe
            self.cursor.execute("SHOW TABLES LIKE 'cierre_neto'")
            tabla_existe = self.cursor.fetchone()

            if not tabla_existe:
                print("⚠️  Tabla cierre_neto no existe, creándola...")
                self.crear_tabla_cierre_neto_completa()
            else:
                print("✅ Tabla cierre_neto existe")

            # Verificar estructura de la tabla
            self.cursor.execute("DESCRIBE cierre_neto")
            columnas = self.cursor.fetchall()

            columnas_existentes = [col[0] for col in columnas]
            columnas_requeridas = [
                'id', 'fecha', 'efectivo_neto', 'tarjeta_neto', 'transferencia_neto',
                'total_ingresos_netos', 'total_gastos', 'total_impuestos',
                'comisiones', 'total_deducciones', 'resultado_neto', 'fecha_registro'
            ]

            print(f"📊 Columnas existentes: {columnas_existentes}")

            # Verificar columnas faltantes
            columnas_faltantes = [col for col in columnas_requeridas if col not in columnas_existentes]

            if columnas_faltantes:
                print(f"⚠️  Columnas faltantes: {columnas_faltantes}")
                for columna in columnas_faltantes:
                    if columna == 'fecha_registro':
                        self.cursor.execute(
                            f"ALTER TABLE cierre_neto ADD COLUMN {columna} TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    else:
                        self.cursor.execute(f"ALTER TABLE cierre_neto ADD COLUMN {columna} DECIMAL(10,2) DEFAULT 0.00")
                    print(f"✅ Columna {columna} agregada")

            # Verificar permisos de escritura con una prueba
            try:
                test_fecha = '1900-01-01'  # Fecha de prueba que no interfiera
                self.cursor.execute("DELETE FROM cierre_neto WHERE fecha = %s", (test_fecha,))
                self.cursor.execute("""
                                    INSERT INTO cierre_neto
                                    (fecha, efectivo_neto, tarjeta_neto, transferencia_neto, total_ingresos_netos,
                                     total_gastos, total_impuestos, comisiones, total_deducciones, resultado_neto)
                                    VALUES (%s, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                                    """, (test_fecha,))
                self.cursor.execute("DELETE FROM cierre_neto WHERE fecha = %s", (test_fecha,))
                self.db_connection.commit()
                print("✅ Permisos de escritura verificados")
            except Exception as e:
                print(f"❌ Error de permisos: {e}")
                raise e

            print("✅ Tabla cierre_neto verificada y lista para usar")
            return True

        except Exception as e:
            print(f"❌ Error al verificar tabla: {e}")
            QMessageBox.critical(self, "Error", f"Error al verificar tabla cierre_neto: {e}")
            return False

    def crear_tabla_cierre_neto_completa(self):
        """
        Crea la tabla cierre_neto con todas las columnas necesarias
        """
        try:
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS cierre_neto
                                (
                                    id
                                    INT
                                    AUTO_INCREMENT
                                    PRIMARY
                                    KEY,
                                    fecha
                                    DATE
                                    NOT
                                    NULL,
                                    efectivo_neto
                                    DECIMAL
                                (
                                    10,
                                    2
                                ) NOT NULL DEFAULT 0.00,
                                    tarjeta_neto DECIMAL
                                (
                                    10,
                                    2
                                ) NOT NULL DEFAULT 0.00,
                                    transferencia_neto DECIMAL
                                (
                                    10,
                                    2
                                ) NOT NULL DEFAULT 0.00,
                                    total_ingresos_netos DECIMAL
                                (
                                    10,
                                    2
                                ) NOT NULL DEFAULT 0.00,
                                    total_gastos DECIMAL
                                (
                                    10,
                                    2
                                ) NOT NULL DEFAULT 0.00,
                                    total_impuestos DECIMAL
                                (
                                    10,
                                    2
                                ) NOT NULL DEFAULT 0.00,
                                    comisiones DECIMAL
                                (
                                    10,
                                    2
                                ) NOT NULL DEFAULT 0.00,
                                    total_deducciones DECIMAL
                                (
                                    10,
                                    2
                                ) NOT NULL DEFAULT 0.00,
                                    resultado_neto DECIMAL
                                (
                                    10,
                                    2
                                ) NOT NULL DEFAULT 0.00,
                                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    UNIQUE KEY unique_fecha
                                (
                                    fecha
                                )
                                    )
                                """)

            self.db_connection.commit()
            print("✅ Tabla cierre_neto creada correctamente")
            return True

        except Exception as e:
            print(f"❌ Error al crear tabla: {e}")
            return False



    def abrir_ventana_denominaciones(self):
        """Abrir ventana para ingresar denominaciones físicas"""
        try:
            from .ventana_denominaciones import VentanaDenominaciones
            self.ventana_denominaciones = VentanaDenominaciones(self)
            self.ventana_denominaciones.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al abrir ventana: {e}")

    def actualizar_efectivo_fisico(self, total_efectivo):
        """Recibir el total de efectivo físico desde la ventana de denominaciones"""
        try:
            # Actualizar el label de efectivo físico
            self.lbl_efectivo_fisico_total.setText(f"Efectivo físico: Q{total_efectivo:.2f}")

            # Actualizar también en la tabla de verificación
            if hasattr(self, 'tabla_verificacion'):
                self.tabla_verificacion.item(1, 1).setText(f"{total_efectivo:.2f}")

            # Verificar cuadre automáticamente
            self.verificar_cuadre()

            print(f"✅ Efectivo físico actualizado: Q{total_efectivo:.2f}")

        except Exception as e:
            print(f"❌ Error actualizando efectivo físico: {e}")

    def obtener_total_efectivo_fisico(self):
        """Obtener el total de efectivo físico (modificado para usar el label)"""
        try:
            # Extraer el valor del label
            texto = self.lbl_efectivo_fisico_total.text()
            # Buscar el patrón "Q" seguido del número
            import re
            match = re.search(r'Q([\d.]+)', texto)
            if match:
                return float(match.group(1))
            return 0.0
        except:
            return 0.0


import sys
from datetime import datetime

import pymysql
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QDateEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QGroupBox, QFormLayout, QMessageBox,
                             QDialog, QLineEdit, QDialogButtonBox, QFileDialog)
from PyQt5.QtCore import Qt, QDate
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


class PagoComisionDialog(QDialog):
    """Diálogo para registrar el pago de comisiones"""

    def __init__(self, doctor, total_comision, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Pago de Comisión")
        self.resize(400, 200)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # Campos del formulario
        self.lbl_doctor = QLabel(doctor)
        self.txt_monto = QLineEdit()
        self.txt_monto.setText(f"{total_comision:.2f}")
        self.fecha_pago = QDateEdit()
        self.fecha_pago.setCalendarPopup(True)
        self.fecha_pago.setDate(QDate.currentDate())
        self.txt_observaciones = QLineEdit()

        form_layout.addRow("Doctor:", self.lbl_doctor)
        form_layout.addRow("Monto a Pagar (Q):", self.txt_monto)
        form_layout.addRow("Fecha de Pago:", self.fecha_pago)
        form_layout.addRow("Observaciones:", self.txt_observaciones)

        layout.addLayout(form_layout)

        # Botones
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)

    def get_datos(self):
        return {
            'monto': float(self.txt_monto.text()),
            'fecha': self.fecha_pago.date().toString("yyyy-MM-dd"),
            'observaciones': self.txt_observaciones.text()
        }


class VentasComisionesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Ventas y Comisiones")
        self.setGeometry(100, 100, 900, 600)

        self.initUI()
        self.conectar_bd()
        self.cargar_doctores()
        self.doctor_actual = "Todos"
        self.comisiones_calculadas = []

    def initUI(self):
        # Widget principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Grupo de filtros
        filtros_group = QGroupBox("Filtros de Búsqueda")
        filtros_layout = QHBoxLayout()

        # Layout para doctores
        doctor_layout = QFormLayout()
        self.doctor_combo = QComboBox()
        doctor_layout.addRow("Doctor:", self.doctor_combo)

        # Layout para fechas
        fechas_layout = QFormLayout()
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))  # Por defecto, último mes

        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDate(QDate.currentDate())

        fechas_layout.addRow("Desde:", self.fecha_desde)
        fechas_layout.addRow("Hasta:", self.fecha_hasta)

        # Botón de consulta
        btn_layout = QVBoxLayout()
        self.btn_consultar = QPushButton("Consultar")
        self.btn_consultar.clicked.connect(self.consultar_ventas)
        btn_layout.addWidget(self.btn_consultar)
        btn_layout.addStretch()

        # Agregar layouts al grupo de filtros
        filtros_layout.addLayout(doctor_layout, 1)
        filtros_layout.addLayout(fechas_layout, 2)
        filtros_layout.addLayout(btn_layout, 1)
        filtros_group.setLayout(filtros_layout)

        # Tabla de resultados - SIN COLUMNA TIPO
        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(7)
        self.tabla_ventas.setHorizontalHeaderLabels(
            ["Cant", "Descripción", "Monto", "Impuestos", "Neto", "Comisión %", "Total Comisión"])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Sección de totales
        totales_group = QGroupBox("Totales")
        totales_layout = QFormLayout()

        self.lbl_total_ventas = QLabel("Q 0.00")
        self.lbl_total_comision = QLabel("Q 0.00")
        self.lbl_comisiones_pendientes = QLabel("Q 0.00")

        totales_layout.addRow("TOTAL VENTAS:", self.lbl_total_ventas)
        totales_layout.addRow("PAGO COMISIONES:", self.lbl_total_comision)
        totales_layout.addRow("COMISIONES PENDIENTES POR TONICC:", self.lbl_comisiones_pendientes)

        totales_group.setLayout(totales_layout)

        # Botón para registrar pago
        self.btn_registrar_pago = QPushButton("Registrar Pago de Comisión")
        self.btn_registrar_pago.clicked.connect(self.registrar_pago_comision)
        self.btn_registrar_pago.setEnabled(False)  # Inicialmente deshabilitado

        # Botón para ver historial de pagos
        self.btn_historial = QPushButton("Ver Historial de Pagos")
        self.btn_historial.clicked.connect(self.ver_historial_pagos)

        # Botón para generar PDF
        self.btn_generar_pdf = QPushButton("Generar PDF")
        self.btn_generar_pdf.clicked.connect(self.generar_pdf)
        self.btn_generar_pdf.setEnabled(False)  # Inicialmente deshabilitado

        # Layout para botones de acción
        btn_actions_layout = QHBoxLayout()
        btn_actions_layout.addWidget(self.btn_registrar_pago)
        btn_actions_layout.addWidget(self.btn_historial)
        btn_actions_layout.addWidget(self.btn_generar_pdf)

        # Agregar todo al layout principal
        main_layout.addWidget(filtros_group)
        main_layout.addWidget(self.tabla_ventas)
        main_layout.addWidget(totales_group)
        main_layout.addLayout(btn_actions_layout)

    def conectar_bd(self):
        try:
            self.conexion = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",
                database="bdhidrocolon"
            )

            print("Conexión exitosa a MySQL")
            self.crear_tabla_pagos_comisiones()
        except Exception as e:
            print(f"Error al conectar a MySQL: {e}")
            QMessageBox.critical(self, "Error de Conexión",
                                 f"No se pudo conectar a la base de datos: {e}")

    def crear_tabla_pagos_comisiones(self):
        """Crear la tabla de pagos_comisiones si no existe"""
        try:
            if hasattr(self, 'conexion') and self.conexion.open:
                cursor = self.conexion.cursor()

                sql_crear_tabla = """
                CREATE TABLE IF NOT EXISTS pagos_comisiones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    doctor VARCHAR(100) NOT NULL,
                    monto DECIMAL(10,2) NOT NULL,
                    fecha DATE NOT NULL,
                    fecha_desde DATE NOT NULL,
                    fecha_hasta DATE NOT NULL,
                    observaciones TEXT,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """

                cursor.execute(sql_crear_tabla)
                self.conexion.commit()
                cursor.close()
                print("Tabla pagos_comisiones verificada/creada correctamente")
        except Exception as e:
            print(f"Error al crear tabla pagos_comisiones: {e}")

    def cargar_doctores(self):
        try:
            if hasattr(self, 'conexion') and self.conexion.open:
                cursor = self.conexion.cursor()

                # Solo obtener doctores de la tabla ventas
                cursor.execute("SELECT DISTINCT doctor FROM ventas WHERE doctor IS NOT NULL ORDER BY doctor")
                doctores = cursor.fetchall()

                self.doctor_combo.clear()
                self.doctor_combo.addItem("Todos")
                for doctor in doctores:
                    self.doctor_combo.addItem(doctor[0])

                cursor.close()
        except Exception as e:
            print(f"Error al cargar doctores: {e}")
            QMessageBox.warning(self, "Error", f"Error al cargar la lista de doctores: {e}")

    def consultar_ventas(self):
        try:
            if hasattr(self, 'conexion') and self.conexion.open:
                cursor = self.conexion.cursor()

                # Preparar los filtros
                self.doctor_actual = self.doctor_combo.currentText()
                fecha_desde = self.fecha_desde.date().toString("yyyy-MM-dd")
                fecha_hasta = self.fecha_hasta.date().toString("yyyy-MM-dd")

                # CONSULTA MEJORADA: Busca comisión en medicamentos Y en terapias
                print("=== DEBUGGING CONSULTA ===")
                sql = """
                SELECT v.id, v.producto, v.cantidad, v.total, v.fecha, v.doctor, 
                       m.nombre as med_nombre, m.comision as med_comision,
                       t.nombre as ter_nombre, t.comision as ter_comision
                FROM ventas v
                LEFT JOIN medicamentos m ON v.producto = m.nombre
                LEFT JOIN terapias t ON v.producto = t.nombre
                WHERE v.fecha BETWEEN %s AND %s AND v.accion = 'Venta'
                """
                params = [fecha_desde, fecha_hasta]

                if self.doctor_actual != "Todos":
                    sql += " AND v.doctor = %s"
                    params.append(self.doctor_actual)

                sql += " ORDER BY v.fecha, v.producto"

                print(f"SQL: {sql}")
                print(f"Params: {params}")

                cursor.execute(sql, params)
                resultados = cursor.fetchall()

                print(f"Resultados encontrados: {len(resultados)}")
                for row in resultados:
                    print(f"Producto: {row[1]}, Med_Comision: {row[7]}, Ter_Comision: {row[9]}")

                # Verificar pagos existentes
                if self.doctor_actual != "Todos":
                    sql_pagos = """
                    SELECT COUNT(*) FROM pagos_comisiones 
                    WHERE doctor = %s AND fecha_desde <= %s AND fecha_hasta >= %s
                    """
                    cursor.execute(sql_pagos, [self.doctor_actual, fecha_hasta, fecha_desde])
                    pagos_existentes = cursor.fetchone()

                    if pagos_existentes and pagos_existentes[0] > 0:
                        QMessageBox.information(
                            self,
                            "Pagos Existentes",
                            f"Ya existen pagos registrados para {self.doctor_actual} en este período. " +
                            "Se mostrarán los datos igualmente."
                        )

                # Mostrar resultados en la tabla
                self.mostrar_resultados(resultados)

                # Habilitar botones si hay resultados
                hay_resultados = len(resultados) > 0
                self.btn_registrar_pago.setEnabled(hay_resultados and self.doctor_actual != "Todos")
                self.btn_generar_pdf.setEnabled(hay_resultados)

                cursor.close()
        except Exception as e:
            print(f"Error al consultar ventas: {e}")
            QMessageBox.warning(self, "Error", f"Error al consultar ventas: {e}")

    def mostrar_resultados(self, resultados):
        # Limpiar la tabla
        self.tabla_ventas.setRowCount(0)
        self.comisiones_calculadas = []

        # Variables para calcular totales
        total_ventas = 0
        total_comision = 0

        # Diccionario para agrupar resultados similares
        agregado = {}

        # Procesar resultados
        for venta in resultados:
            producto = venta[1]  # v.producto

            print(f"=== PROCESANDO: {producto} ===")

            # LÓGICA MEJORADA: Decidir si es medicamento o terapia
            med_comision = venta[7]  # m.comision
            ter_comision = venta[9]  # t.comision

            # Prioridad: Si está en terapias, usar esa comisión. Si no, usar medicamentos
            if ter_comision is not None:
                porcentaje_comision = ter_comision
                tipo_producto = "Terapia"
                print(f"Es TERAPIA - Comisión: {ter_comision}%")
            elif med_comision is not None:
                porcentaje_comision = med_comision
                tipo_producto = "Medicamento"
                print(f"Es MEDICAMENTO - Comisión: {med_comision}%")
            else:
                porcentaje_comision = 0
                tipo_producto = "Sin clasificar"
                print(f"SIN CLASIFICAR - No encontrado en medicamentos ni terapias")

            # Calcular impuestos (12%)
            if venta[3] is not None:  # v.total
                impuestos = venta[3] * 0.12
                neto = venta[3] - impuestos
            else:
                impuestos = 0
                neto = 0

            # Calcular comisión
            comision = neto * (porcentaje_comision / 100) if porcentaje_comision > 0 else 0
            print(f"Neto: Q{neto:.2f}, Porcentaje: {porcentaje_comision}%, Comisión: Q{comision:.2f}")

            # Agrupar por producto
            clave = f"{producto}"
            if clave in agregado:
                agregado[clave]['cantidad'] += venta[2]  # v.cantidad
                agregado[clave]['total'] += venta[3] if venta[3] is not None else 0
                agregado[clave]['impuestos'] += impuestos
                agregado[clave]['neto'] += neto
                agregado[clave]['comision'] += comision
            else:
                agregado[clave] = {
                    'cantidad': venta[2],
                    'producto': producto,
                    'total': venta[3] if venta[3] is not None else 0,
                    'impuestos': impuestos,
                    'neto': neto,
                    'porcentaje_comision': porcentaje_comision,
                    'comision': comision,
                    'tipo': tipo_producto  # Guardamos el tipo para referencia
                }

            # Guardar detalle de la venta para el registro de pago
            self.comisiones_calculadas.append({
                'id_venta': venta[0],
                'producto': producto,
                'cantidad': venta[2],
                'total': venta[3] if venta[3] is not None else 0,
                'comision': comision,
                'doctor': venta[5],
                'tipo': tipo_producto
            })

        # Mostrar resultados agrupados
        for fila, (_, datos) in enumerate(agregado.items()):
            self.tabla_ventas.insertRow(fila)

            # Insertar datos en la tabla
            self.tabla_ventas.setItem(fila, 0, QTableWidgetItem(str(datos['cantidad'])))
            self.tabla_ventas.setItem(fila, 1, QTableWidgetItem(datos['producto']))
            self.tabla_ventas.setItem(fila, 2, QTableWidgetItem(f"Q {datos['total']:.2f}"))
            self.tabla_ventas.setItem(fila, 3, QTableWidgetItem(f"Q {datos['impuestos']:.2f}"))
            self.tabla_ventas.setItem(fila, 4, QTableWidgetItem(f"Q {datos['neto']:.2f}"))
            self.tabla_ventas.setItem(fila, 5, QTableWidgetItem(f"{datos['porcentaje_comision']}%"))
            self.tabla_ventas.setItem(fila, 6, QTableWidgetItem(f"Q {datos['comision']:.2f}"))

            print(
                f"FILA {fila}: {datos['producto']} ({datos['tipo']}) - {datos['porcentaje_comision']}% - Q{datos['comision']:.2f}")

            # Acumular totales
            total_ventas += datos['total']
            total_comision += datos['comision']

        # Actualizar totales
        self.lbl_total_ventas.setText(f"Q {total_ventas:.2f}")
        self.lbl_total_comision.setText(f"Q {total_comision:.2f}")

        # Guardar el total de comisión para usar en el diálogo de pago
        self.total_comision_actual = total_comision

        # Guardar datos agregados para PDF
        self.datos_agregados = agregado
        self.total_ventas_actual = total_ventas

    def registrar_pago_comision(self):
        """Abrir diálogo para registrar pago de comisión"""
        if not self.comisiones_calculadas:
            QMessageBox.warning(self, "Advertencia", "No hay comisiones para registrar.")
            return

        if self.doctor_actual == "Todos":
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un doctor específico.")
            return

        dialogo = PagoComisionDialog(self.doctor_actual, self.total_comision_actual, self)
        if dialogo.exec_() == QDialog.Accepted:
            datos_pago = dialogo.get_datos()
            self.guardar_pago_comision(datos_pago)

    def guardar_pago_comision(self, datos_pago):
        """Guardar el pago de comisión en la base de datos"""
        try:
            if hasattr(self, 'conexion') and self.conexion.open:
                cursor = self.conexion.cursor()

                sql = """
                INSERT INTO pagos_comisiones (doctor, monto, fecha, fecha_desde, fecha_hasta, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

                valores = (
                    self.doctor_actual,
                    datos_pago['monto'],
                    datos_pago['fecha'],
                    self.fecha_desde.date().toString("yyyy-MM-dd"),
                    self.fecha_hasta.date().toString("yyyy-MM-dd"),
                    datos_pago['observaciones']
                )

                cursor.execute(sql, valores)
                self.conexion.commit()
                id_pago = cursor.lastrowid

                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Pago de comisión registrado correctamente con ID: {id_pago}"
                )

                cursor.close()
        except Exception as e:
            print(f"Error al guardar pago de comisión: {e}")
            QMessageBox.critical(self, "Error", f"Error al guardar el pago: {e}")

    def ver_historial_pagos(self):
        """Mostrar historial de pagos realizados"""
        try:
            if hasattr(self, 'conexion') and self.conexion.open:
                cursor = self.conexion.cursor()

                sql = """
                SELECT id, doctor, monto, fecha, fecha_desde, fecha_hasta, 
                       observaciones, fecha_registro
                FROM pagos_comisiones
                """

                params = []
                if self.doctor_actual != "Todos":
                    sql += " WHERE doctor = %s"
                    params.append(self.doctor_actual)

                sql += " ORDER BY fecha DESC"

                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

                pagos = cursor.fetchall()
                cursor.close()

                if not pagos:
                    QMessageBox.information(
                        self,
                        "Historial de Pagos",
                        "No hay pagos registrados para mostrar."
                    )
                    return

                # Formatear resultados
                info_pagos = "Historial de Pagos de Comisiones:\n\n"
                for pago in pagos:
                    info_pagos += f"ID: {pago[0]}\n"
                    info_pagos += f"Doctor: {pago[1]}\n"
                    info_pagos += f"Monto: Q {pago[2]:.2f}\n"
                    info_pagos += f"Fecha de pago: {pago[3]}\n"
                    info_pagos += f"Período: {pago[4]} al {pago[5]}\n"
                    info_pagos += f"Observaciones: {pago[6]}\n"
                    info_pagos += f"Registro: {pago[7]}\n"
                    info_pagos += "-" * 40 + "\n"

                # Mostrar en un mensaje
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Historial de Pagos")
                msg_box.setText(info_pagos)
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec_()

        except Exception as e:
            print(f"Error al consultar historial de pagos: {e}")
            QMessageBox.warning(self, "Error", f"Error al consultar historial: {e}")

    def generar_pdf(self):
        """Generar un PDF con la información de ventas y comisiones"""
        if not hasattr(self, 'datos_agregados') or not self.datos_agregados:
            QMessageBox.warning(self, "Advertencia", "No hay datos para generar el PDF.")
            return

        try:
            # Preguntar dónde guardar el archivo
            opciones = QFileDialog.Options()
            nombre_archivo, _ = QFileDialog.getSaveFileName(
                self, "Guardar PDF",
                f"Reporte_Comisiones_{self.doctor_actual}_{self.fecha_desde.date().toString('yyyy-MM-dd')}_{self.fecha_hasta.date().toString('yyyy-MM-dd')}.pdf",
                "Archivos PDF (*.pdf)", options=opciones)

            if not nombre_archivo:
                return

            # Crear el PDF
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            elementos = []
            estilos = getSampleStyleSheet()

            # Título del reporte
            titulo = Paragraph("Reporte de Ventas y Comisiones", estilos['Heading1'])
            elementos.append(titulo)
            elementos.append(Spacer(1, 12))

            # Información del reporte
            info = []
            info.append(Paragraph(f"Doctor: {self.doctor_actual}", estilos['Normal']))
            info.append(Paragraph(
                f"Período: {self.fecha_desde.date().toString('yyyy-MM-dd')} al {self.fecha_hasta.date().toString('yyyy-MM-dd')}",
                estilos['Normal']))
            info.append(
                Paragraph(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", estilos['Normal']))

            for item in info:
                elementos.append(item)
                elementos.append(Spacer(1, 6))

            elementos.append(Spacer(1, 12))

            # Datos de la tabla
            datos_tabla = [["Cant", "Descripción", "Monto", "Impuestos", "Neto", "Comisión %", "Total Comisión"]]

            for clave, datos in self.datos_agregados.items():
                fila = [
                    str(datos['cantidad']),
                    datos['producto'],
                    f"Q {datos['total']:.2f}",
                    f"Q {datos['impuestos']:.2f}",
                    f"Q {datos['neto']:.2f}",
                    f"{datos['porcentaje_comision']}%",
                    f"Q {datos['comision']:.2f}"
                ]
                datos_tabla.append(fila)

            # Crear la tabla
            tabla = Table(datos_tabla)

            # Estilo de la tabla
            estilo_tabla = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])

            tabla.setStyle(estilo_tabla)
            elementos.append(tabla)
            elementos.append(Spacer(1, 20))

            # Totales
            elementos.append(Paragraph(f"Total Ventas: Q {self.total_ventas_actual:.2f}", estilos['Heading3']))
            elementos.append(Paragraph(f"Total Comisiones: Q {self.total_comision_actual:.2f}", estilos['Heading3']))

            # Generar el PDF
            doc.build(elementos)

            QMessageBox.information(
                self,
                "Éxito",
                f"El PDF se ha generado correctamente.\nUbicación: {nombre_archivo}"
            )

        except Exception as e:
            print(f"Error al generar el PDF: {e}")
            QMessageBox.critical(self, "Error", f"Error al generar el PDF: {e}")


import os

import pymysql
from datetime import datetime
from sql_structures.manager import Manager

from .Modificar_vitacora import *
from .modificar_ventas import *
import sys
from datetime import datetime
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas

from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QVBoxLayout


class DatosCliente(QMainWindow):
    _datos = []
    _numero = 0
    _data = 0

    def __init__(self):
        super(DatosCliente, self).__init__()
        self.funcional = None
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\CU-Factura.ui', self)
        self.datosList = []
        # self.btn_ingresar.clicked.connect(self.show_page_descuentos)
        self.btn_agregar_datos_factura.clicked.connect(self.generar_pdf_comprobante)
        self.pushButton_8.clicked.connect(self.cancelar)
        self.vita = AgregarVitacora()
        self.venta = Metodos_ventas()
        self.mana = Manager()
        self.llenar_combo_vendedores()
        # self.inicializar_funciones_auxiliares()

    def llenar_combo_vendedores(self):
        try:
            conexion =pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",
                database="bdhidrocolon"
            )

            cursor = conexion.cursor()
            query = "SELECT usuario FROM usuario WHERE rol = 'Vendedor'"
            cursor.execute(query)
            resultados = cursor.fetchall()

            # Agregar los nombres al comboBox
            for nombre in resultados:
                self.box_doc.addItem(nombre[0])  # nombre es una tupla

            cursor.close()
            conexion.close()
        except Exception as e:
            print("Error en la base de datos:", e)

    def recibir(self):
        try:
            nombre = self.le_agNombrePaciente.text()
            telefono = self.le_agApellido.text()
            direccion = self.le_agDpi_2.text()
            nit = self.le_NIT.text()
            self.datosList.append(nombre)
            self.datosList.append(telefono)
            self.datosList.append(direccion)
            self.datosList.append(nit)
            DatosCliente._datos = self.datosList
        except Exception as e:
            print(f"Error en recibir datos factura: {e}")

    @staticmethod
    def cargar_estado():
        """Carga el estado del contador desde un archivo."""
        if os.path.exists("estado_contador.txt"):
            try:
                with open("estado_contador.txt", "r") as archivo:
                    data = archivo.read().strip().split(",")
                    if len(data) == 2:
                        return int(data[0]), data[1]
            except (ValueError, IndexError):
                pass
        return 0, ""

    @staticmethod
    def guardar_estado(contador, fecha):
        """Guarda el estado del contador en un archivo."""
        with open("estado_contador.txt", "w") as archivo:
            archivo.write(f"{contador},{fecha}")

    def obtener_numero_comprobante(self):
        DatosCliente._numero, ultima_fecha = self.cargar_estado()
        fecha_actual = datetime.now().strftime("%Y-%m-%d")

        # Si es un nuevo día o no hay fecha guardada, reiniciar contador
        if fecha_actual != ultima_fecha:
            DatosCliente._numero = 1
        else:
            DatosCliente._numero += 1

            # Guardar el nuevo estado
        self.guardar_estado(DatosCliente._numero, fecha_actual)
        return DatosCliente._numero

    def generar_pdf_comprobante(self):
        """Función completa CORREGIDA para generar comprobantes incluyendo ajustes
        COPIAR Y PEGAR COMPLETO EN datos_cliente.py - REEMPLAZAR EL MÉTODO EXISTENTE"""
        try:
            print("🚨🚨🚨 DEBUG DIRECTO - EMPEZANDO 🚨🚨🚨")

            # 1. VERIFICAR QUE CAMBIÓ EL MÉTODO EN MANAGER
            try:
                datos_test = self.mana.print_table_efectivo_v("Efectivo")
                print(f"🔍 DATOS del método print_table_efectivo_v: {datos_test}")
                print(f"🔍 TIPO de datos: {type(datos_test)}")
                print(f"🔍 CANTIDAD de datos: {len(datos_test) if datos_test else 0}")

                if datos_test:
                    print(f"🔍 PRIMERA FILA: {datos_test[0]}")
                else:
                    print("❌ NO HAY DATOS - EL MÉTODO ESTÁ MAL O LA TABLA ESTÁ VACÍA")

            except Exception as e:
                print(f"❌ ERROR EN MÉTODO: {e}")

            # 2. VERIFICAR BASE DE DATOS DIRECTAMENTE
            try:
                import sql_structures
                manager_debug = sql_structures.Manager()

                carrito_directo = manager_debug.print_table("carrito")
                print(f"🔍 TABLA CARRITO DIRECTA: {len(carrito_directo) if carrito_directo else 0} filas")

                if carrito_directo:
                    print(f"🔍 PRIMERA FILA CARRITO: {carrito_directo[0]}")

                    # Probar consulta SQL manual
                    try:
                        query_manual = """SELECT c.nombre, \
                                                 COALESCE(m.presentacion, 'N/A') as presentacion, \
                                                 c.existencias, \
                                                 CASE \
                                                     WHEN c.existencias > 0 THEN ROUND(c.efectivo / c.existencias, 2) \
                                                     ELSE 0 \
                                                     END                         AS precio_unitario, \
                                                 c.efectivo                      AS precio_total
                                          FROM carrito AS c
                                                   LEFT JOIN medicamentos AS m ON m.id = c.medicamentos_id
                                          WHERE c.id != -1;"""

                        manager_debug.cursor.execute(query_manual)
                        resultado_manual = manager_debug.cursor.fetchall()
                        print(f"🔍 CONSULTA MANUAL: {len(resultado_manual) if resultado_manual else 0} filas")
                        if resultado_manual:
                            print(f"🔍 PRIMERA FILA MANUAL: {resultado_manual[0]}")

                    except Exception as e:
                        print(f"❌ ERROR CONSULTA MANUAL: {e}")
                else:
                    print("❌ TABLA CARRITO ESTÁ VACÍA - ESE ES EL PROBLEMA")

            except Exception as e:
                print(f"❌ ERROR BASE DE DATOS: {e}")

            # 3. VERIFICAR TABLA VISUAL
            try:
                print(f"🔍 TABLA VISUAL - Filas: {self.funcional.bd_carrito.rowCount()}")
                print(f"🔍 TABLA VISUAL - Columnas: {self.funcional.bd_carrito.columnCount()}")

                if self.funcional.bd_carrito.rowCount() > 0:
                    for fila in range(min(2, self.funcional.bd_carrito.rowCount())):
                        fila_datos = []
                        for col in range(self.funcional.bd_carrito.columnCount()):
                            item = self.funcional.bd_carrito.item(fila, col)
                            texto = item.text() if item else "None"
                            fila_datos.append(texto)
                        print(f"🔍 FILA VISUAL {fila}: {fila_datos}")
                else:
                    print("❌ TABLA VISUAL VACÍA")

            except Exception as e:
                print(f"❌ ERROR TABLA VISUAL: {e}")

            print("🚨🚨🚨 DEBUG DIRECTO - TERMINANDO 🚨🚨🚨")

            # ============================================================
            # CONTINUAR CON EL RESTO DEL CÓDIGO ORIGINAL
            # ============================================================

            # Obtener datos de la fecha actual
            today = datetime.now()
            desktop = os.path.expanduser("~") + "\\OneDrive\\Escritorio"

            # Crear carpeta "Comprobantes" en el escritorio si no existe
            comprobantes_folder = os.path.join(desktop, "Comprobantes")
            os.makedirs(comprobantes_folder, exist_ok=True)

            # Generar el número de comprobante
            numero_comprobante = self.obtener_numero_comprobante()

            self.recibir()
            self.datosFactura = self.get_datos_factura()
            nombre = self.datosFactura[0]
            telefono = self.datosFactura[1]
            direccion = self.datosFactura[2]
            nit = self.datosFactura[3]

            # ================================================================
            # DETECCIÓN MEJORADA DE VENTAS DE AJUSTE
            # ================================================================
            es_ajuste_recibo = False
            fecha_original_recibo = None
            justificacion_recibo = ""

            try:
                from .ventanaFuncional import VentanaFuncional

                # Verificar múltiples formas de detectar ajuste
                es_ajuste_recibo = (
                                           hasattr(VentanaFuncional,
                                                   '_es_venta_ajuste') and VentanaFuncional._es_venta_ajuste
                                   ) or (
                                           hasattr(VentanaFuncional,
                                                   '_ajuste_activo') and VentanaFuncional._ajuste_activo
                                   )

                if es_ajuste_recibo:
                    # Obtener fecha original
                    if hasattr(VentanaFuncional, '_fecha_ajuste'):
                        fecha_original_recibo = VentanaFuncional._fecha_ajuste
                    elif hasattr(VentanaFuncional, '_fecha_original_ajuste'):
                        fecha_original_recibo = VentanaFuncional._fecha_original_ajuste
                    else:
                        fecha_original_recibo = today.date()

                    # Obtener justificación
                    if hasattr(VentanaFuncional, '_motivo_ajuste'):
                        justificacion_recibo = VentanaFuncional._motivo_ajuste
                    elif hasattr(VentanaFuncional, '_justificacion_ajuste'):
                        justificacion_recibo = VentanaFuncional._justificacion_ajuste
                    else:
                        justificacion_recibo = "Ajuste contable"

                    print(f"🔧 AJUSTE DETECTADO:")
                    print(f"   - Fecha original: {fecha_original_recibo}")
                    print(f"   - Justificación: {justificacion_recibo}")
                else:
                    print(f"💰 Venta normal detectada")

            except Exception as e:
                print(f"⚠️ Error detectando ajuste: {e}")
                es_ajuste_recibo = False

            # ================================================================
            # OBTENER MÉTODO DE PAGO CON VALIDACIÓN MEJORADA
            # ================================================================
            metodo_pago = "efectivo"  # Valor por defecto

            try:
                if hasattr(self.funcional, 'obtener_metodo_pago_seleccionado'):
                    metodo_pago = self.funcional.obtener_metodo_pago_seleccionado()
                elif hasattr(self.funcional, 'radio_efectivo') and hasattr(self.funcional, 'radio_tarjeta'):
                    if self.funcional.radio_tarjeta.isChecked():
                        metodo_pago = "tarjeta"
                    else:
                        metodo_pago = "efectivo"
            except Exception as e:
                print(f"⚠️ Error obteniendo método de pago: {e}")
                metodo_pago = "efectivo"

            print(f"🔍 Método de pago seleccionado: {metodo_pago}")

            # ================================================================
            # CARGAR DATOS DE LA TABLA CON VALIDACIÓN
            # ================================================================
            if metodo_pago == "efectivo":
                self.funcional.cargarTablacarrito()
                tipo_comprobante = "Efectivo"
            elif metodo_pago == "tarjeta":
                self.funcional.cargarTablacarrito_tarjeta()
                tipo_comprobante = "Tarjeta"
            else:
                print(f"⚠️ Método de pago inválido: {metodo_pago}, usando 'Efectivo' por defecto")
                self.funcional.cargarTablacarrito()
                tipo_comprobante = "Efectivo"
                metodo_pago = "efectivo"

            print(f"🔍 Tipo de comprobante: {tipo_comprobante}")

            # ================================================================
            # VALIDAR QUE HAY DATOS EN LA TABLA ANTES DE GENERAR PDF
            # ================================================================
            num_rows = self.funcional.tabla_carrito().rowCount()
            if num_rows == 0:
                print("⚠️ No hay datos en la tabla del carrito")
                QMessageBox.warning(self, 'Aviso', 'No hay productos en el carrito para generar el comprobante.')
                return False

            print(f"🔍 Filas en tabla carrito: {num_rows}")

            # Ruta del archivo PDF en la carpeta "Comprobantes"
            pdf_file = os.path.join(
                comprobantes_folder,
                f"{today.year}{today.month:02d}{today.day:02d}_{numero_comprobante}.pdf"
            )

            # Establecer tamaño de media carta
            from reportlab.lib.units import inch
            from reportlab.lib.pagesizes import landscape
            from reportlab.pdfgen import canvas
            height, width = 5.5 * inch, 8.5 * inch
            pdf = canvas.Canvas(pdf_file, pagesize=landscape((width, height)))

            # ================================================================
            # TÍTULO MODIFICADO PARA AJUSTES
            # ================================================================
            pdf.setFont("Helvetica-Bold", 15)

            if es_ajuste_recibo:
                # Título en ROJO para ajustes
                pdf.setFillColorRGB(1, 0, 0)  # Rojo
                pdf.drawCentredString(width / 2, height - 30,
                                      f"🔧 COMPROBANTE DE AJUSTE ({tipo_comprobante}) No.{today.year}{today.month:02d}{today.day:02d}_{numero_comprobante}")
                pdf.setFillColorRGB(0, 0, 0)  # Volver a negro
            else:
                # Título normal
                pdf.drawCentredString(width / 2, height - 30,
                                      f"Comprobante de Compra ({tipo_comprobante}) No.{today.year}{today.month:02d}{today.day:02d}_{numero_comprobante}")

            DatosCliente._data = f"{today.year}{today.month:02d}{today.day:02d}_{numero_comprobante}"
            print(f"🔍 Número de comprobante generado: {DatosCliente._data}")

            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(50, height - 45, f"Hidrocolon Zona 9")

            # ================================================================
            # FECHAS MODIFICADAS PARA AJUSTES
            # ================================================================
            if es_ajuste_recibo and fecha_original_recibo:
                pdf.drawString(50, height - 60,
                               f"Fecha Original Venta: {fecha_original_recibo.strftime('%d - %m - %Y')}")
                pdf.drawString(50, height - 75, f"Fecha Registro: {today.day:02d} - {today.month:02d} - {today.year}")
                y_info_cliente = height - 90
            else:
                pdf.drawString(50, height - 60, f"Fecha: {today.day:02d} - {today.month:02d} - {today.year}")
                y_info_cliente = height - 75

            # Información del cliente
            pdf.drawString(50, y_info_cliente, f"Nombre: {nombre}")
            pdf.drawString(50, y_info_cliente - 15, f"NIT: {nit}")
            pdf.drawString(50, y_info_cliente - 30, f"Teléfono Cliente: {telefono}")
            pdf.drawString(50, y_info_cliente - 45, f"Dirección: {direccion}")

            # Obtener el total según el método de pago
            if metodo_pago == "efectivo":
                pago = self.obtener_total_efectivo()
            else:
                pago = self.obtener_total_tarjeta()

            # ================================================================
            # DIBUJAR TABLA CON VALIDACIÓN MEJORADA
            # ================================================================
            x = 30
            y = y_info_cliente - 70
            row_height = 15
            col_width = 110

            # Verificar que la tabla tenga columnas
            num_columns = self.funcional.tabla_carrito().columnCount() - 1
            if num_columns <= 0:
                print("⚠️ La tabla no tiene columnas válidas")
                QMessageBox.warning(self, 'Error', 'Error en la estructura de la tabla del carrito.')
                return False

            # Dibujar encabezados
            pdf.setFont("Helvetica-Bold", 8)
            pdf.setFillColorRGB(0.1, 0.4, 0.7)
            pdf.setStrokeColorRGB(0, 0, 0)
            pdf.rect(x, y - row_height, col_width * num_columns, row_height, fill=1)
            pdf.setFillColorRGB(1, 1, 1)

            # Obtener headers de manera segura
            headers = []
            for i in range(num_columns):
                header_item = self.funcional.tabla_carrito().horizontalHeaderItem(i)
                if header_item:
                    headers.append(header_item.text())
                else:
                    headers.append(f"Col {i + 1}")

            for i, header in enumerate(headers):
                pdf.drawString(x + i * col_width + 5, y - 10, header)

            # Dibujar datos de la tabla con validación
            # ================================================================
            # DIBUJAR DATOS DE LA TABLA CON RENDERIZADO MEJORADO
            # ================================================================
            pdf.setFont("Helvetica", 10)  # Aumentar tamaño de fuente
            pdf.setFillColorRGB(0, 0, 0)  # Asegurar que el texto sea negro

            print(f"🔍 DIBUJANDO TABLA MEJORADA - {num_rows} filas x {num_columns} columnas")

            for i in range(num_rows):
                y -= row_height

                # Dibujar borde de la celda
                pdf.setStrokeColorRGB(0, 0, 0)  # Borde negro
                pdf.rect(x, y - row_height, col_width * num_columns, row_height, stroke=1, fill=0)

                fila_datos = []
                for j in range(num_columns):
                    item = self.funcional.tabla_carrito().item(i, j)
                    text = item.text() if item else "N/A"
                    fila_datos.append(text)

                    # Asegurar que el texto no esté vacío
                    if not text or text.strip() == "":
                        text = "N/A"

                    # Truncar texto si es muy largo
                    if len(text) > 12:
                        text = text[:9] + "..."

                    # POSICIÓN MEJORADA Y FORZAR COLOR NEGRO
                    pdf.setFillColorRGB(0, 0, 0)  # Negro
                    text_x = x + j * col_width + 8  # Más margen
                    text_y = y - row_height + 8  # Centrado vertical

                    # Dibujar el texto
                    pdf.drawString(text_x, text_y, str(text))

                    print(f"🔍 Dibujando celda ({i},{j}): '{text}' en ({text_x}, {text_y})")

                print(f"🔍 Fila PDF {i} COMPLETA: {fila_datos}")

            # ================================================================
            # CALCULAR Y DIBUJAR TOTALES CON DESCUENTOS
            # ================================================================
            from . import DescuentoMedi
            subtotal_comprobante = pago
            porcentaje_desc = DescuentoMedi.get_porcentaje()
            cantidad_desc = DescuentoMedi.get_cantidad()

            descuento_aplicado = 0.0
            if porcentaje_desc > 0:
                descuento_aplicado = subtotal_comprobante * porcentaje_desc
            elif cantidad_desc > 0:
                descuento_aplicado = min(cantidad_desc, subtotal_comprobante)

            total_con_descuento = subtotal_comprobante - descuento_aplicado

            # Calcular totales según método de pago
            from .ventanaFuncional import VentanaFuncional
            if metodo_pago == "efectivo":
                total_efectivo = total_con_descuento - VentanaFuncional.get_diferencia_efectivo()
                total_tarjeta = VentanaFuncional.get_diferencia_efectivo()
                total_general = total_con_descuento
            else:
                total_efectivo = VentanaFuncional.get_diferencia_efectivo()
                total_tarjeta = total_con_descuento - VentanaFuncional.get_diferencia_efectivo()
                total_general = total_con_descuento

            # Dibujar los totales en el PDF
            y -= row_height * 2
            pdf.setFont("Helvetica-Bold", 6)

            # Subtotal
            pdf.rect(x, y - row_height, col_width * num_columns, row_height, stroke=1, fill=0)
            pdf.drawCentredString(x + col_width / 2, y - row_height / 2, "Subtotal")
            pdf.drawCentredString(x + col_width * 1.5, y - row_height / 2, f"Q{subtotal_comprobante:.2f}")
            y -= row_height

            # Descuento (solo mostrar si hay descuento)
            if descuento_aplicado > 0:
                pdf.rect(x, y - row_height, col_width * num_columns, row_height, stroke=1, fill=0)
                pdf.drawCentredString(x + col_width / 2, y - row_height / 2, "Descuento")
                pdf.drawCentredString(x + col_width * 1.5, y - row_height / 2, f"-Q{descuento_aplicado:.2f}")
                y -= row_height

            # Total
            pdf.rect(x, y - row_height, col_width * num_columns, row_height, stroke=1, fill=0)
            pdf.drawCentredString(x + col_width / 2, y - row_height / 2, "Total")
            pdf.drawCentredString(x + col_width * 1.5, y - row_height / 2, f"Q{total_general:.2f}")
            y -= row_height

            # Totales por método de pago
            if total_efectivo > 0:
                pdf.rect(x, y - row_height, col_width * num_columns, row_height, stroke=1, fill=0)
                pdf.drawCentredString(x + col_width / 2, y - row_height / 2, "Total Efectivo")
                pdf.drawCentredString(x + col_width * 1.5, y - row_height / 2, f"Q{total_efectivo:.2f}")
                y -= row_height

            if total_tarjeta > 0:
                pdf.rect(x, y - row_height, col_width * num_columns, row_height, stroke=1, fill=0)
                pdf.drawCentredString(x + col_width / 2, y - row_height / 2, "Total Tarjeta")
                pdf.drawCentredString(x + col_width * 1.5, y - row_height / 2, f"Q{total_tarjeta:.2f}")
                y -= row_height

            # ================================================================
            # INFORMACIÓN ADICIONAL PARA AJUSTES
            # ================================================================
            if es_ajuste_recibo:
                y_ajuste = y - 30
                # Marcador de ajuste
                pdf.setFont("Helvetica-Bold", 12)
                pdf.setFillColorRGB(1, 0, 0)  # Rojo
                pdf.drawCentredString(width / 2, y_ajuste + 20, "*** VENTA DE AJUSTE ***")
                pdf.setFillColorRGB(0, 0, 0)  # Volver a negro

                # Información adicional
                pdf.setFont("Helvetica", 9)
                pdf.drawCentredString(width / 2, y_ajuste + 5,
                                      "Esta venta se registró posteriormente como ajuste contable")

                # Fecha original si es diferente
                if fecha_original_recibo and fecha_original_recibo != today.date():
                    pdf.drawCentredString(width / 2, y_ajuste - 8,
                                          f"Venta realizada el: {fecha_original_recibo.strftime('%d/%m/%Y')}")
                    y_justif = y_ajuste - 20
                else:
                    y_justif = y_ajuste - 8

                # Justificación (resumida)
                if justificacion_recibo:
                    justif_corta = justificacion_recibo[:80] + "..." if len(
                        justificacion_recibo) > 80 else justificacion_recibo
                    pdf.setFont("Helvetica", 8)
                    pdf.drawCentredString(width / 2, y_justif, f"Motivo: {justif_corta}")

            # ================================================================
            # GUARDAR PDF
            # ================================================================
            print(f"🔍 GUARDANDO PDF EN: {pdf_file}")
            pdf.save()

            if os.path.exists(pdf_file):
                print(f"✅ ARCHIVO CONFIRMADO EN: {pdf_file}")
                print(f"✅ TAMAÑO DEL ARCHIVO: {os.path.getsize(pdf_file)} bytes")
            else:
                print(f"❌ ARCHIVO NO ENCONTRADO EN: {pdf_file}")
                return False

            # ================================================================
            # PROCESAR VENTAS Y LIMPIAR - VERSIÓN CORREGIDA
            # ================================================================
            try:
                print(f"🔍 PROCESANDO VENTAS - Tipo: {tipo_comprobante}")
                datosss = self.mana.print_table_efectivo_v(tipo_comprobante)
                print(f"🔍 Datos obtenidos para ventas: {len(datosss) if datosss else 0}")

                if datosss:
                    doc = self.box_doc.currentText()
                    for i in datosss:
                        print(f"🔍 Procesando venta: {i}")
                        self.venta.agregar_a_ventas(i[0], i[2], i[4], today, "Venta", doc)
                else:
                    print("⚠️ No hay datos para procesar en ventas")

            except Exception as e:
                print(f"❌ Error procesando ventas: {e}")

            # Limpiar variables de ajuste después de procesar
            self.limpiar_variables_ajuste_al_final_comprobante()

            # Limpiar variables de método de pago y descuentos
            VentanaFuncional._diferencia_efectivo = 0
            DescuentoMedi.reset_descuentos()

            usuario = VentanaFuncional.enviar_usuario()
            tiempo = datetime.now().date()

            if es_ajuste_recibo:
                dato = f"Se realizó una venta de AJUSTE con número {DatosCliente._data}"
            else:
                dato = f"Se realizó una venta con número {DatosCliente._data}"

            self.vita.agregarvitacora("Agregar", "Cierre", tiempo, usuario, dato)

            # Limpiar la tabla directamente
            self.funcional.bd_carrito.setRowCount(0)
            self.funcional.bd_carrito.clearContents()
            self.funcional.bd_carrito.update()
            self.funcional.bd_carrito.repaint()

            # Mensaje de confirmación
            if es_ajuste_recibo:
                mensaje_exito = '🔧 Comprobante de AJUSTE creado en la carpeta "Comprobantes"!'
            else:
                mensaje_exito = 'Comprobante creado en la carpeta "Comprobantes"!'

            self.funcional.borrar_tabla_normal()
            QMessageBox.about(self, 'Aviso', mensaje_exito)
            DatosCliente.close(self)
            return True

        except Exception as e:
            print(f"❌ ERROR CRÍTICO en generar_pdf_comprobante: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, 'Error', f'Error al generar el comprobante: {str(e)}')
            return False

    def insertar_en_registro_caja(self, descripcion, monto, cantidad, total, justificacion, fecha):
        """
        Inserta un registro en la tabla bdihidrocolon.registro_caja
        """
        try:
            # Crear consulta SQL para inserción
            query = """
            INSERT INTO bdhidrocolon.registro_caja (descripcion, monto, cantidad, total, justificacion, fecha)
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            # Ejecutar la consulta usando tu método existente para conexión a BD
            # Asumiendo que tienes un método para ejecutar consultas
            self.ejecutar_consulta_sql(query, (descripcion, monto, cantidad, total, justificacion, fecha))

            print(f"Registro guardado en tabla registro_caja: {descripcion}, {monto}")
            return True
        except Exception as e:
            print(f"Error al insertar en registro_caja: {str(e)}")
            return False

    def insertar_en_ingreso_tarjeta(self, no_voucher, nombre_paciente, total_real, total_bancos, fecha):
        """
        Inserta un registro en la tabla bdhidrocolon.ingreso_tarjeta
        """
        try:
            # Crear consulta SQL para inserción
            query = """
            INSERT INTO bdhidrocolon.ingreso_tarjeta (no_voucher, nombre_paciente, total_real, total_bancos, fecha)
            VALUES (%s, %s, %s, %s, %s)
            """

            # Ejecutar la consulta usando tu método existente para conexión a BD
            # Asumiendo que tienes un método para ejecutar consultas
            self.ejecutar_consulta_sql(query, (no_voucher, nombre_paciente, total_real, total_bancos, fecha))

            print(f"Registro guardado en tabla ingreso_tarjeta: {no_voucher}, {nombre_paciente}")
            return True
        except Exception as e:
            print(f"Error al insertar en ingreso_tarjeta: {str(e)}")
            return False

    def ejecutar_consulta_sql(self, query, params=None):
        """
        Método para ejecutar consultas SQL con parámetros
        Asumiendo que tienes alguna forma de conectar a la base de datos
        """
        try:
            conn = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="2332",
                database="bdhidrocolon")

            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error al ejecutar consulta SQL: {str(e)}")
            return False

    def obtener_total_efectivo(self):
        """Obtiene el total en efectivo del carrito
        COPIAR Y PEGAR en datos_cliente.py si no existe"""
        try:
            import sql_structures
            manager = sql_structures.Manager()
            total = manager.get_dinero_efectivo()
            print(f"🔍 Total efectivo obtenido: {total}")
            return total if total else 0.0
        except Exception as e:
            print(f"❌ Error obteniendo total efectivo: {e}")
            return 0.0

    def obtener_total_tarjeta(self):
        """Obtiene el total en tarjeta del carrito
        COPIAR Y PEGAR en datos_cliente.py si no existe"""
        try:
            import sql_structures
            manager = sql_structures.Manager()
            total = manager.get_dinero_tarjeta()
            print(f"🔍 Total tarjeta obtenido: {total}")
            return total if total else 0.0
        except Exception as e:
            print(f"❌ Error obteniendo total tarjeta: {e}")
            return 0.0

    def validar_datos_factura(self):
        """Valida que los datos de factura estén completos
        COPIAR Y PEGAR en datos_cliente.py"""
        try:
            datos = self.get_datos_factura()

            if not datos or len(datos) < 4:
                return False, "Datos de factura incompletos"

            nombre, telefono, direccion, nit = datos[0], datos[1], datos[2], datos[3]

            # Validaciones básicas
            if not nombre or nombre.strip() == "":
                return False, "El nombre del cliente es requerido"

            if not nit or nit.strip() == "":
                return False, "El NIT es requerido"

            if not telefono or telefono.strip() == "":
                return False, "El teléfono es requerido"

            if not direccion or direccion.strip() == "":
                return False, "La dirección es requerida"

            print(f"✅ Datos de factura validados: {nombre}, {nit}")
            return True, "Datos válidos"

        except Exception as e:
            print(f"❌ Error validando datos de factura: {e}")
            return False, f"Error en validación: {str(e)}"

    def debug_datos_comprobante(self):
        """Función para hacer debug de los datos del comprobante
        COPIAR Y PEGAR en datos_cliente.py"""
        try:
            print("🔍 DEBUG DATOS COMPROBANTE:")

            # Validar datos de factura
            valido, mensaje = self.validar_datos_factura()
            print(f"   - Datos factura válidos: {valido} - {mensaje}")

            # Verificar tabla de carrito
            if hasattr(self, 'funcional') and hasattr(self.funcional, 'bd_carrito'):
                filas = self.funcional.bd_carrito.rowCount()
                columnas = self.funcional.bd_carrito.columnCount()
                print(f"   - Tabla carrito: {filas} filas, {columnas} columnas")
            else:
                print("   - No se puede acceder a la tabla de carrito")

            # Verificar método de pago
            if hasattr(self, 'funcional'):
                try:
                    metodo = self.funcional.obtener_metodo_pago_seleccionado()
                    print(f"   - Método de pago: {metodo}")
                except:
                    print("   - No se puede obtener método de pago")

            # Verificar si es ajuste
            try:
                from .ventanaFuncional import VentanaFuncional
                es_ajuste = VentanaFuncional.es_venta_ajuste()
                print(f"   - Es venta de ajuste: {es_ajuste}")
                if es_ajuste:
                    datos_ajuste = VentanaFuncional.obtener_datos_ajuste()
                    print(f"   - Datos ajuste: {datos_ajuste}")
            except:
                print("   - No se puede verificar estado de ajuste")

        except Exception as e:
            print(f"❌ Error en debug datos comprobante: {e}")

    @classmethod
    def get_datos_factura(cls):
        return cls._datos

    @classmethod
    def get_numero(cls):
        return cls._numero

    @classmethod
    def get_numero_d(cls):
        return cls._data

    def cancelar(self):
        from .descuentosMedi import DescuentoMedi
        DescuentoMedi.reset_descuentos()  # Resetear descuentos al cancelar
        DatosCliente.close(self)

    def closeEvent(self, event):
        from .descuentosMedi import DescuentoMedi
        if self.funcional is not None:
            self.funcional.limpiar_tabla(self.funcional.bd_carrito)
        DescuentoMedi.reset_descuentos()  # Resetear descuentos al cerrar la ventana
        event.accept()

    def limpiar_variables_ajuste_al_final_comprobante(self):
        """Limpiar variables de ajuste después de procesar comprobante
        COPIAR Y PEGAR en datos_cliente.py - VERSIÓN MEJORADA"""
        try:
            from .ventanaFuncional import VentanaFuncional

            # Lista de todas las variables de ajuste posibles
            variables_ajuste = [
                '_es_venta_ajuste', '_ajuste_activo', '_fecha_ajuste',
                '_motivo_ajuste', '_fecha_original_ajuste', '_justificacion_ajuste'
            ]

            variables_limpiadas = []
            for var in variables_ajuste:
                if hasattr(VentanaFuncional, var):
                    delattr(VentanaFuncional, var)
                    variables_limpiadas.append(var)

            if variables_limpiadas:
                print(f"✅ Variables de ajuste limpiadas: {variables_limpiadas}")
            else:
                print("ℹ️ No había variables de ajuste para limpiar")

        except Exception as e:
            print(f"⚠️ Error limpiando variables de ajuste: {e}")
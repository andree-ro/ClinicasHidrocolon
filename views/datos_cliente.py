import os

import pymysql
from PyQt5.QtCore import QTimer
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from reportlab.lib.pagesizes import landscape, legal
from reportlab.pdfgen import canvas
from datetime import datetime
from sql_structures.manager import Manager
from .Modificar_vitacora import *
from .modificar_ventas import *
import sys

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
        import datetime
        DatosCliente._numero, ultima_fecha = self.cargar_estado()
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")

        # Si es un nuevo día o no hay fecha guardada, reiniciar contador
        if fecha_actual != ultima_fecha:
            DatosCliente._numero = 1
        else:
            DatosCliente._numero += 1

            # Guardar el nuevo estado
        self.guardar_estado(DatosCliente._numero, fecha_actual)
        return DatosCliente._numero

    def generar_pdf_comprobante(self, metodo_pago=None):
        from .ventanaFuncional import VentanaFuncional
        from .descuentosMedi import DescuentoMedi
        from reportlab.lib.units import inch
        import os
        import datetime
        from PyQt5.QtWidgets import QMessageBox
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import landscape

        # ✅ SOLUCIÓN DEFINITIVA: USAR LA INSTANCIA ACTUAL, NO CREAR UNA NUEVA
        if hasattr(VentanaFuncional, '_instancia_actual'):
            self.funcional = VentanaFuncional._instancia_actual
            print(f"✅ Usando instancia actual existente")
        else:
            self.funcional = VentanaFuncional()
            print(f"⚠️ Creando nueva instancia (no debería pasar)")

        management = Manager()
        today = datetime.date.today()
        try:
            # Obtener la ruta del escritorio del usuario
            desktop = "C:\\Users\\andre\\OneDrive\\Escritorio"

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

            # ========================================
            # SOLUCIÓN DEFINITIVA: OBTENER MÉTODO DE PAGO
            # ========================================
            try:
                if hasattr(VentanaFuncional, '_metodo_pago_guardado'):
                    metodo_pago = VentanaFuncional._metodo_pago_guardado
                    print(f"✅ Método de pago desde CLASE: {metodo_pago}")
                else:
                    metodo_pago = "efectivo"
                    print(f"⚠️ metodo_pago_actual no encontrado, usando efectivo")

                print(f"🔍 Método de pago final: {metodo_pago}")

            except Exception as e:
                print(f"❌ Error obteniendo método de pago: {e}")
                metodo_pago = "efectivo"

            # ARREGLO: Asegurar que tipo_comprobante siempre tenga un valor
            if metodo_pago == "efectivo":
                self.funcional.cargarTablacarrito()
                tipo_comprobante = "Efectivo"
            elif metodo_pago == "tarjeta":
                self.funcional.cargarTablacarrito_tarjeta()
                tipo_comprobante = "Tarjeta"
            else:
                # Valor por defecto si metodo_pago es inválido
                print(f"⚠️ Método de pago inválido: {metodo_pago}, usando 'Efectivo' por defecto")
                self.funcional.cargarTablacarrito()
                tipo_comprobante = "Efectivo"
                metodo_pago = "efectivo"  # Normalizar también metodo_pago

            print(f"🔍 Tipo de comprobante: {tipo_comprobante}")
            # ========================================
            # FIN DEL ARREGLO
            # ========================================

            # Ruta del archivo PDF en la carpeta "Comprobantes"
            pdf_file = os.path.join(
                comprobantes_folder,
                f"{today.year}{today.month:02d}{today.day:02d}_{numero_comprobante}.pdf"
            )

            # Establecer tamaño de media carta
            height, width = 5.5 * inch, 8.5 * inch
            pdf = canvas.Canvas(pdf_file, pagesize=landscape((width, height)))

            # Logo y encabezados del PDF
            # logo_path = "C:\\Users\\Windows 10\\Desktop\\Sistema-Hidrocolon-main\\views\\InterfaceImages\\logo.png"
            image_width = 70
            image_height = 70
            # pdf.drawImage(logo_path, width - image_width - 80, height - image_height - 45,
            # width=image_width, height=image_height)

            pdf.setFont("Helvetica-Bold", 15)
            pdf.drawCentredString(width / 2, height - 30,
                                  f"Comprobante de Compra ({tipo_comprobante}) No. {today.year}{today.month:02d}{today.day:02d}_{numero_comprobante}")
            DatosCliente._data = f"{today.year}{today.month:02d}{today.day:02d}_{numero_comprobante}"
            print(DatosCliente._data)
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(50, height - 45, f"Hidrocolon Zona 9")
            pdf.drawString(50, height - 60, f"Fecha: {today.day:02d} - {today.month:02d} - {today.year}")
            pdf.drawString(50, height - 75, f"Nombre: {nombre}")
            pdf.drawString(50, height - 90, f"NIT: {nit}")
            pdf.drawString(50, height - 105, f"Teléfono Cliente: {telefono}")
            pdf.drawString(50, height - 120, f"Dirección: {direccion}")

            # Obtener el total según el método de pago
            if metodo_pago == "efectivo":
                pago = self.obtener_total_efectivo()
            else:
                pago = self.obtener_total_tarjeta()

            # Configuración inicial de tabla
            x = 30
            y = height - 135
            row_height = 15
            col_width = 110

            # Dibujar encabezados y datos de la tabla
            num_columns = self.funcional.tabla_carrito().columnCount() - 1
            pdf.setFont("Helvetica-Bold", 8)
            pdf.setFillColorRGB(0.1, 0.4, 0.7)
            pdf.setStrokeColorRGB(0, 0, 0)
            pdf.rect(x, y - row_height, col_width * num_columns, row_height, fill=1)
            pdf.setFillColorRGB(1, 1, 1)

            headers = [
                self.funcional.tabla_carrito().horizontalHeaderItem(i).text()
                for i in range(num_columns)
            ]
            for col, header in enumerate(headers):
                pdf.drawCentredString(x + col * col_width + col_width / 2,
                                      y - row_height / 2, header)

            pdf.setFont("Helvetica", 6)
            pdf.setFillColorRGB(0, 0, 0)
            y -= row_height

            for row in range(self.funcional.tabla_carrito().rowCount()):
                for col in range(num_columns):
                    pdf.rect(x + col * col_width, y - row_height,
                             col_width, row_height, stroke=1, fill=0)

                    item = self.funcional.tabla_carrito().item(row, col)
                    if item is not None:
                        text = item.text()
                        if text in ["0", "None"]:
                            text = "----"
                        pdf.drawCentredString(x + col * col_width + col_width / 2,
                                              y - row_height / 2, text)
                y -= row_height

            # Calcular subtotal, descuento y total
            subtotal_comprobante = 0.0
            for row in range(self.funcional.tabla_carrito().rowCount()):
                precio_item = self.funcional.tabla_carrito().item(row, 4)
                if precio_item and precio_item.text():
                    try:
                        subtotal_comprobante += float(precio_item.text())
                    except ValueError:
                        continue

            # Obtener descuentos aplicados
            porcentaje_desc = DescuentoMedi.get_porcentaje()
            cantidad_desc = DescuentoMedi.get_cantidad()

            descuento_aplicado = 0.0
            if porcentaje_desc > 0:
                descuento_aplicado = subtotal_comprobante * porcentaje_desc
            elif cantidad_desc > 0:
                descuento_aplicado = min(cantidad_desc, subtotal_comprobante)

            total_con_descuento = subtotal_comprobante - descuento_aplicado

            # Calcular totales según método de pago
            if metodo_pago == "efectivo":
                total_efectivo = total_con_descuento - VentanaFuncional.get_diferencia_efectivo()
                total_tarjeta = VentanaFuncional.get_diferencia_efectivo()
                total_general = total_con_descuento
            else:
                total_efectivo = VentanaFuncional.get_diferencia_efectivo()
                total_tarjeta = total_con_descuento - VentanaFuncional.get_diferencia_efectivo()
                total_general = total_con_descuento

            # Dibujar los totales en el PDF
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

            # Total Efectivo
            pdf.rect(x, y - row_height, col_width * num_columns, row_height, stroke=1, fill=0)
            pdf.drawCentredString(x + col_width / 2, y - row_height / 2, "Total Efectivo")
            pdf.drawCentredString(x + col_width * 1.5, y - row_height / 2, f"Q{total_efectivo:.2f}")
            y -= row_height

            # Total Tarjeta
            pdf.rect(x, y - row_height, col_width * num_columns, row_height, stroke=1, fill=0)
            pdf.drawCentredString(x + col_width / 2, y - row_height / 2, "Total Tarjeta")
            pdf.drawCentredString(x + col_width * 1.5, y - row_height / 2, f"Q{total_tarjeta:.2f}")
            y -= row_height

            # Total General
            pdf.rect(x, y - row_height, col_width * num_columns, row_height, stroke=1, fill=0)
            pdf.drawCentredString(x + col_width / 2, y - row_height / 2, "Total Final")
            pdf.drawCentredString(x + col_width * 1.5, y - row_height / 2, f"Q{total_general:.2f}")

            pdf.save()
            datosss = self.mana.print_table_efectivo_v(tipo_comprobante)
            doc = self.box_doc.currentText()

            for i in datosss:
                self.venta.agregar_a_ventas(i[0], i[2], i[4], today, "Venta", doc)

            self.funcional.borrar_tabla_normal()
            QMessageBox.about(self, 'Aviso', 'Comprobante creado en la carpeta "Comprobantes"!')

            VentanaFuncional._diferencia_efectivo = 0
            DescuentoMedi.reset_descuentos()
            from .ventanaFuncional import VentanaFuncional
            usuario = VentanaFuncional.enviar_usuario()

            tiempo = datetime.date.today()
            dato = f"Se realizó una venta con número {DatosCliente._data}"
            self.vita.agregarvitacora("Agregar", "Cierre", tiempo, usuario, dato)
            # Limpiar la tabla directamente
            self.funcional.bd_carrito.setRowCount(0)  # Si es QTableWidget
            self.funcional.bd_carrito.clearContents()
            # O también puedes usar:
            # self.funcional.bd_carrito.clear()

            # Forzar actualización
            self.funcional.bd_carrito.update()
            self.funcional.bd_carrito.repaint()

            DatosCliente.close(self)
            return True

        except Exception as e:
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
        management = Manager()
        # Implementa la lógica para obtener el total en efectivo
        return management.get_dinero_tarjeta()

    def obtener_total_tarjeta(self):
        management = Manager()
        # Implementa la lógica para obtener el total con tarjeta
        return management.get_dinero_tarjeta()

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


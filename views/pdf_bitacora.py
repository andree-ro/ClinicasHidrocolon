import os
from datetime import datetime, date, timedelta
import datetime as dt
from sql_structures.manager import Manager
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from PyQt5.QtWidgets import QMessageBox

class PDFBitacora(QMainWindow):
    def __init__(self):
        super(PDFBitacora, self).__init__()  # Corrección aquí
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\I-PDFBitacora.ui', self)
        self.btn_agregar_medi.clicked.connect(self.crear_pdf)
        self.consulta = Manager()

    def crear_pdf(self):
        try:
            # Obtener fechas de inicio y fin
            inicio = self.fecha_inicio.date().toString("yyyy-MM-dd")
            fin = self.fecha_final.date().toString("yyyy-MM-dd")

            # Obtener la ruta del escritorio
            escritorio = os.path.join(os.path.expanduser("~"), "Desktop")

            # Crear la carpeta de reportes en el escritorio si no existe
            carpeta = os.path.join(escritorio, "Reportes Bitácora")
            os.makedirs(carpeta, exist_ok=True)

            # Ruta del archivo PDF
            pdf_file = os.path.join(carpeta, f"Bitacora_{inicio}_{fin}.pdf")

            # Obtener los datos de la consulta
            filtro = self.consulta.filtro_datos_bitacora(inicio, fin)
            # Si no hay datos, mostramos un mensaje
            if not filtro:
                QMessageBox.warning(self, "Sin Datos", "No se encontraron datos para este rango de fechas.")
                return

            # Crear el documento PDF
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)

            # Definir las cabeceras de la tabla (según la estructura de tus datos)
            encabezados = ["Acción", "Módulo", "Modificación", "Fecha", "Usuario"]

            datos = [encabezados]
            for registro in filtro:
                datos.append([registro[0], registro[1], registro[2], registro[3], registro[4]])

            # Crear la tabla
            tabla = Table(datos)

            # Estilo de la tabla
            estilo = TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ])

            tabla.setStyle(estilo)

            # Agregar la tabla al documento
            doc.build([tabla])

            # Confirmación de generación de PDF
            QMessageBox.information(self, "Éxito", f"El reporte PDF se ha creado correctamente en {pdf_file}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al crear el PDF: {str(e)}")

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))




import os
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyPDF2 import PdfReader, PdfWriter, PageObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .Modificar_vitacora import *
from .modificar_ventas import *


class CodigoAnulacion(QMainWindow):
    _numero = 0

    def __init__(self):
        super(CodigoAnulacion, self).__init__()
        loadUi("C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\CodigoComprobante..ui", self)
        self.vita = AgregarVitacora()
        # Botón conectado a la búsqueda de PDF
        self.btn_codigo_comprobante.clicked.connect(self.buscar_PDF)

    def buscar_PDF(self):
        # Obtener el texto del lineEdit como código o nombre del PDF
        codigoPDF = self.lineEdit.text().strip()
        CodigoAnulacion._numero = codigoPDF
        if not codigoPDF:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingresa el código del comprobante.")
            return

        # Seleccionar carpeta donde buscar el archivo
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if not folder:
            QMessageBox.warning(self, "Advertencia", "No seleccionaste ninguna carpeta.")
            return

        # Buscar el PDF con el nombre proporcionado
        pdf_name = f"{codigoPDF}.pdf"
        pdf_path = None
        for root, dirs, files in os.walk(folder):
            if pdf_name in files:
                pdf_path = os.path.join(root, pdf_name)
                break

        if not pdf_path:
            QMessageBox.critical(self, "Error", f"No se encontró el archivo {pdf_name} en la carpeta seleccionada.")
            return

        # Anular el PDF
        try:
            self.anular_pdf(pdf_path, folder, codigoPDF)
            QMessageBox.information(self, "Éxito", f"El archivo {pdf_name} ha sido anulado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al anular el PDF: {e}")

    def anular_pdf(self, pdf_path, folder, codigoPDF):
        # Crear la carpeta "comprobantes anulados" si no existe
        anulados_folder = os.path.join(folder, "comprobantes anulados")
        os.makedirs(anulados_folder, exist_ok=True)

        # Ruta del nuevo archivo anulado
        new_pdf_path = os.path.join(anulados_folder, f"{codigoPDF}_anulado.pdf")

        # Crear el texto superpuesto "COMPROBANTE ANULADO"
        temp_pdf_path = "temp_overlay.pdf"
        c = canvas.Canvas(temp_pdf_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 40)
        c.setFillColorRGB(1, 0, 0)  # Texto en rojo
        width, height = letter
        c.drawString(5, height / 5, "COMPROBANTE ANULADO")
        c.save()

        # Leer el contenido del PDF original
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        # Leer el contenido del PDF temporal con el texto "COMPROBANTE ANULADO"
        with open(temp_pdf_path, "rb") as temp_pdf:
            overlay_reader = PdfReader(temp_pdf)
            overlay_page = overlay_reader.pages[0]

            # Combinar cada página del PDF original con el texto superpuesto
            for page in reader.pages:
                page.merge_page(overlay_page)
                writer.add_page(page)

        # Guardar el nuevo archivo anulado
        with open(new_pdf_path, "wb") as output_pdf:
            writer.write(output_pdf)

        # Eliminar el archivo temporal
        os.remove(temp_pdf_path)

        dato = f"Se retiro una venta con numero {codigoPDF}_anulado"

        from .ventanaFuncional import VentanaFuncional
        usuario = VentanaFuncional.enviar_usuario()
        import datetime

        tiempo = datetime.date.today()
        self.vita.agregarvitacora("Agregar", "Cierre", tiempo, usuario,
                                  dato)

    @classmethod
    def get_numerro(cls):
        return cls._numero

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem


class DescuentoMedi(QMainWindow):
    _porcentaje = 0  # Variable de clase
    _cantidad = 0

    def __init__(self, ventana_principal=None):
        super(DescuentoMedi, self).__init__()
        loadUi('C:\\Users\\andre\\OneDrive\\Escritorio\\Sistema-Hidrocolon-main\\views\\Descuentos.ui', self)
        self.por = 0
        self.cantidad = 0
        self.ventana_principal = ventana_principal  # Referencia a la ventana principal
        self.pushButton_8.clicked.connect(self.recibir_porcentaje)
        self.pushButton_7.clicked.connect(self.recibir_cantidad)

    def recibir_porcentaje(self):
        valor = self.lineEdit_3.text()
        if valor.isdigit():
            DescuentoMedi._porcentaje = int(valor) / 100
            self.por = DescuentoMedi._porcentaje
            self.lineEdit_3.clear()
            print(f"Porcentaje guardado: {DescuentoMedi._porcentaje}")

            # Actualizar totales en la ventana principal
            if self.ventana_principal:
                self.ventana_principal.actualizar_totales_carrito()

        else:
            print("Error: El valor ingresado no es válido.")

    def recibir_cantidad(self):
        valor = self.lineEdit.text()
        if valor.isdigit():
            DescuentoMedi._cantidad = int(valor)
            self.cantidad = DescuentoMedi._cantidad
            self.lineEdit.clear()
            print(f"Cantidad guardada: {DescuentoMedi._cantidad}")

            # Actualizar totales en la ventana principal
            if self.ventana_principal:
                self.ventana_principal.actualizar_totales_carrito()

        else:
            print("Error: El valor ingresado no es válido.")

    @classmethod
    def get_porcentaje(cls):
        return cls._porcentaje

    @classmethod
    def get_cantidad(cls):
        return cls._cantidad

    @classmethod
    def reset_descuentos(cls):
        """Reinicia los valores de porcentaje y cantidad."""
        cls._porcentaje = 0
        cls._cantidad = 0
        print("Descuentos reiniciados a 0.")
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtGui import QDoubleValidator
from decimal import Decimal


class DialogoPagoDividido(QDialog):
    def __init__(self, parent=None, total=0.0):
        super().__init__(parent)
        self.total = total
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Dividir Pago")
        self.setMinimumWidth(300)

        # Crear layout principal
        layout = QVBoxLayout()

        # Sección Total
        self.lbl_total = QLabel(f"Total a pagar: Q{self.total:.2f}")
        self.lbl_total.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.lbl_total)

        # Sección Efectivo
        layout_efectivo = QHBoxLayout()
        self.lbl_efectivo = QLabel("Monto en efectivo: Q")
        self.txt_efectivo = QLineEdit()
        self.txt_efectivo.setValidator(QDoubleValidator(0.0, self.total, 2))
        self.txt_efectivo.textChanged.connect(self.calcular_tarjeta)
        layout_efectivo.addWidget(self.lbl_efectivo)
        layout_efectivo.addWidget(self.txt_efectivo)
        layout.addLayout(layout_efectivo)

        # Sección Tarjeta
        self.lbl_tarjeta = QLabel(f"Monto en tarjeta: Q{self.total:.2f}")
        self.lbl_tarjeta.setStyleSheet("color: blue;")
        layout.addWidget(self.lbl_tarjeta)

        # Botones
        layout_botones = QHBoxLayout()
        self.btn_aceptar = QPushButton("Aceptar")
        self.btn_aceptar.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet("background-color: #f44336; color: white;")

        self.btn_aceptar.clicked.connect(self.aceptar)
        self.btn_cancelar.clicked.connect(self.reject)

        layout_botones.addWidget(self.btn_aceptar)
        layout_botones.addWidget(self.btn_cancelar)
        layout.addLayout(layout_botones)

        self.setLayout(layout)

    def calcular_tarjeta(self):
        try:
            efectivo = float(self.txt_efectivo.text() or 0)
            tarjeta = self.total - efectivo

            if efectivo > self.total:
                self.lbl_tarjeta.setStyleSheet("color: red;")
                self.lbl_tarjeta.setText("¡Error! Monto en efectivo mayor al total")
                self.btn_aceptar.setEnabled(False)
            else:
                self.lbl_tarjeta.setStyleSheet("color: blue;")
                self.lbl_tarjeta.setText(f"Monto en tarjeta: Q{tarjeta:.2f}")
                self.btn_aceptar.setEnabled(True)

        except ValueError:
            self.lbl_tarjeta.setText("Monto inválido")
            self.btn_aceptar.setEnabled(False)

    def aceptar(self):
        try:
            efectivo = float(self.txt_efectivo.text() or 0)
            tarjeta = self.total - efectivo

            if efectivo < 0 or tarjeta < 0:
                QMessageBox.warning(self, "Error", "Los montos no pueden ser negativos")
                return

            if efectivo > self.total:
                QMessageBox.warning(self, "Error", "El monto en efectivo no puede ser mayor al total")
                return

            self.monto_efectivo = efectivo
            self.monto_tarjeta = tarjeta
            self.accept()

        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor ingrese un monto válido")

    def obtener_montos(self):
        if hasattr(self, 'monto_efectivo') and hasattr(self, 'monto_tarjeta'):
            return self.monto_efectivo, self.monto_tarjeta
        return None, None
import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class VentanaDenominaciones(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # Referencia a la ventana principal
        self.total_efectivo = 0.0

        # Denominaciones
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

        self.initUI()

    def initUI(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle("💰 Registro de Efectivo Físico")
        self.setGeometry(300, 200, 500, 600)
        self.setModal(True)  # Ventana modal

        layout = QVBoxLayout()

        # Título
        titulo = QLabel("💰 REGISTRO DE EFECTIVO FÍSICO")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo.setStyleSheet(
            "background-color: #28a745; color: white; padding: 12px; border-radius: 6px; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # Instrucciones
        instrucciones = QLabel("👆 Ingrese la cantidad física de cada denominación que tiene en caja:")
        instrucciones.setStyleSheet("background-color: #e8f5e8; padding: 8px; border-radius: 4px; margin-bottom: 10px;")
        instrucciones.setWordWrap(True)
        layout.addWidget(instrucciones)

        # Crear tabla
        self.tabla_denominaciones = QTableWidget()
        self.tabla_denominaciones.setColumnCount(3)
        self.tabla_denominaciones.setHorizontalHeaderLabels(["Cantidad", "Denominación", "Total"])
        self.tabla_denominaciones.setRowCount(len(self.denominaciones))

        # Llenar tabla
        for i, (descripcion, valor, display) in enumerate(self.denominaciones):
            # Cantidad (editable)
            cantidad_item = QTableWidgetItem("0")
            cantidad_item.setTextAlignment(Qt.AlignCenter)
            self.tabla_denominaciones.setItem(i, 0, cantidad_item)

            # Denominación (no editable)
            desc_item = QTableWidgetItem(f"{descripcion} {display}")
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.tabla_denominaciones.setItem(i, 1, desc_item)

            # Total (no editable)
            total_item = QTableWidgetItem("0.00")
            total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla_denominaciones.setItem(i, 2, total_item)

        # Configurar tabla
        self.tabla_denominaciones.setColumnWidth(0, 80)  # Cantidad
        self.tabla_denominaciones.setColumnWidth(1, 200)  # Denominación
        self.tabla_denominaciones.setColumnWidth(2, 100)  # Total
        self.tabla_denominaciones.verticalHeader().setVisible(False)

        # Conectar eventos
        self.tabla_denominaciones.itemChanged.connect(self.calcular_total_fila)

        layout.addWidget(self.tabla_denominaciones)

        # Total general
        self.lbl_total_general = QLabel("TOTAL EFECTIVO FÍSICO: Q0.00")
        self.lbl_total_general.setFont(QFont("Arial", 12, QFont.Bold))
        self.lbl_total_general.setStyleSheet(
            "background-color: #2c3e50; color: white; padding: 12px; border-radius: 6px; margin: 10px 0;")
        self.lbl_total_general.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_total_general)

        # Botones
        botones_layout = QHBoxLayout()

        btn_limpiar = QPushButton("🧹 Limpiar Todo")
        btn_limpiar.clicked.connect(self.limpiar_tabla)
        btn_limpiar.setStyleSheet(
            "background-color: #ffc107; color: black; padding: 10px; border-radius: 5px; font-weight: bold;")

        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setStyleSheet(
            "background-color: #6c757d; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")

        btn_confirmar = QPushButton("✅ Confirmar y Aplicar")
        btn_confirmar.clicked.connect(self.confirmar_denominaciones)
        btn_confirmar.setStyleSheet(
            "background-color: #28a745; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")

        botones_layout.addWidget(btn_limpiar)
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(btn_confirmar)

        layout.addLayout(botones_layout)

        self.setLayout(layout)

    def calcular_total_fila(self, item):
        """Calcular el total cuando cambia una cantidad"""
        try:
            if item.column() == 0:  # Solo si cambió la cantidad
                row = item.row()

                # Obtener cantidad
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
                total_item = self.tabla_denominaciones.item(row, 2)
                total_item.setText(f"{total_fila:.2f}")

                # Actualizar total general
                self.actualizar_total_general()

        except (ValueError, TypeError):
            # Si hay error, poner 0
            item.setText("0")

    def actualizar_total_general(self):
        """Actualizar el total general"""
        total = 0.0

        for row in range(self.tabla_denominaciones.rowCount()):
            total_item = self.tabla_denominaciones.item(row, 2)
            if total_item:
                try:
                    total += float(total_item.text())
                except ValueError:
                    pass

        self.total_efectivo = total
        self.lbl_total_general.setText(f"TOTAL EFECTIVO FÍSICO: Q{total:.2f}")

    def limpiar_tabla(self):
        """Limpiar toda la tabla"""
        for row in range(self.tabla_denominaciones.rowCount()):
            cantidad_item = self.tabla_denominaciones.item(row, 0)
            total_item = self.tabla_denominaciones.item(row, 2)

            cantidad_item.setText("0")
            total_item.setText("0.00")

        self.actualizar_total_general()

    def confirmar_denominaciones(self):
        """Confirmar y enviar el total a la ventana principal"""
        try:
            # Mostrar confirmación
            mensaje = f"""
💰 CONFIRMACIÓN DE EFECTIVO FÍSICO

Total calculado: Q{self.total_efectivo:.2f}

¿Desea aplicar este total al cierre?
"""

            respuesta = QMessageBox.question(
                self, "Confirmar Efectivo", mensaje,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )

            if respuesta == QMessageBox.Yes:
                # Enviar total a la ventana principal
                if self.parent:
                    self.parent.actualizar_efectivo_fisico(self.total_efectivo)

                self.accept()  # Cerrar ventana

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al confirmar: {e}")

    def obtener_total(self):
        """Obtener el total calculado"""
        return self.total_efectivo
# PASO 4: CREAR ARCHIVO views/seleccion_paciente.py
# Crea este archivo completo en tu carpeta views/

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sql_structures


class SeleccionPacienteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar Paciente")
        self.setModal(True)
        self.resize(600, 400)

        self.paciente_seleccionado = None
        self.manager = sql_structures.Manager()

        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()

        # Búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por DPI, nombre o teléfono...")
        self.search_btn = QPushButton("Buscar")
        self.search_btn.clicked.connect(self.buscar_paciente)

        search_layout.addWidget(QLabel("Buscar:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)

        # Tabla de resultados
        self.tabla_pacientes = QTableWidget()
        self.tabla_pacientes.setColumnCount(6)
        self.tabla_pacientes.setHorizontalHeaderLabels([
            "ID", "Nombre", "Apellido", "DPI", "Teléfono", "Última Cita"
        ])
        self.tabla_pacientes.doubleClicked.connect(self.seleccionar_paciente)

        # Botones
        buttons_layout = QHBoxLayout()
        self.btn_seleccionar = QPushButton("Seleccionar")
        self.btn_cancelar = QPushButton("Cancelar")

        self.btn_seleccionar.clicked.connect(self.seleccionar_paciente)
        self.btn_cancelar.clicked.connect(self.reject)

        buttons_layout.addWidget(self.btn_seleccionar)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_cancelar)

        layout.addLayout(search_layout)
        layout.addWidget(self.tabla_pacientes)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Conectar Enter en búsqueda
        self.search_input.returnPressed.connect(self.buscar_paciente)

    def buscar_paciente(self):
        texto_busqueda = self.search_input.text().strip()
        if not texto_busqueda:
            QMessageBox.warning(self, "Aviso", "Ingrese texto para buscar")
            return

        resultados = self.manager.buscar_paciente_por_identificador(texto_busqueda)

        # Limpiar tabla
        self.tabla_pacientes.setRowCount(0)

        if isinstance(resultados, tuple):  # Resultado único
            resultados = [resultados]
        elif isinstance(resultados, list) and len(resultados) > 0:  # Múltiples resultados
            pass
        else:
            QMessageBox.information(self, "Sin resultados", "No se encontraron pacientes.")
            return

        # Llenar tabla
        self.tabla_pacientes.setRowCount(len(resultados))
        for i, paciente in enumerate(resultados):
            self.tabla_pacientes.setItem(i, 0, QTableWidgetItem(str(paciente[0])))  # ID
            self.tabla_pacientes.setItem(i, 1, QTableWidgetItem(str(paciente[1])))  # Nombre
            self.tabla_pacientes.setItem(i, 2, QTableWidgetItem(str(paciente[2])))  # Apellido
            self.tabla_pacientes.setItem(i, 3, QTableWidgetItem(str(paciente[4])))  # DPI
            self.tabla_pacientes.setItem(i, 4, QTableWidgetItem(str(paciente[3])))  # Teléfono
            self.tabla_pacientes.setItem(i, 5, QTableWidgetItem(str(paciente[6] if len(paciente) > 6 else "")))  # Cita

    def seleccionar_paciente(self):
        fila_actual = self.tabla_pacientes.currentRow()
        if fila_actual >= 0:
            paciente_id = self.tabla_pacientes.item(fila_actual, 0).text()
            nombre = self.tabla_pacientes.item(fila_actual, 1).text()
            apellido = self.tabla_pacientes.item(fila_actual, 2).text()
            dpi = self.tabla_pacientes.item(fila_actual, 3).text()

            self.paciente_seleccionado = {
                'id': int(paciente_id),
                'nombre_completo': f"{nombre} {apellido}",
                'nombre': nombre,
                'apellido': apellido,
                'dpi': dpi
            }
            self.accept()
        else:
            QMessageBox.warning(self, "Selección", "Por favor seleccione un paciente de la lista.")
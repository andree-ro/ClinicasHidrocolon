from .manager import Manager

columns_ingreso = ['id', 'nombre', 'apellido', 'telefono', 'dpi', 'fecha', 'cita', 'cumpleaños', 'observaciones']


class Pacientes:
    def __init__(self, nombre, apellido, telefono, dpi, fecha, cita, cumpleanos, observaciones, columna=None, valor=None, noInventario=None):
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.dpi = dpi
        self.fecha = fecha
        self.cita = cita
        self.cumpleanos = cumpleanos
        self.observaciones = observaciones
        self.columna = columna
        self.valor = valor
        self.noInventario = noInventario

    def management(self, action):
        if action == 'agre_paciente':
            self.paciente_agre()
        elif action == 'edit_paciente':
            self.paciente_edit()
        elif action == 'elimin_paciente':
            self.paciente_elimin()

    def paciente_edit(self):
        management = Manager()
        management.update_table_with_id('paciente', columns_ingreso, self.columna, self.valor,
                                        self.noInventario)
        # management.update_table_with_id('', '', '', '', '')

    def paciente_agre(self):
        management = Manager()
        data_list = [self.nombre, self.apellido, self.telefono, self.dpi, self.fecha, self.cita, self.cumpleanos, self.observaciones]
        management.insert_into_table('paciente', columns_ingreso, data_list)
        # management.print_table('cliente')

    def paciente_elimin(self):
        management = Manager()
        p = management.delete_id_row_print('paciente', columns_ingreso, self.noInventario, 'nombre')
        return p

    def __str__(self):
        return (f"{self.nombre}, {self.apellido}, {self.telefono}, {self.dpi}, {self.fecha}, {self.cita},"
                f" {self.cumpleanos}, {self.observaciones}")

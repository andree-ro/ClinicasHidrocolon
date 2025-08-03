from .manager import Manager


columns_ingreso = ['id', 'nombre', 'tarjeta', 'efectivo', 'minimo']


class Jornadas:
    def __init__(self, nombre, tarjeta, efectivo, minimo, columna=None, valor=None, noInventario=None):
        self.nombre = nombre
        self.tarjeta = tarjeta
        self.efectivo = efectivo
        self.minimo = minimo
        self.columna = columna
        self.valor = valor
        self.noInventario = noInventario

    def management(self, action):
        if action == 'agre_jornadas':
            self.jornada_agre()
        elif action == 'edit_jornadas':
            self.jornada_edit()
        elif action == 'elimin_jornadas':
            self.jornada_elimin()

    def jornada_edit(self):
        management = Manager()
        management.update_table_with_id('jornadas', columns_ingreso, self.columna, self.valor,
                                        self.noInventario)

    def jornada_agre(self):
        management = Manager()
        data_list = [self.nombre, self.tarjeta, self.efectivo, self.minimo]
        management.insert_into_table('jornadas', columns_ingreso, data_list)

    def jornada_elimin(self):
        management = Manager()
        p = management.delete_id_row_print('jornadas', columns_ingreso, self.noInventario, 'nombre')
        return p

    def __str__(self):
        return (f"{self.nombre}, {self.tarjeta}, {self.efectivo}, {self.minimo}")
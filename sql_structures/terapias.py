from .manager import Manager


columns_ingreso = ['id', 'nombre', 'tarjeta', 'efectivo', 'comision', 'minimo']


class Terapias:
    def __init__(self, nombre, tarjeta, efectivo, comision, minimo, columna=None, valor=None, noInventario=None):
        self.nombre = nombre
        self.tarjeta = tarjeta
        self.efectivo = efectivo
        self.comision = comision
        self.minimo = minimo
        self.columna = columna
        self.valor = valor
        self.noInventario = noInventario

    def management(self, action):
        if action == 'agre_inventarioTerapia':
            self.terapia_agre()
        elif action == 'edit_inventarioTerapia':
            self.terapia_edit()
        elif action == 'elimin_inventarioTerapia':
            self.terapia_elimin()

    def terapia_edit(self):
        management = Manager()
        management.update_table_with_id('terapias', columns_ingreso, self.columna, self.valor,
                                        self.noInventario)

    def terapia_agre(self):
        management = Manager()
        data_list = [self.nombre, self.tarjeta, self.efectivo, self.comision, self.minimo]
        management.insert_into_table('terapias', columns_ingreso, data_list)
        # management.print_table('cliente')

    def terapia_elimin(self):
        management = Manager()
        p = management.delete_id_row_print('terapias', columns_ingreso, self.noInventario, 'nombre')
        return p

    def __str__(self):
        return (f"{self.nombre}, {self.tarjeta}, {self.efectivo}, {self.comision}, {self.minimo}")
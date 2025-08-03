from .manager import Manager

columns_ingreso = ['id', 'nombre', 'tarjeta', 'efectivo', 'minimo']


class Combos:
    def __init__(self, nombre,  tarjeta, efectivo,minimo, columna=None, valor=None,
                 noInventario=None):
        self.nombre = nombre
        self.tarjeta = tarjeta
        self.efectivo = efectivo
        self.minimo = minimo
        self.columna = columna
        self.valor = valor
        self.noInventario = noInventario

    def management(self, action):
        if action == 'agre_promociones':
            self.promociones_agre()
        elif action == 'edit_promociones':
            self.promociones_edit()
        elif action == 'elimin_promociones':
            self.promociones_elimin()

    def promociones_edit(self):
        management = Manager()
        management.update_table_with_id('promociones', columns_ingreso, self.columna, self.valor,
                                        self.noInventario)

    def promociones_agre(self):
        management = Manager()
        data_list = [self.nombre, self.tarjeta, self.efectivo, self.minimo]
        management.insert_into_table('promociones', columns_ingreso, data_list)
        # management.print_table('cliente')

    def promociones_elimin(self):
        management = Manager()
        p = management.delete_id_row_print('promociones', columns_ingreso, self.noInventario, 'nombre')
        return p

    def __str__(self):
        return (f"{self.nombre}, {self.tarjeta}, {self.efectivo}, {self.minimo}")




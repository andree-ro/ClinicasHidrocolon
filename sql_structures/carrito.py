from .manager import Manager

columns_ingreso = ['id', 'nombre', 'existencias', 'tarjeta', 'efectivo', 'medicamentos_id', 'terapias_id',
                   'promociones_id', 'jordas_id', 'ultrasonidos_id', 'consumibles_id']


class Carrito:
    def __init__(self, nombre, existencias, tarjeta, efectivo, medicamentos_id=None, terapias_id=None,
                 promociones_id=None, jordas_id=None, ultrasonidos_id=None, consumibles_id=None, columna=None,
                 valor=None,
                 noInventario=None):
        self.nombre = nombre
        self.tarjeta = tarjeta
        self.efectivo = efectivo
        self.existencias = existencias
        self.medicamentos_id = medicamentos_id
        self.terapias_id = terapias_id
        self.promociones_id = promociones_id
        self.jordas_id = jordas_id
        self.ultrasonidos_id = ultrasonidos_id
        self.consumibles_id = consumibles_id
        self.columna = columna
        self.valor = valor
        self.noInventario = noInventario

    def management(self, action):
        if action == 'agre_carrito':
            self.carrito_agre()
        elif action == 'edit_carrito':
            self.carrito_edit()
        elif action == 'elimin_carrito':
            self.carrito_elimin()

    def carrito_edit(self):
        management = Manager()
        management.update_table_carrito(self.tarjeta, self.efectivo, self.existencias, self.noInventario)

    def carrito_agre(self):
        management = Manager()
        data_list = [self.nombre, self.tarjeta, self.efectivo, self.existencias, self.medicamentos_id,
                     self.terapias_id,
                     self.promociones_id, self.jordas_id, self.ultrasonidos_id, self.consumibles_id]
        print(0)
        management.insert_into_table('carrito', columns_ingreso, data_list
                                )
        print(0)
        # management.print_table('cliente')

    def carrito_elimin(self):
        management = Manager()
        management.delete_id_row('carrito', columns_ingreso, self.noInventario)

    def __str__(self):
        return (f"{self.nombre}, {self.tarjeta}, {self.efectivo}")

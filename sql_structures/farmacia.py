from .manager import Manager

columns_ingreso = ['id', 'nombre', 'presentacion', 'laboratorio', 'existencias', 'fecha', 'tarjeta', 'efectivo',
                   'indicacion', 'contra', 'dosis','costo', 'comision', 'foto']

class InventarioFarmacia:
    def __init__(self, nombre, presentacion, laboratorio, existencias, fecha, tarjeta, efectivo,
                 indicacion, contra, dosis, costo, comision, foto, columna=None, valor=None, noInventario=None):

        self.nombre = nombre
        self.presentacion = presentacion
        self.laboratorio = laboratorio
        self.existencias = existencias
        self.fecha = fecha
        self.tarjeta = tarjeta
        self.efectivo = efectivo
        self.indicacion = indicacion
        self.contra = contra
        self.dosis = dosis
        self.costo = costo
        self.comision = comision

        self.foto = foto
        self.columna = columna
        self.valor = valor
        self.noInventario = noInventario

    def management(self, action):
        if action == 'agre_inventarioFarmacia':
            self.inventarioFarmacia_agre()
        elif action == 'edit_inventarioFarmacia':
            self.inventarioFarmacia_edit()
        elif action == 'elimin_inventarioFarmacia':
            self.inventarioFarmacia_elimin()

    def inventarioFarmacia_edit(self):
        management = Manager()
        print(self.columna, self.valor, self.noInventario)
        management.update_table_with_id('medicamentos', columns_ingreso, self.columna, self.valor,
                                        self.noInventario)

    def inventarioFarmacia_agre(self):
        management = Manager()
        data_list = [self.nombre, self.presentacion, self.laboratorio, self.existencias, self.fecha,
                     self.tarjeta, self.efectivo, self.indicacion, self.contra, self.dosis, self.costo, self.comision,
                     self.foto]
        management.insert_into_table('medicamentos', columns_ingreso, data_list)

    def inventarioFarmacia_elimin(self):
        management = Manager()
        p = management.delete_id_row_print('medicamentos', columns_ingreso, self.noInventario, 'nombre')
        return p
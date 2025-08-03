from .manager import Manager


columns_ingreso = ['id', 'accion', 'modulo', 'modificado', 'fecha', 'usuario']


class Vitacora:
    def __init__(self, accion, modulo, fecha, usuario, modificado, columna=None, valor=None, noInventario=None):
        self.accion = accion
        self.modulo = modulo
        self.fecha = fecha
        self.usuario = usuario
        self.modificado = modificado
        self.columna = columna
        self.valor = valor
        self.noInventario = noInventario

    def management(self, action):
        if action == 'agre_vitacora':
            self.vitacora_agre()

    def vitacora_agre(self):
        management = Manager()
        data_list = [self.accion, self.modulo, self.modificado, self.fecha, self.usuario]
        management.insert_into_table('vitacora', columns_ingreso, data_list)
        # management.print_table('cliente')

    def __str__(self):
        return (f"{self.accion}, {self.modulo}, {self.modificado}, {self.fecha}, {self.usuario}")

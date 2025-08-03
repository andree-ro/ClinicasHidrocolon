from .manager import Manager


columns_ingreso = ['id', 'nombre', 'cantidad', 'total', 'fecha', 'accion', 'doctor','usuario']


class Ventas:
    def __init__(self, nombre, cantidad, total, fecha, accion, doctor, usuario, columna=None, valor=None, noInventario=None):
        self.nombre = nombre
        self.cantidad = cantidad
        self.fecha = fecha
        self.total = total
        self.accion = accion
        self.doctor = doctor
        self.usuario = usuario
        self.columna = columna
        self.valor = valor
        self.noInventario = noInventario

    def management(self, action):
        if action == 'agre_venta':
            self.vitacora_agre()

    def vitacora_agre(self):
        management = Manager()
        print(0)
        data_list = [self.nombre, self.cantidad, self.total, self.fecha, self.accion, self.doctor, self.usuario]
        print(data_list)
        management.insert_into_table('ventas', columns_ingreso, data_list)
        print(10)
        # management.print_table('cliente')

    def __str__(self):
        return (f"{self.nombre}, {self.cantidad}, {self.total}, {self.fecha}, {self.accion}, {self.doctor},"
                f" {self.usuario}")

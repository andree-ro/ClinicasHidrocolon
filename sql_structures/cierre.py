from .manager import Manager

columns_ingreso = ['id', 'nombre', "cantidad", "efectivo", "tarjeta", "monto", "fecha", "usuario", "carrito_id"]


class Cierre:
    def __init__(self, nombre, cantidad, efectivo, tarjeta, monto, fecha, usuario, carrito_id,columna=None, valor=None,
                 noInventario=None):
        self.nombre = nombre
        self.cantidad = cantidad
        self.efectivo = efectivo
        self.tarjeta = tarjeta
        self.monto = monto
        self.fecha = fecha
        self.usuario = usuario
        self.carrito_id = carrito_id
        self.columna = columna
        self.valor = valor
        self.noInventario = noInventario

    def management(self, action):
        if action == 'agre_cierre':
            self.cierre_agre()
        elif action == 'elimi_cierre':
            self.cierre_elimin()

    def cierre_agre(self):
        management = Manager()
        data_list = [self.nombre, self.cantidad, self.efectivo, self.tarjeta, self.monto, self.fecha, self.usuario,
                     self.carrito_id]
        management.insert_into_table('cierre', columns_ingreso, data_list)

    def cierre_elimin(self):
        management = Manager()
        management.delete_id_row('cierre', columns_ingreso, self.noInventario)

    def __str__(self):
        return (f"{self.nombre}, {self.cantidad}, {self.efectivo}, {self.tarjeta}, {self.monto}, {self.fecha},"
                f"{self.usuario},{self.carrito_id}")

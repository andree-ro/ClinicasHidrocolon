from .manager import Manager

# ✅ COLUMNAS ACTUALIZADAS PARA COINCIDIR CON TU TABLA REAL (17 columnas)
columns_ingreso = [
    'id', 'nombre', 'cantidad', 'tarjeta', 'efectivo', 'monto',
    'fecha', 'usuario', 'carrito_id', 'tipo_venta', 'fecha_registro',
    'motivo_ajuste', 'es_ajuste', 'justificacion', 'fecha_original',
    'usuario_ajuste', 'fecha_ajuste'
]

class Cierre:
    def __init__(self, nombre, cantidad, efectivo, tarjeta, monto, fecha, usuario, carrito_id,
                 columna=None, valor=None, noInventario=None, tipo_venta='NORMAL',
                 motivo_ajuste=None, es_ajuste=False, justificacion=None,
                 fecha_original=None, usuario_ajuste=None):
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
        # ✅ NUEVOS CAMPOS PARA AJUSTES
        self.tipo_venta = tipo_venta
        self.motivo_ajuste = motivo_ajuste
        self.es_ajuste = es_ajuste
        self.justificacion = justificacion
        self.fecha_original = fecha_original
        self.usuario_ajuste = usuario_ajuste

    def management(self, action):
        if action == 'agre_cierre':
            self.cierre_agre()
        elif action == 'elimi_cierre':
            self.cierre_elimin()

    def cierre_agre(self):
        management = Manager()
        # ✅ DATOS ACTUALIZADOS CON TODOS LOS CAMPOS (16 valores, el id es AUTO_INCREMENT)
        data_list = [
            self.nombre, self.cantidad, self.tarjeta, self.efectivo, self.monto,
            self.fecha, self.usuario, self.carrito_id, self.tipo_venta,
            None,  # fecha_registro (se maneja automáticamente)
            self.motivo_ajuste, self.es_ajuste, self.justificacion,
            self.fecha_original, self.usuario_ajuste, None  # fecha_ajuste (se maneja automáticamente)
        ]
        # ✅ USAR EL NUEVO MÉTODO SEGURO
        management.insert_into_cierre_safe(data_list)

    def cierre_elimin(self):
        management = Manager()
        management.delete_id_row('cierre', columns_ingreso, self.noInventario)

    def __str__(self):
        return (f"{self.nombre}, {self.cantidad}, {self.efectivo}, {self.tarjeta}, {self.monto}, {self.fecha},"
                f"{self.usuario},{self.carrito_id}")
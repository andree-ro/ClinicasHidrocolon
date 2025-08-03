from .manager import Manager
from encrypt import *

table_name = 'usuario'
table_data = ['id', 'Usuario', 'Contraseña', 'Rol', 'permisos_id']

management = Manager()

encrip = Metodo()
refue = Metodos_refuerzo()
key = "abcdefghijkl12345678!@#$"
key1 = "~~Marp~~__842631597"
a = ""
offset = 8
encrypted = ""


class Usuarios:
    def __init__(self, name, password, role, column=None, data=None, id=None):
        self.name = name
        self.password = password
        self.role = role
        self.column = column
        self.data = data
        self.id = id
        self.encrypted = encrip.encrypt(offset, self.password, key)
        self.permiso_id = self.set_permisos() if self.role != '' else ''

        self.data_list = [self.name, self.encrypted, self.role, self.permiso_id]

    def set_permisos(self):
        if self.role == 'Administrador':
            self.permiso_id = 1
        elif self.role == 'Vendedor':
            self.permiso_id = 2
        elif self.role == 'Secretaria':
            self.permiso_id = 3

        return self.permiso_id

    def validate(self):
        if self.name == '' or self.password == '' or self.role == '--Seleccionar--':
            raise Exception('Datos invalidos')

    def new_use(self):
        self.validate()
        data_list = [self.name, self.encrypted, self.role, self.permiso_id]
        #data_list = [self.name, self.encrypted, self.role, self.permiso_id]
        management.insert_into_table(table_name, table_data, data_list)

    def set_column_name(self):
        if self.column == 'Usuario':
            self.column = 'nombre'

        elif self.column == 'Contraseña':
            self.column = 'contraseña'

    def update_user(self):
        encry = encrip.encrypt(offset, self.data, key)
        management.update_table_with_id('usuario', table_data, "Contraseña", encry, self.id)

    def delete_user(self):
        # management.delete_id_row_print(table_name, table_data, self.id, 'usuario')
        # print(management.delete_id_row_print(table_name, table_data, self.id, 'usuario'))
        p = management.delete_id_row_print(table_name, table_data, self.id, 'usuario')
        return p

    def __str__(self):
        return f"name = {self.name}\npassword = {self.password}\nrole = {self.role}" \
               f"\ncolumn = {self.column}\ndata = {self.data}\nid = {self.id}\n"

import numbers
import datetime

connection = None


import pymysql

def get_db_connection(user, database, password):
    try:
        connection = pymysql.connect(
            host='127.0.0.1',
            user=user,
            password=password,
            database=database,
            port=3306
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


class Manager:
    def __init__(self):
        self.database_user = 'root'
        self.database_password = '2332'
        #self.database_password = '1234'
        self.database_database = 'bdhidrocolon'

        self.conexion = get_db_connection(self.database_user, self.database_database, self.database_password)

        if not self.conexion:
            raise ConnectionError("No se pudo establecer la conexión con la base de datos.")

        self.cursor = self.conexion.cursor()

    def aplicar_precio_efectivosss(self, id_carrito):
        try:
            # Obtener existencias y precio unitario del medicamento
            self.cursor.execute("""
                SELECT existencias, medicamentos_id 
                FROM carrito 
                WHERE id = ?
            """, (id_carrito,))
            resultado = self.cursor.fetchone()

            if resultado:
                existencias, medicamento_id = resultado

                # Obtener precio unitario (efectivo) desde medicamentos
                self.cursor.execute("""
                    SELECT precio_efectivo 
                    FROM medicamentos 
                    WHERE id = ?
                """, (medicamento_id,))
                precio_unitario = self.cursor.fetchone()

                if precio_unitario:
                    total_efectivo = existencias * precio_unitario[0]

                    # Actualizar el total en columna `efectivo`
                    self.cursor.execute("""
                        UPDATE carrito 
                        SET efectivo = ? 
                        WHERE id = ?
                    """, (total_efectivo, id_carrito))
                    self.connection.commit()
        except Exception as e:
            print(f"[ERROR aplicar_precio_efectivo] {e}")

    def get_product_by_id(self, id):
        query = "SELECT * FROM productos WHERE id = ?"
        return self.execute_query(query, (id,))[0]

    def print_table_efectivo_v(self, dato):
        """
        MÉTODO COMPLETO CORREGIDO: Obtiene datos del carrito para generar PDFs
        COPIAR Y PEGAR EN manager.py - REEMPLAZAR EL MÉTODO EXISTENTE
        """
        try:
            print(f"🔍 Obteniendo datos para PDF - Método: {dato}")

            if dato == 'Efectivo':
                query = """SELECT c.nombre, \
                                  COALESCE(m.presentacion, 'N/A') as presentacion, \
                                  c.existencias, \
                                  CASE \
                                      WHEN c.existencias > 0 THEN ROUND(c.efectivo / c.existencias, 2) \
                                      ELSE 0 \
                                      END                         AS precio_unitario, \
                                  c.efectivo                      AS precio_total
                           FROM carrito AS c
                                    LEFT JOIN medicamentos AS m ON m.id = c.medicamentos_id
                           WHERE c.id != -1;"""

            elif dato == 'Tarjeta':
                query = """SELECT c.nombre, \
                                  COALESCE(m.presentacion, 'N/A') as presentacion, \
                                  c.existencias, \
                                  CASE \
                                      WHEN c.existencias > 0 THEN ROUND(c.tarjeta / c.existencias, 2) \
                                      ELSE 0 \
                                      END                         AS precio_unitario, \
                                  c.tarjeta                       AS precio_total
                           FROM carrito AS c
                                    LEFT JOIN medicamentos AS m ON m.id = c.medicamentos_id
                           WHERE c.id != -1;"""
            else:
                # Método por defecto
                query = """SELECT c.nombre, \
                                  COALESCE(m.presentacion, 'N/A') as presentacion, \
                                  c.existencias, \
                                  CASE \
                                      WHEN c.existencias > 0 THEN ROUND(c.efectivo / c.existencias, 2) \
                                      ELSE 0 \
                                      END                         AS precio_unitario, \
                                  c.efectivo                      AS precio_total
                           FROM carrito AS c
                                    LEFT JOIN medicamentos AS m ON m.id = c.medicamentos_id
                           WHERE c.id != -1;"""

            print(f"🔍 Ejecutando consulta SQL...")
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            print(f"🔍 Datos obtenidos: {len(rows) if rows else 0} filas")
            if rows:
                print(f"🔍 Primera fila ejemplo: {rows[0]}")
            else:
                print("⚠️ No se encontraron datos en el carrito")

            return rows

        except Exception as e:
            print(f"❌ ERROR en print_table_efectivo_v: {e}")
            import traceback
            traceback.print_exc()
            return []  # Retornar lista vacía en caso de error

    def obtener_usu(self):
        query = f"SELECT usuario FROM usuario WHERE rol = 'Vendedor'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_id_carrito_id_uni_ve(self, dato):
        query = f"SELECT * FROM cierre WHERE carrito_id = '{dato}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def bitacora_ventas(self):
        consulta = f"SELECT producto, cantidad, total, fecha, accion FROM ventas;"
        self.cursor.execute(consulta)
        datos = self.cursor.fetchall()
        return datos

    def filtro_datos_bitacora(self, fecha_inicio, fecha_fin):
        consulta = f"SELECT accion, modulo, modificado, fecha, usuario FROM vitacora WHERE fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        self.cursor.execute(consulta)
        datos = self.cursor.fetchall()
        return datos

    def contar_datos(self):
        consulta = f"SELECT COUNT(*) AS total_filas FROM carrito;"
        self.cursor.execute(consulta)
        datos = self.cursor.fetchall()
        return datos

    def obtener_datos_desde_mysql_medi(self, tabla):
        consulta = f"SELECT nombre, presentacion, laboratorio, existencias, tarjeta, efectivo, indicacion, contra, dosis, comision, costo FROM {tabla} WHERE id != -1"
        self.cursor.execute(consulta)
        datos = self.cursor.fetchall()
        return datos

    def obtener_datos_desde_mysql(self, tabla):
        consulta = f"SELECT * FROM {tabla} WHERE id != -1"
        self.cursor.execute(consulta)
        datos = self.cursor.fetchall()
        return datos

    def obtener_datos_desde_mysql_paciente(self, tabla):
        consulta = f"SELECT nombre, apellido, telefono, dpi, cita, cumpleaños FROM {tabla} WHERE id != -1"
        self.cursor.execute(consulta)
        datos = self.cursor.fetchall()
        return datos

    def obtener_datos_desde_mysql_cierre(self, tabla):
        consulta = f"SELECT nombre, cantidad, tarjeta, efectivo, monto, fecha, usuario FROM {tabla} WHERE id != -1"
        self.cursor.execute(consulta)
        datos = self.cursor.fetchall()
        return datos

    def close(self):
        self.cursor.close()
        self.conexion.close()

    def is_empty(self, table_name):
        query = f"SELECT COUNT(*) FROM {table_name};"
        self.cursor.execute(query)
        row = self.cursor.fetchall()
        return True if row[0][0] == 0 else False

    def auto_id(self, table_name, table_data):
        if not (self.is_empty(table_name)):
            query = f"SELECT {table_data[0]} FROM {table_name} ORDER BY {table_data[0]} DESC;"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            id = rows[0][0]
            return id + 1
        else:
            id = 1
            return id
        return 0

    def search_by_id(self, table_name, table_data, id_number):
        query = f"SELECT * FROM {table_name} WHERE {table_data[0]} = {id_number}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0]

    def get_id(self, table_name, table_data, data_list):
        query = f"SELECT {table_data[0]} FROM {table_name} WHERE "
        for i, data in enumerate(table_data[1:]):
            value = data_list[i]
            if not (isinstance(value, numbers.Number)):
                query += f"{data} = '{value}' AND " if i != (len(data_list) - 1) else f"{data} = '{value}';"
            else:
                query += f"{data} = {value} AND " if i != (len(data_list) - 1) else f"{data} = {value};"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0][0]

    def get_id_2(self, table_name, dato):
        query = f"SELECT id FROM {table_name} WHERE nombre = '{dato}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0][0]

    def get_montos(self, dato):
        query = f"SELECT {dato} FROM cierre ;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_monto_cierre(self, dato):
        query = f"select (cantidad * {dato}) as monto_total from cierre;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_cantidad(self, dato):
        query = f"SELECT cantidad FROM cierre WHERE id = '{dato}' ;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_cantidad_carrito(self, dato):
        query = f"SELECT existencias FROM carrito WHERE id = '{dato}' ;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_idddd(self, values):
        query = f"SELECT id FROM medicamentos WHERE nombre = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def obtener_id_carrito(self, id):
        query = f"SELECT medicamentos_id FROM carrito where id = '{id}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0][0]


    def get_name(self, values):
        query = f"SELECT nombre FROM cierre WHERE id = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_name_carrito(self, values):
        query = f"SELECT nombre FROM carrito WHERE id = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_dato_tables(self, values, table, dato):
        query = f"SELECT {dato} FROM {table} WHERE id = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_dato_table_real(self, values, table, dato):
        query = f"select ({dato} / existencias) as efectivo from {table} where id = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_tarjeta_tables(self, values, table):
        query = f"SELECT tarjeta FROM {table} WHERE id = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_usuario(self, dato):
        query = f"SELECT rol FROM usuario WHERE contraseña = '{dato}' ;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_existencias(self, dato):
        query = f"SELECT existencias FROM medicamentos WHERE id = '{dato}' ;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0][0]

    def get_id_carrito(self, dato):
        query = f"SELECT cantidad, nombre FROM cierre WHERE carrito_id = '{dato}' ;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_detalle(self, dato):
        query = f"SELECT indicacion, contra, dosis, foto FROM medicamentos WHERE id = '{dato}' ;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows


    def get_id_name(self, dato):
        query = f"SELECT id FROM carrito WHERE nombre = '{dato}' ;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_id_name_pa(self, dato):
        query = f"SELECT id FROM paciente WHERE nombre = '{dato}' ;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0][0]

    def get_id_carrito_id(self, dato, data):
        query = f"SELECT id FROM cierre WHERE cantidad = '{dato}' and carrito_id = '{data}' ;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0][0]

    def get_id_carrito_id_uni (self, dato):
        query = f"SELECT id FROM cierre WHERE cantidad = '{dato}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0][0]

    # def get_ultimo_carrito(self):
    #     # Usando ID (asumiendo que es autoincremental)
    #     query = "SELECT carrito_id FROM cierre ORDER BY id DESC LIMIT 1;"
    #
    #     self.cursor.execute(query)
    #     rows = self.cursor.fetchall()
    #
    #     # Verifica si hay resultados antes de retornar
    #     if rows:
    #         return rows[0]
    #     return None

    def get_ultimo_carrito(self):
        # Usando ID (asumiendo que es autoincremental)
        query = "SELECT carrito_id FROM cierre ORDER BY id DESC LIMIT 1;"

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            # Verifica si hay resultados antes de retornar
            if rows and rows[0]:
                return rows[0]
            else:
                return [0]  # Retorna un valor por defecto si no hay resultados
        except Exception as e:
            print(f"Error al obtener el último carrito: {e}")
            return [0]  # Maneja errores devolviendo un valor por defecto

    def busqueda(self, table_name, dato):
        if dato == "":
            query = f"SELECT * FROM {table_name} WHERE id != -1;"

            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        else:
            query = f"SELECT * FROM {table_name} WHERE nombre LIKE '%{dato}%' AND id != -1;"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows

    def busqueda_medicina(self, dato):
        if dato == "":
            query = f"SELECT id, nombre, presentacion, laboratorio, existencias, fecha, tarjeta, efectivo, indicacion, contra, dosis, comision, costo FROM medicamentos WHERE id != -1;"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        else:
            query = f"SELECT id, nombre, presentacion, laboratorio, existencias, fecha, tarjeta, efectivo, indicacion, contra, dosis, comision, costo FROM medicamentos WHERE nombre LIKE '%{dato}%' AND id != -1;"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows

    def busqueda_usu(self, table_name, dato):
        if dato == "":
            query = f"SELECT * FROM {table_name} WHERE id != -1;"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        else:
            query = f"SELECT * FROM {table_name} WHERE usuario LIKE '%{dato}%' AND id != -1;"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows

    def gett(self, table_name, table_data, data, values):
        query = f"SELECT {table_data} FROM {table_name} WHERE {data} = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0][0]

    def get_carrito(self, table_name, data, values):
        query = f"SELECT id, nombre, existencias, tarjeta, efectivo FROM {table_name} WHERE {data} = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_presentacion(self, table_name, data, values):
        query = f"SELECT presentacion FROM {table_name} WHERE {data} = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0][0]

    def get_carrito_medic(self, table_name, data, values, dato, valor):
        query = f"SELECT nombre, existencias, tarjeta, efectivo FROM {table_name} WHERE {data} = '{values}' and {dato} = '{valor}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_dinero(self, table_name, data):
        query = f"SELECT {data} FROM {table_name};"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_dinero_efectivo(self):
        query = f"SELECT SUM(existencias * (efectivo/existencias)) AS total_efectivo FROM carrito;"
        self.cursor.execute(query)
        result = self.cursor.fetchone()  # ✅ Cambio: fetchone() en lugar de fetchall()

        if result and result[0] is not None:
            return float(result[0])  # ✅ Extraer y convertir a float
        else:
            return 0.0

    def get_dinero_tarjeta(self):
        query = f"SELECT SUM(existencias * (tarjeta/existencias)) AS total_efectivo FROM carrito;"
        self.cursor.execute(query)
        result = self.cursor.fetchone()  # ✅ Cambio: fetchone() en lugar de fetchall()

        if result and result[0] is not None:
            return float(result[0])  # ✅ Extraer y convertir a float
        else:
            return 0.0

    def get_carrito_jo(self, table_name, data, values):
        query = f"SELECT nombre, tarjeta, efectivo FROM {table_name} WHERE {data} = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get(self, table_name, table_data, values, data):
        query = f"SELECT {table_data[0]} FROM {table_name} WHERE {data} = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        # print('rows' + rows[0][0])
        return rows[0][0]

    def get_carrito_devu(self, table_name, table_data, values, data):
        query = f"SELECT carrito_id FROM {table_name} WHERE {data} = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        # print('rows' + rows[0][0])
        return rows[0][0]

    def dar_id_normal(self, table_name, values, data):
        query = f"SELECT id FROM {table_name} WHERE {data} = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0][0]

    def dar_id_normal_nombre(self, table_name, values, data):
        query = f"SELECT id FROM {table_name} WHERE {data} = '{values}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0][0]

    def iniciar_ses(self, data):
        rol = 'rol'
        usuarios = 'Usuario'
        query = f"SELECT {rol} FROM {usuarios} WHERE usuario = '{data}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if rows[0][0] == 'Administrador':
            return 1
        elif rows[0][0] == 'Vendedor':
            return 2
        elif rows[0][0] == 'Secretaria':
            return 3

    def iniciar_contra(self, data):
        contrasena = 'contraseña'
        usuarios = 'Usuario'
        query = f"SELECT {contrasena} FROM {usuarios} WHERE usuario = '{data}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0][0]

    def commi(self):
        self.conexion.commit()

    def rollB(self):
        self.conexion.rollback()

    def insert_into_table(self, table_name, table_data, data_list):
        try:
            self.get_id(table_name, table_data, data_list)
            raise Exception('Dato ya existente')
        except:
            id = self.auto_id(table_name, table_data)
            input_data = f"{id}, "
            for i, value in enumerate(data_list):
                if not (isinstance(value, numbers.Number)):
                    input_data += f"'{value}', " if i != (len(data_list) - 1) else f"'{value}'"
                else:
                    input_data += f"{value}, " if i != (len(data_list) - 1) else f"{value}"
            print(f"INSERT INTO {table_name} VALUES ({input_data})")
            query = f"INSERT INTO {table_name} VALUES ({input_data})"

            self.cursor.execute(query)
            self.conexion.commit()
            return self.print_table(table_name)

    def insert_into_table_NID(self, table_name, table_data, data_list):
        try:
            self.get_id(table_name, table_data, data_list)
            raise Exception('Dato ya existente')
        except:
            self.transactionn()
            input_data = f" "
            for i, value in enumerate(data_list):
                if not (isinstance(value, numbers.Number)):
                    input_data += f"'{value}', " if i != (len(data_list) - 1) else f"'{value}'"
                else:
                    input_data += f"{value}, " if i != (len(data_list) - 1) else f"{value}"
            query = f"INSERT INTO {table_name} VALUES ({input_data})"
            self.cursor.execute(query)
            return self.print_table(table_name)

    def insert_into_cierre_safe(self, data_list):
        query = """
                INSERT INTO cierre
                (nombre, cantidad, tarjeta, efectivo, monto, fecha, usuario, carrito_id,
                 tipo_venta, motivo_ajuste, es_ajuste, justificacion, fecha_original,
                 usuario_ajuste)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        values = (
            data_list[0], data_list[1], data_list[2], data_list[3], data_list[4],
            data_list[5], data_list[6], data_list[7],
            data_list[8] if len(data_list) > 8 else 'NORMAL',
            data_list[10] if len(data_list) > 10 else None,
            data_list[11] if len(data_list) > 11 else False,
            data_list[12] if len(data_list) > 12 else None,
            data_list[13] if len(data_list) > 13 else None,
            data_list[14] if len(data_list) > 14 else None
        )
        self.cursor.execute(query, values)
        self.conexion.commit()
        return self.print_table('cierre')

    def update_table_with_id(self, table_name, table_data, column, data, id):
        data = f"'{data}'" if not (isinstance(data, numbers.Number)) else f"{data}"
        query = f"UPDATE {table_name} SET {column} = {data} WHERE ({table_data[0]} = {id})"
        self.cursor.execute(query)
        self.conexion.commit()
        return self.print_table(table_name)

    def update_table(self, table_name, table_data, data_list, column, data):
        id = self.get_id(table_name, table_data, data_list)
        data = f"'{data}'" if not (isinstance(data, numbers.Number)) else f"{data}"
        query = f"UPDATE {table_name} SET {column} = {data} WHERE ({table_data[0]} = {id})"
        self.cursor.execute(query)
        self.conexion.commit()
        return self.print_table(table_name)

    def update_table_carrito(self, nuevo_tarjeta, nuevo_efectivo, nueva_cantidad, id):
        try:
            query = f"UPDATE carrito SET existencias = {nueva_cantidad}, tarjeta = {nuevo_tarjeta}, efectivo = {nuevo_efectivo} WHERE medicamentos_id = {id}"
            print(nueva_cantidad, nuevo_tarjeta, nuevo_efectivo, id)
            self.cursor.execute(query)
            self.conexion.commit()
            rows = self.cursor.fetchall()
            print(rows)
            return rows
        except Exception as e:
            print(e)

    def obtener_extras_medicamento(self, medicamento_id):
        """Obtiene los extras asociados a un medicamento"""
        try:
            query = "SELECT extra_nombre FROM extras WHERE medicamento_id = %s"
            self.cursor.execute(query, (medicamento_id,))
            extras = [row[0] for row in  self.cursor.fetchall()]
            self.conexion.commit()
            #self.cursor.close()
            #connection.close()
            return extras

        except Exception as e:
            print(f"Error obteniendo extras del medicamento: {e}")
            return []

    def delete_id_row(self, table_name, table_data, id):
        query = f"DELETE FROM {table_name} WHERE ({table_data[0]} = {id});"
        self.cursor.execute(query)
        self.conexion.commit()

        return self.print_table(table_name)

    def delete_id_row_print(self, table_name, table_data, id, dato):
        p = self.print_table_delete(table_name, dato, id)
        query = f"DELETE FROM {table_name} WHERE ({table_data[0]} = {id});"
        self.cursor.execute(query)
        self.conexion.commit()

        return p[0][0]

    def delete_row(self, table_name, table_data, data_list):
        id = self.get_id(table_name, table_data, data_list)
        query = f"DELETE FROM {table_name} WHERE ({table_data[0]} = {id});"
        self.cursor.execute(query)
        self.conexion.commit()
        return self.print_table(table_name)

    def delete_table(self, table_name):
        query = f"DELETE FROM {table_name};"
        self.cursor.execute(query)
        self.conexion.commit()
        return self.print_table(table_name)

    def print_table(self, table_name):
        query = f"SELECT * FROM {table_name} WHERE id != -1;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_citas(self, table_name, cita, hoy):
        query = f"SELECT * FROM {table_name} WHERE DATE(2025-01-09) = DATE(2025-01-08 + INTERVAL 1 DAY);"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_name_carrito(self, table_name):
        query = f"SELECT nombre FROM {table_name} WHERE id != -1;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_cierre(self):
        query = f"""SELECT 
            carrito_id, 
            nombre, 
            cantidad, 
            CASE 
                WHEN tarjeta != 0 THEN ROUND(tarjeta / cantidad, 2) 
                ELSE ROUND(efectivo / cantidad, 2) 
            END AS precio_unitario, 
            CASE 
                WHEN tarjeta != 0 THEN tarjeta 
                ELSE efectivo 
            END AS precio_total, 
            fecha, 
            usuario 
        FROM cierre;"""
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_efectivo(self):
        query = f"SELECT c.nombre, m.presentacion, c.existencias, (c.efectivo/c.existencias) AS Precio, (c.existencias * (c.efectivo/c.existencias)) AS precio_total FROM carrito AS c LEFT JOIN medicamentos AS m ON m.id = c.medicamentos_id;"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_tarjeta(self):
        query = f"SELECT c.nombre, m.presentacion, c.existencias, (c.tarjeta/c.existencias) AS Precio, (c.existencias * (c.tarjeta/c.existencias)) AS precio_total FROM carrito AS c LEFT JOIN medicamentos AS m ON m.id = c.medicamentos_id;"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_delete(self, table_name, dato, id):
        query = f"SELECT {dato} FROM {table_name} WHERE id = {id};"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_farmacia(self):
        try:
            query = f"SELECT id, nombre, presentacion, laboratorio, existencias, fecha, tarjeta, efectivo, indicacion, contra, dosis, costo, comision FROM medicamentos WHERE id != -1;"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print("error en consulta" + str(e))

    def print_table_dia(self, table_name, dato):
        query = f"SELECT * FROM {table_name} WHERE id != -1 AND fecha = '{dato}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_dia_cierre(self, dato):
        query = f"""SELECT 
            carrito_id, 
            nombre, 
            cantidad, 
            CASE 
                WHEN tarjeta != 0 THEN ROUND(tarjeta / cantidad, 2) 
                ELSE ROUND(efectivo / cantidad, 2) 
            END AS precio_unitario, 
            CASE 
                WHEN tarjeta != 0 THEN tarjeta 
                ELSE efectivo 
            END AS precio_total, 
            fecha, 
            usuario 
        FROM cierre 
        WHERE id != -1 AND fecha = '{dato}';"""
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_montos_dia(self, dato, dia):
        query = f"SELECT (cantidad * {dato}) as monto_total FROM cierre WHERE id != -1 AND fecha = '{dia}';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_semana(self, table_name, dato):
        query = f"""SELECT 
            carrito_id, 
            nombre, 
            cantidad, 
            CASE 
                WHEN tarjeta != 0 THEN ROUND(tarjeta / cantidad, 2) 
                ELSE ROUND(efectivo / cantidad, 2) 
            END AS precio_unitario, 
            CASE 
                WHEN tarjeta != 0 THEN tarjeta 
                ELSE efectivo 
            END AS precio_total, 
            fecha, 
            usuario 
        FROM cierre 
        WHERE id != -1 AND WEEK(fecha) = WEEK('{dato}');"""
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_montos_semana(self, dato, dia):
        query = f"SELECT (cantidad * {dato}) as monto_total FROM cierre WHERE id != -1 AND WEEK(fecha) = WEEK('{dia}');"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_mes(self, table_name, dato):
        query = f"""SELECT 
            carrito_id, 
            nombre, 
            cantidad, 
            CASE 
                WHEN tarjeta != 0 THEN ROUND(tarjeta / cantidad, 2) 
                ELSE ROUND(efectivo / cantidad, 2) 
            END AS precio_unitario, 
            CASE 
                WHEN tarjeta != 0 THEN tarjeta 
                ELSE efectivo 
            END AS precio_total, 
            fecha, 
            usuario 
        FROM cierre 
        WHERE id != -1 AND MONTH(fecha) = MONTH('{dato}');"""
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_montos_mes(self, dato, dia):
        query = f"SELECT (cantidad * {dato}) as monto_total FROM cierre WHERE id != -1 AND MONTH(fecha) = MONTH('{dia}');"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_cumple_mes (self, dato):
        query = f"SELECT * FROM paciente WHERE id != -1 AND MONTH(cumpleaños) = MONTH('{dato}') ;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_cita (self, dato):
        query = f"SELECT * FROM paciente WHERE cita = '{dato}' ;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_table_año(self, table_name, dato):
        query = f"""SELECT 
            carrito_id, 
            nombre, 
            cantidad, 
            CASE 
                WHEN tarjeta != 0 THEN ROUND(tarjeta / cantidad, 2) 
                ELSE ROUND(efectivo / cantidad, 2) 
            END AS precio_unitario, 
            CASE 
                WHEN tarjeta != 0 THEN tarjeta 
                ELSE efectivo 
            END AS precio_total, 
            fecha, 
            usuario 
        FROM cierre 
        WHERE id != -1 AND YEAR(fecha) = YEAR('{dato}');"""
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_montos_año(self, dato, dia):
        query = f"SELECT (cantidad * {dato}) as monto_total FROM cierre WHERE id != -1 AND YEAR(fecha) = YEAR('{dia}');"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def aplicar_precio_efectivo(self, carrito_id):
        """Aplica el precio de efectivo a un item del carrito"""
        try:
            #conexion = self.obtener_conexion()
            self.cursor = self.conexion.cursor()


            # Estructura de carrito: id, nombre, existencias, tarjeta, efectivo, medicamentos_id, terapias_id, promociones_id, jordas_id, ultrasonidos_id, consumibles_id

            datos = f"SELECT medicamentos_id, terapias_id, promociones_id, jordas_id, existencias, nombre FROM carrito WHERE id = {carrito_id}"
            self.cursor.execute(datos)
            dato = self.cursor.fetchone()
            print(dato[1])
            if dato[0] > 0:
                # Para medicamentos
                query = """
                       UPDATE carrito c
                       INNER JOIN medicamentos m ON c.medicamentos_id = m.id
                       SET c.efectivo = m.efectivo * c.existencias,
                           c.tarjeta = m.efectivo * c.existencias
                       WHERE c.id = %s AND c.medicamentos_id IS NOT NULL AND c.medicamentos_id != -1
                       """
                self.cursor.execute(query, (carrito_id,))

            # Para terapias
            if dato[1] > 0:
                query = """
                       UPDATE carrito c
                       INNER JOIN terapias t ON c.terapias_id = t.id
                       SET c.efectivo = t.efectivo * c.existencias,
                           c.tarjeta = t.efectivo * c.existencias
                       WHERE c.id = %s AND c.terapias_id IS NOT NULL AND c.terapias_id != -1
                       """
                self.cursor.execute(query, (carrito_id,))

            # Para jornadas
            if dato[3] > 0:
                query = """
                       UPDATE carrito c
                       INNER JOIN jornadas j ON c.jordas_id = j.id
                       SET c.efectivo = j.efectivo * c.existencias,
                           c.tarjeta = j.efectivo * c.existencias
                       WHERE c.id = %s AND c.jordas_id IS NOT NULL AND c.jordas_id != -1
                       """
                self.cursor.execute(query, (carrito_id,))

            # Para promociones
            if dato[2] > 0:
                query = """
                       UPDATE carrito c
                       INNER JOIN promociones p ON c.promociones_id = p.id
                       SET c.efectivo = p.efectivo * c.existencias,
                           c.tarjeta = p.efectivo * c.existencias
                       WHERE c.id = %s AND c.promociones_id IS NOT NULL AND c.promociones_id != -1
                       """
                self.cursor.execute(query, (carrito_id,))

            self.conexion.commit()
            self.cursor.close()
            self.conexion.close()

        except Exception as e:
            print(f"[ERROR aplicar_precio_efectivo] {e}")
            raise

    def aplicar_precio_tarjeta(self, carrito_id):
        """Aplica el precio de tarjeta a un item del carrito"""
        try:
            #conexion = self.obtener_conexion()
            self.cursor = self.conexion.cursor()

            # Para medicamentos
            query = """
                    UPDATE carrito c
                    INNER JOIN medicamentos m ON c.medicamentos_id = m.id
                    SET c.efectivo = m.tarjeta * c.existencias,
                        c.tarjeta = m.tarjeta * c.existencias
                    WHERE c.id = %s AND c.medicamentos_id IS NOT NULL AND c.medicamentos_id != -1
                    """
            self.cursor.execute(query, (carrito_id,))

            # Para terapias
            query = """
                    UPDATE carrito c
                    INNER JOIN terapias t ON c.terapias_id = t.id
                    SET c.efectivo = t.tarjeta * c.existencias,
                        c.tarjeta = t.tarjeta * c.existencias
                    WHERE c.id = %s AND c.terapias_id IS NOT NULL AND c.terapias_id != -1
                    """
            self.cursor.execute(query, (carrito_id,))

            # Para jornadas
            query = """
                    UPDATE carrito c
                    INNER JOIN jornadas j ON c.jordas_id = j.id
                    SET c.efectivo = j.tarjeta * c.existencias,
                        c.tarjeta = j.tarjeta * c.existencias
                    WHERE c.id = %s AND c.jordas_id IS NOT NULL AND c.jordas_id != -1
                    """
            self.cursor.execute(query, (carrito_id,))

            # Para promociones
            query = """
                    UPDATE carrito c
                    INNER JOIN promociones p ON c.promociones_id = p.id
                    SET c.efectivo = p.tarjeta * c.existencias,
                        c.tarjeta = p.tarjeta * c.existencias
                    WHERE c.id = %s AND c.promociones_id IS NOT NULL AND c.promociones_id != -1
                    """
            self.cursor.execute(query, (carrito_id,))

            self.conexion.commit()
            self.cursor.close()
            self.conexion.close()

        except Exception as e:
            print(f"[ERROR aplicar_precio_tarjeta] {e}")
            raise

    def print_table_carrito_individual(self):
        """Obtiene los datos del carrito respetando los precios individuales de cada item"""
        query = f"""SELECT 
            c.nombre, 
            m.presentacion, 
            c.existencias, 
            CASE 
                WHEN c.efectivo = c.tarjeta THEN (c.efectivo/c.existencias)
                ELSE (c.efectivo/c.existencias)
            END AS precio_unitario, 
            c.efectivo AS precio_total 
        FROM carrito AS c 
        LEFT JOIN medicamentos AS m ON m.id = c.medicamentos_id;"""

        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def ejecutar_consulta_personalizada(self, query, params=None):
        """Ejecuta una consulta personalizada y retorna los resultados"""
        try:
            cursor = self.db_connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Si es un SELECT, retornar resultados
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                # Si es INSERT, UPDATE, DELETE, hacer commit
                self.db_connection.commit()
                return cursor.rowcount

        except Exception as e:
            print(f"Error en consulta: {e}")
            self.db_connection.rollback()
            raise e
        finally:
            cursor.close()

    # PASO 3: AGREGAR ESTAS FUNCIONES AL FINAL DE LA CLASE Manager en sql_structures/manager.py

    def buscar_paciente_por_identificador(self, identificador):
        """
        Busca paciente por DPI, nombre completo o teléfono
        """
        try:
            cursor = self.conexion.cursor()

            print(f"🔍 Buscando paciente con: '{identificador}'")

            # Buscar por DPI (exacto)
            cursor.execute("SELECT * FROM paciente WHERE dpi = %s", (identificador,))
            resultado = cursor.fetchone()
            if resultado:
                print(f"✅ Encontrado por DPI: {resultado[1]} {resultado[2]}")
                return resultado

            # Buscar por teléfono (exacto Y como string)
            cursor.execute("SELECT * FROM paciente WHERE telefono = %s OR telefono = %s",
                           (identificador, str(identificador)))
            resultado = cursor.fetchone()
            if resultado:
                print(f"✅ Encontrado por teléfono: {resultado[1]} {resultado[2]}")
                return resultado

            # Buscar por nombre (coincidencia parcial) - MÁS FLEXIBLE
            cursor.execute("""
                           SELECT *
                           FROM paciente
                           WHERE LOWER(CONCAT(nombre, ' ', apellido)) LIKE LOWER(%s)
                              OR LOWER(nombre) LIKE LOWER(%s)
                              OR LOWER(apellido) LIKE LOWER(%s)
                           ORDER BY nombre
                           """, (f"%{identificador}%", f"%{identificador}%", f"%{identificador}%"))

            resultados = cursor.fetchall()
            if resultados:
                print(f"✅ Encontrados {len(resultados)} por nombre")
                return resultados

            print(f"❌ No se encontró paciente con: '{identificador}'")
            return None

        except Exception as e:
            print(f"❌ Error en búsqueda de paciente: {e}")
            return None

    def obtener_paciente_por_id(self, paciente_id):
        """
        Obtiene información de un paciente por su ID
        """
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT * FROM paciente WHERE id = %s", (paciente_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener paciente por ID: {e}")
            return None

    def obtener_historial_compras_paciente(self, paciente_id, limite=None):
        """
        Obtiene el historial de compras de un paciente
        """
        try:
            cursor = self.conexion.cursor()
            query = """
                    SELECT h.id, \
                           h.producto_nombre, \
                           h.cantidad, \
                           h.precio_unitario, \
                           h.precio_total, \
                           h.tipo_pago, \
                           h.fecha_compra, \
                           h.vendedor, \
                           h.observaciones, \
                           m.presentacion, \
                           m.laboratorio
                    FROM historial_compras_pacientes h
                             LEFT JOIN medicamentos m ON h.medicamento_id = m.id
                    WHERE h.paciente_id = %s
                    ORDER BY h.fecha_compra DESC \
                    """

            if limite:
                query += f" LIMIT {limite}"

            cursor.execute(query, (paciente_id,))
            return cursor.fetchall()

        except Exception as e:
            print(f"Error al obtener historial: {e}")
            return []

    def registrar_compra_en_historial(self, paciente_id, venta_id, items_carrito, tipo_pago, vendedor):
        """
        Registra los items del carrito en el historial del paciente
        """
        try:
            cursor = self.conexion.cursor()

            for item in items_carrito:
                cursor.execute("""
                               INSERT INTO historial_compras_pacientes
                               (paciente_id, venta_id, medicamento_id, producto_nombre,
                                cantidad, precio_unitario, precio_total, tipo_pago,
                                fecha_compra, vendedor)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
                               """, (
                                   paciente_id,
                                   venta_id,
                                   item.get('medicamento_id'),
                                   item['nombre'],
                                   item['cantidad'],
                                   item['precio_unitario'],
                                   item['precio_total'],
                                   tipo_pago,
                                   vendedor
                               ))

            self.conexion.commit()
            return True

        except Exception as e:
            print(f"Error al registrar en historial: {e}")
            self.conexion.rollback()
            return False

    def obtener_carrito_completo(self):
        """
        Obtiene todos los items del carrito actual
        """
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                           SELECT c.id,
                                  c.nombre,
                                  c.existencias              as cantidad,
                                  c.efectivo / c.existencias as precio_unitario,
                                  c.efectivo                 as precio_total,
                                  c.medicamentos_id
                           FROM carrito c
                           """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener carrito: {e}")
            return []

    def __str__(self):
        return f"Usuario: {self.database_user}\nContrasenia: {self.database_password}" \
               f"\nBase de datos: {self.database_database}"
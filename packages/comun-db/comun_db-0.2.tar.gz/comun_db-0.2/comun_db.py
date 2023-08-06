import pyodbc


class Sql:
    def __init__(self, driver, servidor, database, user, passw):
        self.nombre = 'DRIVER=' + driver
        self.nombre = self.nombre + ';SERVER=' + servidor
        self.nombre = self.nombre + ';DATABASE=' + database
        self.nombre = self.nombre + ';UID=' + user
        self.nombre = self.nombre + ';PWD=' + passw
        self.conexion = pyodbc.connect(self.nombre, autocommit=False)
        self.cursor = self.conexion.cursor()

    def cerrar_conexion(self):
        self.conexion.close()

    def ejecutar(self, texto, *parametros):
        try:
            if len(parametros):
                if type(parametros[0]) == tuple:
                    parametros = parametros[0]
            self.cursor.execute(texto,parametros)
            self.conexion.commit()
        except Exception as e:
            print(texto)
            print(parametros)
            print(e)
            raise Exception(e)

    def consultar(self, consulta):
        self.cursor.execute(consulta)
        return self.cursor.fetchall()


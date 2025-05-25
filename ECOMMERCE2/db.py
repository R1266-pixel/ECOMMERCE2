import pymysql
import pymysql.cursors
import config  # Asegúrate de tener config.py con DB_CONFIG definido
from colorama import Fore, init

init(autoreset=True)

class Database:
    def __enter__(self):
        try:
            self.conn = pymysql.connect(**config.DB_CONFIG)
            self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
            return self.cur
        except Exception as e:
            print(Fore.RED + f"Error de conexión a la base de datos: {e}")
            self.conn = None
            self.cur = None
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            self.cur.close()
            self.conn.close()

class Cliente:
    def __init__(self, nombre, numero, correo, direccion):
        self.nombre = nombre
        self.numero = numero
        self.correo = correo
        self.direccion = direccion

    def CREATE(self):
        try:
            with Database() as cur:
                sql = """
                INSERT INTO cliente(correo, numero_contacto, nombre, cp, ciudad, calle, numero, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    self.correo,
                    self.numero,
                    self.nombre,
                    self.direccion["cp"],
                    self.direccion["ciudad"],
                    self.direccion["calle"],
                    self.direccion["numero"],
                    "cliente"
                )
                cur.execute(sql, valores)
        except Exception as e:
            print(Fore.RED + f"Error al agregar cliente: {e}")

    @classmethod
    def READ_ALL(cls):
        try:
            with Database() as cur:
                cur.execute("SELECT * FROM cliente")
                return cur.fetchall()
        except Exception as e:
            print(Fore.RED + f"Error al leer clientes: {e}")
            return []

    
    @classmethod
    def LOGIN(cls, correo, numero_contacto):
        try:
            with Database() as cur:
                cur.execute(
                    "SELECT * FROM cliente WHERE correo = %s AND numero_contacto = %s",
                    (correo, numero_contacto)
                )
                return cur.fetchone()
        except Exception as e:
            print(f"Error al iniciar sesión: {e}")
            return None

class Producto:
    """
    Clase para manejar los productos en la base de datos.
    """
    def __init__(self, precio, color, nombre, categoria):
        self.precio = precio
        self.color = color
        self.nombre = nombre
        self.categoria = categoria

    def CREATE(self):
        """
        Inserta un nuevo producto en la base de datos.
        """
        try:
            with Database() as cur:
                sql = """
                INSERT INTO producto (nombre, precio, color, categoria) 
                VALUES (%s, %s, %s, %s)
                """
                valores = (self.nombre, self.precio, self.color, self.categoria)
                print(f"Insertando producto: {valores}")  # Depuración
                cur.execute(sql, valores)
        except Exception as e:
            print(Fore.RED + f"Error al agregar producto: {e}")

    


    @classmethod
    def READ_ALL(cls):
        try:
            with Database() as cur:
             cur.execute("SELECT ID, NOMBRE, PRECIO, COLOR, CATEGORIA FROM producto")
            productos = cur.fetchall()
            
            return productos
        except Exception as e:
           print(Fore.RED + f"Error al leer productos: {e}")
        return []



    @classmethod
    def DELETE(cls, producto_id):
        try:
            with Database() as cur:
                sql = "DELETE FROM producto WHERE ID = %s"
                cur.execute(sql, (producto_id,))
                print(Fore.GREEN + f"Producto con ID {producto_id} eliminado.")
        except Exception as e:
            print(Fore.RED + f"Error al eliminar producto: {e}")

    @classmethod
    def DELETE_VENTAS(cls, ID_PRODUCTO):
        try:
            with Database() as cur:
                sql = "DELETE FROM VENTAS WHERE ID_PRODUCTO = %s"
                cur.execute(sql, (ID_PRODUCTO,))
                print(Fore.GREEN + f"Producto con ID {ID_PRODUCTO} eliminado.")
        except Exception as e:
            print(Fore.RED + f"Error al eliminar producto: {e}")

    class Producto:
     @classmethod
     def READ_BY_ID(cls, producto_id):
        try:
            with Database() as cur:
                sql = "SELECT * FROM producto WHERE ID = %s"
                cur.execute(sql, (producto_id,))
                return cur.fetchone()
        except Exception as e:
            print(Fore.RED + f"Error al buscar producto por ID: {e}")
            return None

class Ventas:
    def __init__(self, cliente_id, producto_id, cantidad):
        self.cliente_id = cliente_id
        self.producto_id = producto_id
        self.cantidad = cantidad

    def CREATE(self):
        try:
            with Database() as cur:
                sql = "INSERT INTO ventas(cliente_id, producto_id, cantidad) VALUES (%s, %s, %s)"
                cur.execute(sql, (self.cliente_id, self.producto_id, self.cantidad))
        except Exception as e:
            print(Fore.RED + f"Error al registrar venta: {e}")

    @classmethod
    def READ_ALL(cls):
        try:
            with Database() as cur:
                cur.execute("SELECT * FROM ventas")
                return cur.fetchall()
        except Exception as e:
            print(Fore.RED + f"Error al leer ventas: {e}")
            return []

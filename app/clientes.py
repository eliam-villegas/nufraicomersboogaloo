import os
import psycopg2
import time
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from database import get_db_postgres

load_dotenv()

class Database:
    #se establece conexion con la base de datos postgres
    def __init__(self):
        self.connection = None
        self._connect_to_db()

    def _connect_to_db(self):
        """Intento de conexión a la base de datos con reintentos"""
        retries = 5
        while retries > 0:
            try:
                # Configuración de conexión directa con PostgreSQL
                self.connection = psycopg2.connect(os.getenv('DATABASE_URI'))
                self.connection.autocommit = True
                print("Conexión exitosa a la base de datos")
                self._initialize_tables()
                break
            except Exception as e:
                print(f"Error al conectar con la base de datos: {e}")
                print("Reintentando en 5 segundos...")
                time.sleep(5)
                retries -= 1
        if retries == 0:
            print("No se pudo establecer conexión con la base de datos después de varios intentos.")
    
    def _initialize_tables(self):
        """Creación de tablas si no existen y usuario administrador"""
        try:
            with self.connection.cursor() as cursor:
                
                admin_email = os.getenv('ADMIN_USER')
                admin_password = os.getenv('ADMIN_PASS')
                
                if not admin_email or not admin_password:
                    print("Error: Las credenciales del administrador no están definidas en el archivo .env")
                    return
                
                # Generar el hash de la contraseña
                hashed_password = generate_password_hash(admin_password)
                
                # Verificar si el usuario administrador ya existe
                cursor.execute("SELECT * FROM users WHERE email = %s;", (admin_email,))
                admin_user = cursor.fetchone()
                
                if not admin_user:
                    cursor.execute("""
                    INSERT INTO users (name, email, address, password,role)
                    VALUES (%s, %s, %s, %s, %s);
                    """, ("Admin", admin_email, "Admin Address", hashed_password,"admin"))
                    print("Usuario administrador creado correctamente")
                else:
                    print("El usuario administrador ya existe")
                    
        except Exception as e:
            print(f"Error al crear las tablas o el usuario administrador: {e}")

    def insert_user(self, name, email, address, password):
        """Inserta un nuevo usuario en la base de datos"""
        try:
            with self.connection.cursor() as cursor:
                #el usuario por defecto tiene el rol de usuario.
                cursor.execute("""
                INSERT INTO users (name, email, address, password,role)
                VALUES (%s, %s, %s, %s,%s)
                RETURNING id;
                """, (name, email, address, password,'usuario'))
                user_id = cursor.fetchone()[0]
                print(f"Usuario insertado con ID: {user_id}")
                return user_id
        except Exception as e:
            print(f"Error al insertar el usuario: {e}")

    def insert_purchase(self, user_id, product_name, amount):
        """Inserta una nueva compra en la base de datos"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                INSERT INTO purchases (user_id, product_name, amount)
                VALUES (%s, %s, %s)
                RETURNING id;
                """, (user_id, product_name, amount))
                purchase_id = cursor.fetchone()[0]
                print(f"Compra insertada con ID: {purchase_id}")
                return purchase_id
        except Exception as e:
            print(f"Error al insertar la compra: {e}")

    def get_user_by_email(self, email):
        conn = get_db_postgres()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = %s;', (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            return user
            """# Devolver los datos del usuario en forma de diccionario
                return {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "address": user[3],
                    "password": user[4],
                    "role": user[5]
                }"""
        except Exception as e:
            print(f"Error al buscar el usuario: {e}")
        return None
    
    def get_user_by_username(self, username):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE name = %s;", (username,))
                user = cursor.fetchone()
                if user:
                    # Devolver los datos del usuario en forma de diccionario
                    return {
                        "id": user[0],
                        "name": user[1],
                        "email": user[2],
                        "address": user[3],
                        "password": user[4],
                        "role": user[5]
                    }
        except Exception as e:
            print(f"Error al buscar el usuario: {e}")
        return None

    def get_all_users(self):
        """Obtiene todos los usuarios de la base de datos"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id, name, email, address FROM users;")
                users = cursor.fetchall()
                # Convertir el resultado en una lista de diccionarios
                return [
                    {"id": user[0], "name": user[1], "email": user[2], "address": user[3]}
                    for user in users
                ]
        except Exception as e:
            print(f"Error al obtener los usuarios: {e}")
            return []

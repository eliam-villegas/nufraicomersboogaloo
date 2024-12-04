import os
import psycopg2
import time
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener la clave secreta desde el archivo .env
SECRET_KEY = 'e5f67a4efab7f3c3d5a82a4a27f601b8742e3edbd8ab6df1a68eac73c9d45e3f'


class Database:
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
                # Crear tabla de roles
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL
                );
                """)

                # Crear tabla de relaciones entre usuarios y roles
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
                    PRIMARY KEY (user_id, role_id)
                );
                """)

                # Crear tabla de usuarios
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(80) NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    address VARCHAR(200) NOT NULL,
                    password VARCHAR(200) NOT NULL
                );
                """)

                # Crear tabla de compras
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    product_name VARCHAR(100) NOT NULL,
                    amount INTEGER NOT NULL
                );
                """)

                print("Tablas creadas o verificadas correctamente")

                # Insertar roles por defecto
                self._insert_default_roles(cursor)
                # Crear el usuario administrador
                self._create_admin_user(cursor)

        except Exception as e:
            print(f"Error al crear las tablas o el usuario administrador: {e}")

    def _insert_default_roles(self, cursor):
        """Insertar roles por defecto"""
        roles = ['admin', 'user', 'moderator', 'guest']  # Definir roles por defecto
        for role in roles:
            cursor.execute("""
            INSERT INTO roles (name) 
            VALUES (%s) 
            ON CONFLICT (name) DO NOTHING;
            """, (role,))

    def _create_admin_user(self, cursor):
        """Crear el usuario administrador"""
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
            INSERT INTO users (name, email, address, password)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """, ("Admin", admin_email, "Admin Address", hashed_password))
            admin_id = cursor.fetchone()[0]
            print("Usuario administrador creado correctamente")

            # Asignar el rol de administrador al usuario
            cursor.execute("""
            INSERT INTO user_roles (user_id, role_id) 
            VALUES (%s, (SELECT id FROM roles WHERE name = 'admin'));
            """, (admin_id,))
        else:
            print("El usuario administrador ya existe")

    def insert_user(self, name, email, address, password):
        """Inserta un nuevo usuario en la base de datos"""
        try:
            hashed_password = generate_password_hash(password)
            with self.connection.cursor() as cursor:
                cursor.execute("""
                INSERT INTO users (name, email, address, password)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """, (name, email, address, hashed_password))
                user_id = cursor.fetchone()[0]
                print(f"Usuario insertado con ID: {user_id}")

                # Asignar el rol de 'user' al nuevo usuario
                cursor.execute("""
                INSERT INTO user_roles (user_id, role_id) 
                VALUES (%s, (SELECT id FROM roles WHERE name = 'user'));
                """, (user_id,))

                return user_id
        except Exception as e:
            print(f"Error al insertar el usuario: {e}")
            return None

    def verify_user(self, email, password):
        """Verifica que el usuario y la contraseña coincidan y genera JWT"""
        user = self.get_user_by_email(email)
        if user:
            if check_password_hash(user["password"], password):
                print("Inicio de sesión exitoso")
                # Obtener los roles del usuario
                with self.connection.cursor() as cursor:
                    cursor.execute("""
                    SELECT r.name FROM roles r
                    JOIN user_roles ur ON r.id = ur.role_id
                    WHERE ur.user_id = %s;
                    """, (user["id"],))
                    roles = [row[0] for row in cursor.fetchall()]
                # Generar JWT con roles
                token = self.generate_jwt(user["id"], roles)
                return token
            else:
                print("Contraseña incorrecta")
        else:
            print("Usuario no encontrado")
        return None

    def generate_jwt(self, user_id, roles):
        """Genera un token JWT con el ID del usuario y sus roles"""
        payload = {
            "user_id": user_id,
            "roles": roles,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Expiración de 24 horas
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token

    def verify_jwt(self, token):
        """Verifica un token JWT"""
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return decoded_token
        except jwt.ExpiredSignatureError:
            print("El token ha expirado")
            return None
        except jwt.InvalidTokenError:
            print("Token inválido")
            return None

    def check_role(self, decoded_token, required_role):
        """Verifica si el usuario tiene el rol necesario"""
        if decoded_token and required_role in decoded_token['roles']:
            return True
        else:
            print(f"No tiene el rol {required_role}")
            return False

    def protected_route(self, token, required_role):
        """Verifica el token y el rol para acceder a la ruta protegida"""
        decoded_token = self.verify_jwt(token)
        if decoded_token and self.check_role(decoded_token, required_role):
            print("Acceso autorizado")
            return True
        else:
            print("Acceso denegado")
            return False

    def get_user_by_email(self, email):
        """Obtiene un usuario por su email, incluyendo el rol"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT users.id, users.name, users.email, users.address, users.password, roles.name AS role
                    FROM users
                    JOIN user_roles ON users.id = user_roles.user_id
                    JOIN roles ON roles.id = user_roles.role_id
                    WHERE users.email = %s;
                """, (email,))

                user = cursor.fetchone()
                if user:
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

    def get_all_users(self, limit, offset):
        """Obtiene todos los usuarios con paginación"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, email, address 
                    FROM users
                    LIMIT %s OFFSET %s
                """, (limit, offset))
                users = cursor.fetchall()
                return users
        except Exception as e:
            print(f"Error al obtener los usuarios: {e}")
        return []

    def get_user_by_id(self, user_id):
        """Obtiene un usuario por su ID, incluyendo sus roles"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT users.id, users.name, users.email, users.address, roles.name AS role
                    FROM users
                    JOIN user_roles ON users.id = user_roles.user_id
                    JOIN roles ON roles.id = user_roles.role_id
                    WHERE users.id = %s;
                """, (user_id,))

                # Traemos todos los roles asociados al usuario
                user = cursor.fetchall()
                if user:
                    # Devolvemos los datos del usuario junto con sus roles
                    return {
                        "id": user[0][0],
                        "name": user[0][1],
                        "email": user[0][2],
                        "address": user[0][3],
                        "roles": [row[4] for row in user]  # Todos los roles del usuario
                    }
        except Exception as e:
            print(f"Error al obtener el usuario por ID: {e}")
        return None

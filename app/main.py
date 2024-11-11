from flask import Flask, render_template, jsonify, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash 
import psycopg2 
from psycopg2.extras import RealDictCursor
from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt 
from flask_cors import CORS

from app.database import get_db
from bson.objectid import ObjectId

from app.auth_service.auth_function import auth

db_postgres = SQLAlchemy()

app = Flask(__name__) 
app.secret_key = 'supercalifrajilisticoespiralidoso'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@postgres:5432/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.register_blueprint(auth, url_prefix='/auth')

#conexion a postgres
db_postgres.init_app(app)

# Conexión a MongoDB
db = get_db()
productos_collection = db['productos']

@app.before_request
def before_request():
    # Verificar si el usuario está logueado y pasar la variable 'logged_in' a todas las plantillas
    g.logged_in = 'user_id' in session  # Booleano que indica si el usuario está logueado
    g.user_id = session.get('user_id')

@app.route('/')
def index():
    if 'user_id' in session:
        # Renderizar una vista para usuario logueado
        return render_template('index.html', logged_in=g.logged_in, user=g.user_id)
    else:
        # Renderizar una vista para usuario no logueado
        return render_template('index.html', logged_in=False)

@app.route('/carrito')
def prueba():
    return render_template('prueba.html', logged_in=g.logged_in, user=g.user_id)

@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    productos = list(productos_collection.find({}, {"_id": 1, "nombre": 1, "precio": 1, "descripcion": 1, "imagenes": 1, "stock": 1, "categoria": 1, "estado": 1}))
    for producto in productos:
        producto["_id"] = str(producto["_id"])  # Convertimos el ObjectId en string
    return jsonify({"productos": productos})

@app.route('/productos')
def productos():
    return render_template('productos.html', logged_in=g.logged_in, user=g.user_id)

@app.route('/logged')
def logged():
    return render_template('logged.html')

# Ruta para obtener un producto por su ID
@app.route('/api/producto/<id>', methods=['GET'])
def obtener_producto(id):
    producto = productos_collection.find_one({"_id": ObjectId(id)}, {"_id": 1, "nombre": 1, "precio": 1, "descripcion": 1, "imagenes": 1, "stock": 1, "categoria": 1, "estado": 1})
    if producto:
        producto["_id"] = str(producto["_id"])  # Convertir ObjectId a string
        return jsonify(producto)
    return jsonify({"error": "Producto no encontrado"}), 404



# Ruta para manejar tanto GET (renderizar el formulario) como POST (procesar el formulario)
@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        # Recoge los datos del formulario enviados en formato JSON
        data = request.get_json()
        nombre = data.get('nombre')
        precio = data.get('precio')
        descripcion = data.get('descripcion')
        stock = data.get('stock')
        categoria = data.get('categoria')
        imagenes = data.get('imagenes')
        estado = data.get('estado')

        # Inserta el nuevo producto en la base de datos
        nuevo_producto = {
            'nombre': nombre,
            'precio': float(precio),
            'descripcion': descripcion,
            'stock': int(stock),
            'categoria': categoria,
            'imagenes': imagenes,
            'estado': estado
        }

        productos_collection.insert_one(nuevo_producto)

        # Devuelve una respuesta JSON
        return jsonify({"mensaje": "Producto agregado correctamente"}), 200

    # Si es una solicitud GET, renderiza la página de agregar productos
    return render_template('agregar_producto.html')
 
# Ruta para actualizar un producto (sin pasar ID en la URL)
@app.route('/actualizar_producto', methods=['GET', 'POST'])
def actualizar_producto():
    if request.method == 'POST':
        data = request.get_json()
        id = data.get('_id')
        nombre = data.get('nombre')
        precio = data.get('precio')
        descripcion = data.get('descripcion')
        stock = data.get('stock')
        categoria = data.get('categoria')
        imagenes = data.get('imagenes')
        estado = data.get('estado')

        # Actualizar el producto en la base de datos
        productos_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                'nombre': nombre,
                'precio': float(precio),
                'descripcion': descripcion,
                'stock': int(stock),
                'categoria': categoria,
                'imagenes': imagenes,
                'estado': estado
            }}
        )
        return jsonify({"mensaje": "Producto actualizado correctamente"}), 200
    return render_template('actualizar_producto.html')
# Ruta para eliminar un producto (sin pasar ID en la URL)
@app.route('/eliminar_producto', methods=['GET', 'POST'])
def eliminar_producto():
    if request.method == 'POST':
        data = request.get_json()
        id = data.get('_id')

        # Elimina el producto de la base de datos
        productos_collection.delete_one({"_id": ObjectId(id)})
        return jsonify({"mensaje": "Producto eliminado correctamente"}), 200
    return render_template('eliminar_producto.html')

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000, debug=True)



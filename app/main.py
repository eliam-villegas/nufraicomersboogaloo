from flask import Flask, render_template, jsonify, request, redirect, url_for, session

from database import get_db
from clientes import Database
from bson.objectid import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_KEY')

# Conexion a Postgres
db_cliente = Database()    

@app.route('/registro', methods=['GET'])
def register():
    return render_template('registro.html')

@app.route('/admin')
def admin_route():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Acceso denegado"}), 403
    return render_template('admin.html')


@app.route('/data_base/register_user', methods=['POST'])
def register_user():
    data = request.get_json()
    password_hash = generate_password_hash(data['password'])
    user_id = db_cliente.insert_user(
        name=data['name'],
        email=data['email'],
        address=data['address'],
        password=password_hash
    )
    if user_id:
        return jsonify({"id": user_id, "username": data['name'], "email": data['email']})
    else:
        return jsonify({"error": "Error al registrar el usuario"}), 500
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']
    else:  # Si el método es GET
        username = request.args.get('username')
        password = request.args.get('password')

    if username == os.getenv('ADMIN_USER') and password == os.getenv('ADMIN_PASS'):
        session['user_id'] = 'admin'
        session['is_admin'] = True
        return admin_panel()
    
    user = db_cliente.get_user_by_username(username)
    if user and check_password_hash(user['password'], password):
        # Iniciar sesión como usuario normal
        session['user_id'] = user['id']
        session['is_admin'] = False
        return render_template('index.html', username=user['name'])  

    # Si las credenciales son incorrectas
    return jsonify({"error": "Credenciales incorrectas"}), 401

def admin_panel():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    # Obtener todos los usuarios de la base de datos
    users = db_cliente.get_all_users()
    
    # Pasar la lista de usuarios a la plantilla admin.html
    return render_template('admin.html', users=users)

@app.route('/protected')
def protected():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return jsonify({"message": "Bienvenido a la ruta protegida"})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Cierre de sesión exitoso"})

# Conexión a MongoDB
db_productos = get_db()
productos_collection = db_productos['productos']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    productos = list(productos_collection.find({}, {"_id": 1, "nombre": 1, "precio": 1, "descripcion": 1, "imagenes": 1, "stock": 1, "categoria": 1, "estado": 1}))
    for producto in productos:
        producto["_id"] = str(producto["_id"])  # Convertimos el ObjectId en string
    return jsonify({"productos": productos})

@app.route('/productos')
def productos():
    return render_template('productos.html')

@app.route('/carrito')
def carrito():
    return render_template('carrito.html')

@app.route('/usuario')
def usuario():
    print(app.url_map)
    return render_template('usuario.html')

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

from flask import Flask, render_template, jsonify, request, redirect, url_for, session

from carrito import carrito_bp
from database import get_db
from clientes import Database
from carrito import carrito_bp
from bson.objectid import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import os
from datetime import timedelta
from database import get_db_postgres

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.error.transbank_error import TransbankError

load_dotenv()

app = Flask(__name__)
app.secret_key = 'e5f67a4efab7f3c3d5a82a4a27f601b8742e3edbd8ab6df1a68eac73c9d45e3f'
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)  # Duración de la sesión
app.config['SESSION_TYPE'] = 'filesystem'
app.register_blueprint(carrito_bp)

@app.context_processor
def inject_user():
    return dict(username=session.get("username"))


# Configuración de Transbank para el modo de prueba
Transaction.commerce_code = '597055555532'  # Código de comercio de prueba
Transaction.api_key = '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'       # API Key de prueba
Transaction.integration_type = IntegrationType.TEST

# Conexion a Postgres
db_cliente = Database()    

@app.route('/registro', methods=['GET'])
def register():
    return render_template('registro.html')

# -------------------------------------------------- RUTAS TRANSBANK ------------------------------------------------- #
@app.route('/iniciar_pago', methods=['POST'])
def iniciar_pago():
    # Obtén el monto total desde el carrito u otro cálculo
    amount = request.json.get("amount")
    session_id = "sesion12345"  # Puedes generar un ID de sesión único para el usuario
    buy_order = "orden" + str(session_id)  # Generar un ID de orden único
    return_url = url_for('confirmar_pago', _external=True)  # URL de retorno después del pago

    # Crear la transacción con Webpay Plus
    response = Transaction().create(buy_order, session_id, amount, return_url)

    if response:
        # Redirigir al usuario a la URL de pago de Webpay Plus
        return jsonify({"url": response['url'], "token": response['token']})
    else:
        return jsonify({"error": "No se pudo iniciar la transacción"}), 400


@app.route('/confirmar_pago', methods=['GET', 'POST'])
def confirmar_pago():
    # Obtener el token de la transacción desde `GET` o `POST`
    token_ws = request.args.get("token_ws") or request.form.get("token_ws")

    # Verificar que el token no esté vacío o nulo
    if not token_ws:
        return "Token no encontrado", 400

    try:
        # Crear una instancia de Transaction y confirmar la transacción con el token
        transaction = Transaction()
        response = transaction.commit(token_ws)

        # Comprobar si la transacción fue aprobada
        if response.get('response_code') == 0:
            # Renderizar una página de éxito
            return render_template("pago_exitoso.html", detalle=response)
        else:
            # Renderizar una página de rechazo o error
            return render_template("pago_rechazado.html", detalle=response)

    except TransbankError as e:
        # Captura errores de Transbank y los muestra en una página de error
        return f"Error en la transacción: {str(e)}", 500

# -------------------------------------------------- FIN RUTAS TRANSBANK --------------------------------------------- #
@app.route('/admin')
def admin_route():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Acceso denegado"}), 403
    return render_template('admin.html')


@app.route('/data_base/register_user', methods=['POST'])
def register_user():

    username = request.form['name']
    email = request.form['email']
    address = request.form['address']
    password_hash = generate_password_hash(request.form['password'])
    role = 'usuario'

    conn = get_db_postgres()
    cur = conn.cursor()

    try:
        cur.execute("""INSERT INTO users (name,email,address,password,role) VALUES (%s,%s,%s,%s,%s)""",
                    (username,email,address,password_hash,role))
        conn.commit()
        cur.close()
        return redirect(url_for('usuario'))
    except Exception as e:
        conn.rollback()
        cur.close()
        return str(e)
    
@app.route('/visitor', methods=['GET','POST'])
def visitor():
    session['username'] = 'visitante'
    session['role'] = 'invitado'
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['password']
    else:
        email = request.args.get('email')
        password = request.args.get('password')

    user = db_cliente.get_user_by_email(email)

    if user is not None:
        #si las contraseñas coinciden y el correo tambien
        if check_password_hash(user[4],password) and email == user[2]:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[5]

            #si el usuario inicio sesion y tiene el rol de admin
            if 'user_id' in session:
                if session['role'] == "admin":
                    return admin_panel()
                else:
                    #si el usuario inicio sesion pero no es admin
                    return render_template('index.html', username=session['username'])
            else:
                return jsonify({"error": "Rol de cluenta no identificado"}), 402
        else:
            #si las credenciales no son correctas al iniciar la sesion
            return jsonify({"error": "Credenciales incorrectas"}), 401
    else:
        return jsonify({'error': 'Ususario no encontrado o no existe'}), 404



    """if request.method == 'POST':
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
        session['username'] = user['name']
        return render_template('index.html', username=user['name'])  

    # Si las credenciales son incorrectas
    return jsonify({"error": "Credenciales incorrectas"}), 401"""

def admin_panel():
    """if 'user_id' not in session or not session.get('role') == 'admin':
        return redirect(url_for('login'))"""

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

# -------------------------------------------------- RUTAS APIS ------------------------------------------------------ #

@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    page = int(request.args.get('page', 1))
    per_page = 10
    total = productos_collection.count_documents({})
    productos = list(
        productos_collection.find({}, {"nombre": 1, "precio": 1, "stock": 1, "imagenes": 1})
        .skip((page - 1) * per_page)
        .limit(per_page)
    )
    for producto in productos:
        producto["_id"] = str(producto["_id"])
    return jsonify({
        "productos": productos,
        "totalPaginas": (total + per_page - 1) // per_page
    })


# Ruta para obtener un producto por su ID
@app.route('/api/producto/<id>', methods=['GET'])
def obtener_producto(id):

    try:
        producto = productos_collection.find_one({"_id": ObjectId(id)}, {"_id": 1, "nombre": 1, "precio": 1, "descripcion": 1, "imagenes": 1, "stock": 1, "categoria": 1, "estado": 1})
        if producto:
            producto["_id"] = str(producto["_id"])  # Convertir ObjectId a string
            return jsonify(producto)
        return jsonify({"error": "Producto no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "ID inválido"}), 499

# -------------------------------------------------- FIN RUTAS APIS ------------------------------------------------- #

@app.route('/productos')
def productos():
    return render_template('productos.html')

@app.route('/carrito')
def carrito():
    return render_template('carrito.html')

@app.route('/usuario')
def usuario():
    return render_template('usuario.html')

@app.route('/logged')
def logged():
    return render_template('logged.html')

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

@app.route('/producto/<id>')
def detalle_producto(id):
    producto = productos_collection.find_one({"_id": ObjectId(id)})
    if producto:
        producto["_id"] = str(producto["_id"])  # Convertimos ObjectId a string
        return render_template('detalle_producto.html', producto=producto)
    return jsonify({"error": "Producto no encontrado"}), 404

# Ruta para la página de inventario
@app.route('/inventario')
def inventario():
    return render_template('inventario.html')

@app.route('/inventario/detalle_producto/<id>')
def inventario_detalle_producto(id):
    return render_template('inventario_detalle_producto.html', producto_id=id)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000, debug=True)

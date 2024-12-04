from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from correo_flask import enviar_correo_confirmacion, init_mail
from database import get_db, restar_inventario, crear_orden
from clientes import Database
from carrito import carrito_bp, obtener_productos_comprados, vaciar_carrito
from bson.objectid import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import os
from datetime import timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.error.transbank_error import TransbankError
import math

load_dotenv()

app = Flask(__name__)
app.secret_key = 'e5f67a4efab7f3c3d5a82a4a27f601b8742e3edbd8ab6df1a68eac73c9d45e3f'
app.register_blueprint(carrito_bp)

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)  # Duración de la sesión
@app.context_processor
def inject_user():
    return dict(username=session.get("username"))


# Configuración de Transbank para el modo de prueba
Transaction.commerce_code = '597055555532'  # Código de comercio de prueba
Transaction.api_key = '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'       # API Key de prueba
Transaction.integration_type = IntegrationType.TEST

# Conexion a Postgres
db_cliente = Database()

# Conexión a MongoDB
db_productos = get_db()
productos_collection = db_productos['productos']

mail = init_mail(app)

# -------------------------------------------------- RUTAS AUTH ------------------------------------------------- #
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    return render_template('registro.html')

@app.route('/register', methods=['POST'])
def register():
    # Obtener los datos JSON de la solicitud
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    address = data.get('address')

    if not username or not email or not password or not address:
        return jsonify({"success": False, "message": "Todos los campos son requeridos"}), 400

    # Verificar si el correo electrónico ya está registrado
    user = db_cliente.get_user_by_email(email)
    if user:
        return jsonify({"success": False, "message": "El correo electrónico ya está registrado"}), 400

    # Insertar el nuevo usuario en la base de datos
    user_id = db_cliente.insert_user(username, email, address, password)

    if user_id:
        return jsonify({"success": True, "message": "Registro exitoso"})
    else:
        return jsonify({"success": False, "message": "Hubo un error al registrar el usuario"}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Si el métodoo es GET, solo renderizamos la página de login (usuario.html)
        return render_template('usuario.html')

    if request.method == 'POST':
        # Si el métodoo es POST, procesamos el login
        data = request.get_json()  # Recibimos los datos JSON del formulario
        email = data.get('email')
        password = data.get('password')

        # Verificar las credenciales del usuario
        token = db_cliente.verify_user(email, password)

        if token:
            user = db_cliente.get_user_by_email(email)
            session['username'] = user['name']
            session['role'] = user['role']
            return jsonify({"success": True, "token": token})
        else:
            return jsonify({"success": False, "message": "Credenciales incorrectas"}), 401
# -------------------------------------------------- FIN RUTAS AUTH ------------------------------------------------- #

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

            productos_comprados = obtener_productos_comprados()

            restar_inventario(productos_comprados)

            crear_orden(response, productos_comprados)

            vaciar_carrito()

            #correo_destino = session.get('email') --- produccion
            correo_destino = 'jesonico258@gmail.com'
            enviar_correo_confirmacion(app, response, productos_comprados, correo_destino)

            # Renderizar una página de éxito
            return render_template("pago_exitoso.html", detalle=response)
        else:
            # Renderizar una página de rechazo o error
            return render_template("pago_rechazado.html", detalle=response)

    except TransbankError as e:
        # Captura errores de Transbank y los muestra en una página de error
        return f"Error en la transacción: {str(e)}", 500

def crear_orden(response, productos_comprados):

    ordenes = db_productos['ordenes']

    # Crear la orden con los productos y detalles del pago
    orden = {
        "orden_id": response.get('buy_order'),
        "estado": "pendiente",  # O el estado que desees asignar
        "productos": productos_comprados,
        "total": response.get('amount'),
        "usuario_id": session.get('user_id'),  # O el ID del usuario logueado
        "fecha": datetime.datetime.utcnow(),
    }

    # Insertar la orden en la base de datos
    ordenes.insert_one(orden)

# -------------------------------------------------- FIN RUTAS TRANSBANK --------------------------------------------- #
@app.route('/admin')
def admin_route():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Acceso denegado"}), 403
    return render_template('admin.html')

def admin_panel():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('usuario'))

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
    session.pop('username', None)
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('usuario'))


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

@app.route('/admin/clientes', methods=['GET'])
def ver_clientes():
    if not session.get('role') == 'admin':
        flash('Acceso denegado. Solo los administradores pueden ver esta página.', 'danger')
        return redirect(url_for('index'))  # Redirigimos a la página principal si no es admin

    # Paginación
    page = request.args.get('page', 1, type=int)  # Página actual, por defecto es 1
    limit = 10  # Número de clientes por página
    offset = (page - 1) * limit  # Desplazamiento para la consulta

    # Usamos el método `get_all_users` para obtener los usuarios con paginación
    clientes = db_cliente.get_all_users(limit, offset)

    # Contamos el total de clientes para calcular el número de páginas
    with db_cliente.connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users")
        total_clientes = cursor.fetchone()[0]
        total_paginas = math.ceil(total_clientes / limit)  # Número total de páginas

    return render_template('admin_clientes.html', clientes=clientes, page=page, total_paginas=total_paginas)

@app.route('/admin/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    if not session.get('role') == 'admin':
        flash('Acceso denegado. Solo los administradores pueden editar clientes.', 'danger')
        return redirect(url_for('index'))  # Redirigimos si no es admin

    # Obtener los datos del cliente con el ID proporcionado, incluyendo los roles
    cliente = db_cliente.get_user_by_id(id)

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        direccion = request.form['direccion']
        roles_seleccionados = request.form.getlist('roles')  # Roles seleccionados (pueden ser múltiples)

        # Actualizar los datos básicos del cliente
        with db_cliente.connection.cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET name = %s, email = %s, address = %s
                WHERE id = %s
            """, (nombre, email, direccion, id))
            db_cliente.connection.commit()

        # Actualizar los roles del cliente
        # Primero, eliminamos los roles existentes
        with db_cliente.connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM user_roles WHERE user_id = %s
            """, (id,))
            db_cliente.connection.commit()

        # Luego, insertamos los nuevos roles
        for role in roles_seleccionados:
            with db_cliente.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES (%s, (SELECT id FROM roles WHERE name = %s))
                """, (id, role))
                db_cliente.connection.commit()

        flash('Cliente actualizado correctamente', 'success')
        return redirect(url_for('ver_clientes'))

    # Obtener todos los roles disponibles para elegir en el formulario
    with db_cliente.connection.cursor() as cursor:
        cursor.execute("SELECT name FROM roles")
        roles_disponibles = [row[0] for row in cursor.fetchall()]

    return render_template('editar_cliente.html', cliente=cliente, roles_disponibles=roles_disponibles)


@app.route('/admin/eliminar_cliente/<int:id>', methods=['POST'])
def eliminar_cliente(id):
    if not session.get('role') == 'admin':
        flash('Acceso denegado. Solo los administradores pueden eliminar clientes.', 'danger')
        return redirect(url_for('index'))  # Redirigimos si no es admin

    db_cliente.execute("DELETE FROM users WHERE id = %s", (id,))
    db_cliente.commit()

    flash('Cliente eliminado correctamente', 'danger')
    return redirect(url_for('ver_clientes'))


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000, debug=True)

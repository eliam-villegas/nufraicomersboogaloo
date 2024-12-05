from flask import Blueprint, jsonify, session, request
from bson.objectid import ObjectId
from database import get_db

carrito_bp = Blueprint('carrito', __name__)
db = get_db()
productos_collection = db['productos']

# Inicializar el carrito en la sesión
def iniciar_carrito():
    if 'carrito' not in session:
        session['carrito'] = []

# Crear (Añadir) un producto al carrito
@carrito_bp.route('/api/carrito/agregar', methods=['POST'])
def agregar_al_carrito():
    iniciar_carrito()
    data = request.get_json()
    producto_id = data.get("producto_id")
    cantidad = data.get("cantidad", 1)

    # Verificar si el producto existe en la base de datos
    producto = productos_collection.find_one({"_id": ObjectId(producto_id)})
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    # Verificar si el producto ya está en el carrito
    for item in session['carrito']:
        if item['producto_id'] == producto_id:
            item['cantidad'] += cantidad
            session.modified = True
            return jsonify({"mensaje": "Cantidad actualizada en el carrito"}), 200

    # Si no está en el carrito, agregarlo
    session['carrito'].append({"producto_id": producto_id, "cantidad": cantidad})
    session.modified = True
    return jsonify({"mensaje": "Producto agregado al carrito"}), 200

# Leer (Obtener) el contenido del carrito
@carrito_bp.route('/api/carrito', methods=['GET'])
def obtener_carrito():
    iniciar_carrito()
    carrito = []
    for item in session['carrito']:
        producto = productos_collection.find_one({"_id": ObjectId(item['producto_id'])})
        if producto:
            carrito.append({
                "producto_id": str(producto["_id"]),
                "nombre": producto["nombre"],
                "precio": producto["precio"],
                "cantidad": item["cantidad"],
                "subtotal": producto["precio"] * item["cantidad"]
            })
    return jsonify({"carrito": carrito})

# Actualizar la cantidad de un producto en el carrito
@carrito_bp.route('/api/carrito/actualizar', methods=['POST'])
def actualizar_carrito():
    iniciar_carrito()
    data = request.get_json()
    producto_id = data.get("producto_id")
    nueva_cantidad = data.get("cantidad")

    for item in session['carrito']:
        if item['producto_id'] == producto_id:
            item['cantidad'] = nueva_cantidad
            session.modified = True
            return jsonify({"mensaje": "Cantidad actualizada en el carrito"}), 200

    return jsonify({"error": "Producto no encontrado en el carrito"}), 404

# Eliminar un producto del carrito
@carrito_bp.route('/api/carrito/eliminar', methods=['POST'])
def eliminar_del_carrito():
    iniciar_carrito()
    data = request.get_json()
    producto_id = data.get("producto_id")

    session['carrito'] = [item for item in session['carrito'] if item['producto_id'] != producto_id]
    session.modified = True
    return jsonify({"mensaje": "Producto eliminado del carrito"}), 200

def vaciar_carrito():
    return session.pop('carrito', None)
def obtener_productos_comprados():
    """
    Obtiene los productos comprados desde el carrito de la sesión del usuario.
    Esta función solo se usa para el procesamiento post-compra, no para mostrar en el frontend.
    """
    carrito = []
    # Verifica si el carrito existe en la sesión
    if 'carrito' in session:
        for item in session['carrito']:
            # Recuperamos el producto de MongoDB usando el ID del producto
            producto = productos_collection.find_one({"_id": ObjectId(item['producto_id'])})
            if producto:
                carrito.append({
                    "producto_id": str(producto["_id"]),
                    "nombre": producto["nombre"],
                    "precio": producto["precio"],
                    "cantidad": item["cantidad"],
                    "subtotal": producto["precio"] * item["cantidad"]
                })
    return carrito  # Ahora se devuelve una lista de productos
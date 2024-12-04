from pymongo import MongoClient
from flask import Flask, session
from bson.objectid import ObjectId
import datetime

# Conectar a la base de datos
def get_db():
    client = MongoClient('mongodb+srv://benjaminsilva:benjaminsilva@cluster0.uawrn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    db = client['mi_ecommerce']
    return db

def restar_inventario(productos_comprados):
    """Resta el inventario de los productos comprados en MongoDB"""
    db = get_db()
    productos = db['productos']  # Colección de productos

    for producto in productos_comprados:
        producto_id = producto['producto_id']  # Aseguramos que obtenemos el ID correcto
        cantidad_comprada = producto['cantidad']  # Obtenemos la cantidad comprada

        # Verificar que el producto exista en la base de datos antes de restar el inventario
        producto_db = productos.find_one({"_id": ObjectId(producto_id)})
        if producto_db:
            # Restar la cantidad comprada del inventario del producto
            productos.update_one(
                {"_id": ObjectId(producto_id)},  # Buscamos el producto por su ID
                {"$inc": {"stock": -cantidad_comprada}}  # Restamos la cantidad comprada del stock
            )
        else:
            print(f"Producto con ID {producto_id} no encontrado en la base de datos.")

def crear_orden(response, productos_comprados):
    """Crea una nueva orden en MongoDB"""

    db = get_db()  # Reemplaza con el nombre de tu base de datos
    ordenes = db['ordenes']  # Colección de órdenes

    # Crear la orden con los productos y detalles del pago
    orden = {
        "orden_id": response.get('buy_order'),
        "estado": "pendiente",  # O el estado que desees asignar
        "productos": productos_comprados,
        "total": response.get('amount'),
        "usuario_id": session.get('email'),  # O el ID del usuario logueado
        "fecha": datetime.datetime.utcnow(),
    }

    # Insertar la orden en la base de datos
    ordenes.insert_one(orden)
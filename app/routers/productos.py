from fastapi import APIRouter
from app.database import get_db

router = APIRouter()

# Obtenemos la referencia a la colección de productos
db = get_db()
productos_collection = db['productos']

# Ruta para obtener todos los productos
@router.get("/productos/")
def obtener_productos():
    productos = list(productos_collection.find({}, {"_id": 0, "nombre": 1, "precio": 1, "descripcion": 1, "categoria": 1}))
    return {"productos": productos}

# Ruta para agregar un nuevo producto
@router.post("/productos/")
def agregar_producto(producto: dict):
    productos_collection.insert_one(producto)
    return {"message": "Producto agregado exitosamente"}

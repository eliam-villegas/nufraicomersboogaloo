from flask_sqlalchemy import SQLAlchemy
import time

# Crear la instancia de SQLAlchemy
db = SQLAlchemy()

class Database:
    def __init__(self, app):
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@postgres:5432/mydb'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)  # Asociar db con la aplicación
        
        # Reintento de conexión a la base de datos
        with self.app.app_context():
            connected = False
            retries = 5
            while not connected and retries > 0:
                try:
                    db.create_all()
                    connected = True
                except Exception as e:
                    print(f"Error al conectar con la base de datos: {e}")
                    print("Reintentando en 5 segundos...")
                    time.sleep(5)
                    retries -= 1

# Modelo User definido fuera de la clase Database
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Modelo Purchase definido fuera de la clase Database
class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref=db.backref('purchases', lazy=True))

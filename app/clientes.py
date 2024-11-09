from flask import Flask
from flask_sqlalchemy import SQLAlchemy

class Database:
    def __init__(self, app: Flask):
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@postgres:5432/mydb'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.db = SQLAlchemy(self.app)

        # Crear todas las tablas en la base de datos si no existen
        with self.app.app_context():
            self.db.create_all()

    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password = db.Column(db.String(200), nullable=False)

    class Purchase(db.Model):
        __tablename__ = 'purchases'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        product_name = db.Column(db.String(100), nullable=False)
        amount = db.Column(db.Integer, nullable=False)
        user = db.relationship('User', backref=db.backref('purchases', lazy=True))

    def add_user(self, username, email, password):
        new_user = self.User(username=username, email=email, password=password)
        self.db.session.add(new_user)
        self.db.session.commit()
        return new_user

    def get_users(self):
        return self.User.query.all()

    def add_purchase(self, user_id, product_name, amount):
        new_purchase = self.Purchase(user_id=user_id, product_name=product_name, amount=amount)
        self.db.session.add(new_purchase)
        self.db.session.commit()
        return new_purchase

    def get_purchases_by_user(self, user_id):
        return self.Purchase.query.filter_by(user_id=user_id).all()

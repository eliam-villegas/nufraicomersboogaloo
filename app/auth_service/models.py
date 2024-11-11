from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model): 
    __tablename__ = "usuarios" 
    user_id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(50), unique=True, nullable=False) 
    password_hash = db.Column(db.String(255), nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False) 
    phone_number = db.Column(db.String(20))
    user_role = db.column(db.String(50)) 
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    activo = db.Column(db.Boolean, nullable=False)
    
    def set_password(self, password): 
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8') 
        
    def check_password(self, password): 
        return bcrypt.check_password_hash(self.password_hash, password) 
    
class Card(db.Model): 
    __tablename__ = "cards" 
    card_id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE')) 
    card_number = db.Column(db.String(16), nullable=False) 
    expiration_date = db.Column(db.Date, nullable=False) 
    cvv = db.Column(db.String(4), nullable=False)
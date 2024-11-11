from flask import Blueprint, jsonify, request, render_template, Flask, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, db
import psycopg2 

auth = Blueprint('auth_service', __name__)

conn = psycopg2.connect( 
    host="postgres", 
    database="mydb", 
    user="postgres", 
    password="password"
)

@auth.route('/register', methods=['GET', 'POST']) 
def register(): 
    if request.method == 'POST': 
        username = request.form['username'] 
        email = request.form['email'] 
        password = request.form['password'] 
        phone_number = request.form['phone_number'] 
        password_hash = generate_password_hash(password) 
        user_role = 'cliente'
        cur = conn.cursor() 

        try: 
            cur.execute(""" INSERT INTO usuarios (username, email, password_hash, phone_number,user_role) VALUES (%s, %s, %s, %s,%s)""",
                         (username, email, password_hash, phone_number,user_role)) 
            conn.commit() 
            cur.close() 

            return redirect(url_for('auth_service.login')) 
        except Exception as e: 
            conn.rollback() 
            cur.close() 
            return str(e) 
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print(f"Received email: {email}, password: {password}")

        # Aquí puedes agregar la lógica de autenticación
        if not email or not password:
            return redirect(url_for('auth_service.login'))
        
        # Validación de login
        user = User.query.filter_by(email=email).first()
        print(f"User password from DB: {user.password_hash}")
        if user and check_password_hash(user.password_hash, password):
            # Iniciar sesión
            session['user_id'] = user.user_id
            print(f"User logged in: {session['user_id']}")
            return redirect(url_for('index'))  # o alguna otra página
        else:
            print("Invalid login credentials")
            return redirect(url_for('auth_service.login'))
    
    return render_template('login.html')

@auth.route('/account',methods=['GET','POST'])
def account():
    if 'user_id' in session:
        # Obtén los datos del usuario desde la base de datos
        user = User.query.get(session['user_id'])
        if not g.logged_in:
            return redirect(url_for('auth_service.login'))  # Redirigir si no está logueado

    # Obtener el usuario desde la base de datos usando el 'user_id' de la sesión
        datos = User.query.filter_by(user_id=session['user_id']).first()

        if user is None:
            return redirect(url_for('auth_service.login'))
    
    return render_template('account.html', logged_in=g.logged_in, user=user, datos=datos)
    
@auth.route('/logout',methods=['GET','POST'])
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
        return redirect(url_for('index'))